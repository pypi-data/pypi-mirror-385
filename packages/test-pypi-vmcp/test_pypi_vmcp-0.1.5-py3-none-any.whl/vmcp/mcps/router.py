"""
MCP Router with Dual Route Support

This router provides endpoints for managing MCP (Model Context Protocol) servers.
Each server-specific endpoint is available via both server name and server ID:

- Name-based routes: /{server_name}/action (e.g., /my-server/connect)
- ID-based routes: /by-id/{server_id}/action (e.g., /by-id/abc123/connect)

The dual_route decorator automatically creates both routes for each endpoint,
allowing clients to use whichever identifier is more convenient.

Available endpoints:
- POST /{server_name}/connect or /by-id/{server_id}/connect
- POST /{server_name}/disconnect or /by-id/{server_id}/disconnect
- POST /{server_name}/ping or /by-id/{server_id}/ping
- POST /{server_name}/auth or /by-id/{server_id}/auth
- POST /{server_name}/tools/call or /by-id/{server_id}/tools/call
- POST /{server_name}/resources/read or /by-id/{server_id}/resources/read
- POST /{server_name}/prompts/get or /by-id/{server_id}/prompts/get
- GET /{server_name}/tools/list or /by-id/{server_id}/tools/list
- GET /{server_name}/resources/list or /by-id/{server_id}/resources/list
- GET /{server_name}/prompts/list or /by-id/{server_id}/prompts/list
- PUT /{server_name}/rename or /by-id/{server_id}/rename
- PUT /{server_name}/update or /by-id/{server_id}/update
- DELETE /{server_name}/uninstall or /by-id/{server_id}/uninstall
"""

import os
import traceback
from typing import Dict, List, Optional, Any, Callable
from functools import wraps
from fastapi import APIRouter, HTTPException, BackgroundTasks, Request, Depends
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from datetime import datetime
from vmcp.mcps.models import MCPInstallRequest, MCPTransportType, MCPAuthConfig, MCPServerConfig, \
    MCPServerInfo, MCPConnectionStatus, MCPToolCallRequest, MCPResourceRequest, MCPPromptRequest, \
    RenameServerRequest, MCPUpdateRequest
from pydantic import BaseModel
from vmcp.storage.dummy_user import UserContext
from vmcp.storage.dummy_user import get_user_context
# trace_mcp_method removed - using standard logging
from vmcp.mcps.mcp_configmanager import MCPConfigManager
from vmcp.mcps.mcp_client import MCPClientManager, AuthenticationError
from vmcp.utilities.logging.config import setup_logging
from mcp.types import TextContent, CallToolResult
from vmcp.vmcps.vmcp_config_manger import VMCPConfigManager


logger = setup_logging("1xN_MCP_ROUTER")

def get_server_not_found_error(server_name: str, config_manager: MCPConfigManager) -> HTTPException:
    """Helper function to create a helpful server not found error"""
    available_servers = config_manager.list_servers()
    available_names = [s.name for s in available_servers]
    
    error_detail = f"Server '{server_name}' not found"
    if available_names:
        error_detail += f". Available servers: {', '.join(available_names)}"
    else:
        error_detail += ". No servers are currently installed. Please install a server first using the /install endpoint."
    
    return HTTPException(status_code=404, detail=error_detail)

def get_server_not_found_error_by_id(server_id: str, config_manager: MCPConfigManager) -> HTTPException:
    """Helper function to create a helpful server not found error for server ID"""
    available_servers = config_manager.list_servers()
    available_ids = [s.server_id for s in available_servers if s.server_id]
    
    error_detail = f"Server with ID '{server_id}' not found"
    if available_ids:
        error_detail += f". Available server IDs: {', '.join(available_ids[:5])}"  # Show first 5 IDs
        if len(available_ids) > 5:
            error_detail += f" and {len(available_ids) - 5} more"
    else:
        error_detail += ". No servers are currently installed. Please install a server first using the /install endpoint."
    
    return HTTPException(status_code=404, detail=error_detail)

router = APIRouter(prefix="/mcps", tags=["MCPs"])

@router.get("/health")
# @trace_mcp_method("MCP API: Health Check")
async def health_check():
    """Health check endpoint for the unified backend server management"""
    return {"status": "healthy", "service": "1xN Unified Backend - MCP Server Management"}

@router.post("/install")
# @trace_mcp_method("MCP API: Install Server", operation="install")
async def install_mcp_server(request: MCPInstallRequest, 
                             background_tasks: BackgroundTasks, 
                             user_context: UserContext = Depends(get_user_context)):
    
    # Get managers from global connection manager
    config_manager = MCPConfigManager(user_context.user_id)
    
    # Validate transport mode
    try:
        transport_type = MCPTransportType(request.mode.lower())
    except ValueError:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid mode. Use: {', '.join([t.value for t in MCPTransportType])}"
        )
    
    # Validate required fields based on transport type
    if transport_type == MCPTransportType.STDIO:
        if not request.command:
            raise HTTPException(status_code=400, detail="Command required for stdio mode")
    elif transport_type in [MCPTransportType.HTTP, MCPTransportType.SSE]:
        if not request.url:
            raise HTTPException(status_code=400, detail="URL required for http/sse mode")
    
    # Check if server already exists
    if config_manager.get_server(request.name):
        raise HTTPException(status_code=409, detail=f"Server '{request.name}' already exists")
    
    # Create auth config
    auth_config = None
    if request.auth_type and request.auth_type != "none":
        auth_config = MCPAuthConfig(
            type=request.auth_type,
            client_id=request.client_id,
            client_secret=request.client_secret,
            auth_url=request.auth_url,
            token_url=request.token_url,
            scope=request.scope,
            access_token=request.access_token
        )
    
    # Create server config
    server_config = MCPServerConfig(
        name=request.name,
        transport_type=transport_type,
        description=request.description,
        command=request.command,
        args=request.args,
        env=request.env,
        url=request.url,
        headers=request.headers,
        auth=auth_config,
        auto_connect=request.auto_connect,
        enabled=request.enabled
    )
    
    # Generate server ID
    server_id = server_config.ensure_server_id()
    logger.info(f"Generated server ID: {server_id} for server: {server_config.name}")
    
    logger.info(f"Adding server to config: {server_config}")
    # Add to config
    success = config_manager.add_server(server_config)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to save server configuration")
    
    # Try to connect if enabled and auto_connect
    if server_config.enabled and server_config.auto_connect:
        background_tasks.add_task(connect_server_background, 
                                  server_id, user_context.user_id, config_manager)
    
    return {
        "success": True,
        "message": f"MCP server '{request.name}' installed successfully",
        "server": MCPServerInfo(
            name=server_config.name,
            transport_type=server_config.transport_type.value,
            status=server_config.status.value,
            server_id=server_config.server_id,
            description=server_config.description,
            url=server_config.url,
            command=server_config.command,
            auto_connect=server_config.auto_connect,
            enabled=server_config.enabled
        )
    }

@router.post("/generate-server-id")
# @trace_mcp_method("MCP API: Generate Server ID", operation="generate_id")
async def generate_server_id(request: MCPInstallRequest):
    """Generate a consistent server ID from server configuration without saving"""
    try:
        # Validate transport mode
        transport_type = MCPTransportType(request.mode.lower())
    except ValueError:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid mode. Use: {', '.join([t.value for t in MCPTransportType])}"
        )
    
    # Create a temporary server config to generate ID
    temp_server_config = MCPServerConfig(
        name=request.name,
        transport_type=transport_type,
        description=request.description,
        url=request.url,
        command=request.command,
        args=request.args,
        env=request.env,
        headers=request.headers,
        auto_connect=request.auto_connect,
        enabled=request.enabled
    )
    
    # Generate the server ID
    server_id = temp_server_config.generate_server_id()
    
    return {
        "success": True,
        "server_id": server_id,
        "message": f"Generated server ID for '{request.name}'"
    }

