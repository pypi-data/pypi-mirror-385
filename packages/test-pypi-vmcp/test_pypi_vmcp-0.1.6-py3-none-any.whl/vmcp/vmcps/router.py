import logging
import traceback
import json
import re
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from vmcp.vmcps.models import (
    VMCPCreateRequest, VMCPUdateRequest, VMCPToolCallRequest, VMCPResourceRequest,
    VMCPPromptRequest, VMCPShareRequest, VMCPInstallRequest, VMCPEnvironmentVariablesRequest,
    StatsFilterRequest, StatsResponse, LogEntry, StatsSummary, VMCPConfig, VMCPShareState
)
from vmcp.storage.database import get_db, SessionLocal
from sqlalchemy.orm import Session
from vmcp.storage.dummy_user import UserContext
from vmcp.storage.dummy_user import get_user_context
from vmcp.mcps.mcp_configmanager import MCPConfigManager
from vmcp.mcps.mcp_client import MCPClientManager, AuthenticationError
from vmcp.vmcps.vmcp_config_manger import VMCPConfigManager
from vmcp.mcps.models import MCPServerConfig, MCPTransportType, MCPConnectionStatus
from vmcp.storage.base import StorageBase
from vmcp.storage.models import VMCPStats, VMCP
from datetime import datetime
import copy
import random

router = APIRouter(prefix="/vmcps", tags=["vMCPs"])

logger = logging.getLogger(__name__)

# Request/Response models for Python tool generation
class CollectionVariable(BaseModel):
    key: str
    value: str
    description: Optional[str] = None
    type: Optional[str] = "string"

# Request/Response models for Python function parsing
class PythonFunctionParameter(BaseModel):
    name: str
    description: str
    required: bool
    type: str
    default_value: Optional[Any] = None

class PythonFunctionInfo(BaseModel):
    name: str
    parameters: List[PythonFunctionParameter]
    returnType: Optional[str] = None
    docstring: Optional[str] = None

class ParsePythonFunctionRequest(BaseModel):
    code: str

class ParsePythonFunctionResponse(BaseModel):
    functions: List[PythonFunctionInfo]

class CollectionMetadata(BaseModel):
    name: str
    description: Optional[str] = None
    variables: List[CollectionVariable] = []
    baseUrl: Optional[str] = None

class GeneratePythonToolsRequest(BaseModel):
    collection: Dict[str, Any]
    collectionType: str = "postman"
    selectedIndices: List[str] = []

class GeneratedTool(BaseModel):
    name: str
    method: str
    url: str
    description: str
    code: str
    parameters: Dict[str, Any]
    collectionMetadata: CollectionMetadata

class GeneratePythonToolsResponse(BaseModel):
    success: bool
    tools: List[GeneratedTool]
    collectionMetadata: CollectionMetadata
    message: Optional[str] = None

# Helper functions for Python code generation
def slugify_to_name(input_str: str) -> str:
    """Convert text to snake_case"""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', input_str)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower().replace(' ', '_').replace('-', '_')

def detect_api_key_from_headers(headers: Dict[str, str]) -> Optional[Dict[str, str]]:
    """Detect API key from headers"""
    for key, value in headers.items():
        lower = key.lower()
        if lower == 'authorization' and re.search(r'bearer|api[-_ ]?key|token', value or '', re.I):
            return {"headerName": key, "varName": "API_TOKEN", "location": "header"}
        if re.search(r'api[-_ ]?key|x-api-key|apikey', lower):
            return {"headerName": key, "varName": "API_KEY", "location": "header"}
    return None

def detect_api_key_from_postman_auth(auth: Dict[str, Any]) -> Optional[Dict[str, str]]:
    """Detect API key from Postman auth"""
    if not auth or not auth.get('type'):
        return None
    
    auth_type = auth['type']
    
    def get_value(arr: List[Dict], key: str) -> Optional[str]:
        if not isinstance(arr, list):
            return None
        found = next((e for e in arr if e.get('key') == key), None)
        return found.get('value') if found else None
    
    if auth_type == 'apikey' and auth.get('apikey'):
        key = get_value(auth['apikey'], 'key') or 'X-API-Key'
        value = get_value(auth['apikey'], 'value') or '{{API_KEY}}'
        location = get_value(auth['apikey'], 'in') or 'header'
        return {"headerName": key, "varName": "API_KEY", "location": location}
    
    if auth_type == 'bearer' and auth.get('bearer'):
        token = get_value(auth['bearer'], 'token') or '{{API_TOKEN}}'
        return {"headerName": "Authorization", "varName": "API_TOKEN", "location": "header"}
    
    return None

def generate_python_function(endpoint: Dict[str, Any], collection_metadata: CollectionMetadata) -> str:
    """Generate Python function code for an endpoint"""
    func_name = slugify_to_name(endpoint.get('name', 'unnamed_endpoint'))
    method = endpoint.get('method', 'GET')
    url = endpoint.get('url', '')
    description = endpoint.get('description', f'Function to {method} {endpoint.get("name", "")}')
    
    # Extract parameters
    path_params = endpoint.get('pathParams', [])
    query_params = endpoint.get('queryParamsMeta', [])
    body_params = endpoint.get('body', {})
    
    # Build function parameters
    all_params = []
    for param in path_params:
        all_params.append(f"{param['name']}: str")
    
    for param in query_params:
        param_def = f"{param['name']}: str"
        if param.get('default') is not None:
            param_def += f' = "{param["default"]}"'
        elif not param.get('required', False):
            param_def += " = None"
        all_params.append(param_def)
    
    if body_params and isinstance(body_params, dict):
        all_params.append("body: dict = None")
    
    params_str = ", ".join(all_params)
    
    # Build docstring
    docstring_params = []
    for param in path_params:
        param_name = param['name']
        param_desc = param.get('description', f'Path parameter: {param_name}')
        docstring_params.append(f"     * @param {{string}} {param_name} - {param_desc}")
    
    for param in query_params:
        param_name = param['name']
        param_desc = param.get('description', f'Query parameter: {param_name}')
        docstring_params.append(f"     * @param {{string}} {param_name} - {param_desc}")
    
    if body_params and isinstance(body_params, dict):
        docstring_params.append("     * @param {Object} body - Request body parameters")
    
    docstring_params_str = "\n".join(docstring_params)
    
    # Build URL construction
    base_url = collection_metadata.baseUrl or ""
    if base_url:
        # Replace collection variables
        for variable in collection_metadata.variables:
            if variable.key != 'baseUrl':
                base_url = base_url.replace(f"{{{{{variable.key}}}}}", variable.value)
    
    # Replace path parameters
    path = url
    if path.startswith(base_url):
        path = path[len(base_url):]
    
    for param in path_params:
        param_name = param['name']
        path = path.replace(f":{param_name}", f"{{{param_name}}}")
    
    url_construction = f'    base_url = "{base_url}"\n'
    url_construction += f'    url = base_url + "{path}"\n'
    
    # Build query parameters
    query_code = ""
    if query_params:
        query_code = "    params = {}\n"
        for param in query_params:
            query_code += f"    if {param['name']} is not None:\n"
            query_code += f"        params[\"{param['name']}\"] = {param['name']}\n"
        query_code += "    if params:\n"
        query_code += '        query_string = "&".join([f"{k}={v}" for k, v in params.items()])\n'
        query_code += '        url += "?" + query_string\n'
    
    # Build headers
    headers_code = '    headers = {\n'
    headers_code += "        'Content-Type': 'application/json',\n"
    headers_code += "        'Accept': 'application/json'\n"
    headers_code += "    }\n"
    
    # Add authorization
    api_key = endpoint.get('apiKey')
    if api_key:
        env_var_name = api_key.get('varName', 'API_TOKEN')
        headers_code += f'\n    token = os.environ.get("{env_var_name}")\n'
        headers_code += "    if token:\n"
        headers_code += f"        headers['{api_key['headerName']}'] = f\"Bearer {{token}}\"\n"
    elif collection_metadata.variables:
        # Check for common API key variables in collection
        api_key_var = next((v for v in collection_metadata.variables 
                           if 'api' in v.key.lower() and ('key' in v.key.lower() or 'token' in v.key.lower())), None)
        if api_key_var:
            headers_code += f'\n    # Using collection variable: {api_key_var.key}\n'
            headers_code += f'    token = os.environ.get("{api_key_var.key.upper()}")\n'
            headers_code += "    if token:\n"
            headers_code += '        headers["Authorization"] = f"Bearer {token}"\n'
    
    # Build body
    body_code = ""
    if body_params and isinstance(body_params, dict):
        body_code = "\n    if body is None:\n"
        body_code += "        body = {}\n"
    
    # Build request call
    request_code = "\n    try:\n"
    request_code += f"        response = requests.{method.lower()}(url, headers=headers"
    if body_params and isinstance(body_params, dict):
        request_code += ", json=body"
    request_code += ")\n"
    request_code += "        response.raise_for_status()\n"
    request_code += "        return response.json()\n"
    request_code += "    except requests.exceptions.RequestException as e:\n"
    request_code += "        return {\"error\": str(e)}\n"
    
    # Build collection variables comment
    collection_vars_comment = ""
    if collection_metadata.variables:
        collection_vars_comment = "# Collection Variables Available:\n"
        for var in collection_metadata.variables:
            collection_vars_comment += f"# - {var.key}: {var.description or var.value}\n"
        collection_vars_comment += "# Set these as environment variables or modify the base_url below\n"
    
    # Build parameters for tool definition
    parameters = {}
    required = []
    
    for param in path_params:
        param_name = param['name']
        param_desc = param.get('description', f"Path parameter: {param_name}")
        parameters[param_name] = {
            "type": "string",
            "description": param_desc
        }
        required.append(param_name)
    
    for param in query_params:
        param_name = param['name']
        param_desc = param.get('description', f"Query parameter: {param_name}")
        parameters[param_name] = {
            "type": "string",
            "description": param_desc
        }
        if param.get('required', False):
            required.append(param_name)
    
    if body_params and isinstance(body_params, dict):
        parameters["body"] = {
            "type": "object",
            "description": "Request body parameters"
        }
    
    return f"""{collection_vars_comment}import requests
import os
from typing import Dict, Any, Optional


def {func_name}({params_str}) -> Dict[str, Any]:
    \"\"\"
    {description}
    
    Args:
{docstring_params_str}
    
    Returns:
        Dict[str, Any]: API response
    \"\"\"
{url_construction}{query_code}{headers_code}{body_code}{request_code}


# Tool configuration for {endpoint.get('name', '')}
api_tool = {{
    "function": {func_name},
    "definition": {{
        "type": "function",
        "function": {{
            "name": "{func_name}",
            "description": "{description}",
            "parameters": {{
                "type": "object",
                "properties": {json.dumps(parameters, indent=16)},
                "required": {json.dumps(required)}
            }}
        }}
    }}
}}

# Export the tool for use
"""

