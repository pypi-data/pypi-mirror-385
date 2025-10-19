from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
from mcp.types import Tool, Resource, ResourceTemplate, Prompt
from vmcp.mcps.models import MCPRegistryConfig, MCPServerConfig
from copy import deepcopy
from enum import Enum

class VMCPInfo(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    config: Optional[Dict[str, Any]] = None

# vMCP creation request model
class VMCPCreateRequest(BaseModel):
    name: str = Field(..., description="vMCP name")
    description: Optional[str] = Field(None, description="vMCP description")
    system_prompt: Optional[Dict[str, Any]] = Field(None, description="System prompt object with text and variables")
    vmcp_config: Optional[Dict[str, Any]] = Field(None, description="vMCP configuration")
    custom_prompts: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Custom prompts")
    custom_tools: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Custom tools")
    custom_context: Optional[List[str]] = Field(default_factory=list, description="Custom context")
    custom_resources: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Custom resources")
    custom_resource_templates: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Custom resource templates")
    custom_resource_uris: Optional[List[str]] = Field(default_factory=list, description="Custom resource URIs")
    environment_variables: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Environment variables")
    uploaded_files: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Uploaded files")

# vMCP update request model
class VMCPUdateRequest(BaseModel):
    name: Optional[str] = Field(None, description="vMCP name")
    description: Optional[str] = Field(None, description="vMCP description")
    system_prompt: Optional[Dict[str, Any]] = Field(None, description="System prompt object with text and variables")
    vmcp_config: Optional[Dict[str, Any]] = Field(None, description="vMCP configuration")
    custom_prompts: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Custom prompts")
    custom_tools: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Custom tools")
    custom_context: Optional[List[str]] = Field(default_factory=list, description="Custom context")
    custom_resources: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Custom resources")
    custom_resource_templates: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Custom resource templates")
    custom_resource_uris: Optional[List[str]] = Field(default_factory=list, description="Custom resource URIs")
    environment_variables: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Environment variables")
    uploaded_files: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Uploaded files")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadata")

class VMCPToolCallRequest(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]

class VMCPResourceRequest(BaseModel):
    uri: str

class VMCPResourceTemplateRequest(BaseModel):
    template_name: str
    parameters: Optional[Dict[str, Any]] = None

class VMCPPromptRequest(BaseModel):
    prompt_id: str
    arguments: Optional[Dict[str, Any]] = None

class VMCPEnvironmentVariablesRequest(BaseModel):
    environment_variables: List[Dict[str, Any]] = Field(..., description="List of environment variables to save")


class VMCPShareState(Enum):
    PUBLIC = "public"
    SHARED = "shared"
    PRIVATE = "private"


class VMCPShareRequest(BaseModel):
    vmcp_id: str
    state: VMCPShareState
    tags: Optional[List[str]] = None
    
    class Config:
        extra = "forbid"  # Reject any extra fields

class VMCPInstallRequest(BaseModel):
    public_vmcp_id: str

@dataclass
class PublicVMCPInfo(BaseModel):
    # Additional public sharing fields
    creator_id: str
    creator_username: str
    install_count: int = 0
    rating: Optional[float] = None
    rating_count: int = 0