@router.put("/{server_id}/rename")
# @trace_mcp_method("MCP API: Rename Server", operation="rename")
async def rename_mcp_server(server_id: str, request: RenameServerRequest, user_context: UserContext = Depends(get_user_context)):
    """Rename an MCP server"""
    logger.info(f"📋 Rename server endpoint called: {server_id} -> {request.new_name}")
    logger.info(f"   👤 User context: {user_context.user_id if user_context else 'None'}")
    
    try:
        # Get managers from global connection manager
        config_manager = MCPConfigManager(user_context.user_id)
        
        # Check if server exists
        server_config = config_manager.get_server(server_id)
        if not server_config:
            raise get_server_not_found_error(server_id, config_manager)
        
        # Check if new name already exists
        existing_server = config_manager.get_server(request.new_name)
        if existing_server:
            raise HTTPException(status_code=409, detail=f"Server with name '{request.new_name}' already exists")
        
        # Rename the server
        success = config_manager.rename_server(server_id, request.new_name)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to rename server")
        
        logger.info(f"   ✅ Successfully renamed server '{server_id}' to '{request.new_name}'")
        return {
            "success": True,
            "message": f"Server renamed from '{server_id}' to '{request.new_name}' successfully",
            "old_name": server_id,
            "new_name": request.new_name,
            "server_id": server_config.server_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"   ❌ Error renaming server: {e}")
        logger.error(f"   ❌ Exception type: {type(e).__name__}")
        logger.error(f"   ❌ Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to rename server: {str(e)}")

@router.put("/{server_id}/update")
# @trace_mcp_method("MCP API: Update Server", operation="update")
async def update_mcp_server(server_id: str, request: MCPUpdateRequest, user_context: UserContext = Depends(get_user_context)):
    """Update an MCP server configuration"""
    logger.info(f"📋 Update server endpoint called: {server_id}")
    logger.info(f"   👤 User context: {user_context.user_id if user_context else 'None'}")
    
    try:
        # Get managers from global connection manager
        config_manager = MCPConfigManager(user_context.user_id)
        
        # Check if server exists
        server_config = config_manager.get_server(server_id)
        if not server_config:
            raise get_server_not_found_error(server_id, config_manager)
        
        # Check if name is being changed
        new_name = request.name
        if new_name != server_config.name:
            # Check if new name already exists
            existing_server = config_manager.get_server(new_name)
            if existing_server:
                raise HTTPException(status_code=409, detail=f"Server with name '{new_name}' already exists")
            logger.info(f"   🔄 Server name will be changed from '{server_config.name}' to '{new_name}'")
        
        # Validate transport mode
        try:
            transport_type = MCPTransportType(request.mode.lower())
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid mode. Use: {', '.join([t.value for t in MCPTransportType])}"
            )
        
        # Validate required fields based on transport type
        if transport_type == MCPTransportType.STDIO:
            if not request.command:
                raise HTTPException(status_code=400, detail="Command required for stdio mode")
        elif transport_type in [MCPTransportType.HTTP, MCPTransportType.SSE]:
            if not request.url:
                raise HTTPException(status_code=400, detail="URL required for http/sse mode")
        
        # Create auth config
        auth_config = None
        if request.auth_type and request.auth_type != "none":
            auth_config = MCPAuthConfig(
                type=request.auth_type,
                client_id=request.client_id,
                client_secret=request.client_secret,
                auth_url=request.auth_url,
                token_url=request.token_url,
                scope=request.scope,
                access_token=request.access_token
            )
        
        # Create updated server config
        updated_config = MCPServerConfig(
            name=new_name,  # Use the new name from request
            transport_type=transport_type,
            description=request.description,
            command=request.command,
            args=request.args,
            env=request.env,
            url=request.url,
            headers=request.headers,
            auth=auth_config,
            auto_connect=request.auto_connect,
            enabled=request.enabled
        )
        
        # Preserve the server ID and connection status
        updated_config.server_id = server_config.server_id
        updated_config.status = server_config.status
        updated_config.last_connected = server_config.last_connected
        updated_config.last_error = server_config.last_error
        updated_config.tools = server_config.tools
        updated_config.resources = server_config.resources
        updated_config.prompts = server_config.prompts
        updated_config.capabilities = server_config.capabilities
        
        
        # Just update the existing server
        success = config_manager.update_server_config(server_config.server_id, updated_config)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update server configuration")
        logger.info(f"   ✅ Successfully updated server '{server_config.name}' '{server_config.server_id}'")
        
        return {
            "success": True,
            "message": f"MCP server '{server_id}' updated successfully" + (f" and renamed to '{new_name}'" if new_name != server_config.name else ""),
            "server": MCPServerInfo(
                name=updated_config.name,
                transport_type=updated_config.transport_type.value,
                status=updated_config.status.value,
                server_id=updated_config.server_id,
                description=updated_config.description,
                url=updated_config.url,
                command=updated_config.command,
                auto_connect=updated_config.auto_connect,
                enabled=updated_config.enabled
            )
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"   ❌ Error updating server: {e}")
        logger.error(f"   ❌ Exception type: {type(e).__name__}")
        logger.error(f"   ❌ Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to update server: {str(e)}")

