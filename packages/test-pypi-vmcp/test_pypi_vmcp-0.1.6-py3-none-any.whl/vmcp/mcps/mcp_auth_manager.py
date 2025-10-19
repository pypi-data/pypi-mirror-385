"""
MCP Client Implementation
Handles connections and communication with MCP servers
"""

# Standard library imports
import os
import httpx
import secrets
import hashlib
import base64
import urllib.parse
from typing import Dict, List, Optional, Any, AsyncIterator, Union
from datetime import datetime, timedelta, timezone
from vmcp.utilities.logging.config import setup_logging
# Local imports
from vmcp.mcps.models import MCPAuthConfig
from urllib.parse import urlparse, urlunparse
from vmcp.storage.base import StorageBase
from vmcp.config import settings


logger = setup_logging("1xN_MCP_AUTH_MANAGER")

class MCPAuthManager:
    """Handles OAuth and other authentication flows for MCP servers"""
    
    def __init__(self):
        pass  # No longer need pending_auths since we use OAuth state manager
    
    async def get_access_token(self, auth_config: MCPAuthConfig) -> Optional[str]:
        """Get or refresh access token"""
        if not auth_config:
            return None
        
        # Check if current token is still valid
        if (auth_config.access_token and auth_config.expires_at and 
            datetime.now() < auth_config.expires_at - timedelta(minutes=5)):
            return auth_config.access_token
        
        # Try to refresh token if we have a refresh token
        if auth_config.refresh_token and auth_config.token_url:
            return await self._refresh_token(auth_config)
        
        # Otherwise, need new authorization flow
        return None
    
    async def _refresh_token(self, auth_config: MCPAuthConfig) -> Optional[str]:
        """Refresh OAuth access token"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    auth_config.token_url,
                    data={
                        'grant_type': 'refresh_token',
                        'refresh_token': auth_config.refresh_token,
                        'client_id': auth_config.client_id,
                        'client_secret': auth_config.client_secret,
                    }
                )
                
                if response.status_code == 200:
                    token_data = response.json()
                    auth_config.access_token = token_data['access_token']
                    auth_config.expires_at = datetime.now() + timedelta(
                        seconds=token_data.get('expires_in', 3600)
                    )
                    if 'refresh_token' in token_data:
                        auth_config.refresh_token = token_data['refresh_token']
                    
                    return auth_config.access_token
                    
        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            return None
    
    def generate_pkce_pair(self) -> tuple[str, str]:
        """Generate PKCE code verifier and challenge"""
        # Generate code verifier (43-128 characters, URL-safe)
        code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
        
        # Generate code challenge (SHA256 hash of verifier, base64url encoded)
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode('utf-8')).digest()
        ).decode('utf-8').rstrip('=')
        
        return code_verifier, code_challenge
    
    async def initiate_oauth_flow(self, server_name: str, server_url: str, user_id: str,
                                callback_url: str = None, headers: Optional[Dict[str, str]] = None, **kwargs) -> Dict[str, str]:
        """Initiate OAuth authorization flow with PKCE"""
        logger.info(f"initiate_oauth_flow kwargs: {kwargs}")
        
        # Set default callback URL if not provided
        if callback_url is None:
            from vmcp.config import settings
            callback_url = f"{settings.base_url}/api/otherservers/oauth/callback"
        
        try:
            client_id = '1xn-cli'  # Default client ID
            client_secret = None
            if server_url.startswith("https://api.githubcopilot.com/mcp") and (not headers):
                provider = "github"
                config = settings.OAUTH_CONFIG[provider]
                client_id = config['client_id']
                client_secret = config['client_secret']
                auth_url = config['auth_url']
                token_url = config['token_url']
                registration_endpoint = None

                # # Store OAuth state using storage class
                # state = secrets.token_urlsafe(32)
                # web_client_url = None
                # provider = "github"
                # client_id = "1xn"
                # oauth_flow = True
                # original_state = None
                # storage = StorageBase(user_id=None)  # Global mode for OAuth state
                # state_data = {
                #     "third_party_oauth_state": state,
                #     "web_client_url": web_client_url,
                #     "provider": provider,
                #     "client_id": client_id,
                #     "oauth_flow": oauth_flow,  # Store whether this is OAuth flow or normal sign-in
                #     "original_state": original_state,  # Store the original state from client
                #     "created_at": datetime.now(timezone.utc).isoformat(),
                #     "expires_at": (datetime.now(timezone.utc) + timedelta(minutes=30)).isoformat()
                # }
                # storage.save_third_party_oauth_state(state_data)
                
                # logger.info(f"Stored OAuth state: {state}, web_client_url: {web_client_url}, provider: {provider}, oauth_flow: {oauth_flow}, original_state: {original_state}")
                
                # # Build authorization URL
                
                # params = {
                #     "client_id": config["client_id"],
                #     "redirect_uri": f"{settings.UNIFIED_BACKEND_URL}/oauth/{provider}/callback",
                #     "response_type": "code",
                #     "scope": " ".join(config["scopes"]),
                #     "state": state  # Use the state (either original or generated)
                # }
                
                # auth_url = f"{config['auth_url']}?{urllib.parse.urlencode(params)}"

                # return {
                #     'authorization_url': auth_url,
                #     'state': state,
                #     'status': 'pending'
                # }

            else:
                # First, discover OAuth endpoints
                discovery_response = await self._discover_oauth_endpoints(server_url, callback_url)
                if not discovery_response:
                    raise Exception("Could not discover OAuth endpoints")
                
                auth_url = discovery_response.get('authorization_endpoint')
                token_url = discovery_response.get('token_endpoint')
                registration_endpoint = discovery_response.get('registration_endpoint')
            
            if not auth_url or not token_url:
                raise Exception("Missing required OAuth endpoints")
            
            # If there's a registration endpoint, register the client first
            
            if registration_endpoint:
                logger.info(f"Registering client with {server_name} at {registration_endpoint}")
                client_id = await self._register_oauth_client(registration_endpoint, callback_url)
                if not client_id:
                    raise Exception("Failed to register OAuth client")
                logger.info(f"Successfully registered client with ID: {client_id}")
            
            # Generate PKCE parameters
            code_verifier, code_challenge = self.generate_pkce_pair()
            state = secrets.token_urlsafe(32)
            
            # Store PKCE parameters in OAuth state manager
            oauth_config = {
                'server_name': server_name,
                'state': state,
                'code_challenge': code_challenge,
                'user_id': user_id,
                'code_verifier': code_verifier,
                'token_url': token_url,
                'callback_url': callback_url,
                'client_id': client_id,
                'client_secret': client_secret
            }
            if 'conversation_id' in kwargs:
                oauth_config['conversation_id'] = kwargs['conversation_id']
            if 'chat_client_callback_url' in kwargs:
                oauth_config['chat_client_callback_url'] = kwargs['chat_client_callback_url']
            
            # Store in OAuth state manager
            try:
                from vmcp.mcps.oauth_state_manager import OAuthStateManager
                oauth_state_manager = OAuthStateManager()
                oauth_state_manager.create_oauth_state(
                    server_name=server_name,
                    mcp_state=state,
                    user_id=user_id,
                    oauth_config=oauth_config
                )
                logger.info(f"✅ Stored OAuth configuration in state manager for user {user_id}")
            except Exception as e:
                logger.error(f"❌ Failed to store OAuth configuration in state manager: {e}")
                return {'error': f'Failed to store OAuth configuration: {e}', 'status': 'error'}
            
            # Build authorization URL
            auth_params = {
                'response_type': 'code',
                'client_id': client_id,
                'redirect_uri': callback_url,
                'state': state,
                'code_challenge': code_challenge,
                'code_challenge_method': 'S256'
            }
            
            full_auth_url = f"{auth_url}?{urllib.parse.urlencode(auth_params)}"
            
            # Debug: Log the authorization parameters
            logger.info(f"🔍 Authorization URL parameters:")
            logger.info(f"   Code Challenge: {code_challenge[:10]}...")
            logger.info(f"   Code Verifier: {code_verifier[:10]}...")
            logger.info(f"   State: {state[:10]}...")
            logger.info(f"   Client ID: {client_id}")
            logger.info(f"   Redirect URI: {callback_url}")
            
            return {
                'authorization_url': full_auth_url,
                'state': state,
                'status': 'pending'
            }
            
        except Exception as e:
            logger.error(f"OAuth flow initiation failed: {e}")
            return {'error': str(e), 'status': 'error'}
        



    @staticmethod
    def get_base_url(url):
            parsed = urlparse(url)
            # Only remove the last path component if there is a meaningful path
            if parsed.path and parsed.path != '/':
                path_parts = parsed.path.rstrip('/').split('/')
                if len(path_parts) > 1:
                    new_path = '/'.join(path_parts[:-1])
                else:
                    new_path = ''
            else:
                new_path = ''
            
            return urlunparse((parsed.scheme, parsed.netloc, new_path, '', '', ''))



    async def _discover_oauth_endpoints(self, server_url: str, callback_url: str = None) -> Optional[Dict[str, str]]:
        """Discover OAuth endpoints from server using MCP SDK approach"""
        try:
            # Import MCP SDK's discovery logic
            from mcp.client.auth import OAuthClientProvider
            from mcp.shared.auth import OAuthClientMetadata
            
            # Set default callback URL if not provided
            if callback_url is None:
                from vmcp.config import settings
                callback_url = f"{settings.base_url}/api/otherservers/oauth/callback"
            
            # Create a temporary OAuth provider just for discovery
            temp_metadata = OAuthClientMetadata(
                client_name="1xn-discovery",
                redirect_uris=[callback_url],
                grant_types=["authorization_code"],
                response_types=["code"],
                token_endpoint_auth_method="none"
            )
            
            # Create a minimal storage that returns None (no cached data)
            class DiscoveryStorage:
                async def get_tokens(self): return None
                async def set_tokens(self, tokens): pass
                async def get_client_info(self): return None
                async def set_client_info(self, client_info): pass
            
            # Create OAuth provider to leverage MCP SDK's discovery
            oauth_provider = OAuthClientProvider(
                server_url=server_url,
                client_metadata=temp_metadata,
                storage=DiscoveryStorage(),
                redirect_handler=lambda url: None,  # Not used for discovery
                callback_handler=lambda: (None, None)  # Not used for discovery
            )
            
            # Use the MCP SDK's exact discovery mechanism
            async with httpx.AsyncClient() as client:
                # Step 1: Get initial response to trigger discovery
                response = await client.get(server_url)
                
                if response.status_code == 401:
                    # Step 2: Use MCP SDK's protected resource discovery
                    discovery_request = await oauth_provider._discover_protected_resource(response)
                    discovery_response = await client.send(discovery_request)
                    
                    if discovery_response.status_code == 200:
                        protected_resource_data = discovery_response.json()
                        logger.info(f"✅ Found protected resource metadata")
                        
                        # Check if this contains authorization_servers (RFC 9728 flow)
                        if 'authorization_servers' in protected_resource_data:
                            auth_servers = protected_resource_data.get('authorization_servers', [])
                            if auth_servers:
                                auth_server_url = auth_servers[0]
                                
                                # Step 3: Use MCP SDK's OAuth metadata discovery
                                oauth_provider.context.auth_server_url = auth_server_url
                                discovery_urls = oauth_provider._get_discovery_urls()
                                
                                for url in discovery_urls:
                                    oauth_metadata_request = oauth_provider._create_oauth_metadata_request(url)
                                    oauth_metadata_response = await client.send(oauth_metadata_request)
                                    
                                    if oauth_metadata_response.status_code == 200:
                                        oauth_metadata = oauth_metadata_response.json()
                                        logger.info(f"✅ Found OAuth metadata at: {url}")
                                        return oauth_metadata
                        
                        # If it's direct OAuth metadata, return it
                        elif 'authorization_endpoint' in protected_resource_data:
                            return protected_resource_data
                
                # Fallback: try standard discovery URLs
                oauth_provider.context.auth_server_url = server_url
                discovery_urls = oauth_provider._get_discovery_urls()
                
                for url in discovery_urls:
                    oauth_metadata_request = oauth_provider._create_oauth_metadata_request(url)
                    oauth_metadata_response = await client.send(oauth_metadata_request)
                    
                    if oauth_metadata_response.status_code == 200:
                        oauth_metadata = oauth_metadata_response.json()
                        logger.info(f"✅ Found OAuth metadata at: {url}")
                        return oauth_metadata
                
        except Exception as e:
            logger.error(f"OAuth discovery failed: {e}")
        
        return None
    
    async def _register_oauth_client(self, registration_endpoint: str, callback_url: str) -> Optional[str]:
        """Register OAuth client with the server"""
        try:
            async with httpx.AsyncClient() as client:
                registration_data = {
                    'client_name': '1xn-cli',
                    'redirect_uris': [callback_url],
                    'grant_types': ['authorization_code'],
                    'response_types': ['code'],
                    'token_endpoint_auth_method': 'none'
                }
                
                response = await client.post(
                    registration_endpoint,
                    json=registration_data,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200 or response.status_code == 201:
                    registration_result = response.json()
                    logger.info(f"🔍 Registration result: {registration_result}")
                    client_id = registration_result.get('client_id')
                    
                    if client_id:
                        logger.info(f"Client registered successfully with ID: {client_id}")
                        return client_id
                    else:
                        logger.error("Registration successful but no client_id returned")
                        return None
                else:
                    logger.error(f"Client registration failed: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Client registration error: {e}")
            return None
    
    async def handle_oauth_callback(self, code: str, state: str, oauth_config: Dict[str, Any]) -> Dict[str, Any]:
        """Handle OAuth callback and exchange code for tokens"""
        # Use OAuth config from state manager
        if not oauth_config:
            return {'error': 'Missing OAuth configuration', 'status': 'error'}
        
        auth_data = oauth_config
        logger.info(f"🔍 Using OAuth config from state manager")
        
        try:
            # Debug: Log what we're sending to the token endpoint
            logger.info(f"🔍 Token exchange request:")
            logger.info(f"   URL: {auth_data['token_url']}")
            logger.info(f"   Code: '{code}'")
            logger.info(f"   Code length: {len(code)}")
            logger.info(f"   Redirect URI: '{auth_data['callback_url']}'")
            logger.info(f"   Client ID: '{auth_data.get('client_id', '1xn-cli')}'")
            logger.info(f"   Code Verifier: '{auth_data['code_verifier']}'")
            logger.info(f"   Code Verifier length: {len(auth_data['code_verifier'])}")
            logger.info(f"   Grant Type: authorization_code")
            
            # Show the exact data being sent
            token_data = {
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': auth_data['callback_url'],
                'client_id': auth_data.get('client_id', '1xn-cli'),
                'code_verifier': auth_data['code_verifier']
            }
            logger.info(f"🔍 Exact token exchange data:")
            for key, value in token_data.items():
                logger.info(f"   {key}: '{value}'")
            
            post_request_data={
                        'grant_type': 'authorization_code',
                        'code': code,
                        'redirect_uri': auth_data['callback_url'],
                        'client_id': auth_data.get('client_id', '1xn-cli'),
                        'code_verifier': auth_data['code_verifier']
                    }
            if auth_data.get('client_secret'):
                post_request_data['client_secret'] = auth_data.get('client_secret')
            # Exchange authorization code for access token
            async with httpx.AsyncClient() as client:
                token_response = await client.post(
                    auth_data['token_url'],
                    headers= {
                        'Accept': 'application/json'
                    },
                    data=post_request_data
                )
                
                if token_response.status_code == 200:
                    token_data = token_response.json()
                    logger.info(f"🔍 Token response: {token_data}")
                    return token_data
                else:
                    return {
                        'error': f"Token exchange failed: {token_response.text}",
                        'status': 'error'
                    }
                    
        except Exception as e:
            logger.error(f"OAuth callback handling failed: {e}")
            return {'error': str(e), 'status': 'error'}

