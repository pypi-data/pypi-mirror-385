#!/usr/bin/env python3
"""
Resource Manager
================

Handles resource CRUD operations and resource fetching for vMCP.
"""

import logging
import asyncio
import urllib.parse
from datetime import datetime
from typing import Dict, Any, Optional

from mcp.types import TextResourceContents, BlobResourceContents, ReadResourceResult

from vmcp.config import settings

logger = logging.getLogger("1xN_vMCP_RESOURCE_MANAGER")


def add_resource(storage, vmcp_id: str, resource_data: Dict[str, Any]) -> bool:
    """
    Add a resource to the vMCP.

    Args:
        storage: StorageBase instance
        vmcp_id: VMCP identifier
        resource_data: Resource data dictionary

    Returns:
        True if successful, False otherwise
    """
    logger.info(f"Adding resource to vMCP: {vmcp_id} with data: {resource_data}")
    try:
        vmcp_config = storage.load_vmcp_config(vmcp_id)
        if not vmcp_config:
            return False

        vmcp_config.uploaded_files.append(resource_data)
        vmcp_config.custom_resources.append(resource_data)
        vmcp_config.updated_at = datetime.now()
        logger.info(f"Updated VMCP config: {vmcp_config.custom_resources} (ID: {vmcp_id})")
        return storage.update_vmcp(vmcp_config)
    except Exception as e:
        logger.error(f"Error adding resource to vMCP {vmcp_id}: {e}")
        return False


def update_resource(storage, vmcp_id: str, resource_data: Dict[str, Any]) -> bool:
    """
    Update a resource in the vMCP.

    Args:
        storage: StorageBase instance
        vmcp_id: VMCP identifier
        resource_data: Updated resource data dictionary

    Returns:
        True if successful, False otherwise
    """
    logger.info(f"Updating resource in vMCP: {vmcp_id} with data: {resource_data}")
    try:
        vmcp_config = storage.load_vmcp_config(vmcp_id)
        if not vmcp_config:
            return False

        vmcp_config.uploaded_files = [resource for resource in vmcp_config.uploaded_files if resource.get('id') != resource_data.get('id')]
        vmcp_config.custom_resources = [resource for resource in vmcp_config.custom_resources if resource.get('id') != resource_data.get('id')]
        vmcp_config.uploaded_files += [resource_data]
        vmcp_config.custom_resources += [resource_data]
        vmcp_config.updated_at = datetime.now()
        logger.info(f"Updated VMCP config: {vmcp_config.custom_resources} (ID: {vmcp_id})")
        logger.info(f"VMCP config dict: {vmcp_config.to_dict()}")
        return storage.update_vmcp(vmcp_config)
    except Exception as e:
        logger.error(f"Error updating resource in vMCP {vmcp_id}: {e}")
        return False


def delete_resource(storage, vmcp_id: str, resource_data: Dict[str, Any]) -> bool:
    """
    Delete a resource from the vMCP.

    Args:
        storage: StorageBase instance
        vmcp_id: VMCP identifier
        resource_data: Resource data dictionary with 'id' field

    Returns:
        True if successful, False otherwise
    """
    logger.info(f"Deleting resource from vMCP: {vmcp_id} with data: {resource_data}")
    try:
        vmcp_config = storage.load_vmcp_config(vmcp_id)
        if not vmcp_config:
            return False

        vmcp_config.uploaded_files = [resource for resource in vmcp_config.uploaded_files if resource.get('id') != resource_data.get('id')]
        vmcp_config.custom_resources = [resource for resource in vmcp_config.custom_resources if resource.get('id') != resource_data.get('id')]
        vmcp_config.updated_at = datetime.now()
        logger.info(f"Updated VMCP config: {vmcp_config.custom_resources} (ID: {vmcp_id})")
        return storage.update_vmcp(vmcp_config)
    except Exception as e:
        logger.error(f"Error deleting resource from vMCP {vmcp_id}: {e}")
        return False


