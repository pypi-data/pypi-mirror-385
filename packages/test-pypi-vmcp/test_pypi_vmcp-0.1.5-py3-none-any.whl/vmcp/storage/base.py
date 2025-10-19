"""
Storage base class for vMCP OSS version.

Provides a unified interface for database operations with VMCP and MCP server configurations.
This is a simplified version for OSS - single user, no complex authentication.
"""

import logging
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from vmcp.storage.database import SessionLocal
from vmcp.storage.models import (
    User,
    MCPServer,
    VMCP,
    VMCPMCPMapping,
    VMCPEnvironment,
    VMCPStats,
    ThirdPartyOAuthState,
    OAuthStateMapping,
    ApplicationLog,
)
from vmcp.vmcps.models import VMCPConfig

logger = logging.getLogger(__name__)


class StorageBase:
    """
    Storage abstraction layer for vMCP OSS.

    Provides CRUD operations for vMCPs, MCP servers, and related data.
    Always uses user_id=1 (the dummy user) in OSS version.
    """

    def __init__(self, user_id: int = 1):
        """
        Initialize storage handler.

        Args:
            user_id: User ID (always 1 in OSS version)
        """
        self.user_id = user_id
        logger.debug(f"StorageBase initialized for user {user_id}")

    def _get_session(self) -> Session:
        """Get a new database session."""
        return SessionLocal()

    # ========================== MCP SERVER METHODS ==========================

    def get_mcp_servers(self) -> Dict[str, Any]:
        """Get all MCP servers for the user."""
        session = self._get_session()
        try:
            servers = session.query(MCPServer).filter(
                MCPServer.user_id == self.user_id
            ).all()

            servers_dict = {}
            for server in servers:
                servers_dict[server.server_id] = server.mcp_server_config

            logger.debug(f"Found {len(servers_dict)} MCP servers for user {self.user_id}")
            return servers_dict

        except Exception as e:
            logger.error(f"Error getting MCP servers: {e}")
            return {}
        finally:
            session.close()

    def get_mcp_server_ids(self) -> List[str]:
        """Get list of MCP server IDs for the user."""
        session = self._get_session()
        try:
            servers = session.query(MCPServer.server_id).filter(
                MCPServer.user_id == self.user_id
            ).all()

            server_ids = [server.server_id for server in servers]
            logger.debug(f"Found {len(server_ids)} MCP server IDs")
            return server_ids

        except Exception as e:
            logger.error(f"Error getting MCP server IDs: {e}")
            return []
        finally:
            session.close()

    def get_mcp_server(self, server_id: str) -> Dict[str, Any]:
        """Get MCP server configuration by ID."""
        session = self._get_session()
        try:
            server = session.query(MCPServer).filter(
                MCPServer.user_id == self.user_id,
                MCPServer.server_id == server_id
            ).first()

            if not server:
                logger.warning(f"MCP server not found: {server_id}")
                return {}

            return {
                "server_id": server.server_id,
                "name": server.name,
                "description": server.description,
                "mcp_server_config": server.mcp_server_config,
                "oauth_state": server.oauth_state,
            }

        except Exception as e:
            logger.error(f"Error getting MCP server {server_id}: {e}")
            return {}
        finally:
            session.close()

    def save_mcp_server(self, server_id: str, server_config: Dict[str, Any]) -> bool:
        """Save or update MCP server configuration."""
        session = self._get_session()
        try:
            # Check if server exists
            server = session.query(MCPServer).filter(
                MCPServer.user_id == self.user_id,
                MCPServer.server_id == server_id
            ).first()

            if server:
                # Update existing server
                server.name = server_config.get("name", server.name)
                server.description = server_config.get("description")
                server.mcp_server_config = server_config
                logger.info(f"Updated MCP server: {server_id}")
            else:
                # Create new server
                server = MCPServer(
                    id=f"{self.user_id}_{server_id}",
                    user_id=self.user_id,
                    server_id=server_id,
                    name=server_config.get("name", server_id),
                    description=server_config.get("description"),
                    mcp_server_config=server_config,
                )
                session.add(server)
                logger.info(f"Created new MCP server: {server_id}")

            session.commit()
            return True

        except Exception as e:
            logger.error(f"Error saving MCP server {server_id}: {e}")
            session.rollback()
            return False
        finally:
            session.close()

    def save_mcp_servers(self, servers: List[Dict[str, Any]]) -> bool:
        """Save multiple MCP servers to database."""
        try:
            logger.info(f"Saving {len(servers)} MCP servers")
            
            success = True
            for server in servers:
                server_id = server.get("server_id")
                if server_id:
                    # Use the existing save_mcp_server method for each server
                    if not self.save_mcp_server(server_id, server):
                        success = False
                        logger.error(f"Failed to save MCP server: {server_id}")
                else:
                    logger.error("No server_id found in server config")
                    success = False
            
            if success:
                logger.info(f"Successfully saved {len(servers)} MCP servers")
            else:
                logger.error("Some MCP servers failed to save")
            
            return success
            
        except Exception as e:
            logger.error(f"Error saving MCP servers: {e}")
            return False

    def delete_mcp_server(self, server_id: str) -> bool:
        """Delete MCP server by ID."""
        session = self._get_session()
        try:
            server = session.query(MCPServer).filter(
                MCPServer.user_id == self.user_id,
                MCPServer.server_id == server_id
            ).first()

            if server:
                session.delete(server)
                session.commit()
                logger.info(f"Deleted MCP server: {server_id}")
                return True
            else:
                logger.warning(f"MCP server not found for deletion: {server_id}")
                return False

        except Exception as e:
            logger.error(f"Error deleting MCP server {server_id}: {e}")
            session.rollback()
            return False
        finally:
            session.close()

    # ========================== VMCP METHODS ==========================

    def save_vmcp(self, vmcp_id: str, vmcp_config: Dict[str, Any]) -> bool:
        """Save or update vMCP configuration."""
        session = self._get_session()
        try:
            # Check if vMCP exists
            vmcp = session.query(VMCP).filter(
                VMCP.user_id == self.user_id,
                VMCP.vmcp_id == vmcp_id
            ).first()

            if vmcp:
                # Update existing vMCP
                vmcp.name = vmcp_config.get("name", vmcp.name)
                vmcp.description = vmcp_config.get("description")
                vmcp.vmcp_config = vmcp_config
                logger.info(f"Updated vMCP: {vmcp_id}")
            else:
                # Create new vMCP
                vmcp = VMCP(
                    id=f"{self.user_id}_{vmcp_id}",
                    user_id=self.user_id,
                    vmcp_id=vmcp_id,
                    name=vmcp_config.get("name", vmcp_id),
                    description=vmcp_config.get("description"),
                    vmcp_config=vmcp_config,
                )
                session.add(vmcp)
                logger.info(f"Created new vMCP: {vmcp_id}")

            session.commit()
            return True

        except Exception as e:
            logger.error(f"Error saving vMCP {vmcp_id}: {e}")
            session.rollback()
            return False
        finally:
            session.close()

    def load_vmcp_config(self, vmcp_id: str) -> Optional[VMCPConfig]:
        """Load vMCP configuration by ID."""
        session = self._get_session()
        try:
            vmcp = session.query(VMCP).filter(
                VMCP.user_id == self.user_id,
                VMCP.vmcp_id == vmcp_id
            ).first()

            if not vmcp:
                logger.warning(f"vMCP not found: {vmcp_id}")
                return None

            # Load environment variables from VMCPEnvironment table
            env = session.query(VMCPEnvironment).filter(
                VMCPEnvironment.user_id == self.user_id,
                VMCPEnvironment.vmcp_id == vmcp.id
            ).first()

            # The vmcp_config field contains the entire VMCPConfig data
            vmcp_dict = vmcp.vmcp_config.copy()

            # Convert environment vars from dict format (VMCPEnvironment) to list format (API)
            if env and env.environment_vars:
                env_list = [{"name": k, "value": v} for k, v in env.environment_vars.items()]
                vmcp_dict["environment_variables"] = env_list

            # Convert dict to VMCPConfig object
            config = VMCPConfig.from_dict(vmcp_dict)

            logger.debug(f"Loaded vMCP config: {vmcp_id}")
            return config

        except Exception as e:
            logger.error(f"Error loading vMCP {vmcp_id}: {e}")
            return None
        finally:
            session.close()

    def list_vmcps(self) -> List[Dict[str, Any]]:
        """List all vMCP configurations for the user."""
        session = self._get_session()
        try:
            vmcps = session.query(VMCP).filter(
                VMCP.user_id == self.user_id,
                VMCP.vmcp_id.isnot(None)  # Only include records with valid vmcp_id
            ).all()

            vmcp_list = []
            for vmcp in vmcps:
                # Skip if vmcp_id is None (safety check)
                if not vmcp.vmcp_id:
                    logger.warning(f"Skipping vMCP with None vmcp_id: {vmcp.id}")
                    continue

                config = vmcp.vmcp_config or {}
                vmcp_list.append({
                    "id": vmcp.vmcp_id,
                    "vmcp_id": vmcp.vmcp_id,
                    "name": vmcp.name or "Unnamed vMCP",
                    "description": vmcp.description,
                    "total_tools": config.get("total_tools", 0),
                    "total_resources": config.get("total_resources", 0),
                    "total_resource_templates": config.get("total_resource_templates", 0),
                    "total_prompts": config.get("total_prompts", 0),
                    "created_at": vmcp.created_at.isoformat() if vmcp.created_at else None,
                    "updated_at": vmcp.updated_at.isoformat() if vmcp.updated_at else None,
                })

            logger.debug(f"Found {len(vmcp_list)} vMCPs for user {self.user_id}")
            return vmcp_list

        except Exception as e:
            logger.error(f"Error listing vMCPs: {e}")
            return []
        finally:
            session.close()

    def delete_vmcp(self, vmcp_id: str) -> bool:
        """Delete vMCP by ID."""
        session = self._get_session()
        try:
            vmcp = session.query(VMCP).filter(
                VMCP.user_id == self.user_id,
                VMCP.vmcp_id == vmcp_id
            ).first()

            if vmcp:
                session.delete(vmcp)
                session.commit()
                logger.info(f"Deleted vMCP: {vmcp_id}")
                return True
            else:
                logger.warning(f"vMCP not found for deletion: {vmcp_id}")
                return False

        except Exception as e:
            logger.error(f"Error deleting vMCP {vmcp_id}: {e}")
            session.rollback()
            return False
        finally:
            session.close()

    def update_vmcp(self, vmcp_config: VMCPConfig) -> bool:
        """Update an existing VMCP configuration."""
        from datetime import datetime

        # Update the updated_at timestamp
        vmcp_config.updated_at = datetime.now()

        # Save the updated configuration using save_vmcp
        success = self.save_vmcp(vmcp_config.id, vmcp_config.to_dict())

        if success:
            logger.info(f"Successfully updated vMCP: {vmcp_config.id}")
        else:
            logger.error(f"Failed to update vMCP: {vmcp_config.id}")

        return success

    # ========================== VMCP ENVIRONMENT METHODS ==========================

    def save_vmcp_environment(self, vmcp_id: str, environment_vars: Dict[str, str]) -> bool:
        """Save environment variables for a vMCP."""
        session = self._get_session()
        try:
            # Get vMCP internal ID
            vmcp = session.query(VMCP).filter(
                VMCP.user_id == self.user_id,
                VMCP.vmcp_id == vmcp_id
            ).first()

            if not vmcp:
                logger.error(f"vMCP not found: {vmcp_id}")
                return False

            # Check if environment exists
            env = session.query(VMCPEnvironment).filter(
                VMCPEnvironment.user_id == self.user_id,
                VMCPEnvironment.vmcp_id == vmcp.id
            ).first()

            if env:
                # Update existing environment
                env.environment_vars = environment_vars
                logger.info(f"Updated environment for vMCP: {vmcp_id}")
            else:
                # Create new environment
                env = VMCPEnvironment(
                    id=f"{self.user_id}_{vmcp_id}_env",
                    user_id=self.user_id,
                    vmcp_id=vmcp.id,
                    environment_vars=environment_vars,
                )
                session.add(env)
                logger.info(f"Created environment for vMCP: {vmcp_id}")

            session.commit()
            return True

        except Exception as e:
            logger.error(f"Error saving vMCP environment {vmcp_id}: {e}")
            session.rollback()
            return False
        finally:
            session.close()

    def load_vmcp_environment(self, vmcp_id: str) -> Dict[str, str]:
        """Load environment variables for a vMCP."""
        session = self._get_session()
        try:
            # Get vMCP internal ID
            vmcp = session.query(VMCP).filter(
                VMCP.user_id == self.user_id,
                VMCP.vmcp_id == vmcp_id
            ).first()

            if not vmcp:
                logger.warning(f"vMCP not found: {vmcp_id}")
                return {}

            env = session.query(VMCPEnvironment).filter(
                VMCPEnvironment.user_id == self.user_id,
                VMCPEnvironment.vmcp_id == vmcp.id
            ).first()

            if not env:
                logger.debug(f"No environment found for vMCP: {vmcp_id}")
                return {}

            return env.environment_vars or {}

        except Exception as e:
            logger.error(f"Error loading vMCP environment {vmcp_id}: {e}")
            return {}
        finally:
            session.close()

    # ========================== OAUTH STATE METHODS ==========================

    def save_third_party_oauth_state(self, state: str, state_data: Dict[str, Any]) -> bool:
        """Save third-party OAuth state."""
        session = self._get_session()
        try:
            from datetime import datetime, timezone, timedelta

            # Check if state exists
            oauth_state = session.query(ThirdPartyOAuthState).filter(
                ThirdPartyOAuthState.state == state
            ).first()

            expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

            if oauth_state:
                # Update existing state
                oauth_state.state_data = state_data
                oauth_state.expires_at = expires_at
                logger.info(f"Updated OAuth state: {state[:8]}...")
            else:
                # Create new state
                oauth_state = ThirdPartyOAuthState(
                    state=state,
                    state_data=state_data,
                    expires_at=expires_at,
                )
                session.add(oauth_state)
                logger.info(f"Created OAuth state: {state[:8]}...")

            session.commit()
            return True

        except Exception as e:
            logger.error(f"Error saving OAuth state: {e}")
            session.rollback()
            return False
        finally:
            session.close()

    def get_third_party_oauth_state(self, state: str) -> Optional[Dict[str, Any]]:
        """Get third-party OAuth state."""
        session = self._get_session()
        try:
            from datetime import datetime, timezone

            oauth_state = session.query(ThirdPartyOAuthState).filter(
                ThirdPartyOAuthState.state == state
            ).first()

            if not oauth_state:
                logger.warning(f"OAuth state not found: {state[:8]}...")
                return None

            # Check if expired
            if oauth_state.expires_at < datetime.now(timezone.utc):
                logger.warning(f"OAuth state expired: {state[:8]}...")
                session.delete(oauth_state)
                session.commit()
                return None

            return oauth_state.state_data

        except Exception as e:
            logger.error(f"Error getting OAuth state: {e}")
            return None
        finally:
            session.close()

    def delete_third_party_oauth_state(self, state: str) -> bool:
        """Delete third-party OAuth state."""
        session = self._get_session()
        try:
            oauth_state = session.query(ThirdPartyOAuthState).filter(
                ThirdPartyOAuthState.state == state
            ).first()

            if oauth_state:
                session.delete(oauth_state)
                session.commit()
                logger.info(f"Deleted OAuth state: {state[:8]}...")
                return True
            else:
                logger.warning(f"OAuth state not found for deletion: {state[:8]}...")
                return False

        except Exception as e:
            logger.error(f"Error deleting OAuth state: {e}")
            session.rollback()
            return False
        finally:
            session.close()

    def save_oauth_state(self, state_data: Dict[str, Any]) -> bool:
        """Save OAuth state for MCP servers (using OAuthStateMapping table)"""
        session = self._get_session()
        try:
            # Use mcp_state as the key
            mcp_state = state_data.get("mcp_state")
            if not mcp_state:
                logger.error("No mcp_state found in state_data")
                return False
            
            # Check if state already exists
            existing_state = session.query(OAuthStateMapping).filter(
                OAuthStateMapping.mcp_state == mcp_state
            ).first()
            
            if existing_state:
                # Update existing state
                existing_state.user_id = state_data.get("user_id")
                existing_state.server_name = state_data.get("server_name")
                existing_state.state = state_data.get("state")
                existing_state.code_challenge = state_data.get("code_challenge")
                existing_state.code_verifier = state_data.get("code_verifier")
                existing_state.token_url = state_data.get("token_url")
                existing_state.callback_url = state_data.get("callback_url")
                existing_state.client_id = state_data.get("client_id")
                existing_state.client_secret = state_data.get("client_secret")
                existing_state.expires_at = datetime.fromtimestamp(
                    state_data.get("expires_at", time.time() + 3600)
                )
            else:
                # Create new state
                new_state = OAuthStateMapping(
                    mcp_state=mcp_state,
                    user_id=state_data.get("user_id"),
                    server_name=state_data.get("server_name"),
                    state=state_data.get("state"),
                    code_challenge=state_data.get("code_challenge"),
                    code_verifier=state_data.get("code_verifier"),
                    token_url=state_data.get("token_url"),
                    callback_url=state_data.get("callback_url"),
                    client_id=state_data.get("client_id"),
                    client_secret=state_data.get("client_secret"),
                    expires_at=datetime.fromtimestamp(
                        state_data.get("expires_at", time.time() + 3600)
                    )
                )
                session.add(new_state)
            
            session.commit()
            logger.info(f"Saved OAuth state: {mcp_state[:8]}...")
            return True
        except Exception as e:
            logger.error(f"Error saving OAuth state: {e}")
            session.rollback()
            return False
        finally:
            session.close()

    def get_oauth_state(self, state: str) -> Optional[Dict[str, Any]]:
        """Get OAuth state for MCP servers"""
        session = self._get_session()
        try:
            oauth_state = session.query(OAuthStateMapping).filter(
                OAuthStateMapping.mcp_state == state
            ).first()
            
            if oauth_state:
                return oauth_state.to_dict()
            return None
        except Exception as e:
            logger.error(f"Error getting OAuth state: {e}")
            return None
        finally:
            session.close()

    def delete_oauth_state(self, state: str) -> bool:
        """Delete OAuth state for MCP servers"""
        session = self._get_session()
        try:
            oauth_state = session.query(OAuthStateMapping).filter(
                OAuthStateMapping.mcp_state == state
            ).first()

            if oauth_state:
                session.delete(oauth_state)
                session.commit()
                logger.info(f"Deleted OAuth state: {state[:8]}...")
                return True
            else:
                logger.warning(f"OAuth state not found for deletion: {state[:8]}...")
                return False
        except Exception as e:
            logger.error(f"Error deleting OAuth state: {e}")
            session.rollback()
            return False
        finally:
            session.close()

    def get_oauth_states(self) -> List[Dict[str, Any]]:
        """Get all OAuth states (for cleanup)"""
        session = self._get_session()
        try:
            oauth_states = session.query(OAuthStateMapping).all()
            
            states = []
            for state in oauth_states:
                states.append(state.to_dict())
            return states
        except Exception as e:
            logger.error(f"Error getting OAuth states: {e}")
            return []
        finally:
            session.close()

    # ========================== STATS & LOGGING METHODS ==========================

    def save_vmcp_stats(self, vmcp_id: str, operation_type: str, operation_name: str,
                       success: bool, duration_ms: Optional[int] = None,
                       error_message: Optional[str] = None,
                       operation_metadata: Optional[Dict[str, Any]] = None,
                       mcp_server_id: Optional[str] = None) -> bool:
        """Save vMCP operation statistics."""
        session = self._get_session()
        try:
            # Get vMCP internal ID
            vmcp = session.query(VMCP).filter(
                VMCP.user_id == self.user_id,
                VMCP.vmcp_id == vmcp_id
            ).first()

            if not vmcp:
                logger.error(f"vMCP not found for stats: {vmcp_id}")
                return False

            stats = VMCPStats(
                vmcp_id=vmcp.id,
                operation_type=operation_type,
                operation_name=operation_name,
                mcp_server_id=mcp_server_id,
                success=success,
                error_message=error_message,
                duration_ms=duration_ms,
                operation_metadata=operation_metadata,
            )
            session.add(stats)
            session.commit()

            logger.debug(f"Saved stats for vMCP {vmcp_id}: {operation_type}:{operation_name}")
            return True

        except Exception as e:
            logger.error(f"Error saving vMCP stats: {e}")
            session.rollback()
            return False
        finally:
            session.close()

    def save_application_log(self, level: str, logger_name: str, message: str,
                            vmcp_id: Optional[str] = None,
                            mcp_server_id: Optional[str] = None,
                            log_metadata: Optional[Dict[str, Any]] = None,
                            traceback: Optional[str] = None) -> bool:
        """Save application log entry."""
        session = self._get_session()
        try:
            log = ApplicationLog(
                level=level,
                logger_name=logger_name,
                message=message,
                vmcp_id=vmcp_id,
                mcp_server_id=mcp_server_id,
                log_metadata=log_metadata,
                traceback=traceback,
            )
            session.add(log)
            session.commit()

            logger.debug(f"Saved application log: {level} - {logger_name}")
            return True

        except Exception as e:
            logger.error(f"Error saving application log: {e}")
            session.rollback()
            return False
        finally:
            session.close()

    # ========================== REGISTRY METHODS ==========================

    def save_public_vmcp(self, vmcp_config: 'VMCPConfig') -> bool:
        """Save a vMCP as public for sharing (OSS version - simplified)."""
        try:
            logger.info(f"Saving public vMCP: {vmcp_config.id}")
            
            # In OSS version, we treat all vMCPs as "public" since there's only one user
            # We simply save the vMCP using the existing save_vmcp method
            return self.save_vmcp(vmcp_config)
            
        except Exception as e:
            logger.error(f"Error saving public vMCP {vmcp_config.id}: {e}")
            return False

    def remove_public_vmcp(self, vmcp_id: str) -> bool:
        """Remove a vMCP from public list (OSS version - simplified)."""
        try:
            logger.info(f"Removing public vMCP: {vmcp_id}")
            
            # In OSS version, we simply delete the vMCP using the existing delete_vmcp method
            return self.delete_vmcp(vmcp_id)
            
        except Exception as e:
            logger.error(f"Error removing public vMCP {vmcp_id}: {e}")
            return False

    def list_public_vmcps(self) -> List[Dict[str, Any]]:
        """List all public vMCPs available for installation (OSS version - simplified)."""
        try:
            logger.info("Listing public vMCPs (OSS version - returns all vMCPs)")
            
            # In OSS version, all vMCPs are considered "public" since there's only one user
            # We simply return all vMCPs using the existing list_vmcps method
            vmcps = self.list_vmcps()
            
            # Convert to the expected format (list of vmcp_config dictionaries)
            public_vmcps = []
            for vmcp in vmcps:
                if 'vmcp_config' in vmcp:
                    public_vmcps.append(vmcp['vmcp_config'])
            
            logger.debug(f"Found {len(public_vmcps)} public vMCPs")
            return public_vmcps
            
        except Exception as e:
            logger.error(f"Error listing public vMCPs: {e}")
            return []

    def get_public_vmcp(self, vmcp_id: str) -> Optional[Dict[str, Any]]:
        """Get details of a specific public vMCP (OSS version - simplified)."""
        try:
            logger.info(f"Getting public vMCP: {vmcp_id}")
            
            # In OSS version, we simply get the vMCP using the existing get_vmcp method
            vmcp = self.get_vmcp(vmcp_id)
            
            if vmcp and 'vmcp_config' in vmcp:
                return vmcp['vmcp_config']
            
            logger.warning(f"Public vMCP not found: {vmcp_id}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting public vMCP {vmcp_id}: {e}")
            return None

    def update_private_vmcp_registry(self, private_vmcp_id: str, private_vmcp_registry_data: Dict[str, Any], operation: str) -> bool:
        """Update private vMCP registry (OSS version - simplified)."""
        try:
            logger.info(f"Private registry operation '{operation}' for vMCP {private_vmcp_id}")
            
            if operation == "add":
                # Extract vmcp_config from registry data
                vmcp_config = private_vmcp_registry_data.get('vmcp_config')
                if vmcp_config:
                    # Save using vmcp_id and config dict
                    return self.save_vmcp(private_vmcp_id, vmcp_config)
                return False

            elif operation == "delete":
                return self.delete_vmcp(private_vmcp_id)

            elif operation == "update":
                # Extract vmcp_config from registry data
                vmcp_config = private_vmcp_registry_data.get('vmcp_config')
                if vmcp_config:
                    # Save using vmcp_id and config dict
                    return self.save_vmcp(private_vmcp_id, vmcp_config)
                return False
                
            elif operation == "read":
                vmcp = self.get_vmcp(private_vmcp_id)
                return vmcp is not None
                
            else:
                logger.error(f"Invalid private registry operation: {operation}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating private vMCP registry: {e}")
            return False

    def update_public_vmcp_registry(self, public_vmcp_id: str, public_vmcp_registry_data: Dict[str, Any], operation: str) -> bool:
        """Update public vMCP registry (OSS version - simplified)."""
        try:
            logger.info(f"Public registry operation '{operation}' for vMCP {public_vmcp_id}")
            
            if operation == "add":
                # Extract vmcp_config from registry data
                vmcp_config = public_vmcp_registry_data.get('vmcp_config')
                if vmcp_config:
                    # Convert to VMCPConfig object and save
                    from vmcp.vmcps.models import VMCPConfig
                    vmcp_obj = VMCPConfig.from_dict(vmcp_config)
                    return self.save_public_vmcp(vmcp_obj)
                return False
                
            elif operation == "delete":
                return self.remove_public_vmcp(public_vmcp_id)
                
            elif operation == "update":
                # Extract vmcp_config from registry data
                vmcp_config = public_vmcp_registry_data.get('vmcp_config')
                if vmcp_config:
                    # Convert to VMCPConfig object and save
                    from vmcp.vmcps.models import VMCPConfig
                    vmcp_obj = VMCPConfig.from_dict(vmcp_config)
                    return self.save_public_vmcp(vmcp_obj)
                return False
                
            elif operation == "read":
                vmcp = self.get_public_vmcp(public_vmcp_id)
                return vmcp is not None
                
            else:
                logger.error(f"Invalid public registry operation: {operation}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating public vMCP registry: {e}")
            return False
    
    def get_agent_name(self, bearer_token: str) -> Optional[str]:
        """Get agent name from bearer token (OSS version - simplified)"""
        try:
            # In OSS version, we don't have multi-agent support
            # Return a default agent name or extract from token if needed
            if bearer_token:
                # For OSS, we can use a simple approach
                # You could implement token parsing here if needed
                return "oss-agent"
            return None
        except Exception as e:
            logger.error(f"Error getting agent name: {e}")
            return None
    
    def find_vmcp_name_in_private_registry(self, vmcp_name: str) -> Optional[str]:
        """Find vMCP ID by name in private registry (OSS version)"""
        try:
            # Query the database directly to get the actual vmcp_config
            session = self._get_session()
            vmcps = session.query(VMCP).filter(
                VMCP.user_id == self.user_id,
                VMCP.name == vmcp_name
            ).all()
            
            logger.info(f"🔍 Searching for vMCP with name '{vmcp_name}' in {len(vmcps)} vMCPs")
            
            for vmcp in vmcps:
                vmcp_config = vmcp.vmcp_config or {}
                actual_vmcp_id = vmcp_config.get('id')  # This is the UUID from the JSON
                table_vmcp_id = vmcp.vmcp_id  # This is the composite ID from the table
                
                logger.info(f"🔍 Checking vMCP: table_id={table_vmcp_id}, actual_id={actual_vmcp_id}, name={vmcp.name}")
                
                if vmcp.name == vmcp_name and actual_vmcp_id:
                    logger.info(f"✅ Found vMCP: {vmcp_name} -> {actual_vmcp_id}")
                    return actual_vmcp_id  # Return the UUID from vmcp_config, not the table ID
            
            logger.warning(f"❌ vMCP not found: {vmcp_name}")
            return None
        except Exception as e:
            logger.error(f"Error finding vMCP by name '{vmcp_name}': {e}")
            return None
    
    def save_user_vmcp_logs(self, log_entry: Dict[str, Any], log_suffix: str = "") -> bool:
        """Save vMCP operation logs (OSS version - using save_vmcp_stats method)"""
        try:
            # Extract log details from the log_entry
            # The log_entry comes from log_vmcp_operation with rich data
            vmcp_id = log_entry.get('vmcp_id')
            method = log_entry.get('method', 'unknown')
            operation_type = log_entry.get('mcp_method', method)  # Use mcp_method or fallback to method
            operation_name = log_entry.get('original_name') or method  # Use original_name or fallback to method (ensure not None)
            mcp_server_id = log_entry.get('mcp_server', 'vmcp')
            success = True  # Assume success unless we have error info
            error_message = None
            duration_ms = None
            
            # Create comprehensive operation metadata
            operation_metadata = {
                'agent_name': log_entry.get('agent_name', 'oss-agent'),
                'agent_id': log_entry.get('agent_id', 'unknown'),
                'client_id': log_entry.get('client_id', 'unknown'),
                'operation_id': log_entry.get('operation_id', 'N/A'),
                'arguments': log_entry.get('arguments', 'No arguments'),
                'result': log_entry.get('result', 'No result'),
                'vmcp_name': log_entry.get('vmcp_name', 'unknown'),
                'total_tools': log_entry.get('total_tools', 0),
                'total_resources': log_entry.get('total_resources', 0),
                'total_resource_templates': log_entry.get('total_resource_templates', 0),
                'total_prompts': log_entry.get('total_prompts', 0),
                'timestamp': log_entry.get('timestamp'),
                'user_id': log_entry.get('user_id', self.user_id)
            }
            
            # Validate required fields before saving
            if not vmcp_id:
                logger.error(f"Missing vmcp_id in log entry: {log_entry}")
                return False
            
            if not operation_name:
                logger.error(f"Missing operation_name in log entry: {log_entry}")
                return False
            
            # Use the existing save_vmcp_stats method
            return self.save_vmcp_stats(
                vmcp_id=vmcp_id,
                operation_type=operation_type,
                operation_name=operation_name,
                success=success,
                duration_ms=duration_ms,
                error_message=error_message,
                operation_metadata=operation_metadata,
                mcp_server_id=mcp_server_id
            )
                
        except Exception as e:
            logger.error(f"Error saving vMCP logs for user {self.user_id}: {e}")
            return False