@router.post("/generate-python-tools", response_model=GeneratePythonToolsResponse)
async def generate_python_tools(request: GeneratePythonToolsRequest, 
                               user_context: UserContext = Depends(get_user_context)):
    """Generate Python tools from Postman collection or OpenAPI spec"""
    logger.info("📋 Generate Python tools endpoint called")
    logger.info(f"   👤 User context: {user_context.user_id if user_context else 'None'}")
    logger.info(f"   📝 Collection type: {request.collectionType}")
    logger.info(f"   📊 Selected indices: {len(request.selectedIndices)}")
    
    try:
        collection = request.collection
        
        # Extract collection metadata
        collection_metadata = CollectionMetadata(
            name=collection.get('info', {}).get('name', 'Unknown Collection'),
            description=collection.get('info', {}).get('description', ''),
            variables=[
                CollectionVariable(
                    key=var.get('key', ''),
                    value=var.get('value', ''),
                    description=var.get('description', ''),
                    type=var.get('type', 'string')
                ) for var in collection.get('variable', [])
            ],
            baseUrl=next((var.get('value') for var in collection.get('variable', []) 
                         if var.get('key') == 'baseUrl'), None)
        )
        
        # Parse endpoints from collection
        endpoints = []
        
        def process_item(item: Dict[str, Any], path_stack: List[str] = []):
            if 'request' in item:
                # This is an endpoint
                request_data = item['request']
                method = request_data.get('method', 'GET')
                
                # Build URL
                url_data = request_data.get('url', {})
                if isinstance(url_data, str):
                    url = url_data
                else:
                    protocol = url_data.get('protocol', '')
                    host = url_data.get('host', [])
                    path = url_data.get('path', [])
                    
                    if isinstance(host, list):
                        host = '.'.join(host)
                    if isinstance(path, list):
                        path = '/' + '/'.join(path)
                    elif path:
                        path = '/' + path
                    
                    url = f"{protocol}://{host}{path}" if protocol else f"{host}{path}"
                
                # Extract headers
                headers = {}
                for header in request_data.get('header', []):
                    if header.get('key') and header.get('value'):
                        headers[header['key']] = header['value']
                
                # Extract body
                body = None
                body_data = request_data.get('body', {})
                if body_data.get('mode') == 'raw' and body_data.get('raw'):
                    try:
                        body = json.loads(body_data['raw'])
                    except json.JSONDecodeError:
                        body = body_data['raw']
                elif body_data.get('mode') == 'urlencoded' and body_data.get('urlencoded'):
                    body = {}
                    for param in body_data['urlencoded']:
                        if param.get('key'):
                            body[param['key']] = param.get('value', '')
                
                # Extract path parameters
                path_params = []
                if isinstance(url_data, dict):
                    for var in url_data.get('variable', []):
                        path_params.append({
                            'name': var.get('key', ''),
                            'description': var.get('description', ''),
                            'default': var.get('value')
                        })
                
                # Extract query parameters
                query_params = []
                if isinstance(url_data, dict):
                    for query in url_data.get('query', []):
                        query_params.append({
                            'name': query.get('key', ''),
                            'description': query.get('description', ''),
                            'default': query.get('value'),
                            'required': not query.get('disabled', False)
                        })
                
                # Detect API key
                api_key = detect_api_key_from_headers(headers)
                if not api_key:
                    api_key = detect_api_key_from_postman_auth(request_data.get('auth', {}))
                
                endpoint = {
                    'name': item.get('name', 'Unnamed Endpoint'),
                    'method': method,
                    'url': url,
                    'description': request_data.get('description', item.get('name', '')),
                    'headers': headers,
                    'body': body,
                    'pathParams': path_params,
                    'queryParamsMeta': query_params,
                    'apiKey': api_key,
                    'groupPath': path_stack
                }
                
                endpoints.append(endpoint)
            
            # Process nested items
            if 'item' in item:
                next_path = path_stack + [item.get('name', '')] if item.get('name') else path_stack
                for child in item['item']:
                    process_item(child, next_path)
        
        # Process all items in collection
        for item in collection.get('item', []):
            process_item(item, [])
        
        # Generate Python code for each endpoint
        generated_tools = []
        for endpoint in endpoints:
            try:
                code = generate_python_function(endpoint, collection_metadata)
                
                # Build parameters for tool definition
                parameters = {}
                required = []
                
                for param in endpoint.get('pathParams', []):
                    param_name = param['name']
                    param_desc = param.get('description', f"Path parameter: {param_name}")
                    parameters[param_name] = {
                        "type": "string",
                        "description": param_desc
                    }
                    required.append(param_name)
                
                for param in endpoint.get('queryParamsMeta', []):
                    param_name = param['name']
                    param_desc = param.get('description', f"Query parameter: {param_name}")
                    parameters[param_name] = {
                        "type": "string",
                        "description": param_desc
                    }
                    if param.get('required', False):
                        required.append(param_name)
                
                if endpoint.get('body') and isinstance(endpoint['body'], dict):
                    parameters["body"] = {
                        "type": "object",
                        "description": "Request body parameters"
                    }
                
                generated_tool = GeneratedTool(
                    name=endpoint['name'],
                    method=endpoint['method'],
                    url=endpoint['url'],
                    description=endpoint['description'],
                    code=code,
                    parameters={
                        "type": "object",
                        "properties": parameters,
                        "required": required
                    },
                    collectionMetadata=collection_metadata
                )
                
                generated_tools.append(generated_tool)
                
            except Exception as e:
                logger.error(f"   ❌ Error generating tool for endpoint {endpoint.get('name', 'unknown')}: {e}")
                continue
        
        logger.info(f"✅ Generated {len(generated_tools)} Python tools")
        
        return GeneratePythonToolsResponse(
            success=True,
            tools=generated_tools,
            collectionMetadata=collection_metadata,
            message=f"Successfully generated {len(generated_tools)} Python tools"
        )
        
    except Exception as e:
        logger.error(f"   ❌ Error generating Python tools: {e}")
        logger.error(f"   ❌ Exception type: {type(e).__name__}")
        logger.error(f"   ❌ Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to generate Python tools: {str(e)}")

@router.get("/health")
async def health_check():
    # can you return a html so that it can open in a new tab and show
    """Health check endpoint for the unified backend server management"""
    return {"status": "healthy", "service": "1xN Unified Backend - MCP Server Management"}