@router.delete("/{server_id}/uninstall")
# @trace_mcp_method("MCP API: Uninstall Server", operation="uninstall")
async def uninstall_mcp_server(server_id: str, user_context: UserContext = Depends(get_user_context)):
    """Uninstall an MCP server"""
    
    # Get managers from global connection manager
    config_manager = MCPConfigManager(user_context.user_id)
    
    # Check if server exists
    server_config = config_manager.get_server(server_id)
    if not server_config:
        raise get_server_not_found_error(server_id, config_manager)
    
    # Remove from config
    success = config_manager.remove_server(server_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to remove server configuration")
    
    return {
        "success": True,
        "message": f"MCP server '{server_id}' uninstalled successfully"
    }

@router.post("/{server_id}/disconnect")
# @trace_mcp_method("MCP API: Disconnect Server", operation="disconnect")
async def disconnect_mcp_server(server_id: str, user_context: UserContext = Depends(get_user_context)):
    """Disconnect an MCP server by clearing auth and session, setting status to disconnected"""
    logger.info(f"📋 Disconnect server endpoint called for server: {server_id}")
    logger.info(f"   👤 User context: {user_context.user_id if user_context else 'None'}")
    
    try:
        # Get managers from global connection manager
        config_manager = MCPConfigManager(user_context.user_id)
        
        # Check if server exists
        server_config = config_manager.get_server(server_id)
        if not server_config:
            raise get_server_not_found_error(server_id, config_manager)
        
        # Clear auth and session information
        server_config.auth = None
        server_config.session_id = None
        
        # Set status to disconnected
        config_manager.update_server_status(server_id, MCPConnectionStatus.DISCONNECTED)
        
        # Update vMCPs using server status
        vmcps_using_server = server_config.vmcps_using_server
        if vmcps_using_server:
            logger.info(f"   🔄 Updating vMCPs using {server_id} status: disconnected")
            vmcp_config_manager = VMCPConfigManager(user_context.user_id)
            for vmcp_id in vmcps_using_server:
                if vmcp_id.startswith('@'):
                    continue
                vmcp_config = vmcp_config_manager.load_vmcp_config(specific_vmcp_id=vmcp_id)
                if vmcp_config:
                    vmcp_config_manager.update_vmcp_server(vmcp_id, server_config)
        
        logger.info(f"   ✅ Successfully disconnected server '{server_id}'")
        return {
            "success": True,
            "message": f"Server '{server_id}' disconnected successfully",
            "status": "disconnected"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"   ❌ Error disconnecting server: {e}")
        logger.error(f"   ❌ Exception type: {type(e).__name__}")
        logger.error(f"   ❌ Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to disconnect server: {str(e)}")

@router.post("/{server_id}/connect")
# @trace_mcp_method("MCP API: Connect Server", operation="connect")
async def connect_mcp_server_with_capabilities(server_id: str, user_context: UserContext = Depends(get_user_context)):
    """Connect to an MCP server by pinging and discovering capabilities"""
    logger.info(f"📋 Connect server endpoint called for server: {server_id}")
    logger.info(f"   👤 User context: {user_context.user_id if user_context else 'None'}")
    
    try:
        # Get managers from global connection manager
        config_manager = MCPConfigManager(user_context.user_id)
        client_manager = MCPClientManager(config_manager)
        
        # Check if server exists
        server_config = config_manager.get_server(server_id)
        if not server_config:
            raise get_server_not_found_error(server_id, config_manager)
        
        if not server_config.enabled:
            raise HTTPException(status_code=400, detail=f"Server '{server_id}' is disabled")
        
        # Try to ping the server first
        try:
            current_status = await client_manager.ping_server(server_id)
            logger.info(f"   🔍 Server {server_id}: ping result = {current_status.value if current_status else 'None'}")
        except AuthenticationError as e:
            logger.error(f"   ❌ Authentication error for server {server_id}: {e}")
            current_status = MCPConnectionStatus.AUTH_REQUIRED
        except Exception as e:
            logger.error(f"   ❌ Error pinging server {server_id}: {traceback.format_exc()}")
            logger.error(f"   ❌ Error pinging server {server_id}: {e}")
            current_status = MCPConnectionStatus.ERROR
            config_manager.update_server_status(server_id, current_status, str(e))
            return {
                "success": False,
                "message": f"Failed to connect to server '{server_id}'",
                "status": current_status.value,
                "error": str(e)
            }
        
        # Update server status
        config_manager.update_server_status(server_id, current_status)
        
        # If connected, discover capabilities
        if current_status == MCPConnectionStatus.CONNECTED:
            try:
                capabilities = await client_manager.discover_capabilities(server_id)
                if capabilities:
                    # Update server config with discovered capabilities
                    if capabilities.get('tools',[]):
                        server_config.tools = capabilities.get('tools', []).copy()
                    if capabilities.get('resources',[]):
                        server_config.resources = capabilities.get('resources', [])
                    if capabilities.get('prompts',[]):
                        server_config.prompts = capabilities.get('prompts', [])
                    if capabilities.get('tool_details',[]):
                        server_config.tool_details = capabilities.get('tool_details', []).copy()
                    if capabilities.get('resource_details',[]):
                        server_config.resource_details = capabilities.get('resource_details', [])
                    if capabilities.get('resource_templates',[]):
                        server_config.resource_templates = capabilities.get('resource_templates', [])
                    if capabilities.get('resource_template_details',[]):
                        server_config.resource_template_details = capabilities.get('resource_template_details', [])
                    if capabilities.get('prompt_details',[]):
                        server_config.prompt_details = capabilities.get('prompt_details', [])
                    server_config.capabilities = {
                        "tools": bool(server_config.tools and len(server_config.tools) > 0),
                        "resources": bool(server_config.resources and len(server_config.resources) > 0),
                        "prompts": bool(server_config.prompts and len(server_config.prompts) > 0)
                    }
                    
                    # Save updated config
                    config_manager.update_server_config(server_id, server_config)
                    logger.info(f"   ✅ Successfully discovered capabilities for server '{server_id}'")
            except Exception as e:
                logger.error(f"   ❌ Error discovering capabilities for server {server_id}: {e}")
                # Don't fail the connection if capabilities discovery fails
        
        # Update vMCPs using server status
        vmcps_using_server = server_config.vmcps_using_server
        if vmcps_using_server:
            logger.info(f"   🔄 Updating vMCPs using {server_id} status: {current_status.value}")
            vmcp_config_manager = VMCPConfigManager(user_context.user_id)
            for vmcp_id in vmcps_using_server:
                if vmcp_id.startswith('@'):
                    continue
                vmcp_config = vmcp_config_manager.load_vmcp_config(specific_vmcp_id=vmcp_id)
                if vmcp_config:
                    vmcp_config_manager.update_vmcp_server(vmcp_id, server_config)
        
        if current_status == MCPConnectionStatus.AUTH_REQUIRED:
            return {
                "success": False,
                "message": f"Authentication required for server '{server_id}'",
                "status": current_status.value,
                "requires_auth": True
            }
        elif current_status == MCPConnectionStatus.CONNECTED:
            return {
                "success": True,
                "message": f"Successfully connected to server '{server_id}'",
                "status": current_status.value
            }
        else:
            return {
                "success": False,
                "message": f"Failed to connect to server '{server_id}'",
                "status": current_status.value
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"   ❌ Error connecting server: {e}")
        logger.error(f"   ❌ Exception type: {type(e).__name__}")
        logger.error(f"   ❌ Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to connect server: {str(e)}")

@router.post("/{server_id}/clear-cache")
# @trace_mcp_method("MCP API: Clear Cache", operation="clear_cache")
async def clear_cache_and_connect(server_id: str, user_context: UserContext = Depends(get_user_context)):
    """Clear cache (auth and session) and then try to connect and discover capabilities"""
    logger.info(f"📋 Clear cache endpoint called for server: {server_id}")
    logger.info(f"   👤 User context: {user_context.user_id if user_context else 'None'}")
    
    try:
        # Get managers from global connection manager
        config_manager = MCPConfigManager(user_context.user_id)
        client_manager = MCPClientManager(config_manager)
        
        # Check if server exists
        server_config = config_manager.get_server(server_id)
        if not server_config:
            raise get_server_not_found_error(server_id, config_manager)
        
        # Clear auth and session information
        server_config.auth = None
        server_config.session_id = None
        
        # Try to ping the server
        try:
            current_status = await client_manager.ping_server(server_id)
            logger.info(f"   🔍 Server {server_id}: ping result = {current_status.value}")
        except AuthenticationError as e:
            logger.error(f"   ❌ Authentication error for server {server_id}: {e}")
            current_status = MCPConnectionStatus.AUTH_REQUIRED
        except Exception as e:
            logger.error(f"   ❌ Error pinging server {server_id}: {e}")
            current_status = MCPConnectionStatus.ERROR
            config_manager.update_server_status(server_id, current_status, str(e))
            return {
                "success": False,
                "message": f"Failed to connect to server '{server_id}' after clearing cache",
                "status": current_status.value,
                "error": str(e)
            }
        
        # Update server status
        config_manager.update_server_status(server_id, current_status)
        
        # If connected, discover capabilities
        if current_status == MCPConnectionStatus.CONNECTED:
            try:
                capabilities = await client_manager.discover_capabilities(server_id)
                if capabilities:
                    # Update server config with discovered capabilities
                    if capabilities.get('tools',[]):
                        server_config.tools = capabilities.get('tools', []).copy()
                    if capabilities.get('resources',[]):
                        server_config.resources = capabilities.get('resources', [])
                    if capabilities.get('prompts',[]):
                        server_config.prompts = capabilities.get('prompts', [])
                    if capabilities.get('tool_details',[]):
                        server_config.tool_details = capabilities.get('tool_details', []).copy()
                    if capabilities.get('resource_details',[]):
                        server_config.resource_details = capabilities.get('resource_details', [])
                    if capabilities.get('resource_templates',[]):
                        server_config.resource_templates = capabilities.get('resource_templates', [])
                    if capabilities.get('resource_template_details',[]):
                        server_config.resource_template_details = capabilities.get('resource_template_details', [])
                    if capabilities.get('prompt_details',[]):
                        server_config.prompt_details = capabilities.get('prompt_details', [])
                    server_config.capabilities = {
                        "tools": bool(server_config.tools and len(server_config.tools) > 0),
                        "resources": bool(server_config.resources and len(server_config.resources) > 0),
                        "prompts": bool(server_config.prompts and len(server_config.prompts) > 0)
                    }
                    
                    # Save updated config
                    config_manager.update_server_config(server_id, server_config)
                    logger.info(f"   ✅ Successfully discovered capabilities for server '{server_id}'")
            except Exception as e:
                logger.error(f"   ❌ Error discovering capabilities for server {server_id}: {e}")
                # Don't fail the connection if capabilities discovery fails
        
        # Update vMCPs using server status
        vmcps_using_server = server_config.vmcps_using_server
        if vmcps_using_server:
            logger.info(f"   🔄 Updating vMCPs using {server_id} status: {current_status.value}")
            vmcp_config_manager = VMCPConfigManager(user_context.user_id)
            for vmcp_id in vmcps_using_server:
                if vmcp_id.startswith('@'):
                    continue
                vmcp_config = vmcp_config_manager.load_vmcp_config(specific_vmcp_id=vmcp_id)
                if vmcp_config:
                    vmcp_config_manager.update_vmcp_server(vmcp_id, server_config)
        
        if current_status == MCPConnectionStatus.AUTH_REQUIRED:
            return {
                "success": False,
                "message": f"Authentication required for server '{server_id}' after clearing cache",
                "status": current_status.value,
                "requires_auth": True
            }
        elif current_status == MCPConnectionStatus.CONNECTED:
            return {
                "success": True,
                "message": f"Successfully connected to server '{server_id}' after clearing cache",
                "status": current_status.value
            }
        else:
            return {
                "success": False,
                "message": f"Failed to connect to server '{server_id}' after clearing cache",
                "status": current_status.value
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"   ❌ Error clearing cache and connecting server: {e}")
        logger.error(f"   ❌ Exception type: {type(e).__name__}")
        logger.error(f"   ❌ Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to clear cache and connect server: {str(e)}")

@router.post("/{server_id}/clear-auth")
# @trace_mcp_method("MCP API: Clear Auth", operation="clear_auth")
async def clear_server_auth(server_id: str, user_context: UserContext = Depends(get_user_context)):
    """Clear authentication information for an MCP server"""
    logger.info(f"📋 Clear auth endpoint called for server: {server_id}")
    logger.info(f"   👤 User context: {user_context.user_id if user_context else 'None'}")
    
    try:
        # Get managers from global connection manager
        config_manager = MCPConfigManager(user_context.user_id)
        client_manager = MCPClientManager(config_manager)
        # Check if server exists
        server_config = config_manager.get_server(server_id)
        if not server_config:
            raise get_server_not_found_error(server_id, config_manager)
        
        # Clear auth and session information
        server_config.auth = None
        server_config.session_id = None
        
        # Update server status to disconnected since auth is cleared
        current_status = await config_manager.ping_server(server_id,client_manager)
        capabilities = await config_manager.discover_capabilities(server_id,client_manager)

        updated_server_config = config_manager.get_server(server_id)

        # Update vMCPs using server status
        vmcps_using_server = updated_server_config.vmcps_using_server
        if vmcps_using_server:
            logger.info(f"""   🔄 Updating vMCPs using {server_id} status: {current_status.value} and 
                        Capabilities: 
                        Tools: {len(capabilities.get('tools',[]))}
                        Resources: {len(capabilities.get('resources',[]))}
                        Prompts: {len(capabilities.get('prompts',[]))}""")
            vmcp_config_manager = VMCPConfigManager(user_context.user_id)
            for vmcp_id in vmcps_using_server:
                vmcp_config = vmcp_config_manager.load_vmcp_config(specific_vmcp_id=vmcp_id)
                if vmcp_config:
                    vmcp_config_manager.update_vmcp_server(vmcp_id, updated_server_config)
        
        # # Save updated config
        # success = config_manager.update_server_config(server_id, updated_server_config)
        # if not success:
        #     raise HTTPException(status_code=500, detail="Failed to clear server authentication")
        
        logger.info(f"   ✅ Successfully cleared auth for server '{server_id}'")
        return {
            "success": True,
            "message": f"Authentication information cleared for server '{server_id}'"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"   ❌ Error clearing server auth: {e}")
        logger.error(f"   ❌ Exception type: {type(e).__name__}")
        logger.error(f"   ❌ Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to clear server authentication: {str(e)}")

@router.get("/list")
# @trace_mcp_method("MCP API: List Servers", operation="list")
async def list_mcp_servers(user_context: UserContext = Depends(get_user_context), background_tasks: BackgroundTasks = None):
    """List all configured MCP servers without pinging (fast response)"""
    logger.info("📋 List servers endpoint called (fast mode)")
    logger.info(f"   👤 User context: {user_context.user_id if user_context else 'None'}")
    
    try:
        # Get managers from global connection manager
        logger.info("   🔧 Getting managers from global connection manager...")
        config_manager = MCPConfigManager(user_context.user_id)
        
        logger.info(f"   🔍 Config manager available: {config_manager is not None}")
        
        if not config_manager:
            logger.error("   ❌ Config manager is None - cannot list servers!")
            raise HTTPException(status_code=500, detail="Configuration manager not available")
        
        logger.info("   📊 Listing servers from config manager...")
        servers = config_manager.list_servers()
        logger.info(f"   📊 Found {len(servers)} servers in config")
        server_info = []
        
        for server in servers:
            # Create dictionary with stored status (no pinging)
            # server_dict = {
            #     "name": server.name,
            #     "server_id": server.ensure_server_id(),  # Ensure ID is generated
            #     "transport_type": server.transport_type.value,
            #     "status": server.status.value,  # Use stored status
            #     "description": server.description,
            #     "url": server.url,
            #     "command": server.command,
            #     "last_connected": server.last_connected,  # Keep as datetime object
            #     "last_error": server.last_error,
            #     "capabilities": {
            #         "tools_count": len(server.tools),
            #         "resources_count": len(server.resources),
            #         "prompts_count": len(server.prompts)
            #     } if server.capabilities else {
            #         "tools_count": 0,
            #         "resources_count": 0,
            #         "prompts_count": 0
            #     },
            #     "tools_list": server.tools if server.tools else [],
            #     "resources_list": server.resources if server.resources else [],
            #     "prompts_list": server.prompts if server.prompts else [],
            #     "resource_templates_list": server.resource_templates if server.resource_templates else [],
            #     "tool_details": server.tool_details if server.tool_details else [],
            #     "resource_details": server.resource_details if server.resource_details else [],
            #     "resource_template_details": server.resource_template_details if server.resource_template_details else [],
            #     "prompt_details": server.prompt_details if server.prompt_details else [],
            #     "auto_connect": server.auto_connect,
            #     "enabled": server.enabled,
            #     "auth_information": "present" if (server.auth or server.session_id) else "absent"
            # }
            # server_info.append(server_dict)
            server_info.append(server.to_dict())
        # Log the response summary
        connected_count = len([s for s in server_info if s.get("status") == "connected"])
        disconnected_count = len([s for s in server_info if s.get("status") == "disconnected"])
        auth_required_count = len([s for s in server_info if s.get("status") == "auth_required"])
        error_count = len([s for s in server_info if s.get("status") == "error"])
        
        logger.info(f"   📊 Response summary (from stored status):")
        logger.info(f"      • Total servers: {len(server_info)}")
        logger.info(f"   ✅ Successfully returning server list (fast mode)")
        return {
            "servers": server_info,
            "total": len(server_info),
            "connected": connected_count,
            "disconnected": disconnected_count,
            "auth_required": auth_required_count,
            "errors": error_count
        }
    except Exception as e:
        logger.error(f"   ❌ Error in list_mcp_servers: {e}")
        logger.error(f"   ❌ Exception type: {type(e).__name__}")
        logger.error(f"   ❌ Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/{server_id}/status")
# @trace_mcp_method("MCP API: Get Server Status", operation="status")
async def get_server_status(server_id: str, user_context: UserContext = Depends(get_user_context)):
    """Get real-time status for a specific server by pinging it"""
    logger.info(f"📋 Get server status endpoint called for: {server_id}")
    logger.info(f"   👤 User context: {user_context.user_id if user_context else 'None'}")
    
    try:
        # Get managers from global connection manager
        config_manager = MCPConfigManager(user_context.user_id)
        client_manager = MCPClientManager(config_manager)
        
        # Check if server exists
        server_config = config_manager.get_server(server_id)
        if not server_config:
            raise get_server_not_found_error(server_id, config_manager)
        
        # Ping the server to get current status
        try:
            current_status = await client_manager.ping_server(server_id)
            logger.info(f"   🔍 Server {server_id}: ping result = {current_status.value}")
        except AuthenticationError as e:
            logger.error(f"   ❌ Authentication error for server {server_id}: {e}")
            current_status = MCPConnectionStatus.AUTH_REQUIRED
        except Exception as e:
            logger.error(f"   ❌ Error pinging server {server_id}: {e}")
            current_status = MCPConnectionStatus.UNKNOWN
        
        # Update stored status if it changed
        if current_status != server_config.status:
            logger.info(f"   🔄 Updating {server_id} status: {server_config.status.value} → {current_status.value}")
            config_manager.update_server_status(server_id, current_status)

        # Update vMCPs using server status
        vmcps_using_server = server_config.vmcps_using_server
        logger.info(f"   🔄 vMCPs using server {server_id}: {vmcps_using_server}")
        if vmcps_using_server:
            logger.info(f"   🔄 Updating vMCPs using {server_id} status: {current_status.value}")
            vmcp_config_manager = VMCPConfigManager(user_context.user_id)
            for vmcp_id in vmcps_using_server:
                if vmcp_id.startswith('@'):
                    continue
                vmcp_config = vmcp_config_manager.load_vmcp_config(specific_vmcp_id=vmcp_id)
                if vmcp_config:
                    vmcp_config_manager.update_vmcp_server(vmcp_id, server_config)
        
        return {
            "server_id": server_id,
            "status": current_status.value,
            "last_updated": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"   ❌ Error getting server status: {e}")
        logger.error(f"   ❌ Exception type: {type(e).__name__}")
        logger.error(f"   ❌ Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to get server status: {str(e)}")

@router.post("/{server_id}/connect")
# @trace_mcp_method("MCP API: Connect Server (Legacy)", operation="connect_legacy")
async def connect_mcp_server(server_id: str, user_context: UserContext = Depends(get_user_context)):
    """Connect to an MCP server"""
    
    # Get managers from global connection manager
    config_manager = MCPConfigManager(user_context.user_id)
    client_manager = MCPClientManager(config_manager)
    
    server_config = config_manager.get_server(server_id)
    if not server_config:
        raise get_server_not_found_error(server_id, config_manager)
    
    if not server_config.enabled:
        raise HTTPException(status_code=400, detail=f"Server '{server_id}' is disabled")
    
    success = False
    try:
        status = await client_manager.ping_server(server_id)
        if status:
            return {
                "success": True,
                "message": f"Connected to '{server_id}' successfully"
            }
    except AuthenticationError as e:
        logger.error(f"   ❌ Authentication error for server {server_id}: {e}")
        return {
            "success": False,
            "message": f"Failed to connect to '{server_id}'",
            "status": server_config.status.value,
            "error": server_config.last_error
        }
    except Exception as e:
        logger.error(f"   ❌ Error pinging server {server_id}: {e}")
        return {
            "success": False,
            "message": f"Failed to connect to '{server_id}'",
            "status": server_config.status.value,
            "error": server_config.last_error
        }
    

    return {
        "success": False,
        "message": f"Failed to connect to '{server_id}'",
        "status": server_config.status.value,
        "error": server_config.last_error
    }
   
@router.post("/{server_id}/discover-capabilities")
# @trace_mcp_method("MCP API: Discover Capabilities", operation="discover")
async def discover_server_capabilities(server_id: str, user_context: UserContext = Depends(get_user_context)):
    """Discover capabilities of an MCP server"""
    logger.info(f"📋 Discover capabilities endpoint called for server: {server_id}")
    logger.info(f"   👤 User context: {user_context.user_id if user_context else 'None'}")
    
    try:
        # Get managers from global connection manager
        config_manager = MCPConfigManager(user_context.user_id)
        client_manager = MCPClientManager(config_manager)
        
        server_config = config_manager.get_server(server_id)
        if not server_config:
            raise get_server_not_found_error(server_id, config_manager)
        
        # Discover capabilities using the client manager
        try:
            capabilities = await client_manager.discover_capabilities(server_id)
            if capabilities:
                # Update server config with discovered capabilities
                if capabilities.get('tools',[]):
                    server_config.tools = capabilities.get('tools', []).copy()
                    logger.info(f"   🔍 Updated tools: {server_config.tools}")
                if capabilities.get('resources',[]):
                    server_config.resources = capabilities.get('resources', [])
                if capabilities.get('prompts',[]):
                    server_config.prompts = capabilities.get('prompts', [])
                if capabilities.get('tool_details',[]):
                    server_config.tool_details = capabilities.get('tool_details', []).copy()
                    logger.info(f"   🔍 Updated tool details: {server_config.tool_details}")
                if capabilities.get('resource_details',[]):
                    server_config.resource_details = capabilities.get('resource_details', [])
                if capabilities.get('resource_templates',[]):
                    server_config.resource_templates = capabilities.get('resource_templates', [])
                if capabilities.get('resource_template_details',[]):
                    server_config.resource_template_details = capabilities.get('resource_template_details', [])
                if capabilities.get('prompt_details',[]):
                    server_config.prompt_details = capabilities.get('prompt_details', [])
                server_config.capabilities = {
                    "tools": bool(server_config.tools and len(server_config.tools) > 0),
                    "resources": bool(server_config.resources and len(server_config.resources) > 0),
                    "prompts": bool(server_config.prompts and len(server_config.prompts) > 0)
                }
                
                # Save updated config
                config_manager.update_server_config(server_id, server_config)
                # Update vMCPs using server status
                vmcps_using_server = server_config.vmcps_using_server
                if vmcps_using_server:
                    logger.info(f"""   🔄 Updating vMCPs using {server_id} status: {server_config.status.value} and 
                        Capabilities: 
                        Tools: {len(capabilities.get('tools',[]))}
                        Resources: {len(capabilities.get('resources',[]))}
                        Prompts: {len(capabilities.get('prompts',[]))}""")
                    vmcp_config_manager = VMCPConfigManager(user_context.user_id)
                    for vmcp_id in vmcps_using_server:
                        if vmcp_id.startswith('@'):
                            continue
                        vmcp_config = vmcp_config_manager.load_vmcp_config(specific_vmcp_id=vmcp_id)
                        if vmcp_config:
                            vmcp_config_manager.update_vmcp_server(vmcp_id, server_config)
                

                logger.info(f"   ✅ Successfully discovered capabilities for server '{server_id}'")
                return {
                    "success": True,
                    "message": f"Successfully discovered capabilities for server '{server_id}'",
                    "capabilities": {
                        "tools_count": len(server_config.tools) if server_config.tools else 0,
                        "resources_count": len(server_config.resources) if server_config.resources else 0,
                        "prompts_count": len(server_config.prompts) if server_config.prompts else 0
                    },
                    "tools_list": server_config.tools if server_config.tools else [],
                    "resources_list": server_config.resources if server_config.resources else [],
                    "prompts_list": server_config.prompts if server_config.prompts else [],
                    "tool_details": server_config.tool_details if server_config.tool_details else [],
                    "resource_details": server_config.resource_details if server_config.resource_details else [],
                    "resource_templates": server_config.resource_templates if server_config.resource_templates else [],
                    "resource_template_details": server_config.resource_template_details if server_config.resource_template_details else [],
                    "prompt_details": server_config.prompt_details if server_config.prompt_details else []
                }
            else:
                raise HTTPException(status_code=500, detail="Failed to discover capabilities")
                
        except AuthenticationError as e:
            logger.error(f"   ❌ Authentication error for server {server_id}: {e}")
            return {
                "success": False,
                "message": f"Authentication required for server '{server_id}'",
                "error": "Authentication required",
                "capabilities": {
                    "tools": 0,
                    "resources": 0,
                    "prompts": 0
                }
            }
        except Exception as e:
            logger.error(f"   ❌ Error discovering capabilities for server {server_id}: {e}")
            return {
                "success": False,
                "message": f"Failed to discover capabilities for server '{server_id}'",
                "error": str(e),
                "capabilities": {
                    "tools": 0,
                    "resources": 0,
                    "prompts": 0
                }
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"   ❌ Error in discover capabilities endpoint: {e}")
        logger.error(f"   ❌ Exception type: {type(e).__name__}")
        logger.error(f"   ❌ Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to discover capabilities: {str(e)}")

@router.post("/{server_id}/ping")
# @trace_mcp_method("MCP API: Ping Server", operation="ping")
async def ping_mcp_server(server_id: str, user_context: UserContext = Depends(get_user_context)):
    """Ping an MCP server to check connectivity"""
    
    # Get managers from global connection manager
    config_manager = MCPConfigManager(user_context.user_id)
    client_manager = MCPClientManager(config_manager)
    
    server_config = config_manager.get_server(server_id)
    if not server_config:
        raise get_server_not_found_error(server_id, config_manager)
    
    success = False
    try:
        status = await client_manager.ping_server(server_id,server_config)
        if status:
            success = True
    except AuthenticationError as e:
        logger.error(f"   ❌ Authentication error for server {server_id}: {e}")
    except Exception as e:
        logger.error(f"   ❌ Error pinging server {server_id}: {e}")
    
    return {
        "server": server_id,
        "alive": success,
        "timestamp": datetime.now().isoformat()
    }

@router.post("/{server_id}/auth")
# @trace_mcp_method("MCP API: Initiate Auth", operation="auth")
async def initiate_auth(server_id: str, request: Request, user_context: UserContext = Depends(get_user_context)):
    """Initiate OAuth authentication for a server"""
    logger.info(f"📋 Initiate auth endpoint called for server: {server_id}")
    logger.info(f"   👤 User context: {user_context.user_id if user_context else 'None'}")
    
    try:
        # Get managers from global connection manager
        config_manager = MCPConfigManager(user_context.user_id)
        client_manager = MCPClientManager(config_manager)
        
        # Find the server configuration
        server_config = config_manager.get_server(server_id)
        if not server_config:
            raise get_server_not_found_error(server_id, config_manager)
        
        if not server_config.url:
            raise HTTPException(status_code=400, detail=f"Server '{server_id}' does not have a URL")
        
        # Initiate OAuth flow with callback URL to MCP proxy server
        # The callback should go to the OSS server where tokens are saved
        from vmcp.config import settings
        callback_url = f"{settings.base_url}/api/otherservers/oauth/callback"
        
        logger.info(f"   🔗 Using OAuth callback URL: {callback_url}")
        
        # Let MCPAuthManager generate its own state and initiate the flow
        result = await client_manager.auth_manager.initiate_oauth_flow(
            server_name=server_id,
            server_url=server_config.url,
            callback_url=callback_url,
            user_id=user_context.user_id,
            headers=server_config.headers
        )
        
        if result.get('status') == 'error':
            raise HTTPException(status_code=400, detail=result.get('error'))
        
        # Get the state that MCPAuthManager generated
        mcp_state = result.get('state')
        if not mcp_state:
            raise HTTPException(status_code=500, detail="No state returned from OAuth flow")
        
        logger.info(f"   🔑 Using MCP-generated state: {mcp_state[:8]}...")
        
        if result.get('status') == 'error':
            raise HTTPException(status_code=400, detail=result.get('error'))
        
        logger.info(f"   ✅ Successfully initiated OAuth flow for server '{server_id}'")
        return {
            "authorization_url": result['authorization_url'],
            "state": mcp_state,  # Return the MCP-generated state
            "message": f"Please visit the authorization URL to authenticate {server_id}",
            "instructions": "The URL will open in your default browser. After authorization, you'll be redirected back to complete the setup."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"   ❌ Error initiating auth for server '{server_id}': {e}")
        logger.error(f"   ❌ Exception type: {type(e).__name__}")
        logger.error(f"   ❌ Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{server_id}/tools/call")
# @trace_mcp_method("MCP API Tool Call", operation="api_call")
async def call_mcp_tool(server_id: str, request: MCPToolCallRequest, user_context: UserContext = Depends(get_user_context)):
    """Call a tool on an MCP server"""
    logger.info(f"📋 Call MCP tool endpoint called for server: {server_id}, tool: {request.tool_name}")
    logger.info(f"   👤 User context: {user_context.user_id if user_context else 'None'}")
    
    try:
        # Get managers from global connection manager
        config_manager = MCPConfigManager(user_context.user_id)
        client_manager = MCPClientManager(config_manager)
        
        try:
            result = await client_manager.call_tool(
                server_id, 
                request.tool_name, 
                request.arguments,
                connect_if_needed=True
            )
        except Exception as tool_error:
            logger.error(f"   ❌ Tool call failed: {tool_error}")
            logger.error(f"   ❌ Tool call exception type: {type(tool_error).__name__}")
            logger.error(f"   ❌ Tool call full traceback: {traceback.format_exc()}")
            raise
    
        if result is None:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to call tool '{request.tool_name}' on server '{server_id}'"
            )
        
        logger.info(f"   ✅ Successfully called tool '{request.tool_name}' on server '{server_id}'")
        return {
            "server": server_id,
            "tool": request.tool_name,
            "result": result
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"   ❌ Error calling MCP tool: {e}")
        logger.error(f"   ❌ Exception type: {type(e).__name__}")
        logger.error(f"   ❌ Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to call MCP tool: {str(e)}")

