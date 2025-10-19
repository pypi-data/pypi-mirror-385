from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, List, Any
from enum import Enum
from dataclasses import dataclass, asdict
from datetime import datetime
from mcp.types import Tool, Resource, ResourceTemplate, Prompt
import hashlib
import json
from dataclasses import field


class MCPInstallRequest(BaseModel):
    name: str = Field(..., description="Unique name for the MCP server")
    mode: str = Field(..., description="Transport mode: stdio, http, or sse")
    description: Optional[str] = Field(None, description="Server description")
    
    # For stdio servers
    command: Optional[str] = Field(None, description="Command to run for stdio server")
    args: Optional[List[str]] = Field(None, description="Command arguments")
    env: Optional[Dict[str, str]] = Field(None, description="Environment variables")
    
    # For HTTP/SSE servers
    url: Optional[str] = Field(None, description="Server URL for http/sse mode")
    headers: Optional[Dict[str, str]] = Field(None, description="HTTP headers")
    
    # Authentication
    auth_type: Optional[str] = Field("none", description="Auth type: none, oauth, bearer, basic")
    client_id: Optional[str] = Field(None, description="OAuth client ID")
    client_secret: Optional[str] = Field(None, description="OAuth client secret")
    auth_url: Optional[str] = Field(None, description="OAuth authorization URL")
    token_url: Optional[str] = Field(None, description="OAuth token URL")
    scope: Optional[str] = Field(None, description="OAuth scope")
    access_token: Optional[str] = Field(None, description="Bearer token")
    
    # Settings
    auto_connect: bool = Field(True, description="Auto-connect on startup")
    enabled: bool = Field(True, description="Server enabled")

    # add field validation for mode in pydantic way
    class Config:
        json_schema_extra = {
            "example_server_config": {
                "name": "My MCP Server",
                "mode": "stdio",
                "description": "My MCP Server Description"
            }
        }

class MCPServerInfo(BaseModel):
    name: str
    transport_type: str
    status: str
    server_id: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    command: Optional[str] = None
    last_connected: Optional[str] = None
    last_error: Optional[str] = None
    capabilities: Optional[Dict[str, Any]] = None
    tools: Optional[List[str]] = None
    resources: Optional[List[str]] = None
    prompts: Optional[List[str]] = None
    auto_connect: bool = True
    enabled: bool = True

class MCPTransportType(Enum):
    STDIO = "stdio"
    HTTP = "http"
    SSE = "sse"