@router.post("/create")
async def create_vmcp(request: VMCPCreateRequest, 
                      user_context: UserContext = Depends(get_user_context)):
    """Create a new vMCP configuration for the current user"""
    logger.info("📋 Create vMCP endpoint called")
    logger.info(f"   👤 User context: {user_context.user_id if user_context else 'None'}")
    
    try:
        # Get managers from global connection manager
        config_manager = MCPConfigManager(user_context.user_id)
        client_manager = MCPClientManager(config_manager)
        user_vmcp_manager = VMCPConfigManager(user_context.user_id)
        
        # Parse Python functions and update their variables
        updated_custom_tools = []
        for tool in request.custom_tools:
            if tool.get('tool_type') == 'python' and tool.get('code'):
                try:
                    # Parse Python function to extract variables with types
                    import ast
                    from typing import get_origin
                    
                    def map_python_type(type_annotation) -> str:
                        if type_annotation is None:
                            return 'str'
                        
                        if isinstance(type_annotation, str):
                            type_map = {
                                'str': 'str', 'string': 'str',
                                'int': 'int', 'integer': 'int',
                                'float': 'float', 'number': 'float',
                                'bool': 'bool', 'boolean': 'bool',
                                'list': 'list', 'array': 'list',
                                'dict': 'dict', 'object': 'dict',
                                'tuple': 'list', 'set': 'list',
                            }
                            return type_map.get(type_annotation.lower(), 'str')
                        
                        if hasattr(type_annotation, '__name__'):
                            type_map = {
                                'str': 'str', 'int': 'int', 'float': 'float',
                                'bool': 'bool', 'list': 'list', 'dict': 'dict',
                                'tuple': 'list', 'set': 'list',
                            }
                            return type_map.get(type_annotation.__name__, 'str')
                        
                        origin = get_origin(type_annotation)
                        if origin is not None:
                            if origin is list or origin is tuple or origin is set:
                                return 'list'
                            elif origin is dict:
                                return 'dict'
                        
                        return 'str'
                    
                    # Parse the Python code
                    tree = ast.parse(tool['code'])
                    variables = []
                    
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            # Extract parameters
                            for arg in node.args.args:
                                if arg.arg == 'self':
                                    continue
                                    
                                type_annotation = None
                                if arg.annotation:
                                    if isinstance(arg.annotation, ast.Name):
                                        type_annotation = arg.annotation.id
                                    elif isinstance(arg.annotation, ast.Constant):
                                        type_annotation = arg.annotation.value
                                    elif isinstance(arg.annotation, ast.Subscript):
                                        # Handle generic types like list[int], dict[str, str]
                                        if isinstance(arg.annotation.value, ast.Name):
                                            type_annotation = arg.annotation.value.id

                                has_default = (len(node.args.defaults) > 0 and
                                             node.args.args.index(arg) >= len(node.args.args) - len(node.args.defaults))
                                
                                # Extract default value if present
                                default_value = None
                                if has_default:
                                    default_index = node.args.args.index(arg) - (len(node.args.args) - len(node.args.defaults))
                                    if default_index < len(node.args.defaults):
                                        default_ast = node.args.defaults[default_index]
                                        if isinstance(default_ast, ast.Constant):
                                            default_value = default_ast.value
                                        elif isinstance(default_ast, ast.Str):  # Python < 3.8
                                            default_value = default_ast.s
                                        elif isinstance(default_ast, ast.Num):  # Python < 3.8
                                            default_value = default_ast.n
                                        elif isinstance(default_ast, ast.NameConstant):  # Python < 3.8
                                            default_value = default_ast.value
                                        elif isinstance(default_ast, ast.Name):
                                            # Handle variable references (e.g., default=some_var)
                                            default_value = f"@{default_ast.id}"
                                
                                variables.append({
                                    'name': arg.arg,
                                    'description': f"Parameter: {arg.arg}",
                                    'required': not has_default,
                                    'type': map_python_type(type_annotation),
                                    'default_value': default_value
                                })
                            break  # Only process the first function
                    
                    # Update the tool with parsed variables
                    updated_tool = tool.copy()
                    updated_tool['variables'] = variables
                    updated_custom_tools.append(updated_tool)
                    
                except Exception as e:
                    logger.warning(f"Error parsing Python function in tool '{tool.get('name', 'unknown')}': {e}")
                    updated_custom_tools.append(tool)
            else:
                updated_custom_tools.append(tool)
        
        # Create vMCP configuration
        vmcp_id = user_vmcp_manager.create_vmcp_config(
            name=request.name,
            description=request.description,
            system_prompt=request.system_prompt,
            vmcp_config=request.vmcp_config,
            custom_prompts=request.custom_prompts,
            custom_tools=updated_custom_tools,
            custom_context=request.custom_context,
            custom_resources=request.custom_resources,
            custom_resource_uris=request.custom_resource_uris,
            environment_variables=request.environment_variables,
            uploaded_files=request.uploaded_files
        )
        
        if not vmcp_id:
            raise HTTPException(status_code=400, detail="Failed to create vMCP")
        
        # Get the created vMCP details
        vmcp_manager_with_id = VMCPConfigManager(user_context.user_id, vmcp_id)
        vmcp_config = vmcp_manager_with_id.load_vmcp_config()
        
        logger.info(f"✅ Created vMCP: {vmcp_id} ({request.name})")
        return {
            "success": True,
            "vMCP": {
                "id": vmcp_config.id,
                "name": vmcp_config.name,
                "description": vmcp_config.description,
                "system_prompt": vmcp_config.system_prompt,
                "vmcp_config": vmcp_config.vmcp_config,
                "custom_prompts": vmcp_config.custom_prompts,
                "custom_tools": vmcp_config.custom_tools,
                "custom_context": vmcp_config.custom_context,
                "custom_resources": vmcp_config.custom_resources,
                "environment_variables": vmcp_config.environment_variables,
                "uploaded_files": vmcp_config.uploaded_files,
                "created_at": vmcp_config.created_at.isoformat(),
                "updated_at": vmcp_config.updated_at.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"   ❌ Error creating vMCP: {e}")
        logger.error(f"   ❌ Exception type: {type(e).__name__}")
        logger.error(f"   ❌ Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to create vMCP: {str(e)}")

@router.post("/install")
async def install_vmcp_from_remote(request: VMCPInstallRequest, 
                                  user_context: UserContext = Depends(get_user_context)):
    """Install a vMCP from remote source (public or well-known) by copying JSON as-is and adding remote tag"""
    from urllib.parse import unquote
    public_vmcp_id = unquote(request.public_vmcp_id)
    logger.info(f"📋 Install  a public vMCP {public_vmcp_id}")
    logger.info(f"   👤 User context: {user_context.user_id if user_context else 'None'}")
    
    try:
        # Get managers from global connection manager
        config_manager = MCPConfigManager(user_context.user_id)
        client_manager = MCPClientManager(config_manager)
        user_vmcp_manager = VMCPConfigManager(user_context.user_id)
        
        """
        Read the public vMCP details and convert to VMCPConfig
        """
        try:
            public_vmcp = VMCPConfigManager.get_public_vmcp_static(public_vmcp_id)
            if not public_vmcp:
                raise HTTPException(status_code=404, detail=f"Public vMCP '{public_vmcp_id}' not found")
            public_vmcp = VMCPConfig.from_dict(public_vmcp)
        except Exception as e:
            logger.error(f"Error getting public vMCP: {traceback.format_exc()}")
            logger.error(f"Error converting public vMCP to VMCPConfig: {e}")
            raise HTTPException(status_code=404, detail=f"Error converting public vMCP to VMCPConfig: {e}")
        
        logger.info(f"Public vMCP {public_vmcp.id}: {public_vmcp.to_dict().keys()}")
        """
        Create a registry vMCP config from the public vMCP
        """
        try:
            registry_vmcp = public_vmcp.to_vmcp_registry_config()
            public_vmcp_registry_data = {
                "vmcp_registry_config": registry_vmcp.to_dict(),
                "vmcp_config": public_vmcp.to_dict()
            }
        except Exception as e:
            logger.error(f"Error converting public vMCP to VMCPRegistryConfig: {traceback.format_exc()}")
            logger.error(f"Error converting public vMCP to VMCPRegistryConfig: {e}")
            raise HTTPException(status_code=404, detail=f"Error converting public vMCP to VMCPRegistryConfig: {e}")
        
        """
        Update users public vmcp registry with the new registry vMCP
        """
        try:
            user_vmcp_manager.storage.update_public_vmcp_registry(public_vmcp.id, public_vmcp_registry_data, "add")
        except Exception as e:
            logger.error(f"Error updating users public vmcp registry: {traceback.format_exc()}")
            logger.error(f"Error updating users public vmcp registry: {e}")
            raise HTTPException(status_code=404, detail=f"Error updating users public vmcp registry: {e}")

        logger.info(f"Updated user public vMCP registry for Public vMCP {public_vmcp.id}: {public_vmcp.to_dict().keys()}")

        # Process servers in the vMCP config
        processed_servers = []
        selected_servers = registry_vmcp.vmcp_config.get('selected_servers', [])
        logger.info(f"   🔍 Processing {len(selected_servers)} servers from vMCP config for Public vMCP {public_vmcp.id}")
        
        for server in selected_servers:
            server_id = server.server_id
            server_name = server.name
            
            # Skip servers without valid ID or name
            if not server_id and not server_name:
                logger.warning(f"   ⚠️  Skipping server with no ID or name: {server}")
                continue
            
            # Check if server exists in user's config
            existing_server = config_manager.get_server(server_id) if server_id else None
            
            if existing_server:
                # Server exists, ping it to get actual status
                logger.info(f"   🔍 Found existing server: {server_name} ({server_id})")
                try:
                    # Ping server to get real status
                    ping_status = await config_manager.ping_server(server_id, client_manager)
                    logger.info(f"   📡 Server {server_name} ping result: {ping_status.value}")
                    
                    server_copy = server.to_dict()
                    server_copy['auth'] = None  # Reset auth
                    server_copy['session_id'] = None  # Reset session_id
                    server_copy['vmcps_using_server'] = []  # Reset vmcps_using_server
                    # Update server status in config
                    config_manager.update_server_status(server_id, ping_status)
                    e_esrver = config_manager.get_server(server_id)
                    server_copy['status'] = e_esrver.status.value
                    server_copy['vmcps_using_server'] = e_esrver.vmcps_using_server
                    
                    processed_servers.append(server_copy)
                    
                except Exception as e:
                    logger.error(f"   ❌ Error pinging server {server_name}: {e}")
                    # Add server with error status
                    server_copy = server.to_dict()
                    server_copy['status'] = 'error'
                    processed_servers.append(server_copy)
            else:
                # Server doesn't exist, create it from vMCP config
                logger.info(f"   🔧 Creating new server from vMCP config: {server_name}")
                
                try:
                    # Create server config from vMCP data by dereferencing the dictionary
                    from vmcp.mcps.models import MCPServerConfig, MCPTransportType, MCPConnectionStatus
                    
                    # Create a copy of the server dict and reset specific fields
                    server_data = server.to_dict()
                    
                    # Reset the three specific fields
                    server_data['auth'] = None  # Reset auth
                    server_data['session_id'] = None  # Reset session_id
                    server_data['vmcps_using_server'] = [public_vmcp.id]  # Reset vmcps_using_server
                    server_data['status'] = MCPConnectionStatus.DISCONNECTED.value  # Start as disconnected
                    
                    # Create server config from the dictionary
                    server_config = MCPServerConfig.from_dict(server_data)
                    
                    # Add server to config
                    success = config_manager.add_server(server_config)
                    if not success:
                        logger.error(f"   ❌ Failed to create server {server_name}")
                        # Add server with error status
                        server_copy = server.to_dict()
                        server_copy['status'] = 'error'
                        processed_servers.append(server_copy)
                        continue
                    
                    logger.info(f"   ✅ Created server {server_name} with ID: {server_config.server_id}")
                    
                    # Try to ping the new server
                    try:
                        ping_status = await config_manager.ping_server(server_config.server_id, client_manager)
                        logger.info(f"   📡 New server {server_name} ping result: {ping_status.value}")
                        config_manager.update_server_status(server_config.server_id, ping_status)
                        
                        # Add server with actual status
                        server_copy = server.to_dict()
                        server_copy['status'] = ping_status.value
                        processed_servers.append(server_copy)
                        
                    except Exception as e:
                        logger.error(f"   ❌ Error pinging new server {server_name}: {e}")
                        # Add server with error status
                        server_copy = server.to_dict()
                        server_copy['status'] = 'error'
                        processed_servers.append(server_copy)
                        
                except Exception as e:
                    logger.error(f"   ❌ Error creating server {server_name}: {e}")
                    # Add server with error status
                    server_copy = server.to_dict()
                    server_copy['status'] = 'error'
                    processed_servers.append(server_copy)
        
        # Update the vMCP config with processed servers (with actual statuses)
        public_vmcp.vmcp_config['selected_servers'] = processed_servers
        
        
        # Count server statuses
        server_status_counts = {}
        for server in processed_servers:
            status = server.get('status', 'unknown')
            server_status_counts[status] = server_status_counts.get(status, 0) + 1
        
        logger.info(f"✅ Installed vMCP from remote: {public_vmcp.id} ({public_vmcp.name})")
        logger.info(f"   📊 Server status summary: {server_status_counts}")
        
        return {
            "success": True,
            "message": f"vMCP '{public_vmcp.name}' installed successfully",
            "vmcp_id": public_vmcp.id,
            "servers_processed": len(processed_servers),
            "server_status_summary": server_status_counts,
            "servers": processed_servers
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"   ❌ Error installing vMCP from remote: {e}")
        logger.error(f"   ❌ Exception type: {type(e).__name__}")
        logger.error(f"   ❌ Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to install vMCP from remote: {str(e)}")

@router.get("/list")
async def list_vmcps(user_context: UserContext = Depends(get_user_context)):
    """List all available vMCP configurations for the current user with full configuration data"""
    logger.info("📋 List vMCPs endpoint called")
    logger.info(f"   👤 User context: {user_context.user_id if user_context else 'None'}")
    
    try:
        # Get managers from global connection manager
        config_manager = MCPConfigManager(user_context.user_id)
        client_manager = MCPClientManager(config_manager)
        user_vmcp_manager = VMCPConfigManager(user_context.user_id)
        vmcps = user_vmcp_manager.list_available_vmcps()
        logger.info(f"   📊 Found {len(vmcps)} vMCPs")
        # # Return full vMCP configuration data instead of just VMCPInfo
        # full_vmcp_data = []
        # vmcp_manager = VMCPConfigManager(user_context.user_id)
        # for vmcp in tqdm(vmcps, desc="Loading vMCPs"):
        #     try:
        #         # Load the full configuration for each vMCP
                
        #         full_config = vmcp_manager.load_vmcp_config(specific_vmcp_id=vmcp['id'])
        #             # Create the full vMCP data object
        #         vmcp_data = full_config.for_vmcp_listing()
        #         full_vmcp_data.append(vmcp_data)
                    
        #     except Exception as e:
        #         logger.warn(f"   ⚠️ Failed to load full config for vMCP {vmcp.get('id', 'unknown')}: {e}")
        #         # Fallback to basic info if full config fails to load
        #         full_vmcp_data.append(vmcp)
        
        # return vmcps
        response_data = {
            "private": vmcps,
            "public": []  # Empty for now, public vMCPs are handled by /public/list endpoint
        }
        return response_data
        
    except Exception as e:
        logger.error(f"   ❌ Error listing vMCPs: {e}")
        logger.error(f"   ❌ Exception type: {type(e).__name__}")
        logger.error(f"   ❌ Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to list vMCPs: {str(e)}")

# add refresh endpoint
@router.post("/{vmcp_id}/refresh")
async def refresh_vmcp(vmcp_id: str, user_context: UserContext = Depends(get_user_context)):
    """Refresh a vMCP configuration for the current user - checks servers and updates status/capabilities"""
    logger.info(f"📋 Refresh vMCP endpoint called for vmcp_id: {vmcp_id}")
    logger.info(f"   👤 User context: {user_context.user_id if user_context else 'None'}")
    
    try:
        # Get managers from global connection manager
        config_manager = MCPConfigManager(user_context.user_id)
        client_manager = MCPClientManager(config_manager)
        user_vmcp_manager = VMCPConfigManager(user_context.user_id, vmcp_id)
        
        # Load the vMCP configuration
        vmcp_config = user_vmcp_manager.load_vmcp_config()
        if not vmcp_config:
            raise HTTPException(status_code=404, detail=f"vMCP '{vmcp_id}' not found")
        
        # Process servers in the vMCP config
        processed_servers = []
        selected_servers = vmcp_config.vmcp_config.get('selected_servers', [])
        logger.info(f"   🔍 Processing {len(selected_servers)} servers from vMCP config for vMCP {vmcp_id}")
        
        for server in selected_servers:
            server_id = server.get('server_id')
            server_name = server.get('name')
            server_data = server
            
            # Check if server already exists in server list
            existing_server = config_manager.get_server_by_id(server_id)
            
            mcp_server = None
            
            if existing_server:
                # Server exists, use it
                logger.info(f"   ✅ Found existing server: {existing_server.name} ({existing_server.server_id})")
                mcp_server = existing_server
                server_name  = mcp_server.name
                server_id = mcp_server.server_id
            else:
                user_vmcp_manager._create_server_from_vmcp_config(server_data, vmcp_id)
                mcp_server = config_manager.get_server_by_id(server_id,from_db=True)
                logger.info(f"   ✅ Fetched new server from db: {mcp_server.name if mcp_server else 'None'} ({mcp_server.server_id if mcp_server else 'None'})")
            
            # Try to connect and discover capabilities and upate server config
            try:
                logger.info(f"   🔗 Attempting to connect to server: {server_name}")
                if mcp_server:
                    # Ping the server to get current status
                    try:
                        current_status = await client_manager.ping_server(mcp_server.server_id)
                        logger.info(f"   🔍 Server {mcp_server.name}: ping result = {current_status.value}")
                    except AuthenticationError as e:
                        logger.error(f"   ❌ Traceback: {traceback.format_exc()}")
                        logger.error(f"   ❌ Authentication error for server {mcp_server.name}: {e}")
                        current_status = MCPConnectionStatus.AUTH_REQUIRED
                    except Exception as e:
                        logger.error(f"   ❌ Traceback: {traceback.format_exc()}")
                        logger.error(f"   ❌ Error pinging server {mcp_server.name}: {mcp_server.server_id}: {e}")
                        current_status = MCPConnectionStatus.UNKNOWN

                    mcp_server.status = current_status
                    
                    # Discover capabilities
                    try:
                        capabilities = await client_manager.discover_capabilities(mcp_server.server_id)
                    except Exception as e:
                        logger.error(f"   ❌ Error discovering capabilities for server {mcp_server.name}: {mcp_server.server_id}: {e}")
                        logger.error(f"   ❌ Traceback: {traceback.format_exc()}")
                        capabilities = None

                
                    if capabilities:
                        # Update server config with discovered capabilities
                        if capabilities.get('tools',[]):
                            mcp_server.tools = capabilities.get('tools', [])
                        if capabilities.get('resources',[]):
                            mcp_server.resources = capabilities.get('resources', [])
                        if capabilities.get('prompts',[]):
                            mcp_server.prompts = capabilities.get('prompts', [])
                        if capabilities.get('tool_details',[]):
                            mcp_server.tool_details = capabilities.get('tool_details', [])
                        if capabilities.get('resource_details',[]):
                            mcp_server.resource_details = capabilities.get('resource_details', [])
                        if capabilities.get('resource_templates',[]):
                            mcp_server.resource_templates = capabilities.get('resource_templates', [])
                        if capabilities.get('resource_template_details',[]):
                            mcp_server.resource_template_details = capabilities.get('resource_template_details', [])
                        if capabilities.get('prompt_details',[]):
                            mcp_server.prompt_details = capabilities.get('prompt_details', [])
                        
                        mcp_server.capabilities = {
                            "tools": bool(mcp_server.tools and len(mcp_server.tools) > 0),
                            "resources": bool(mcp_server.resources and len(mcp_server.resources) > 0),
                            "prompts": bool(mcp_server.prompts and len(mcp_server.prompts) > 0)
                        }

                    vmcps_using_server = mcp_server.vmcps_using_server
                    if vmcps_using_server:
                        logger.info(f"   🔄 vMCPs using server {mcp_server.server_id}: {vmcps_using_server}")
                        # Add vmcp id to vmcps_using_server
                        vmcps_using_server.append(vmcp_id)
                        mcp_server.vmcps_using_server = list(set(vmcps_using_server))
                    else:
                        mcp_server.vmcps_using_server = [vmcp_id]
                    
                    logger.info(f"   ✅ Successfully tried to discover capabilities for server '{mcp_server.server_id} Current status {mcp_server.status.value}'")
                    
                    # Save updated server config
                    config_manager.update_server_config(mcp_server.server_id, mcp_server)
                    
            except Exception as e:
                logger.error(f"   ❌ Full traceback: {traceback.format_exc()}")
                logger.warning(f"   ⚠️ Failed to connect/discover capabilities for server {mcp_server.name}: {mcp_server.server_id}: {e}")
                # Continue anyway - server will be added but not connected
            
            processed_servers.append(mcp_server.server_id)
            mcp_server = config_manager.get_server_by_id(mcp_server.server_id)
            logger.info(f"   📊 Server to add: {mcp_server.status.value}")
            # Add server to vMCP configuration
            server_for_vmcp = mcp_server.to_dict_for_vmcp()
            
            # Update vMCP config
            updated_vmcp_config = vmcp_config.vmcp_config.copy() if vmcp_config.vmcp_config else {}
            
            # Add server to selected_servers
            selected_servers = updated_vmcp_config.get('selected_servers', [])
            if not any(s.get('server_id') == server_for_vmcp.get('server_id') for s in selected_servers):
                selected_servers.append(server_for_vmcp)
                updated_vmcp_config['selected_servers'] = selected_servers
            

        #==============================================
        return {
            "success": True,
            "message": f"vMCP '{vmcp_config.name}' refreshed successfully",
            "vmcp_id": vmcp_id,
            "servers_processed": len(processed_servers),
            "servers": processed_servers
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"   ❌ Error refreshing vMCP '{vmcp_id}': {e}")
        logger.error(f"   ❌ Exception type: {type(e).__name__}")
        logger.error(f"   ❌ Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to refresh vMCP: {str(e)}")

@router.get("/{vmcp_id}")
async def get_vmcp_details(vmcp_id: str, user_context: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    """Get detailed information about a specific vMCP for the current user"""
    logger.info(f"📋 Get vMCP details endpoint called for vmcp_id: {vmcp_id}")
    logger.info(f"   👤 User context: {user_context.user_id if user_context else 'None'}")

    try:
        # Get managers from global connection manager
        config_manager = MCPConfigManager(user_context.user_id)
        client_manager = MCPClientManager(config_manager)
        user_vmcp_manager = VMCPConfigManager(user_context.user_id, vmcp_id)
        vmcp_config = user_vmcp_manager.load_vmcp_config()
        if not vmcp_config:
            raise HTTPException(status_code=404, detail=f"vMCP '{vmcp_id}' not found")

        # Load widgets for this vMCP
        logger.info(f"🎨 Loading widgets for vMCP: {vmcp_id}")
        from vmcp.storage.models import Widget
        widgets = db.query(Widget).filter(
            Widget.user_id == user_context.user_id,
            Widget.vmcp_id == vmcp_id
        ).all()
        logger.info(f"   Found {len(widgets)} widgets")

        # Add widgets to vmcp_config
        vmcp_config.custom_widgets = [widget.to_dict() for widget in widgets]
        if widgets:
            for widget in widgets:
                logger.info(f"      - {widget.name} ({widget.widget_id}) - status: {widget.build_status}")
        logger.info(f"✅ Widgets loaded successfully")

        # Now we need to replace the selected_servers section with the mcp server config of the servers
        selected_servers = vmcp_config.vmcp_config.get('selected_servers', [])
        for idx,server in enumerate(selected_servers):
            server_config = config_manager.get_server(server.get('server_id'))
            if not server_config:
                selected_servers[idx]['status'] = 'not_found'
                continue
            logger.info(f"Replacing server config for {server.get('name')} ==> {server_config.name}")
            selected_servers[idx] = server_config.to_dict()

        # Update the vmcp_config with the processed servers
        if selected_servers:
            vmcp_config.vmcp_config['selected_servers'] = selected_servers

        return vmcp_config.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"   ❌ Error getting vMCP details '{vmcp_id}': {e}")
        logger.error(f"   ❌ Exception type: {type(e).__name__}")
        logger.error(f"   ❌ Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to get vMCP details: {str(e)}")

@router.put("/{vmcp_id}")
async def update_vmcp(vmcp_id: str, request: VMCPUdateRequest, user_context: UserContext = Depends(get_user_context)):
    """Update an existing vMCP configuration for the current user"""
    logger.info(f"📋 Update vMCP endpoint called for vmcp_id: {vmcp_id}")
    logger.info(f"   👤 User context: {user_context.user_id if user_context else 'None'}")
    
    try:
        # Get managers from global connection manager
        config_manager = MCPConfigManager(user_context.user_id)
        client_manager = MCPClientManager(config_manager)
        user_vmcp_manager = VMCPConfigManager(user_context.user_id, vmcp_id)
        
        # Parse Python functions and update their variables
        updated_custom_tools = []
        for tool in request.custom_tools:
            if tool.get('tool_type') == 'python' and tool.get('code'):
                try:
                    # Parse Python function to extract variables with types
                    import ast
                    from typing import get_origin
                    
                    def map_python_type(type_annotation) -> str:
                        if type_annotation is None:
                            return 'str'
                        
                        if isinstance(type_annotation, str):
                            type_map = {
                                'str': 'str', 'string': 'str',
                                'int': 'int', 'integer': 'int',
                                'float': 'float', 'number': 'float',
                                'bool': 'bool', 'boolean': 'bool',
                                'list': 'list', 'array': 'list',
                                'dict': 'dict', 'object': 'dict',
                                'tuple': 'list', 'set': 'list',
                            }
                            return type_map.get(type_annotation.lower(), 'str')
                        
                        if hasattr(type_annotation, '__name__'):
                            type_map = {
                                'str': 'str', 'int': 'int', 'float': 'float',
                                'bool': 'bool', 'list': 'list', 'dict': 'dict',
                                'tuple': 'list', 'set': 'list',
                            }
                            return type_map.get(type_annotation.__name__, 'str')
                        
                        origin = get_origin(type_annotation)
                        if origin is not None:
                            if origin is list or origin is tuple or origin is set:
                                return 'list'
                            elif origin is dict:
                                return 'dict'
                        
                        return 'str'
                    
                    # Parse the Python code
                    tree = ast.parse(tool['code'])
                    variables = []
                    
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            # Extract parameters
                            for arg in node.args.args:
                                if arg.arg == 'self':
                                    continue
                                    
                                type_annotation = None
                                if arg.annotation:
                                    if isinstance(arg.annotation, ast.Name):
                                        type_annotation = arg.annotation.id
                                    elif isinstance(arg.annotation, ast.Constant):
                                        type_annotation = arg.annotation.value
                                    elif isinstance(arg.annotation, ast.Subscript):
                                        # Handle generic types like list[int], dict[str, str]
                                        if isinstance(arg.annotation.value, ast.Name):
                                            type_annotation = arg.annotation.value.id

                                has_default = (len(node.args.defaults) > 0 and
                                             node.args.args.index(arg) >= len(node.args.args) - len(node.args.defaults))
                                
                                # Extract default value if present
                                default_value = None
                                if has_default:
                                    default_index = node.args.args.index(arg) - (len(node.args.args) - len(node.args.defaults))
                                    if default_index < len(node.args.defaults):
                                        default_ast = node.args.defaults[default_index]
                                        if isinstance(default_ast, ast.Constant):
                                            default_value = default_ast.value
                                        elif isinstance(default_ast, ast.Str):  # Python < 3.8
                                            default_value = default_ast.s
                                        elif isinstance(default_ast, ast.Num):  # Python < 3.8
                                            default_value = default_ast.n
                                        elif isinstance(default_ast, ast.NameConstant):  # Python < 3.8
                                            default_value = default_ast.value
                                        elif isinstance(default_ast, ast.Name):
                                            # Handle variable references (e.g., default=some_var)
                                            default_value = f"@{default_ast.id}"
                                
                                variables.append({
                                    'name': arg.arg,
                                    'description': f"Parameter: {arg.arg}",
                                    'required': not has_default,
                                    'type': map_python_type(type_annotation),
                                    'default_value': default_value
                                })
                            break  # Only process the first function
                    
                    # Update the tool with parsed variables
                    updated_tool = tool.copy()
                    updated_tool['variables'] = variables
                    updated_custom_tools.append(updated_tool)
                    
                except Exception as e:
                    logger.warning(f"Error parsing Python function in tool '{tool.get('name', 'unknown')}': {e}")
                    updated_custom_tools.append(tool)
            else:
                updated_custom_tools.append(tool)
        
        # Update vMCP configuration
        success = user_vmcp_manager.update_vmcp_config(
            vmcp_id=vmcp_id,
            name=request.name,
            description=request.description,
            system_prompt=request.system_prompt,
            vmcp_config=request.vmcp_config,
            custom_prompts=request.custom_prompts,
            custom_tools=updated_custom_tools,
            custom_context=request.custom_context,
            custom_resources=request.custom_resources,
            custom_resource_uris=request.custom_resource_uris,
            environment_variables=request.environment_variables,
            uploaded_files=request.uploaded_files,
            metadata=request.metadata
        )
        
        if not success:
            raise HTTPException(status_code=404, detail=f"vMCP '{vmcp_id}' not found")
        
        # Get the updated vMCP details
        vmcp_config = user_vmcp_manager.load_vmcp_config()

        try:
            vmcp_registry_config = vmcp_config.to_vmcp_registry_config()
            private_vmcp_registry_data = {
                "vmcp_registry_config": vmcp_registry_config.to_dict(),
                "vmcp_config": vmcp_config.to_dict()
            }
            logger.info(f"Updating Private vMCP registry data:{vmcp_config.name}")
            user_vmcp_manager.storage.update_private_vmcp_registry(private_vmcp_id=vmcp_config.id, 
                                                                   private_vmcp_registry_data= private_vmcp_registry_data, 
                                                                   operation="update")
        except Exception as e:
            logger.error(f"Error updating users private vmcp registry: {traceback.format_exc()}")
            logger.error(f"Error updating users private vmcp registry: {e}")
            raise HTTPException(status_code=404, detail=f"Error updating users private vmcp registry: {e}")
        
        logger.info(f"✅ Updated vMCP: {vmcp_id}")
        return {
            "success": True,
            "vMCP": vmcp_config.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"   ❌ Error updating vMCP '{vmcp_id}': {e}")
        logger.error(f"   ❌ Exception type: {type(e).__name__}")
        logger.error(f"   ❌ Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to update vMCP: {str(e)}")

@router.delete("/{vmcp_id}")
async def delete_vmcp(vmcp_id: str, user_context: UserContext = Depends(get_user_context)):
    """Delete an vMCP configuration for the current user"""
    logger.info(f"📋 Delete vMCP endpoint called for vmcp_id: {vmcp_id}")
    logger.info(f"   👤 User context: {user_context.user_id if user_context else 'None'}")
    
    try:
        # Create VMCP config manager and delegate deletion
        user_vmcp_manager = VMCPConfigManager(user_context.user_id, vmcp_id)
        
        # Delete the vMCP (this will handle all cleanup including storage and servers)
        result = user_vmcp_manager.delete_vmcp(vmcp_id)
        
        if not result.get("success", False):
            raise HTTPException(status_code=400, detail=result.get("message", "Failed to delete vMCP"))
        
        logger.info(f"✅ Deleted vMCP: {vmcp_id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"   ❌ Error deleting vMCP '{vmcp_id}': {e}")
        logger.error(f"   ❌ Exception type: {type(e).__name__}")
        logger.error(f"   ❌ Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to delete vMCP: {str(e)}")

# New sharing endpoints
@router.post("/share")
async def share_vmcp(request: VMCPShareRequest, 
                     user_context: UserContext = Depends(get_user_context)):
    """Make a vMCP public or private"""
    logger.info(f"📋 Share vMCP endpoint called for vmcp_id: {request.vmcp_id}")
    logger.info(f"   👤 User context: {user_context.user_id if user_context else 'None'}")
    # logger.info(f"   📝 Request data: {request}")
    logger.info(f"   📝 Request type: {type(request)}")
    logger.info(f"   📝 Request model: {request.__class__.__name__}")
    logger.info(f"   📝 Request fields: {request.model_fields.keys() if hasattr(request, 'model_fields') else 'No model_fields'}")
    
    if not request.vmcp_id:
        raise HTTPException(status_code=400, detail="vMCP ID is required")

    vmcp_id = request.vmcp_id
    try:
        user_vmcp_manager = VMCPConfigManager(user_context.user_id, vmcp_id)
        vmcp_config = user_vmcp_manager.load_vmcp_config()
        
        if not vmcp_config:
            raise HTTPException(status_code=404, detail=f"vMCP '{vmcp_id}' not found")
        
        logger.info(f"   📋 Loaded vMCP config: {vmcp_config.name}")
        
        # Create a sanitized version for public sharing
        if request.state == VMCPShareState.PUBLIC or request.state == VMCPShareState.SHARED:
            logger.info(f"   🔓 Making vMCP public")
            
            # Get user email
            try:
                db = SessionLocal()
                from vmcp.storage.models import User
                user = db.query(User).filter(User.id == user_context.user_id).first()
                if not user:
                    raise HTTPException(status_code=404, detail=f"User '{user_context.user_id}' not found")
                user_email = user.email
                username = user.username
                creator_username = username if username else f"public_{random.randint(1,10)}"
            except Exception as e:
                logger.error(f"   ❌ Error getting user email: {e}")
                raise HTTPException(status_code=500, detail="Failed to get user email")
            finally:
                db.close()

            # Save the updated vMCP config
            save_success = user_vmcp_manager.update_vmcp_config(
                vmcp_id,
                is_public=True,
                public_tags=[request.state.value],
                public_at=datetime.utcnow().isoformat(),
                creator_username=creator_username,
            )
            if not save_success:
                raise HTTPException(status_code=500, detail="Failed to update vMCP configuration")
            
            vmcp_config = user_vmcp_manager.load_vmcp_config()
            # Remove sensitive environment variables and replace with placeholders
            sanitized_config = vmcp_config.to_dict()
            
            logger.info(f"""   🧹 Sanitized config: {sanitized_config.get("total_tools"),
                    sanitized_config.get("total_resources"),
                    sanitized_config.get("total_prompts")}""")
            # Sanitize environment variables
            if vmcp_config.environment_variables:
                sanitized_env_vars = []
                for env_var in vmcp_config.environment_variables:
                    sanitized_env_vars.append({
                        "name": env_var.get("name", ""),
                        "description": env_var.get("description", ""),
                        "required": env_var.get("required", False),
                        "value": "<<NEED_INPUT_FROM_USER>>" if env_var.get("value") else None
                    })
                sanitized_config["environment_variables"] = sanitized_env_vars
            
            sanitized_config["creator_id"] = user_context.user_id
            sanitized_config["id"] = f"@{creator_username}:{vmcp_config.name}"
            sanitized_config["name"] = f"@{creator_username}/{vmcp_config.name}"
            metadata = {
                "url": f"https://1xn.ai/@{creator_username}/{vmcp_config.name}/vmcp",
                "type": "vmcp"
            }
            sanitized_config["metadata"] = metadata
            logger.info(f"   🧹 Sanitized config created")

            # We need to remove any auth of the MCP server from the sanitized config
            for idx,server in enumerate(sanitized_config["vmcp_config"]["selected_servers"]):
                sanitized_config["vmcp_config"]["selected_servers"][idx]["auth"] = None
                sanitized_config["vmcp_config"]["selected_servers"][idx]["session_id"] = None
                sanitized_config["vmcp_config"]["selected_servers"][idx]["status"] = MCPConnectionStatus.UNKNOWN

                
            
            try:
                user_context.storage.save_public_vmcp(VMCPConfig.from_dict(sanitized_config))
            except Exception as e:
                logger.error(f"   ❌ Error saving public vMCP: {e}")
                logger.error(f"   ❌ Exception type: {type(e).__name__}")
                logger.error(f"   ❌ Full traceback: {traceback.format_exc()}")
                logger.error(f"Error saving public vMCP: {e}")
                raise HTTPException(status_code=500, detail="Failed to make vMCP public")
            
            logger.info(f"✅ Made vMCP public: {vmcp_id}")
            return {
                "success": True,
                "message": f"vMCP '{vmcp_config.name}' is now public",
                "share_url": f"/{vmcp_config.name.lower()}/{vmcp_id}/vmcp"
            }
        else:
            logger.info(f"   🔒 Making vMCP private")
            
            # Save the updated vMCP config
            save_success = user_vmcp_manager.update_vmcp_config(
                vmcp_id,
                is_public=False,
                public_tags=[],
                public_at=None
            )
            if not save_success:
                raise HTTPException(status_code=500, detail="Failed to update vMCP configuration")
            
            # Make private
            try:
                db = SessionLocal()
                from vmcp.storage.models import User
                user = db.query(User).filter(User.id == user_context.user_id).first()
                if not user:
                    raise HTTPException(status_code=404, detail=f"User '{user_context.user_id}' not found")
                username = user.username
                public_vmcp_id = f"@{username}:{vmcp_config.name}"
                user_context.storage.remove_public_vmcp(public_vmcp_id)
                return {
                    "success": True,
                    "message": f"vMCP '{vmcp_config.name}' is now private"
                }
            except Exception as e:
                logger.error(f"Error making vMCP private: {e}")
                raise HTTPException(status_code=500, detail="Failed to make vMCP private")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"   ❌ Error sharing vMCP '{vmcp_id}': {e}")
        logger.error(f"   ❌ Exception type: {type(e).__name__}")
        logger.error(f"   ❌ Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to share vMCP: {str(e)}")

@router.get("/public/list", response_model=List[VMCPConfig])
async def list_public_vmcps(user_context: UserContext = Depends(get_user_context)):
    """List all public vMCPs available for installation"""
    logger.info("📋 List public vMCPs endpoint called")
    logger.info(f"   👤 User context: {user_context.user_id if user_context else 'None'}")
    
    try:
        public_vmcps = VMCPConfigManager.list_public_vmcps_static()
        
        logger.info(f"   📊 Found {len(public_vmcps)} public vMCPs")
        
        return public_vmcps
        
    except Exception as e:
        logger.error(f"   ❌ Error listing public vMCPs: {e}")
        logger.error(f"   ❌ Exception type: {type(e).__name__}")
        logger.error(f"   ❌ Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to list public vMCPs: {str(e)}")

@router.get("/public/{vmcp_id}")
async def get_public_vmcp_details(vmcp_id: str, user_context: UserContext = Depends(get_user_context)):
    """Get details of a public vMCP"""
    logger.info(f"📋 Get public vMCP details endpoint called for vmcp_id: {vmcp_id}")
    logger.info(f"   👤 User context: {user_context.user_id if user_context else 'None'}")
    
    try:
        public_vmcp = VMCPConfigManager.get_public_vmcp_static(vmcp_id)
        
        if not public_vmcp:
            raise HTTPException(status_code=404, detail=f"Public vMCP '{vmcp_id}' not found")
        
        return public_vmcp
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"   ❌ Error getting public vMCP details '{vmcp_id}': {e}")
        logger.error(f"   ❌ Exception type: {type(e).__name__}")
        logger.error(f"   ❌ Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to get public vMCP details: {str(e)}")