async def get_resource(
    storage,
    vmcp_id: str,
    user_id: str,
    mcp_client_manager,
    log_operation_func,
    resource_id: str,
    connect_if_needed: bool = True
) -> ReadResourceResult:
    """
    Get a specific resource by ID.

    Supports:
    - Custom resources (custom:vmcp-scheme://filename)
    - Widget resources (ui://widget/...)
    - Server resources (server:resource_name)

    Args:
        storage: StorageBase instance
        vmcp_id: VMCP identifier
        user_id: User identifier
        mcp_client_manager: MCP client manager for server resources
        log_operation_func: Function to log operations
        resource_id: Resource identifier/URI
        connect_if_needed: Whether to connect to server if needed

    Returns:
        ReadResourceResult with resource contents
    """
    # Convert resource_id to string if it's a Pydantic AnyUrl or other object
    resource_id_str = str(resource_id)
    logger.info(f"🔍 VMCP Config Manager: Searching for resource '{resource_id_str}' in vMCP '{vmcp_id}'")

    vmcp_config = storage.load_vmcp_config(vmcp_id)
    if not vmcp_config:
        raise ValueError(f"vMCP config not found: {vmcp_id}")

    custom_resources = vmcp_config.custom_resources

    # Check if this is a custom resource URI (starts with "custom:")
    if resource_id_str.startswith('custom:'):
        logger.info(f"🔍 VMCP Config Manager: Detected custom resource URI: '{resource_id_str}'")

        # Parse the custom URI to extract the filename
        # Format: custom:vmcp-scheme://encoded_filename
        try:
            uri_parts = resource_id_str.split('://', 1)
            if len(uri_parts) == 2:
                scheme_part = uri_parts[0]  # custom:vmcp-scheme
                encoded_filename = uri_parts[1]  # encoded_filename

                # Decode the filename
                original_filename = urllib.parse.unquote(encoded_filename)

                logger.info(f"🔍 VMCP Config Manager: Decoded filename: '{original_filename}'")

                # Find the custom resource by original_filename
                for resource in custom_resources:
                    logger.info(f"🔍 VMCP Config Manager: Checking custom resource: '{resource.get('original_filename')}' against '{original_filename}'")
                    if resource.get('resource_name') == original_filename:
                        logger.info(f"✅ VMCP Config Manager: Found matching custom resource for '{original_filename}'")
                        result = await call_custom_resource(storage, vmcp_id, user_id, resource_id_str)
                        return result

                logger.warning(f"⚠️ VMCP Config Manager: Custom resource with filename '{original_filename}' not found in custom_resources")
            else:
                logger.warning(f"⚠️ VMCP Config Manager: Invalid custom resource URI format: '{resource_id_str}'")
        except Exception as e:
            logger.error(f"❌ VMCP Config Manager: Error parsing custom resource URI '{resource_id_str}': {e}")

    # Legacy check for resource_name matching (for backward compatibility)
    for resource in custom_resources:
        logger.info(f"🔍 VMCP Config Manager: Checking custom resource resource_name: '{resource.get('resource_name')}' against '{resource_id_str}'")
        if resource.get('resource_name') == resource_id_str:
            result = await call_custom_resource(storage, vmcp_id, user_id, resource_id_str)
            return result

    # Check if this is a widget resource URI (ui://widget/...)
    if resource_id_str.startswith('ui://widget/'):
        logger.info(f"🔍 VMCP Config Manager: Detected widget resource URI: '{resource_id_str}'")

        # Load widgets from database and match by template_uri
        from vmcp.storage.database import get_db
        from vmcp.storage.models import Widget
        db = next(get_db())
        try:
            widget = db.query(Widget).filter(
                Widget.user_id == user_id,
                Widget.vmcp_id == vmcp_id,
                Widget.template_uri == resource_id_str
            ).first()

            if widget and widget.build_status == 'built':
                logger.info(f"✅ VMCP Config Manager: Found widget '{widget.name}' with template_uri '{resource_id_str}'")

                widget_data = widget.widget_data or {}

                # Get the built HTML from blob storage
                widget_html = ""
                built_files = widget_data.get('built_files', {})
                html_blob_id = built_files.get('html')

                if html_blob_id:
                    logger.info(f"Fetching HTML blob: {html_blob_id}")
                    from vmcp.storage.models import Blob
                    html_blob = db.query(Blob).filter(Blob.id == html_blob_id).first()

                    if html_blob and html_blob.content:
                        # Decode bytes to string
                        if isinstance(html_blob.content, bytes):
                            widget_html = html_blob.content.decode('utf-8')
                        else:
                            widget_html = str(html_blob.content)
                        logger.info(f"✅ Fetched HTML blob, size: {len(widget_html)} bytes")
                    else:
                        logger.warning("⚠️ HTML blob not found, falling back to reference HTML")

                # Fallback: create reference HTML if no built HTML exists
                if not widget_html:
                    css_url = f"{settings.base_url}/api/widgets/{widget.widget_id}/serve/css"
                    js_url = f"{settings.base_url}/api/widgets/{widget.widget_id}/serve/js"
                    root_id = widget_data.get('root_id', f'{widget.name.lower().replace(" ", "-")}-root')
                    widget_html = f'<link rel="stylesheet" href="{css_url}">\n<div id="{root_id}"></div>\n<script type="module" src="{js_url}"></script>'
                    logger.info("Using fallback reference HTML")

                # Return widget resource in MCP format following OpenAI Apps SDK spec
                # Build metadata following OpenAI format
                invoking_msg = widget_data.get('invoking_message', f'Loading {widget.name}...')
                invoked_msg = widget_data.get('invoked_message', f'{widget.name} ready')

                content = TextResourceContents(
                    uri=resource_id_str,
                    mimeType="text/html+skybridge",
                    text=widget_html,
                    _meta={
                        "openai/outputTemplate": resource_id_str,
                        "openai/toolInvocation/invoking": invoking_msg,
                        "openai/toolInvocation/invoked": invoked_msg,
                        "openai/widgetAccessible": True,
                        "openai/resultCanProduceWidget": True,
                        "annotations": {
                            "destructiveHint": False,
                            "openWorldHint": False,
                            "readOnlyHint": True
                        }
                    }
                )
                return ReadResourceResult(contents=[content])
            else:
                logger.error(f"❌ VMCP Config Manager: Widget with template_uri '{resource_id_str}' not found or not built")
        except Exception as e:
            logger.error(f"❌ VMCP Config Manager: Error loading widget with template_uri '{resource_id_str}': {e}")
        finally:
            db.close()

    # Parse server resource URI (server:resource_name)
    resource_server_name = resource_id_str.split(':')[0]
    resource_original_name = ":".join(resource_id_str.split(':')[1:])

    logger.info(f"🔍 VMCP Config Manager: Parsed resource name - server: '{resource_server_name}', original: '{resource_original_name}'")

    vmcp_servers = vmcp_config.vmcp_config.get('selected_servers', [])
    logger.info(f"🔍 VMCP Config Manager: Found {len(vmcp_servers)} servers in vMCP config")
    logger.info(f"🔍 VMCP Config Manager: Server details: {[(s.get('name'), s.get('name', '').replace('_', '')) for s in vmcp_servers]}")

    for server in vmcp_servers:
        server_name = server.get('name')
        server_id = server.get('server_id')
        server_name_clean = server_name.replace('_', '')

        logger.info(f"🔍 VMCP Config Manager: Checking server '{server_name}' (clean: '{server_name_clean}') against '{resource_server_name}'")

        if server_name_clean.lower() == resource_server_name.lower():
            logger.info(f"✅ VMCP Config Manager: Found matching server '{server_name}' for resource '{resource_id_str}'")
            logger.info(f"🔍 VMCP Config Manager: Calling resource '{resource_original_name}' on server '{server_name}'")

            result = await mcp_client_manager.read_resource(
                server_id,
                resource_original_name)

            logger.info(f"✅ VMCP Config Manager: Resource read successful, result type: {type(result)}")
            logger.info(f"[BACKGROUND TASK LOGGING] Adding background task to log resource read for vMCP {vmcp_id}")
            if user_id:
                # Fire and forget - don't await, just call and let it run
                asyncio.create_task(
                    log_operation_func(
                        operation_type="resource_get",
                        operation_id=resource_id_str,
                        arguments=resource_original_name,
                        result=result,
                        metadata={"server": server_name, "resource": resource_original_name, "server_id": server_id}
                    )
                )

            return result

    logger.error(f"❌ VMCP Config Manager: Resource '{resource_id_str}' not found in any server")
    logger.error(f"❌ VMCP Config Manager: Searched servers: {[s.get('name') for s in vmcp_servers]}")
    raise ValueError(f"Resource {resource_id_str} not found in vMCP {vmcp_id}")