@router.post("/{server_id}/resources/read")
# @trace_mcp_method("MCP API: Read Resource", operation="read_resource")
async def get_mcp_resource(server_id: str, request: MCPResourceRequest, user_context: UserContext = Depends(get_user_context)):
    """Get a resource from an MCP server"""
    logger.info(f"📋 Get MCP resource endpoint called for server: {server_id}")
    logger.info(f"   👤 User context: {user_context.user_id if user_context else 'None'}")
    
    try:
        # Get managers from global connection manager
        config_manager = MCPConfigManager(user_context.user_id)
        client_manager = MCPClientManager(config_manager)
        
        try:
            contents = await client_manager.read_resource(server_id, request.uri)
            logger.info(f"   🔍 get_resource returned: {contents}")
        except Exception as e:
            logger.error(f"   ❌ Exception in client_manager.read_resource: {e}")
            logger.error(f"   ❌ Exception type: {type(e).__name__}")
            logger.error(f"   ❌ Full traceback: {traceback.format_exc()}")
            raise e
        
        if contents is None:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get resource '{request.uri}' from server '{server_id}'"
            )
        
        logger.info(f"   ✅ Successfully retrieved resource '{request.uri}' from server '{server_id}'")
        return {
            "server": server_id,
            "uri": request.uri,
            "contents": contents
        }
    except Exception as e:
        logger.error(f"   ❌ Error getting MCP resource: {e}")
        logger.error(f"   ❌ Exception type: {type(e).__name__}")
        logger.error(f"   ❌ Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to get MCP resource: {str(e)}")