@router.post("/{vmcp_id}/fork")
async def fork_public_vmcp(vmcp_id: str, user_context: UserContext = Depends(get_user_context)):
    """Fork a public vMCP by copying it and making it private for the current user"""
    logger.info(f"📋 Fork public vMCP endpoint called for vmcp_id: {vmcp_id}")
    logger.info(f"   👤 User context: {user_context.user_id if user_context else 'None'}")
    
    try:
        user_vmcp_manager = VMCPConfigManager(user_context.user_id)
        
        # Get the public vMCP details
        public_vmcp = VMCPConfigManager.get_public_vmcp_static(vmcp_id)
        if not public_vmcp:
            raise HTTPException(status_code=404, detail=f"Public vMCP '{vmcp_id}' not found")
        
        # Generate new vMCP ID
        import uuid
        new_vmcp_id = str(uuid.uuid4())
        
        # Create forked name
        original_name = public_vmcp.get('name', 'Unnamed vMCP')
        forked_name = f"{original_name}_fork"
        
        # Create new VMCPConfig from public vMCP data
        forked_vmcp = VMCPConfig(
            id=new_vmcp_id,
            name=forked_name,
            user_id=user_context.user_id,
            description=public_vmcp.get('description'),
            system_prompt=public_vmcp.get('system_prompt'),
            vmcp_config=public_vmcp.get('vmcp_config', {}),
            custom_prompts=public_vmcp.get('custom_prompts', []),
            custom_tools=public_vmcp.get('custom_tools', []),
            custom_context=public_vmcp.get('custom_context', []),
            custom_resources=public_vmcp.get('custom_resources', []),
            custom_resource_templates=public_vmcp.get('custom_resource_templates', []),
            environment_variables=public_vmcp.get('environment_variables', []),
            uploaded_files=public_vmcp.get('uploaded_files', []),
            custom_resource_uris=public_vmcp.get('custom_resource_uris', []),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            total_tools=public_vmcp.get('total_tools', 0),
            total_resources=public_vmcp.get('total_resources', 0),
            total_resource_templates=public_vmcp.get('total_resource_templates', 0),
            total_prompts=public_vmcp.get('total_prompts', 0),
            # Make it private by setting these fields
            is_public=False,
            public_tags=[],
            public_at=None
        )
        
        # Save the forked vMCP
        success = user_vmcp_manager.save_vmcp_config(forked_vmcp)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to save forked vMCP")
        
        logger.info(f"✅ Forked public vMCP: {vmcp_id} -> {new_vmcp_id} ({forked_name})")
        return {
            "success": True,
            "vMCP": {
                "id": new_vmcp_id,
                "name": forked_name,
                "description": public_vmcp.get('description'),
                "user_id": user_context.user_id,
                "created_at": forked_vmcp.created_at.isoformat() if forked_vmcp.created_at else None,
                "updated_at": forked_vmcp.updated_at.isoformat() if forked_vmcp.updated_at else None
            },
            "message": f"vMCP '{original_name}' forked successfully as '{forked_name}'"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"   ❌ Error forking public vMCP '{vmcp_id}': {e}")
        logger.error(f"   ❌ Exception type: {type(e).__name__}")
        logger.error(f"   ❌ Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to fork public vMCP: {str(e)}")