async def call_custom_resource(
    storage,
    vmcp_id: str,
    user_id: str,
    resource_id: str,
    connect_if_needed: bool = True
) -> ReadResourceResult:
    """
    Call a custom resource and return its contents.

    Args:
        storage: StorageBase instance
        vmcp_id: VMCP identifier
        user_id: User identifier
        resource_id: Resource identifier
        connect_if_needed: Whether to connect if needed

    Returns:
        ReadResourceResult with resource contents
    """
    logger.info(f"🔍 VMCP Config Manager: Calling custom resource '{resource_id}'")
    vmcp_config = storage.load_vmcp_config(vmcp_id)
    if not vmcp_config:
        raise ValueError(f"vMCP config not found: {vmcp_id}")

    # Find the custom resource
    custom_resource = None

    # Check if this is a custom resource URI (starts with "custom:")
    if resource_id.startswith('custom:'):
        logger.info(f"🔍 VMCP Config Manager: Detected custom resource URI in call_custom_resource: '{resource_id}'")

        # Parse the custom URI to extract the filename
        # Format: custom:vmcp-scheme://encoded_filename
        try:
            uri_parts = resource_id.split('://', 1)
            if len(uri_parts) == 2:
                scheme_part = uri_parts[0]  # custom:vmcp-scheme
                encoded_filename = uri_parts[1]  # encoded_filename

                # Decode the filename
                original_filename = urllib.parse.unquote(encoded_filename)

                logger.info(f"🔍 VMCP Config Manager: Decoded filename in call_custom_resource: '{original_filename}'")

                # Find the custom resource by original_filename
                for resource in vmcp_config.custom_resources:
                    logger.info(f"🔍 VMCP Config Manager: Checking custom resource in call_custom_resource: '{resource.get('original_filename')}' against '{original_filename}'")
                    if resource.get('original_filename') == original_filename:
                        logger.info(f"✅ VMCP Config Manager: Found matching custom resource in call_custom_resource for '{original_filename}'")
                        custom_resource = resource
                        break

                if not custom_resource:
                    logger.warning(f"⚠️ VMCP Config Manager: Custom resource with filename '{original_filename}' not found in custom_resources in call_custom_resource")
            else:
                logger.warning(f"⚠️ VMCP Config Manager: Invalid custom resource URI format in call_custom_resource: '{resource_id}'")
        except Exception as e:
            logger.error(f"❌ VMCP Config Manager: Error parsing custom resource URI in call_custom_resource '{resource_id}': {e}")

    # Legacy check for resource_name matching (for backward compatibility)
    if not custom_resource:
        for resource in vmcp_config.custom_resources:
            logger.info(f"🔍 VMCP Config Manager: Checking custom resource resource_name in call_custom_resource: '{resource.get('resource_name')}' against '{resource_id}'")
            if resource.get('resource_name') == resource_id:
                custom_resource = resource
                break

    if not custom_resource:
        raise ValueError(f"Custom resource '{resource_id}' not found in vMCP {vmcp_id}")

    # Direct database fetch for resource content
    from vmcp.storage.models import Blob
    from vmcp.storage.database import get_db

    db = next(get_db())
    try:
        if vmcp_id and vmcp_id.startswith("@"):
            blob = db.query(Blob).filter(
                Blob.id == custom_resource.get('id')
            ).first()
        else:
            blob = db.query(Blob).filter(
                Blob.id == custom_resource.get('id'),
                Blob.user_id == user_id,
                Blob.vmcp_id == vmcp_id
            ).first()

        if not blob:
            raise ValueError(f"Resource blob '{custom_resource.get('id')}' not found in database")

        # Handle content based on content type
        content_type = custom_resource.get('content_type') or blob.content_type

        # For text files, decode the binary data to string
        if content_type and content_type.startswith('text/'):
            try:
                if isinstance(blob.content, bytes):
                    resource_content = blob.content.decode('utf-8')
                else:
                    resource_content = str(blob.content)
            except UnicodeDecodeError:
                # If UTF-8 decoding fails, fall back to base64 encoding
                import base64
                if isinstance(blob.content, bytes):
                    resource_content = base64.b64encode(blob.content).decode('ascii')
                else:
                    resource_content = str(blob.content)
        else:
            # For binary files, return as-is or base64 encode if needed
            resource_content = blob.content

        contents = []
        match resource_content:
            case str() as resource_content:
                contents = [TextResourceContents(
                    uri=resource_id,
                    text=resource_content,
                    mimeType=content_type or "text/plain",
                )]
            case bytes() as resource_content:
                contents = [BlobResourceContents(
                    uri=resource_id,
                    blob=resource_content,
                    mimeType=content_type or "application/octet-stream",
                )]

        return ReadResourceResult(contents=contents)

    except Exception as e:
        logger.error(f"❌ Error fetching custom resource '{resource_id}': {e}")
        raise
    finally:
        db.close()