@router.post("/{server_id}/prompts/get")
# @trace_mcp_method("MCP API: Get Prompt", operation="get_prompt")
async def get_mcp_prompt(server_id: str, request: MCPPromptRequest, user_context: UserContext = Depends(get_user_context)):
    """Get a prompt from an MCP server"""
    logger.info(f"📋 Get MCP prompt endpoint called for server: {server_id}")
    logger.info(f"   👤 User context: {user_context.user_id if user_context else 'None'}")
    
    try:
        # Get managers from global connection manager
        config_manager = MCPConfigManager(user_context.user_id)
        client_manager = MCPClientManager(config_manager)
        
        try:
            messages = await client_manager.get_prompt(
                server_id, 
                request.prompt_name, 
                request.arguments,
                connect_if_needed=True
            )
            logger.info(f"   🔍 get_prompt returned: {messages}")
        except Exception as e:
            logger.error(f"   ❌ Exception in client_manager.get_prompt: {e}")
            logger.error(f"   ❌ Exception type: {type(e).__name__}")
            logger.error(f"   ❌ Full traceback: {traceback.format_exc()}")
            raise e
        
        if messages is None:
            logger.error(f"   ❌ get_prompt returned None for prompt '{request.prompt_name}' from server '{server_id}'")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get prompt '{request.prompt_name}' from server '{server_id}'"
            )
        
        logger.info(f"   ✅ Successfully retrieved prompt '{request.prompt_name}' from server '{server_id}'")
        return {
            "server": server_id,
            "prompt": request.prompt_name,
            "messages": messages
        }
    except Exception as e:
        logger.error(f"   ❌ Error getting MCP prompt: {e}")
        logger.error(f"   ❌ Exception type: {type(e).__name__}")
        logger.error(f"   ❌ Full traceback: {traceback.format_exc()}")
        
        # If it's a validation error, return 422 with details
        if hasattr(e, 'status_code') and e.status_code == 422:
            logger.error(f"   ❌ Validation error details: {getattr(e, 'detail', 'No details')}")
            raise HTTPException(status_code=422, detail=f"Validation error: {str(e)}")
        
        raise HTTPException(status_code=500, detail=f"Failed to get MCP prompt: {str(e)}")