@router.post("/{vmcp_id}/tools/list")
async def list_tools(vmcp_id: str, user_context: UserContext = Depends(get_user_context)):
    user_vmcp_manager = VMCPConfigManager(user_context.user_id,vmcp_id)    
    tools_list = await user_vmcp_manager.tools_list()
    return tools_list

@router.post("/{vmcp_id}/resources/list")
async def list_resources(vmcp_id: str, user_context: UserContext = Depends(get_user_context)):
    # Prefix selected resources with the server names
    config_manager = MCPConfigManager(user_context.user_id)
    client_manager = MCPClientManager(config_manager)
    user_vmcp_manager = VMCPConfigManager(user_context.user_id, vmcp_id)
    vmcp_config = user_vmcp_manager.load_vmcp_config()
    # Prefix selected_resources with the server names
    # and create resources list with input schema and description    
    resources_list = []
    for resource in vmcp_config.custom_resources:
        resource_name = resource.get("name")
        resource_input = resource.get("input")
        resource_description = resource.get("description")
        resources_list.append({"name": resource_name, "input": resource_input, "description": resource_description})

    # we also need to add the resources from each of the mcp servers that are selected in the vmcp config
    for mcp_server in vmcp_config.vmcp_config.get("mcp_servers", []):
        mcp_server_name = mcp_server.get("name")
        mcp_server_resources = mcp_server.get("resources", [])
        for resource in mcp_server_resources:
            resources_list.append({"name": f"{mcp_server_name}.{resource.get('name')}", 
                               "input": resource.get("input"), 
                               "description": resource.get("description")})

@router.post("/{vmcp_id}/prompts/list")
async def list_prompts(vmcp_id: str, user_context: UserContext = Depends(get_user_context)):
    user_vmcp_manager = VMCPConfigManager(user_context.user_id, vmcp_id,
        logging_config={"agent_name": "1xn-test", "client_id": user_context.client_id})
    prompts_list = await user_vmcp_manager.prompts_list()
    return prompts_list

@router.post("/{vmcp_id}/tools/call")
async def call_mcp_tool(vmcp_id: str, request: VMCPToolCallRequest, user_context: UserContext = Depends(get_user_context)):
    user_vmcp_manager = VMCPConfigManager(user_context.user_id, vmcp_id,
        logging_config={"agent_name": "1xn-test", "client_id": user_context.client_id})
    tool_response = await user_vmcp_manager.call_tool(request,connect_if_needed=True)
    return tool_response

@router.post("/{vmcp_id}/resources/read")
async def get_mcp_resource(vmcp_id: str, request: VMCPResourceRequest, user_context: UserContext = Depends(get_user_context)):
    # config_manager = MCPConfigManager(user_context.user_id)
    # client_manager = MCPClientManager(config_manager)
    # user_vmcp_manager = VMCPConfigManager(user_context.user_id, vmcp_id)
    # vmcp_config = user_vmcp_manager.load_vmcp_config()
    # # Get the resource
    # resource_name = request.resource_name
    # resource_uri = request.uri
    # resource_server_name = request.server_name
    # resource_server = client_manager.get_mcp_server(resource_server_name)
    # resource_response = resource_server.get_resource(resource_uri, connect_if_needed=True)

    user_vmcp_manager = VMCPConfigManager(user_context.user_id, vmcp_id,
        logging_config={"agent_name": "1xn-test", "client_id": user_context.client_id})
    resource_response = await user_vmcp_manager.get_resource(request.uri, connect_if_needed=True)
    return resource_response

@router.post("/{vmcp_id}/prompts/get")
async def get_mcp_prompt(vmcp_id: str, request: VMCPPromptRequest, user_context: UserContext = Depends(get_user_context)):
    # config_manager = MCPConfigManager(user_context.user_id)
    # client_manager = MCPClientManager(config_manager)
    # user_vmcp_manager = VMCPConfigManager(user_context.user_id, vmcp_id)
    # vmcp_config = user_vmcp_manager.load_vmcp_config()
    # # Get the prompt
    # prompt_name = request.prompt_name
    # prompt_input = request.arguments
    # prompt_server_name = request.server_name
    # prompt_server = client_manager.get_mcp_server(prompt_server_name)
    # prompt_response = prompt_server.get_prompt(prompt_name, prompt_input, connect_if_needed=True)

    user_vmcp_manager = VMCPConfigManager(user_context.user_id, vmcp_id,
        logging_config={"agent_name": "1xn-test", "client_id": user_context.client_id})
    prompt_response = await user_vmcp_manager.get_prompt(request.prompt_id, request.arguments,connect_if_needed=True)
    return prompt_response