class MCPConnectionStatus(Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    AUTH_REQUIRED = "auth_required"
    ERROR = "error"
    UNKNOWN = "unknown"
    NOT_FOUND = "not_found"

@dataclass
class MCPAuthConfig:
    """MCP Authentication configuration"""
    type: str  # "oauth", "bearer", "basic", "none"
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    auth_url: Optional[str] = None
    token_url: Optional[str] = None
    scope: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None

@dataclass
class MCPRegistryConfig:
    """MCP Registry configuration"""
    name: str
    transport_type: MCPTransportType
    description: Optional[str] = None
    server_id: Optional[str] = None  # Unique identifier based on configuration
    favicon_url: Optional[str] = None
    
    # For stdio servers
    command: Optional[str] = None
    args: Optional[List[str]] = None
    env: Optional[Dict[str, str]] = None
    
    # For HTTP/SSE servers
    url: Optional[str] = None
    headers: Optional[Dict[str, str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        # Handle enum serialization
        data['transport_type'] = self.transport_type.value
        return data

@dataclass
class MCPServerConfig:
    """MCP Server configuration"""
    name: str
    transport_type: MCPTransportType
    description: Optional[str] = None
    server_id: Optional[str] = None  # Unique identifier based on configuration
    favicon_url: Optional[str] = None
    
    # For stdio servers
    command: Optional[str] = None
    args: Optional[List[str]] = None
    env: Optional[Dict[str, str]] = None
    
    # For HTTP/SSE servers
    url: Optional[str] = None
    headers: Optional[Dict[str, str]] = None
    
    # Authentication
    auth: Optional[MCPAuthConfig] = None
    
    # Session ID for persistence across connections
    session_id: Optional[str] = None
    
    # Status and metadata
    status: MCPConnectionStatus = MCPConnectionStatus.UNKNOWN
    last_connected: Optional[datetime] = None
    last_error: Optional[str] = None
    
    # Capabilities discovered from server
    capabilities: Optional[Dict[str, Any]] = field(default_factory=dict)
    tools: Optional[List[str]] = field(default_factory=list)
    tool_details: Optional[List[Tool]] = field(default_factory=list)  # Full Tool objects with schemas
    resources: Optional[List[str]] = field(default_factory=list)  # Resource URIs for backward compatibility
    resource_details: Optional[List[Resource]] = field(default_factory=list)  # Full Resource objects with metadata
    resource_templates: Optional[List[str]] = field(default_factory=list)  # Resource template names for backward compatibility
    resource_template_details: Optional[List[ResourceTemplate]] = field(default_factory=list)  # Full ResourceTemplate objects with metadata
    prompts: Optional[List[str]] = field(default_factory=list)  # Prompt names for backward compatibility
    prompt_details: Optional[List[Prompt]] = field(default_factory=list)  # Full Prompt objects with schemas
    
    # Auto-connect settings
    auto_connect: bool = True
    enabled: bool = True
    
    # vMCP usage tracking
    vmcps_using_server: List[str] = field(default_factory=list)  # List of vMCP IDs using this server
    
    def to_mcp_registry_config(self) -> MCPRegistryConfig:
        return MCPRegistryConfig(
            name=self.name,
            transport_type=self.transport_type,
            description=self.description,
            server_id=self.server_id,
            favicon_url=self.favicon_url,
            command=self.command,
            args=self.args,
            env=self.env,
            url=self.url,
            headers=self.headers,
        )
    
    def generate_server_id(self) -> str:
        """Generate a unique server ID based on transport configuration"""
        # Create a configuration fingerprint
        config_data = {
            "transport_type": self.transport_type.value,
        }
        
        if self.transport_type == MCPTransportType.STDIO:
            # For stdio, use command and args
            config_data.update({
                "command": self.command,
                "args": sorted(self.args) if self.args else [],
                "env": dict(sorted(self.env.items())) if self.env else {}
            })
        else:
            # For HTTP/SSE, use URL and headers
            config_data.update({
                "url": self.url,
                "headers": dict(sorted(self.headers.items())) if self.headers else {}
            })
        
        # Create a stable JSON string and hash it
        config_json = json.dumps(config_data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(config_json.encode()).hexdigest()[:16]  # Use first 16 chars
    
    def ensure_server_id(self) -> str:
        """Ensure server has an ID, generate if missing"""
        if not self.server_id:
            self.server_id = self.generate_server_id()
        return self.server_id
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        # Handle enum serialization
        data['transport_type'] = self.transport_type.value
        data['status'] = self.status.value if self.status else 'unknown'
        
        # Ensure server_id is set
        if not data.get('server_id'):
            data['server_id'] = self.ensure_server_id()
        
        # Handle datetime serialization
        if self.last_connected:
            data['last_connected'] = self.last_connected.isoformat()
        
        # Handle auth object serialization
        if self.auth:
            data['auth'] = asdict(self.auth)
            if self.auth.expires_at:
                data['auth']['expires_at'] = self.auth.expires_at.isoformat()
        
        # Handle MCP type objects serialization
        if self.tool_details:
            data['tool_details'] = [self._serialize_mcp_object(tool) for tool in self.tool_details]
        
        if self.resource_details:
            data['resource_details'] = [self._serialize_mcp_object(resource) for resource in self.resource_details]
        
        if self.resource_template_details:
            data['resource_template_details'] = [self._serialize_mcp_object(template) for template in self.resource_template_details]
        
        if self.prompt_details:
            data['prompt_details'] = [self._serialize_mcp_object(prompt) for prompt in self.prompt_details]
            
        return data
    
    def to_dict_for_vmcp(self) -> Dict[str, Any]:
        """Convert to dictionary for vMCP usage, excluding auth and session_id fields"""
        data = self.to_dict()
        
        # Remove auth and session_id fields for vMCP usage
        data.pop('auth', None)
        data.pop('session_id', None)
        
        return data
    
    def _serialize_mcp_object(self, obj) -> Dict[str, Any]:
        """Serialize MCP objects (Tool, Resource, etc.) to dictionary"""
        if hasattr(obj, 'model_dump'):
            # Pydantic model
            return obj.model_dump(mode='json')
        elif hasattr(obj, '__dataclass_fields__'):
            # Dataclass (like MCP Tool, Resource, etc.)
            return asdict(obj)
        else:
            # Fallback - try to convert to dict
            return obj if isinstance(obj, dict) else str(obj)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MCPServerConfig':
        """Create from dictionary (JSON deserialization)"""
        # Handle enum deserialization
        data['transport_type'] = MCPTransportType(data['transport_type'])
        data['status'] = MCPConnectionStatus(data['status'])
        
        # Handle datetime deserialization
        if data.get('last_connected'):
            data['last_connected'] = datetime.fromisoformat(data['last_connected'])
        
        # Handle auth object
        if data.get('auth'):
            auth_data = data['auth']
            if auth_data.get('expires_at'):
                auth_data['expires_at'] = datetime.fromisoformat(auth_data['expires_at'])
            data['auth'] = MCPAuthConfig(**auth_data)
        
        # Handle null values for list fields - convert to empty lists
        list_fields = [
            'args', 'tools', 'tool_details', 'resources', 'resource_details', 
            'resource_templates', 'resource_template_details', 'prompts', 'prompt_details',
            'vmcps_using_server'
        ]
        for field in list_fields:
            if data.get(field) is None:
                data[field] = []
        
        # Handle null values for dict fields - convert to empty dicts
        dict_fields = ['env', 'headers', 'capabilities']
        for field in dict_fields:
            if data.get(field) is None:
                data[field] = {}
        
        # Handle MCP type objects deserialization
        if data.get('tool_details'):
            from mcp.types import Tool
            data['tool_details'] = [Tool(**tool_data) if isinstance(tool_data, dict) else tool_data for tool_data in data['tool_details']]
        
        if data.get('resource_details'):
            from mcp.types import Resource
            data['resource_details'] = [Resource(**resource_data) if isinstance(resource_data, dict) else resource_data for resource_data in data['resource_details']]
        
        if data.get('resource_template_details'):
            from mcp.types import ResourceTemplate
            data['resource_template_details'] = [ResourceTemplate(**template_data) if isinstance(template_data, dict) else template_data for template_data in data['resource_template_details']]
        
        if data.get('prompt_details'):
            from mcp.types import Prompt
            data['prompt_details'] = [Prompt(**prompt_data) if isinstance(prompt_data, dict) else prompt_data for prompt_data in data['prompt_details']]
        
        return cls(**data)
    
class MCPToolCallRequest(BaseModel):
    server_id: str
    tool_name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)

class MCPResourceRequest(BaseModel):
    server_id: str
    uri: str

class MCPPromptRequest(BaseModel):
    server_id: str
    prompt_name: str
    arguments: Optional[Dict[str, Any]] = None


class RenameServerRequest(BaseModel):
    new_name: str

class MCPUpdateRequest(BaseModel):
    name: str = Field(..., description="Server name (can be changed)")
    mode: str = Field(..., description="Transport mode: stdio, http, or sse")
    description: Optional[str] = Field(None, description="Server description")
    
    # For stdio servers
    command: Optional[str] = Field(None, description="Command to run for stdio server")
    args: Optional[List[str]] = Field(None, description="Command arguments")
    env: Optional[Dict[str, str]] = Field(None, description="Environment variables")
    
    # For HTTP/SSE servers
    url: Optional[str] = Field(None, description="Server URL for http/sse mode")
    headers: Optional[Dict[str, str]] = Field(None, description="HTTP headers")
    
    # Authentication
    auth_type: Optional[str] = Field("none", description="Auth type: none, oauth, bearer, basic")
    client_id: Optional[str] = Field(None, description="OAuth client ID")
    client_secret: Optional[str] = Field(None, description="OAuth client secret")
    auth_url: Optional[str] = Field(None, description="OAuth authorization URL")
    token_url: Optional[str] = Field(None, description="OAuth token URL")
    scope: Optional[str] = Field(None, description="OAuth scope")
    access_token: Optional[str] = Field(None, description="Bearer token")
    
    # Settings
    auto_connect: bool = Field(True, description="Auto-connect on startup")
    enabled: bool = Field(True, description="Server enabled")


# Custom exception classes for MCP operations
class AuthenticationError(Exception):
    """Raised when authentication fails"""
    pass

class HTTPError(Exception):
    """Raised when HTTP errors occur"""
    pass

class OperationCancelledError(Exception):
    """Raised when operations are cancelled"""
    pass

class OperationTimedOutError(Exception):
    """Raised when operations timeout"""
    pass

class MCPOperationError(Exception):
    """Raised when operations fail"""
    pass

class InvalidSessionIdError(Exception):
    """Raised when session id is invalid"""
    pass

class BadMCPRequestError(Exception):
    """Raised when MCP server returns a bad request"""
    pass

class MCPBadRequestError(Exception):
    """Raised when MCP server returns a bad request"""
    pass