@router.get("/tools/discover")
# @trace_mcp_method("MCP API: Discover Tools", operation="discover_tools")
async def discover_mcp_tools(user_context: UserContext = Depends(get_user_context)):
    """Discover all available tools from connected MCP servers"""
    logger.info("📋 Discover MCP tools endpoint called")
    logger.info(f"   👤 User context: {user_context.user_id if user_context else 'None'}")
    
    try:
        # Get managers from global connection manager
        config_manager = MCPConfigManager(user_context.user_id)
        
        servers = config_manager.list_servers()
        
        tools = []
        
        for server in servers:
            if server.status == MCPConnectionStatus.CONNECTED and server.tools:
                for tool in server.tools:
                    # Prefix tool name with server name to avoid conflicts
                    prefixed_name = f"{server.name}_{tool}"
                    tools.append({
                        "name": prefixed_name,
                        "original_name": tool,
                        "server": server.name,
                        "description": f"Tool '{tool}' from {server.name} server",
                        "server_id": server.server_id
                    })
        
        return {
            "tools": tools,
            "total_tools": len(tools),
            "connected_servers": len([s for s in servers if s.status == MCPConnectionStatus.CONNECTED])
        }
    except Exception as e:
        logger.error(f"   ❌ Error discovering MCP tools: {e}")
        logger.error(f"   ❌ Exception type: {type(e).__name__}")
        logger.error(f"   ❌ Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to discover MCP tools: {str(e)}")