@router.post("/{vmcp_id}/system-prompt/get")
async def get_vmcp_system_prompt(vmcp_id: str, request: dict, user_context: UserContext = Depends(get_user_context)):
    """Get the system prompt for a vMCP with variable substitution"""
    logger.info(f"📋 Get vMCP system prompt endpoint called for vmcp_id: {vmcp_id}")
    logger.info(f"   👤 User context: {user_context.user_id if user_context else 'None'}")
    
    try:
        user_vmcp_manager = VMCPConfigManager(user_context.user_id, vmcp_id,
            logging_config={"agent_name": "1xn-test", "client_id": user_context.client_id})
        
        # Get the system prompt with variable substitution
        arguments = request.get('arguments', {})
        system_prompt_result = await user_vmcp_manager.get_system_prompt(arguments)
        
        return {
            "success": True,
            "system_prompt": system_prompt_result.messages[0].content.text if system_prompt_result.messages else "",
            "description": system_prompt_result.description
        }
        
    except Exception as e:
        logger.error(f"   ❌ Error getting vMCP system prompt '{vmcp_id}': {e}")
        logger.error(f"   ❌ Exception type: {type(e).__name__}")
        logger.error(f"   ❌ Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to get vMCP system prompt: {str(e)}")

@router.get("/{vmcp_id}/system-prompt/variables")
async def get_vmcp_system_prompt_variables(vmcp_id: str, user_context: UserContext = Depends(get_user_context)):
    """Get the variables required for a vMCP's system prompt"""
    logger.info(f"📋 Get vMCP system prompt variables endpoint called for vmcp_id: {vmcp_id}")
    logger.info(f"   👤 User context: {user_context.user_id if user_context else 'None'}")
    
    try:
        user_vmcp_manager = VMCPConfigManager(user_context.user_id, vmcp_id,
            logging_config={"agent_name": "1xn-test", "client_id": user_context.client_id})
        vmcp_config = user_vmcp_manager.load_vmcp_config()
        
        if not vmcp_config or not vmcp_config.system_prompt:
            return {
                "success": True,
                "variables": [],
                "environment_variables": []
            }
        
        system_prompt = vmcp_config.system_prompt
        variables = system_prompt.get('variables', [])
        environment_variables = system_prompt.get('environment_variables', [])
        
        return {
            "success": True,
            "variables": variables,
            "environment_variables": environment_variables
        }
        
    except Exception as e:
        logger.error(f"   ❌ Error getting vMCP system prompt variables '{vmcp_id}': {e}")
        logger.error(f"   ❌ Exception type: {type(e).__name__}")
        logger.error(f"   ❌ Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to get vMCP system prompt variables: {str(e)}")

@router.post("/{vmcp_id}/environment-variables/save")
async def save_vmcp_environment_variables(vmcp_id: str, request: VMCPEnvironmentVariablesRequest, user_context: UserContext = Depends(get_user_context)):
    """Save environment variables for a vMCP (primarily for remote vMCPs)"""
    logger.info(f"📋 Save vMCP environment variables endpoint called for vmcp_id: {vmcp_id}")
    logger.info(f"   👤 User context: {user_context.user_id if user_context else 'None'}")
    
    try:
        user_vmcp_manager = VMCPConfigManager(user_context.user_id, vmcp_id,
            logging_config={"agent_name": "1xn-test", "client_id": user_context.client_id})
        
        # Load current vMCP config
        vmcp_config = user_vmcp_manager.load_vmcp_config()
        if not vmcp_config:
            raise HTTPException(status_code=404, detail=f"vMCP '{vmcp_id}' not found")
        
        # Update environment variables
        success = user_vmcp_manager.update_vmcp_config(
            vmcp_id=vmcp_id,
            environment_variables=request.environment_variables
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to save environment variables")
        
        # Reload updated config
        updated_vmcp = user_vmcp_manager.load_vmcp_config()
        
        logger.info(f"✅ Successfully saved environment variables for vMCP: {vmcp_id}")
        
        return {
            "success": True,
            "message": "Environment variables saved successfully",
            "environment_variables": updated_vmcp.environment_variables
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"   ❌ Error saving environment variables for vMCP '{vmcp_id}': {e}")
        logger.error(f"   ❌ Exception type: {type(e).__name__}")
        logger.error(f"   ❌ Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to save environment variables: {str(e)}")

@router.post("/{vmcp_id}/add-server")
async def add_server_to_vmcp(vmcp_id: str, request: dict, user_context: UserContext = Depends(get_user_context)):
    """Add a server to a vMCP configuration"""
    logger.info(f"📋 Add server to vMCP endpoint called for vmcp_id: {vmcp_id}")
    logger.info(f"   👤 User context: {user_context.user_id if user_context else 'None'}")
    # logger.info(f"   📝 Request data: {request}")
    
    try:
        # Get managers
        config_manager = MCPConfigManager(user_context.user_id)
        client_manager = MCPClientManager(config_manager)
        user_vmcp_manager = VMCPConfigManager(user_context.user_id, vmcp_id)
        
        # Load vMCP config
        vmcp_config = user_vmcp_manager.load_vmcp_config()
        if not vmcp_config:
            raise HTTPException(status_code=404, detail=f"vMCP '{vmcp_id}' not found")
        
        server_data = request.get('server_data', {})
        if server_data.get("mcp_server_config"):
            server_data = server_data.get("mcp_server_config")
        server_id = server_data.get('server_id')
        server_name = server_data.get('name')
        
        if not server_id and not server_name:
            raise HTTPException(status_code=400, detail="Either server id or server name is required")
        
        # Check if server already exists in server list
        existing_server = config_manager.get_server_by_id(server_id)
        
        server_to_add = None
        
        if existing_server:
            # Server exists, use it
            logger.info(f"   ✅ Found existing server: {existing_server.name} ({existing_server.server_id})")
            server_to_add = existing_server
            server_name  = server_to_add.name
            server_id = server_to_add.server_id
        else:
            # Server doesn't exist, create it from server_data
            logger.info(f"   🔧 Creating new server from data: {server_name}")
            
            # Map transport type
            transport_type = MCPTransportType(server_data.get('transport', 'http'))
            
            # Create server config
            server_config = MCPServerConfig(
                name=server_data.get('name', ''),
                transport_type=transport_type,
                description=server_data.get('description', ''),
                url=server_data.get('url'),
                command=server_data.get('command'),
                args=server_data.get('args'),
                env=server_data.get('env'),
                headers=server_data.get('headers'),
                auto_connect=server_data.get('auto_connect', True),
                enabled=server_data.get('enabled', True),
                status=MCPConnectionStatus.DISCONNECTED,
                favicon_url=server_data.get('favicon_url')
            )
            
            # Generate server ID
            server_id = server_config.ensure_server_id()
            server_name  = server_config.name
            server_id = server_config.server_id
            
            # Add server to backend
            success = config_manager.add_server(server_config)
            if not success:
                raise HTTPException(status_code=500, detail="Failed to create server")
            
            # Assign the created server config to server_to_add
            server_to_add = server_config
            
            logger.info(f"   ✅ Created new server: {server_config.name} ({server_id})")
        
        # Try to connect and discover capabilities and upate server config
        try:
            logger.info(f"   🔗 Attempting to connect to server: {server_name}")
            mcp_server = config_manager.get_server(server_id)
            if mcp_server:
                # Ping the server to get current status
                try:
                    current_status = await client_manager.ping_server(mcp_server.server_id)
                    logger.info(f"   🔍 Server {mcp_server.server_id}: ping result = {current_status.value}")
                except AuthenticationError as e:
                    logger.error(f"   ❌ Traceback: {traceback.format_exc()}")
                    logger.error(f"   ❌ Authentication error for server {mcp_server.server_id}: {e}")
                    current_status = MCPConnectionStatus.AUTH_REQUIRED
                except Exception as e:
                    logger.error(f"   ❌ Traceback: {traceback.format_exc()}")
                    logger.error(f"   ❌ Error pinging server {mcp_server.server_id}: {e}")
                    current_status = MCPConnectionStatus.UNKNOWN

                mcp_server.status = current_status
                
                # Discover capabilities
                try:
                    capabilities = await client_manager.discover_capabilities(mcp_server.server_id)
                except Exception as e:
                    logger.error(f"   ❌ Traceback: {traceback.format_exc()}")
                    logger.error(f"   ❌ Error discovering capabilities for server {mcp_server.server_id}: {e}")
                    capabilities = None

            
                if capabilities:
                    # Update server config with discovered capabilities
                    if capabilities.get('tools',[]):
                        mcp_server.tools = capabilities.get('tools', [])
                    if capabilities.get('resources',[]):
                        mcp_server.resources = capabilities.get('resources', [])
                    if capabilities.get('prompts',[]):
                        mcp_server.prompts = capabilities.get('prompts', [])
                    if capabilities.get('tool_details',[]):
                        mcp_server.tool_details = capabilities.get('tool_details', [])
                    if capabilities.get('resource_details',[]):
                        mcp_server.resource_details = capabilities.get('resource_details', [])
                    if capabilities.get('resource_templates',[]):
                        mcp_server.resource_templates = capabilities.get('resource_templates', [])
                    if capabilities.get('resource_template_details',[]):
                        mcp_server.resource_template_details = capabilities.get('resource_template_details', [])
                    if capabilities.get('prompt_details',[]):
                        mcp_server.prompt_details = capabilities.get('prompt_details', [])
                    
                    mcp_server.capabilities = {
                        "tools": bool(mcp_server.tools and len(mcp_server.tools) > 0),
                        "resources": bool(mcp_server.resources and len(mcp_server.resources) > 0),
                        "prompts": bool(mcp_server.prompts and len(mcp_server.prompts) > 0)
                    }

                vmcps_using_server = mcp_server.vmcps_using_server
                if vmcps_using_server:
                    logger.info(f"   🔄 vMCPs using server {mcp_server.server_id}: {vmcps_using_server}")
                    # Add vmcp id to vmcps_using_server
                    vmcps_using_server.append(vmcp_id)
                    mcp_server.vmcps_using_server = list(set(vmcps_using_server))
                else:
                    mcp_server.vmcps_using_server = [vmcp_id]
                
                logger.info(f"   ✅ Successfully tried to discover capabilities for server '{mcp_server.server_id} Current status {mcp_server.status.value}'")
                
                # Save updated server config
                config_manager.update_server_config(mcp_server.server_id, mcp_server)
                
        except Exception as e:
            logger.error(f"   ❌ Full traceback: {traceback.format_exc()}")
            logger.warning(f"   ⚠️ Failed to connect/discover capabilities for server {server_to_add.server_id}: {e}")
            # Continue anyway - server will be added but not connected
        
        server_to_add = config_manager.get_server_by_id(server_to_add.server_id)
        logger.info(f"   📊 Server to add: {server_to_add.status.value}")
        # Add server to vMCP configuration
        server_for_vmcp = server_to_add.to_dict_for_vmcp()
        
        # Update vMCP config
        updated_vmcp_config = vmcp_config.vmcp_config.copy() if vmcp_config.vmcp_config else {}
        
        # Add server to selected_servers
        selected_servers = updated_vmcp_config.get('selected_servers', [])
        if not any(s.get('server_id') == server_for_vmcp.get('server_id') for s in selected_servers):
            selected_servers.append(server_for_vmcp)
            updated_vmcp_config['selected_servers'] = selected_servers
        
        # Auto-select all tools, prompts, and resources
        selected_tools = updated_vmcp_config.get('selected_tools', {})
        selected_prompts = updated_vmcp_config.get('selected_prompts', {})
        selected_resources = updated_vmcp_config.get('selected_resources', {})
        
        # Get all tool names, prompt names, and resource URIs
        all_tool_names = [tool.get('name') for tool in server_for_vmcp.get('tool_details', []) ]
        all_prompt_names = [prompt.get('name') for prompt in server_for_vmcp.get('prompt_details', []) ]
        all_resource_uris = [resource.get('uri') for resource in server_for_vmcp.get('resource_details', []) ]
        
        selected_tools[server_for_vmcp.get('server_id')] = all_tool_names
        selected_prompts[server_for_vmcp.get('server_id')] = all_prompt_names
        selected_resources[server_for_vmcp.get('server_id')] = all_resource_uris
        
        updated_vmcp_config['selected_tools'] = selected_tools
        updated_vmcp_config['selected_prompts'] = selected_prompts
        updated_vmcp_config['selected_resources'] = selected_resources
        
        # Save updated vMCP config
        save_success = user_vmcp_manager.update_vmcp_config(
            vmcp_id=vmcp_id,
            vmcp_config=updated_vmcp_config
        )
        
        if not save_success:
            raise HTTPException(status_code=500, detail="Failed to update vMCP configuration")
        
        # Reload updated vMCP config
        updated_vmcp = user_vmcp_manager.load_vmcp_config()
        
        logger.info(f"✅ Successfully added server {server_to_add.name} to vMCP {vmcp_id}")
        
        return {
            "success": True,
            "message": f"Server '{server_to_add.name}' added to vMCP successfully",
            "vmcp_config": updated_vmcp,
            "server": server_for_vmcp
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"   ❌ Error adding server to vMCP '{vmcp_id}': {e}")
        logger.error(f"   ❌ Exception type: {type(e).__name__}")
        logger.error(f"   ❌ Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to add server to vMCP: {str(e)}")

@router.delete("/{vmcp_id}/remove-server")
async def remove_server_from_vmcp(vmcp_id: str, server_id: str, user_context: UserContext = Depends(get_user_context)):
    """Remove a server from a vMCP configuration"""
    logger.info(f"📋 Remove server from vMCP endpoint called for vmcp_id: {vmcp_id}")
    logger.info(f"   👤 User context: {user_context.user_id if user_context else 'None'}")
    logger.info(f"   🗑️ Server ID to remove: {server_id}")
    
    try:
        # Get managers
        config_manager = MCPConfigManager(user_context.user_id)
        user_vmcp_manager = VMCPConfigManager(user_context.user_id, vmcp_id)
        
        # Load vMCP config
        vmcp_config = user_vmcp_manager.load_vmcp_config()
        if not vmcp_config:
            raise HTTPException(status_code=404, detail=f"vMCP '{vmcp_id}' not found")
        
        if not server_id:
            raise HTTPException(status_code=400, detail="server_id is required")
        
        # Get the server to remove
        server_to_remove = config_manager.get_server_by_id(server_id)

        # Update vMCP config
        updated_vmcp_config = vmcp_config.vmcp_config

        if not server_to_remove:
            logger.warning(f"⚠️ Server '{server_id}' not found in MCP servers list")
        #     # Delete unknown MCP, could be left over from deleted server when Importing vMCP from json
        #     vmcp_config = user_vmcp_manager.load_vmcp_config()
        #     vmcp_config.vmcp_config.get('selected_servers', []).remove(server_id)
        #     user_vmcp_manager.update_vmcp_config(
        #         vmcp_id=vmcp_id,
        #         vmcp_config=vmcp_config.vmcp_config
        #     )
        #     logger.info(f"✅ Successfully removed non-existing server {server_id} from vMCP {vmcp_id}")
        #     raise HTTPException(status_code=404, detail=f"Server '{server_id}' not found")
        
        # Remove server from selected_servers
        else:
            logger.info(f"Removing server {server_to_remove.name} from vMCP {vmcp_id}")
        
        selected_servers = updated_vmcp_config.get('selected_servers', [])
        updated_selected_servers = [s for s in selected_servers if s.get('server_id') != server_id]
        updated_vmcp_config['selected_servers'] = updated_selected_servers
        
        # Remove server's tools, prompts, and resources from selections
        selected_tools = updated_vmcp_config.get('selected_tools', {})
        selected_prompts = updated_vmcp_config.get('selected_prompts', {})
        selected_resources = updated_vmcp_config.get('selected_resources', {})
        
        # Remove server from all selections
        if server_id in selected_tools:
            del selected_tools[server_id]
        if server_id in selected_prompts:
            del selected_prompts[server_id]
        if server_id in selected_resources:
            del selected_resources[server_id]
        
        updated_vmcp_config['selected_tools'] = selected_tools
        updated_vmcp_config['selected_prompts'] = selected_prompts
        updated_vmcp_config['selected_resources'] = selected_resources
        
        # Save updated vMCP config
        save_success = user_vmcp_manager.update_vmcp_config(
            vmcp_id=vmcp_id,
            vmcp_config=updated_vmcp_config
        )
        
        if not save_success:
            raise HTTPException(status_code=500, detail="Failed to update vMCP configuration")
        
        # Reload updated vMCP config
        updated_vmcp = user_vmcp_manager.load_vmcp_config()
        
        # Check if server is used in any other vMCPs
        # server_vmcps = []
        # try:
        #     # Get all vMCPs for this user
        #     all_vmcps = user_vmcp_manager.storage.list_vmcps_by_id()
        #     for other_vmcp_id in all_vmcps:
        #         if other_vmcp_id != vmcp_id:  # Skip current vMCP
        #             other_vmcp_manager = VMCPConfigManager(user_context.user_id, other_vmcp_id)
        #             other_vmcp_config = other_vmcp_manager.load_vmcp_config()
        #             if other_vmcp_config and other_vmcp_config.vmcp_config:
        #                 other_selected_servers = other_vmcp_config.vmcp_config.get('selected_servers', [])
        #                 if any(s.get('server_id') == server_id for s in other_selected_servers):
        #                     server_vmcps.append(other_vmcp_id)
        # except Exception as e:
        #     logger.error(f"   ❌ Full traceback: {traceback.format_exc()}")
        #     logger.warning(f"   ⚠️ Could not check other vMCPs for server {server_id}: {e}")
        
        # logger.info(f"   📊 Server is still used in {len(server_vmcps)} other vMCPs: {server_vmcps}")
        
        # Prepare response
        response_data = {
            "success": True,
            "message": f"Server '{server_to_remove.name if server_to_remove else server_id}' removed from vMCP successfully",
            "vmcp_config": updated_vmcp,
            "server": None  # Will be set below if server is still used
        }
        
        # If server is still used in other vMCPs, return updated server info
        # if server_vmcps:
        #     # Get updated server info
        #     updated_server = {
        #         "name": server_to_remove.name,
        #         "server_id": server_to_remove.server_id,
        #         "transport_type": server_to_remove.transport_type.value,
        #         "status": server_to_remove.status.value,
        #         "description": server_to_remove.description,
        #         "url": server_to_remove.url,
        #         "command": server_to_remove.command,
        #         "last_connected": server_to_remove.last_connected,
        #         "last_error": server_to_remove.last_error,
        #         "capabilities": {
        #             "tools_count": len(server_to_remove.tools) if server_to_remove.tools else 0,
        #             "resources_count": len(server_to_remove.resources) if server_to_remove.resources else 0,
        #             "prompts_count": len(server_to_remove.prompts) if server_to_remove.prompts else 0
        #         } if server_to_remove.capabilities else {
        #             "tools_count": 0,
        #             "resources_count": 0,
        #             "prompts_count": 0
        #         },
        #         "tools_list": server_to_remove.tools if server_to_remove.tools else [],
        #         "resources_list": server_to_remove.resources if server_to_remove.resources else [],
        #         "prompts_list": server_to_remove.prompts if server_to_remove.prompts else [],
        #         "resource_templates_list": server_to_remove.resource_templates if server_to_remove.resource_templates else [],
        #         "tool_details": server_to_remove.tool_details if server_to_remove.tool_details else [],
        #         "resource_details": server_to_remove.resource_details if server_to_remove.resource_details else [],
        #         "resource_template_details": server_to_remove.resource_template_details if server_to_remove.resource_template_details else [],
        #         "prompt_details": server_to_remove.prompt_details if server_to_remove.prompt_details else [],
        #         "auto_connect": server_to_remove.auto_connect,
        #         "enabled": server_to_remove.enabled,
        #         "auth_information": "present" if (server_to_remove.auth or server_to_remove.session_id) else "absent",
        #         "vmcp_list": server_vmcps  # List of vMCPs this server is still used in
        #     }
        #     response_data["server"] = updated_server
        # else:
        #     # delete the server from the config manager
        #     # config_manager.remove_server(server_to_remove.server_id)
        #     # logger.info(f"✅ Successfully removed server {server_to_remove.name} from config manager")
        #     pass
            
        # If server is not used in any other vMCPs, server will be None (indicating it should be removed from context)
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"   ❌ Error removing server from vMCP '{vmcp_id}': {e}")
        logger.error(f"   ❌ Exception type: {type(e).__name__}")
        logger.error(f"   ❌ Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to remove server from vMCP: {str(e)}")