@dataclass
class VMCPRegistryConfig:
    """Agent configuration data structure"""
    id: str
    name: str
    user_id: str
    description: Optional[str] = None
    vmcp_config: Optional[Dict[str, List[MCPRegistryConfig]]] = field(default_factory=dict)  # Full vMCP configuration structure
    environment_variables: Optional[List[Dict[str, Any]]] = field(default_factory=list)  # List of environment variables
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    creator_id: Optional[str] = None
    creator_username: Optional[str] = None
    total_tools: Optional[int] = None
    total_resources: Optional[int] = None
    total_resource_templates: Optional[int] = None
    total_prompts: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    creator_id: Optional[str] = None
    creator_username: Optional[str] = None
    public_info: Optional[PublicVMCPInfo] = None
    # Sharing fields
    is_public: bool = False
    public_tags: List[str] = field(default_factory=list)
    public_at: Optional[str] = None
    is_wellknown: bool = False
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        
        # Handle datetime serialization
        if self.created_at:
            data['created_at'] = self.created_at.isoformat()
        if self.updated_at:
            data['updated_at'] = self.updated_at.isoformat()
        
        # Handle PublicVMCPInfo serialization
        if self.public_info:
            data['public_info'] = asdict(self.public_info)
        
        # Handle selected_servers in vmcp_config if they are MCPRegistryConfig objects
        if self.vmcp_config and 'selected_servers' in self.vmcp_config:
            selected_servers = self.vmcp_config['selected_servers']
            if isinstance(selected_servers, list):
                serialized_servers = []
                for server in selected_servers:
                    if hasattr(server, 'to_dict'):
                        serialized_servers.append(server.to_dict())
                    else:
                        serialized_servers.append(server)
                data['vmcp_config']['selected_servers'] = serialized_servers
        
        # Handle any remaining enum serialization in the data
        data = self._serialize_enums(data)
        
        return data
    
    def _serialize_enums(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively serialize enums in the data dictionary"""
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                if hasattr(value, 'value'):  # Check if it's an enum
                    result[key] = value.value
                elif isinstance(value, dict):
                    result[key] = self._serialize_enums(value)
                elif isinstance(value, list):
                    result[key] = [self._serialize_enums(item) if isinstance(item, dict) else (item.value if hasattr(item, 'value') else item) for item in value]
                else:
                    result[key] = value
            return result
        elif isinstance(data, list):
            return [self._serialize_enums(item) if isinstance(item, dict) else (item.value if hasattr(item, 'value') else item) for item in data]
        else:
            return data.value if hasattr(data, 'value') else data

@dataclass
class VMCPConfig:
    """vMCP configuration data structure"""
    id: str
    name: str
    user_id: str
    description: Optional[str] = None
    system_prompt: Optional[Dict[str, Any]] = None  # System prompt object with text and variables
    vmcp_config: Optional[Dict[str, Any]] = field(default_factory=dict)  # Full vMCP configuration structure
    custom_prompts: List[Dict[str, Any]] = field(default_factory=list)  # List of prompt objects with variables
    custom_tools: List[Dict[str, Any]] = field(default_factory=list)  # List of custom tool objects
    custom_context: List[str] = field(default_factory=list)  # List of context strings
    custom_resources: List[Dict[str, Any]] = field(default_factory=list)  # List of custom resource objects
    custom_resource_templates: List[Dict[str, Any]] = field(default_factory=list) # List of custom resource template objects
    custom_widgets: List[Dict[str, Any]] = field(default_factory=list)  # List of custom widgets (OpenAI Apps SDK)
    environment_variables: List[Dict[str, Any]] = field(default_factory=list)  # List of environment variables
    uploaded_files: List[Dict[str, Any]] = field(default_factory=list)  # List of uploaded files with metadata
    custom_resource_uris: List[str] = field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    creator_id: Optional[str] = None
    creator_username: Optional[str] = None
    total_tools: Optional[int] = None
    total_resources: Optional[int] = None
    total_resource_templates: Optional[int] = None
    total_prompts: Optional[int] = None
    public_info: Optional[PublicVMCPInfo] = None
    # Sharing fields
    is_public: bool = False
    public_tags: List[str] = field(default_factory=list)
    public_at: Optional[str] = None
    is_wellknown: bool = False
    metadata: Optional[Dict[str, Any]] = None


    def __post_init__(self):
        """Set default timestamps if not provided"""
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VMCPConfig':
        """Create VMCPConfig from dictionary"""
        # Handle datetime string conversion
        processed_data = data.copy()

        # Convert string timestamps to datetime objects if they exist
        if 'created_at' in processed_data and isinstance(processed_data['created_at'], str):
            try:
                processed_data['created_at'] = datetime.fromisoformat(processed_data['created_at'].replace('Z', '+00:00'))
            except (ValueError, TypeError):
                processed_data['created_at'] = None

        if 'updated_at' in processed_data and isinstance(processed_data['updated_at'], str):
            try:
                processed_data['updated_at'] = datetime.fromisoformat(processed_data['updated_at'].replace('Z', '+00:00'))
            except (ValueError, TypeError):
                processed_data['updated_at'] = None

        return cls(**processed_data)

    def to_dict(self, include_environment_variables: bool = True) -> Dict[str, Any]:
        """Convert VMCPConfig to dictionary for JSON serialization"""
        from datetime import datetime
        
        vmcp_dict = {
            "id": self.id,
            "name": self.name,
            "user_id": self.user_id,
            "description": self.description,
            "system_prompt": self.system_prompt,
            "vmcp_config": self.vmcp_config,
            "custom_prompts": self.custom_prompts,
            "custom_tools": self.custom_tools,
            "custom_context": self.custom_context,
            "custom_resources": self.custom_resources,
            "custom_resource_templates": self.custom_resource_templates,
            "custom_widgets": self.custom_widgets,
            "uploaded_files": self.uploaded_files,
            "custom_resource_uris": self.custom_resource_uris,
            "total_tools": self.total_tools,
            "total_resources": self.total_resources,
            "total_resource_templates": self.total_resource_templates,
            "total_prompts": self.total_prompts,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "creator_id": self.creator_id,
            "creator_username": self.creator_username,
            # Sharing fields
            "is_public": self.is_public,
            "public_tags": self.public_tags,
            "public_at": self.public_at,
            "metadata": self.metadata
        }
        
        # Conditionally include environment variables (for backward compatibility)
        if include_environment_variables:
            vmcp_dict["environment_variables"] = self.environment_variables
        
        # Handle any enum serialization in the data
        vmcp_dict = self._serialize_enums(vmcp_dict)
        
        return vmcp_dict
    
    def _serialize_enums(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively serialize enums in the data dictionary"""
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                if hasattr(value, 'value'):  # Check if it's an enum
                    result[key] = value.value
                elif isinstance(value, dict):
                    result[key] = self._serialize_enums(value)
                elif isinstance(value, list):
                    result[key] = [self._serialize_enums(item) if isinstance(item, dict) else (item.value if hasattr(item, 'value') else item) for item in value]
                else:
                    result[key] = value
            return result
        elif isinstance(data, list):
            return [self._serialize_enums(item) if isinstance(item, dict) else (item.value if hasattr(item, 'value') else item) for item in data]
        else:
            return data.value if hasattr(data, 'value') else data

    def for_vmcp_listing(self) -> Dict[str, Any]:
        return self.to_dict()
        
    def to_summary_dict(self) -> Dict[str, Any]:
        """Convert VMCPConfig to a summary dictionary with only essential fields for listing"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_public": self.is_public,
            "public_tags": self.public_tags,
            "metadata": self.metadata
        }
    
    def to_vmcp_registry_config(self) -> VMCPRegistryConfig:
        # Convert selected_servers to MCPRegistryConfig objects if they exist
        # just copy doesnt work it changes the vmcp config
        registry_vmcp_config = deepcopy(self.vmcp_config) if self.vmcp_config else {}

        if 'selected_servers' in registry_vmcp_config:
            from vmcp.mcps.models import MCPRegistryConfig
            selected_servers = registry_vmcp_config['selected_servers']
            if isinstance(selected_servers, list):
                # Convert each server dict to MCPRegistryConfig
                registry_servers = []
                for server in selected_servers:
                    if isinstance(server, dict):
                        loaded_server = MCPServerConfig.from_dict(server)
                        registry_servers.append(loaded_server.to_mcp_registry_config())
                    else:
                        registry_servers.append(server)
                registry_vmcp_config['selected_servers'] = registry_servers
        
        return VMCPRegistryConfig(
            id=self.id,
            name=self.name,
            user_id=self.user_id,
            description=self.description,
            vmcp_config=registry_vmcp_config,
            environment_variables=self.environment_variables,
            created_at=self.created_at,
            updated_at=self.updated_at,
            creator_id=self.creator_id,
            creator_username=self.creator_username,
            total_tools=self.total_tools,
            total_resources=self.total_resources,
            total_resource_templates=self.total_resource_templates,
            total_prompts=self.total_prompts,
            public_info=self.public_info,
            is_public=self.is_public,
            public_tags=self.public_tags,
            public_at=self.public_at,
            is_wellknown=self.is_wellknown,
            metadata=self.metadata,
        )


# Stats models
class StatsFilterRequest(BaseModel):
    agent_name: Optional[str] = Field(None, description="Filter by agent name")
    vmcp_name: Optional[str] = Field(None, description="Filter by vMCP name")
    method: Optional[str] = Field(None, description="Filter by method name")
    search: Optional[str] = Field(None, description="Search across all fields")
    page: int = Field(1, description="Page number for pagination")
    limit: int = Field(50, description="Number of items per page")

class LogEntry(BaseModel):
    timestamp: str
    method: str
    agent_name: str
    agent_id: str
    user_id: int
    client_id: str
    operation_id: str
    mcp_server: Optional[str] = None
    mcp_method: Optional[str] = None
    original_name: Optional[str] = None
    arguments: Optional[Any] = None
    result: Optional[Any] = None
    vmcp_id: Optional[str] = None
    vmcp_name: Optional[str] = None
    total_tools: Optional[int] = None
    total_resources: Optional[int] = None
    total_resource_templates: Optional[int] = None
    total_prompts: Optional[int] = None

class StatsResponse(BaseModel):
    logs: List[LogEntry]
    pagination: Dict[str, Any]
    stats: Dict[str, Any]
    filter_options: Dict[str, List[str]]  # New field for dropdown options

class StatsSummary(BaseModel):
    total_logs: int
    total_agents: int
    total_vmcps: int
    total_tool_calls: int
    total_resource_calls: int
    total_prompt_calls: int
    unique_methods: List[str]
    agent_breakdown: Dict[str, int]
    vmcp_breakdown: Dict[str, int]
    method_breakdown: Dict[str, int]