@router.get("/{server_id}/tools/list")
# @trace_mcp_method("MCP API: List Server Tools", operation="list_tools")
async def list_server_tools(server_id: str, user_context: UserContext = Depends(get_user_context)):
    """List all tools for a specific server"""
    logger.info(f"📋 List server tools endpoint called for server: {server_id}")
    logger.info(f"   👤 User context: {user_context.user_id if user_context else 'None'}")

    try:
        # Create fresh managers for this request
        config_manager = MCPConfigManager(user_context.user_id)
        client_manager = MCPClientManager(config_manager)
        
        server_config = config_manager.get_server(server_id)
        if not server_config:
            raise get_server_not_found_error(server_id, config_manager)
        
        tools_dict = await client_manager.tools_list(server_id)
    except AuthenticationError as e:
        logger.error(f"   ❌ Authentication error for server {server_id}: {e}")
        raise HTTPException(status_code=401, detail=f"Authentication error for server {server_id}: {e}")
    except Exception as e:
        logger.error(f"   ❌ Error listing server tools: {e}")
        logger.error(f"   ❌ Exception type: {type(e).__name__}")
        logger.error(f"   ❌ Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to list server tools: {str(e)}")
    
    # Get tools from live connection
    tools = []
    for tool_name, tool_info in tools_dict.items():
        tool_data = {
            "name": tool_name,
            "server": server_id,
            "description": tool_info.description,
            "inputSchema": tool_info.inputSchema,
            "annotations": tool_info.annotations,
        }
        tools.append(tool_data)
    
    # Update server config after successful operation
    config_manager.update_server_status(server_id, MCPConnectionStatus.CONNECTED)
    
    logger.info(f"   ✅ Successfully listed {len(tools)} tools for server '{server_id}'")
    return {
        "server": server_id,
        "tools": tools,
        "total_tools": len(tools)
    }

@router.get("/{server_id}/resources/list")
# @trace_mcp_method("MCP API: List Server Resources", operation="list_resources")
async def list_server_resources(server_id: str, user_context: UserContext = Depends(get_user_context)):
    """List all resources for a specific server"""
    logger.info(f"📋 List server resources endpoint called for server: {server_id}")
    logger.info(f"   👤 User context: {user_context.user_id if user_context else 'None'}")
    
    try:
        # Create fresh managers for this request
        config_manager = MCPConfigManager(user_context.user_id)
        client_manager = MCPClientManager(config_manager)
        
        server_config = config_manager.get_server(server_id)
        if not server_config:
            raise get_server_not_found_error(server_id, config_manager)
        
        resources_dict = await client_manager.resources_list(server_id)
    except AuthenticationError as e:
        logger.error(f"   ❌ Authentication error for server {server_id}: {e}")
        raise HTTPException(status_code=401, detail=f"Authentication error for server {server_id}: {e}")
    except Exception as e:
        logger.error(f"   ❌ Error listing server resources: {e}")
        logger.error(f"   ❌ Exception type: {type(e).__name__}")
        logger.error(f"   ❌ Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to list server resources: {str(e)}")
    
    resources = []
    for resource_uri, resource_info in resources_dict.items():
        resources.append({
            "uri": resource_uri,
            "server": server_id,
            "description": resource_info.description,
            "annotations": resource_info.annotations,
        })
        
    logger.info(f"   ✅ Successfully listed {len(resources)} resources for server '{server_id}'")
    return {
        "server": server_id,
        "resources": resources,
        "total_resources": len(resources)
    }

@router.get("/{server_id}/prompts/list")
# @trace_mcp_method("MCP API: List Server Prompts", operation="list_prompts")
async def list_server_prompts(server_id: str, user_context: UserContext = Depends(get_user_context)):
    """List all prompts for a specific server"""
    logger.info(f"📋 List server prompts endpoint called for server: {server_id}")
    logger.info(f"   👤 User context: {user_context.user_id if user_context else 'None'}")

    try:
        # Create fresh managers for this request
        config_manager = MCPConfigManager(user_context.user_id)
        client_manager = MCPClientManager(config_manager)
        
        server_config = config_manager.get_server(server_id)
        if not server_config:
            raise get_server_not_found_error(server_id, config_manager)
        
        prompts_dict = await client_manager.prompts_list(server_id)
    except AuthenticationError as e:
        logger.error(f"   ❌ Authentication error for server {server_id}: {e}")
        raise HTTPException(status_code=401, detail=f"Authentication error for server {server_id}: {e}")
    except Exception as e:
        logger.error(f"   ❌ Error listing server prompts: {e}")
        logger.error(f"   ❌ Exception type: {type(e).__name__}")
        logger.error(f"   ❌ Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to list server prompts: {str(e)}")

    prompts = []
    for prompt_name, prompt_info in prompts_dict.items():
        prompts.append({
            "name": prompt_name,
            "server": server_id,
            "description": prompt_info.description,
            "arguments": prompt_info.arguments
        })
    
    # Update server config after successful operation
    config_manager.update_server_status(server_id, MCPConnectionStatus.CONNECTED)
    
    logger.info(f"   ✅ Successfully listed {len(prompts)} prompts for server '{server_id}'")
    return {
        "server": server_id,
        "prompts": prompts,
        "total_prompts": len(prompts)
    }

@router.get("/stats")
# @trace_mcp_method("MCP API: Get Stats", operation="stats")
async def get_mcp_stats(user_context: UserContext = Depends(get_user_context)):
    """Get MCP system statistics"""
    logger.info("📋 Get MCP stats endpoint called")
    logger.info(f"   👤 User context: {user_context.user_id if user_context else 'None'}")
    
    try:
        # Get managers from global connection manager
        config_manager = MCPConfigManager(user_context.user_id)
        client_manager = MCPClientManager(config_manager)
        
        servers = config_manager.list_servers()
        
        total_tools = 0
        total_resources = 0
        total_prompts = 0
        connected_count = 0
        
        for server in servers:
            if server.status == MCPConnectionStatus.CONNECTED:
                connected_count += 1
                if server.tools:
                    total_tools += len(server.tools)
                if server.resources:
                    total_resources += len(server.resources)
                if server.prompts:
                    total_prompts += len(server.prompts)
        
        logger.info(f"   ✅ Successfully retrieved stats: {len(servers)} servers, {connected_count} connected")
        return {
            "servers": {
                "total": len(servers),
                "connected": connected_count,
                "disconnected": len([s for s in servers if s.status == MCPConnectionStatus.DISCONNECTED]),
                "auth_required": len([s for s in servers if s.status == MCPConnectionStatus.AUTH_REQUIRED]),
                "errors": len([s for s in servers if s.status == MCPConnectionStatus.ERROR])
            },
            "capabilities": {
                "tools": total_tools,
                "resources": total_resources,
                "prompts": total_prompts
            }
        }
    except Exception as e:
        logger.error(f"   ❌ Error getting MCP stats: {e}")
        logger.error(f"   ❌ Exception type: {type(e).__name__}")
        logger.error(f"   ❌ Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to get MCP stats: {str(e)}")