@router.post("/stats", response_model=StatsResponse)
async def get_stats(request: StatsFilterRequest, user_context: UserContext = Depends(get_user_context)):
    """Get paginated stats with filtering capabilities"""
    logger.info(f"📊 Stats endpoint called for user: {user_context.user_id}")
    logger.info(f"   🔍 Filters: agent_name={request.agent_name}, vmcp_name={request.vmcp_name}, method={request.method}")
    logger.info(f"   📄 Pagination: page={request.page}, limit={request.limit}")

    try:
        # OSS: Query VMCPStats from database
        session = SessionLocal()
        try:
            stats_records = session.query(VMCPStats).join(VMCP).filter(
                VMCP.user_id == user_context.user_id
            ).order_by(VMCPStats.created_at.desc()).all()

            # Convert to log format with rich data from operation_metadata
            all_logs = []
            for stat in stats_records:
                metadata = stat.operation_metadata or {}
                all_logs.append({
                    "timestamp": stat.created_at.isoformat() if stat.created_at else None,
                    "method": stat.operation_type,
                    "agent_name": metadata.get("agent_name", "unknown"),
                    "agent_id": metadata.get("agent_id", "unknown"),
                    "user_id": metadata.get("user_id", user_context.user_id),
                    "client_id": metadata.get("client_id", "unknown"),
                    "operation_id": metadata.get("operation_id", "N/A"),
                    "mcp_server": stat.mcp_server_id,
                    "mcp_method": stat.operation_type,
                    "original_name": stat.operation_name,
                    "arguments": metadata.get("arguments", "No arguments"),
                    "result": metadata.get("result", "No result"),
                    "vmcp_id": stat.vmcp_id,
                    "vmcp_name": metadata.get("vmcp_name", stat.vmcp.vmcp_id if stat.vmcp else "unknown"),
                    "total_tools": metadata.get("total_tools", 0),
                    "total_resources": metadata.get("total_resources", 0),
                    "total_resource_templates": metadata.get("total_resource_templates", 0),
                    "total_prompts": metadata.get("total_prompts", 0),
                    "success": stat.success,
                    "error_message": stat.error_message,
                    "duration_ms": stat.duration_ms
                })
        finally:
            session.close()
        
        if not all_logs:
            return StatsResponse(
                logs=[],
                pagination={
                    "page": request.page,
                    "limit": request.limit,
                    "total": 0,
                    "total_pages": 0
                },
                stats={
                    "total_logs": 0,
                    "total_agents": 0,
                    "total_vmcps": 0,
                    "total_tool_calls": 0,
                    "total_resource_calls": 0,
                    "total_prompt_calls": 0,
                    "avg_tools_per_call": 0,
                    "unique_methods": [],
                    "agent_breakdown": {},
                    "vmcp_breakdown": {},
                    "method_breakdown": {}
                },
                filter_options={
                    "agent_names": [],
                    "vmcp_names": [],
                    "methods": []
                }
            )
        
        # Apply filters
        filtered_logs = all_logs.copy()
        
        if request.agent_name:
            agent_names = [name.strip() for name in request.agent_name.split(',') if name.strip()]
            filtered_logs = [log for log in filtered_logs if any(
                agent_name.lower() in log.get("agent_name", "").lower() for agent_name in agent_names
            )]
        
        if request.vmcp_name:
            vmcp_names = [name.strip() for name in request.vmcp_name.split(',') if name.strip()]
            filtered_logs = [log for log in filtered_logs if any(
                vmcp_name.lower() in log.get("vmcp_name", "").lower() for vmcp_name in vmcp_names
            )]
        
        if request.method:
            methods = [method.strip() for method in request.method.split(',') if method.strip()]
            filtered_logs = [log for log in filtered_logs if any(
                method.lower() in log.get("method", "").lower() for method in methods
            )]
        
        if request.search:
            search_term = request.search.lower()
            filtered_logs = [log for log in filtered_logs if 
                search_term in log.get("agent_name", "").lower() or
                search_term in log.get("vmcp_name", "").lower() or
                search_term in log.get("method", "").lower() or
                search_term in log.get("mcp_server", "").lower() or
                search_term in log.get("operation_id", "").lower() or
                search_term in str(log.get("arguments", "")).lower() or
                search_term in str(log.get("result", "")).lower()
            ]
        
        # Calculate stats from filtered logs
        total_logs = len(filtered_logs)
        
        # Calculate filter options from ALL logs (not filtered) so users can see all available options
        all_unique_agents = set(log.get("agent_name") if log.get("agent_name") is not None else "unknown" for log in all_logs )
        all_unique_vmcps = set(log.get("vmcp_name") if log.get("vmcp_name") is not None else "unknown" for log in all_logs )
        all_unique_methods = set(log.get("method") if log.get("method") is not None else "unknown" for log in all_logs )
        
        # Calculate stats for filtered results
        unique_agents = set(log.get("agent_name") if log.get("agent_name") is not None else "unknown" for log in filtered_logs )
        unique_vmcps = set(log.get("vmcp_name") if log.get("vmcp_name") is not None else "unknown" for log in filtered_logs )
        unique_methods = set(log.get("method") if log.get("method") is not None else "unknown" for log in filtered_logs )
        
        # Count different types of calls
        tool_calls = len([log for log in filtered_logs if log.get("method") in ["tool_list", "tool_call"]])
        resource_calls = len([log for log in filtered_logs if log.get("method") in ["resource_list", "resource_get"]])
        prompt_calls = len([log for log in filtered_logs if log.get("method") in ["prompt_list", "prompt_get"]])
        
        # Calculate average active tools per tool call
        tool_call_logs = [log for log in filtered_logs if log.get("method") in ["tool_call"]]
        total_tools_in_calls = sum(log.get("total_tools", 0) for log in tool_call_logs)
        avg_tools_per_call = total_tools_in_calls / tool_calls if tool_calls > 0 else 0
        
        # Calculate breakdowns
        agent_breakdown = {}
        for log in filtered_logs:
            agent_name = log.get("agent_name", "unknown")
            agent_breakdown[agent_name] = agent_breakdown.get(agent_name, 0) + 1
        
        vmcp_breakdown = {}
        for log in filtered_logs:
            vmcp_name = log.get("vmcp_name", "unknown")
            if vmcp_name:
                vmcp_breakdown[vmcp_name] = vmcp_breakdown.get(vmcp_name, 0) + 1
        
        method_breakdown = {}
        for log in filtered_logs:
            method = log.get("method", "unknown")
            method_breakdown[method] = method_breakdown.get(method, 0) + 1
        
        # Pagination
        total_pages = (total_logs + request.limit - 1) // request.limit
        start_index = (request.page - 1) * request.limit
        end_index = start_index + request.limit
        paginated_logs = filtered_logs[start_index:end_index]
        
        # Convert to LogEntry objects
        log_entries = []
        for log in paginated_logs:
            try:
                log_entry = LogEntry(
                    timestamp=log.get("timestamp", ""),
                    method=log.get("method", ""),
                    agent_name=log.get("agent_name", ""),
                    agent_id=log.get("agent_id", ""),
                    user_id=log.get("user_id", 0),
                    client_id=log.get("client_id", ""),
                    operation_id=log.get("operation_id", ""),
                    mcp_server=log.get("mcp_server"),
                    mcp_method=log.get("mcp_method"),
                    original_name=log.get("original_name"),
                    arguments=log.get("arguments"),
                    result=log.get("result"),
                    vmcp_id=log.get("vmcp_id"),
                    vmcp_name=log.get("vmcp_name"),
                    total_tools=log.get("total_tools"),
                    total_resources=log.get("total_resources"),
                    total_resource_templates=log.get("total_resource_templates"),
                    total_prompts=log.get("total_prompts")
                )
                log_entries.append(log_entry)
            except Exception as e:
                logger.warning(f"Failed to parse log entry: {e}")
                continue
        
        return StatsResponse(
            logs=log_entries,
            pagination={
                "page": request.page,
                "limit": request.limit,
                "total": total_logs,
                "total_pages": total_pages
            },
            stats={
                "total_logs": total_logs,
                "total_agents": len(unique_agents),
                "total_vmcps": len(unique_vmcps),
                "total_tool_calls": tool_calls,
                "total_resource_calls": resource_calls,
                "total_prompt_calls": prompt_calls,
                "avg_tools_per_call": round(avg_tools_per_call, 2),
                "unique_methods": sorted(list(unique_methods)),
                "agent_breakdown": agent_breakdown,
                "vmcp_breakdown": vmcp_breakdown,
                "method_breakdown": method_breakdown
            },
            filter_options={
                "agent_names": sorted(list(all_unique_agents)),
                "vmcp_names": sorted(list(all_unique_vmcps)),
                "methods": sorted(list(all_unique_methods))
            }
        )
        
    except Exception as e:
        logger.error(f"   ❌ Error fetching stats: {e}")
        logger.error(f"   ❌ Exception type: {type(e).__name__}")
        logger.error(f"   ❌ Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch stats: {str(e)}")