async def connect_server_background(server_id: str, user_id: str, 
                                    config_manager: MCPConfigManager):
    """Background task to connect to a server"""
    logger.info(f"""🔄 Background connection attempt for server '{server_id}' by user '{user_id}' and 
                config manager {config_manager._servers.keys()}""")
    
    try:
        # Load server configuration from shared storage
        server_config = config_manager.get_server(server_id)
        if server_config and server_config.enabled:
            try:
                # Update status to indicate connection attempt
                config_manager.update_server_status(server_id, MCPConnectionStatus.DISCONNECTED)
                logger.info(f"✅ Background connection request sent for server '{server_id}'")
                logger.info(f"   ℹ️ Actual connection will be handled by MCP server")
            except Exception as e:
                logger.error(f"❌ Background connection failed for server '{server_id}': {e}")
                config_manager.update_server_status(server_id, MCPConnectionStatus.ERROR, str(e))
        else:
            logger.warning(f"⚠️ Server '{server_id}' not found or not enabled for background connection")
    except Exception as e:
        logger.error(f"❌ Error in background connection task for server '{server_id}': {e}")
        logger.error(f"❌ Exception type: {type(e).__name__}")
        logger.error(f"❌ Full traceback: {traceback.format_exc()}")


# Global MCP Registry endpoints
@router.get("/registry/servers")
# @trace_mcp_method("MCP API: List Registry Servers", operation="registry_list")
async def list_global_mcp_servers(
    category: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    user_context: UserContext = Depends(get_user_context)
):
    """
    List all global MCP servers with optional filtering
    
    Returns a list of pre-configured MCP servers that are available globally.
    """
    try:
        logger.info(f"📋 Listing global MCP servers for user {user_context.user_id}")
        
        # Import here to avoid circular imports
        from sqlalchemy.orm import Session
        from vmcp.storage.models import GlobalMCPServerRegistry
        from vmcp.storage.database import SessionLocal

        # Get database session
        db = SessionLocal()
        
        # Build query
        query = db.query(GlobalMCPServerRegistry)
        
        # Apply filters
        if category:
            query = query.filter(GlobalMCPServerRegistry.server_metadata['category'].astext == category)
        
        if search:
            search_term = f"%{search.lower()}%"
            query = query.filter(
                db.or_(
                    GlobalMCPServerRegistry.name.ilike(search_term),
                    GlobalMCPServerRegistry.description.ilike(search_term)
                )
            )
        
        # Apply pagination
        total_count = query.count()
        servers = query.offset(offset).limit(limit).all()
        
        # Convert to response format
        server_list = []
        for server in servers:
            server_data = {
                "id": server.server_id,
                "name": server.name,
                "description": server.description,
                "transport": server.mcp_registry_config.get("transport_type", "http"),
                "url": server.mcp_registry_config.get("url"),
                "favicon_url": server.mcp_registry_config.get("favicon_url"),
                "category": server.server_metadata.get("category", "MCP Servers"),
                "icon": server.server_metadata.get("icon", "🔍"),
                "requiresAuth": server.server_metadata.get("requiresAuth", False),
                "env_vars": server.server_metadata.get("env_vars", ""),
                "note": server.server_metadata.get("note", ""),
                "mcp_registry_config": server.mcp_registry_config,
                "mcp_server_config": server.mcp_server_config,
                "stats": server.stats,
                "created_at": server.created_at.isoformat() if server.created_at else None,
                "updated_at": server.updated_at.isoformat() if server.updated_at else None
            }
            server_list.append(server_data)
        
        logger.info(f"✅ Retrieved {len(server_list)} global MCP servers (total: {total_count})")
        
        return {
            "success": True,
            "servers": server_list,
            "total": total_count,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"❌ Error listing global MCP servers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/registry/servers/{server_id}")
# @trace_mcp_method("MCP API: Get Registry Server", operation="registry_get")
async def get_global_mcp_server(
    server_id: str,
    user_context: UserContext = Depends(get_user_context)
):
    """
    Get a specific global MCP server by ID
    """
    try:
        logger.info(f"📋 Getting global MCP server {server_id} for user {user_context.user_id}")
        
        # Import here to avoid circular imports
        from sqlalchemy.orm import Session
        from vmcp.storage.models import GlobalMCPServerRegistry
        from vmcp.storage.database import SessionLocal

        # Get database session
        db = SessionLocal()
        
        server = db.query(GlobalMCPServerRegistry).filter(
            GlobalMCPServerRegistry.server_id == server_id
        ).first()
        
        if not server:
            raise HTTPException(status_code=404, detail=f"Global MCP server not found: {server_id}")
        
        server_data = {
            "id": server.server_id,
            "name": server.name,
            "description": server.description,
            "transport": server.mcp_registry_config.get("transport_type", "http"),
            "url": server.mcp_registry_config.get("url"),
            "favicon_url": server.mcp_registry_config.get("favicon_url"),
            "category": server.server_metadata.get("category", "MCP Servers"),
            "icon": server.server_metadata.get("icon", "🔍"),
            "requiresAuth": server.server_metadata.get("requiresAuth", False),
            "env_vars": server.server_metadata.get("env_vars", ""),
            "note": server.server_metadata.get("note", ""),
            "mcp_registry_config": server.mcp_registry_config,
            "mcp_server_config": server.mcp_server_config,
            "stats": server.stats,
            "created_at": server.created_at.isoformat() if server.created_at else None,
            "updated_at": server.updated_at.isoformat() if server.updated_at else None
        }
        
        logger.info(f"✅ Retrieved global MCP server: {server_id}")
        
        return {
            "success": True,
            "server": server_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting global MCP server {server_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/registry/categories")
# @trace_mcp_method("MCP API: Get Registry Categories", operation="registry_categories")
async def get_global_mcp_categories(
    user_context: UserContext = Depends(get_user_context)
):
    """
    Get all available categories from global MCP servers
    """
    try:
        logger.info(f"📋 Getting global MCP categories for user {user_context.user_id}")
        
        # Import here to avoid circular imports
        from sqlalchemy.orm import Session
        from auth_service.database import get_db
        from auth_service.models import GlobalMCPServerRegistry
        from sqlalchemy import distinct, func
        
        # Get database session
        db = next(get_db())
        
        # Get distinct categories
        categories = db.query(
            func.json_extract_path_text(GlobalMCPServerRegistry.server_metadata, 'category').label('category')
        ).filter(
            func.json_extract_path_text(GlobalMCPServerRegistry.server_metadata, 'category').isnot(None)
        ).distinct().all()
        
        category_list = [cat.category for cat in categories if cat.category]
        
        logger.info(f"✅ Retrieved {len(category_list)} categories")
        
        return {
            "success": True,
            "categories": category_list
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting global MCP categories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/registry/servers/{server_id}/install")
# @trace_mcp_method("MCP API: Install Registry Server", operation="registry_install")
async def install_global_mcp_server(
    server_id: str,
    user_context: UserContext = Depends(get_user_context)
):
    """
    Install a global MCP server (placeholder for future implementation)
    """
    try:
        logger.info(f"📋 Installing global MCP server {server_id} for user {user_context.user_id}")
        
        # For now, this is a placeholder - in the future this could:
        # - Create a user-specific MCP server configuration
        # - Add the server to the user's MCP servers list
        # - Set up authentication if required
        
        logger.info(f"✅ Global MCP server installation requested: {server_id}")
        return {
            "success": True,
            "message": f"Global MCP server {server_id} installation initiated",
            "server_id": server_id
        }
        
    except Exception as e:
        logger.error(f"❌ Error installing global MCP server {server_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 