@router.get("/stats/summary", response_model=StatsSummary)
async def get_stats_summary(user_context: UserContext = Depends(get_user_context)):
    """Get overall stats summary without pagination"""
    logger.info(f"📊 Stats summary endpoint called for user: {user_context.user_id}")

    try:
        # OSS: Query VMCPStats from database
        session = SessionLocal()
        try:
            stats_records = session.query(VMCPStats).join(VMCP).filter(
                VMCP.user_id == user_context.user_id
            ).order_by(VMCPStats.created_at.desc()).all()

            # Convert to log format with rich data from operation_metadata
            all_logs = []
            for stat in stats_records:
                metadata = stat.operation_metadata or {}
                all_logs.append({
                    "timestamp": stat.created_at.isoformat() if stat.created_at else None,
                    "method": stat.operation_type,
                    "agent_name": metadata.get("agent_name", "unknown"),
                    "agent_id": metadata.get("agent_id", "unknown"),
                    "user_id": metadata.get("user_id", user_context.user_id),
                    "client_id": metadata.get("client_id", "unknown"),
                    "operation_id": metadata.get("operation_id", "N/A"),
                    "mcp_server": stat.mcp_server_id,
                    "mcp_method": stat.operation_type,
                    "original_name": stat.operation_name,
                    "arguments": metadata.get("arguments", "No arguments"),
                    "result": metadata.get("result", "No result"),
                    "vmcp_id": stat.vmcp_id,
                    "vmcp_name": metadata.get("vmcp_name", stat.vmcp.vmcp_id if stat.vmcp else "unknown"),
                    "total_tools": metadata.get("total_tools", 0),
                    "total_resources": metadata.get("total_resources", 0),
                    "total_resource_templates": metadata.get("total_resource_templates", 0),
                    "total_prompts": metadata.get("total_prompts", 0),
                    "success": stat.success,
                    "error_message": stat.error_message,
                    "duration_ms": stat.duration_ms
                })
        finally:
            session.close()
        
        if not all_logs:
            return StatsSummary(
                total_logs=0,
                total_agents=0,
                total_vmcps=0,
                total_tool_calls=0,
                total_resource_calls=0,
                total_prompt_calls=0,
                unique_methods=[],
                agent_breakdown={},
                vmcp_breakdown={},
                method_breakdown={}
            )
        
        # Calculate stats
        total_logs = len(all_logs)
        unique_agents = set(log.get("agent_name", "unknown") for log in all_logs)
        unique_vmcps = set(log.get("vmcp_name", "unknown") for log in all_logs if log.get("vmcp_name"))
        unique_methods = set(log.get("method", "unknown") for log in all_logs)
        
        # Count different types of calls
        tool_calls = len([log for log in all_logs if log.get("method") in ["tool_list", "tool_call"]])
        resource_calls = len([log for log in all_logs if log.get("method") in ["resource_list", "resource_get"]])
        prompt_calls = len([log for log in all_logs if log.get("method") in ["prompt_list", "prompt_get"]])
        
        # Calculate breakdowns
        agent_breakdown = {}
        for log in all_logs:
            agent_name = log.get("agent_name", "unknown")
            agent_breakdown[agent_name] = agent_breakdown.get(agent_name, 0) + 1
        
        vmcp_breakdown = {}
        for log in all_logs:
            vmcp_name = log.get("vmcp_name", "unknown")
            if vmcp_name:
                vmcp_breakdown[vmcp_name] = vmcp_breakdown.get(vmcp_name, 0) + 1
        
        method_breakdown = {}
        for log in all_logs:
            method = log.get("method", "unknown")
            method_breakdown[method] = method_breakdown.get(method, 0) + 1
        
        return StatsSummary(
            total_logs=total_logs,
            total_agents=len(unique_agents),
            total_vmcps=len(unique_vmcps),
            total_tool_calls=tool_calls,
            total_resource_calls=resource_calls,
            total_prompt_calls=prompt_calls,
            unique_methods=sorted(list(unique_methods)),
            agent_breakdown=agent_breakdown,
            vmcp_breakdown=vmcp_breakdown,
            method_breakdown=method_breakdown
        )
        
    except Exception as e:
        logger.error(f"   ❌ Error fetching stats summary: {e}")
        logger.error(f"   ❌ Exception type: {type(e).__name__}")
        logger.error(f"   ❌ Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch stats summary: {str(e)}")


@router.post("/parse-python-function", response_model=ParsePythonFunctionResponse)
async def parse_python_function(
    request: ParsePythonFunctionRequest,
    user_context: UserContext = Depends(get_user_context)
):
    """
    Parse Python function code and extract function information including parameters and types.
    """
    try:
        import ast
        from typing import get_origin, get_args
        
        # Map Python type annotations to our internal type system
        def map_python_type(type_annotation) -> str:
            if type_annotation is None:
                return 'str'
            
            # Handle string type annotations
            if isinstance(type_annotation, str):
                type_map = {
                    'str': 'str',
                    'string': 'str',
                    'int': 'int',
                    'integer': 'int',
                    'float': 'float',
                    'number': 'float',
                    'bool': 'bool',
                    'boolean': 'bool',
                    'list': 'list',
                    'array': 'list',
                    'dict': 'dict',
                    'object': 'dict',
                    'tuple': 'list',
                    'set': 'list',
                }
                return type_map.get(type_annotation.lower(), 'str')
            
            # Handle actual type annotations
            if hasattr(type_annotation, '__name__'):
                type_map = {
                    'str': 'str',
                    'int': 'int',
                    'float': 'float',
                    'bool': 'bool',
                    'list': 'list',
                    'dict': 'dict',
                    'tuple': 'list',
                    'set': 'list',
                }
                return type_map.get(type_annotation.__name__, 'str')
            
            # Handle generic types like List[str], Dict[str, int], etc.
            origin = get_origin(type_annotation)
            if origin is not None:
                if origin is list or origin is tuple or origin is set:
                    return 'list'
                elif origin is dict:
                    return 'dict'
            
            return 'str'
        
        functions = []
        
        try:
            # Parse the Python code
            tree = ast.parse(request.code)
            
            # Find all function definitions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    parameters = []
                    
                    # Extract parameters
                    for arg in node.args.args:
                        # Skip 'self' parameter
                        if arg.arg == 'self':
                            continue
                            
                        # Get type annotation
                        type_annotation = None
                        if arg.annotation:
                            if isinstance(arg.annotation, ast.Name):
                                type_annotation = arg.annotation.id
                            elif isinstance(arg.annotation, ast.Constant):
                                type_annotation = arg.annotation.value
                        
                        # Check if parameter has default value (not required)
                        has_default = len(node.args.defaults) > 0 and node.args.args.index(arg) >= len(node.args.args) - len(node.args.defaults)
                        
                        # Extract default value if present
                        default_value = None
                        if has_default:
                            default_index = node.args.args.index(arg) - (len(node.args.args) - len(node.args.defaults))
                            if default_index < len(node.args.defaults):
                                default_ast = node.args.defaults[default_index]
                                if isinstance(default_ast, ast.Constant):
                                    default_value = default_ast.value
                                elif isinstance(default_ast, ast.Str):  # Python < 3.8
                                    default_value = default_ast.s
                                elif isinstance(default_ast, ast.Num):  # Python < 3.8
                                    default_value = default_ast.n
                                elif isinstance(default_ast, ast.NameConstant):  # Python < 3.8
                                    default_value = default_ast.value
                                elif isinstance(default_ast, ast.Name):
                                    # Handle variable references (e.g., default=some_var)
                                    default_value = f"@{default_ast.id}"
                        
                        parameters.append(PythonFunctionParameter(
                            name=arg.arg,
                            description=f"Parameter: {arg.arg}",
                            required=not has_default,
                            type=map_python_type(type_annotation),
                            default_value=default_value
                        ))
                    
                    # Extract return type
                    return_type = None
                    if node.returns:
                        if isinstance(node.returns, ast.Name):
                            return_type = node.returns.id
                        elif isinstance(node.returns, ast.Constant):
                            return_type = node.returns.value
                    
                    # Extract docstring
                    docstring = None
                    if (node.body and 
                        isinstance(node.body[0], ast.Expr) and 
                        isinstance(node.body[0].value, ast.Constant) and 
                        isinstance(node.body[0].value.value, str)):
                        docstring = node.body[0].value.value.strip()
                    
                    functions.append(PythonFunctionInfo(
                        name=node.name,
                        parameters=parameters,
                        returnType=return_type,
                        docstring=docstring
                    ))
        
        except SyntaxError as e:
            logger.warning(f"Syntax error in Python code: {e}")
            # Return empty list for syntax errors
            pass
        except Exception as e:
            logger.error(f"Error parsing Python code: {e}")
            # Return empty list for other errors
            pass
        
        return ParsePythonFunctionResponse(functions=functions)
        
    except Exception as e:
        logger.error(f"Error in parse_python_function: {e}")
        logger.error(f"Exception type: {type(e).__name__}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to parse Python function: {str(e)}")
