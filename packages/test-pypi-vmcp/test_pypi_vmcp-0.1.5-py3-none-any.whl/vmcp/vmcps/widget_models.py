"""
Widget models for OpenAI Apps SDK integration
Pydantic models for API requests/responses and data validation
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Literal
from datetime import datetime
from enum import Enum


class WidgetBuildStatus(str, Enum):
    """Widget build status enumeration"""
    PENDING = "pending"
    BUILDING = "building"
    BUILT = "built"
    FAILED = "failed"


class WidgetMetadata(BaseModel):
    """Widget metadata for tool integration"""
    invoking_message: Optional[str] = Field(None, description="Message shown while tool is running")
    invoked_message: Optional[str] = Field(None, description="Message shown when tool completes")
    widget_accessible: bool = Field(True, description="Widget is accessible")
    result_can_produce_widget: bool = Field(True, description="Result can produce widget")
    annotations: Optional[Dict[str, Any]] = Field(None, description="Additional annotations")


class WidgetSourceFile(BaseModel):
    """Widget source file metadata"""
    id: str
    filename: str
    path: str
    blob_id: str
    size: int
    content_type: Optional[str] = None
    is_entry_point: bool = False


class WidgetBuiltFiles(BaseModel):
    """Widget built output files"""
    html: Optional[str] = None
    css: Optional[str] = None
    js: Optional[str] = None
    hash: Optional[str] = None


class Widget(BaseModel):
    """Complete widget model"""
    id: str
    vmcp_id: str
    user_id: str
    name: str
    description: Optional[str] = None
    template_uri: str
    source_files: List[WidgetSourceFile]
    built_files: WidgetBuiltFiles
    build_status: WidgetBuildStatus
    build_error: Optional[str] = None
    build_log: Optional[str] = None
    metadata: WidgetMetadata
    created_at: datetime
    updated_at: datetime

    class Config:
        use_enum_values = True


class WidgetUploadRequest(BaseModel):
    """Request to upload widget source files"""
    name: str = Field(..., description="Widget name", min_length=1, max_length=50)
    description: Optional[str] = Field(None, description="Widget description", max_length=500)
    # Files will be handled via FastAPI UploadFile


class WidgetBuildConfig(BaseModel):
    """Widget build configuration"""
    entry: str = Field("index.jsx", description="Entry point file")
    out_dir: str = Field("dist", description="Output directory")
    root_id: str = Field("widget-root", description="Root element ID")
    options: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Build options")


class WidgetBuildRequest(BaseModel):
    """Request to build a widget"""
    config: Optional[WidgetBuildConfig] = None


class WidgetBuildResponse(BaseModel):
    """Response from widget build"""
    success: bool
    widget_id: str
    build_status: WidgetBuildStatus
    build_error: Optional[str] = None
    build_log: Optional[str] = None
    built_files: Optional[WidgetBuiltFiles] = None

    class Config:
        use_enum_values = True


class WidgetUpdateRequest(BaseModel):
    """Request to update widget metadata"""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    metadata: Optional[WidgetMetadata] = None


class WidgetListResponse(BaseModel):
    """Response for listing widgets"""
    widgets: List[Widget]


class WidgetResponse(BaseModel):
    """Response for single widget"""
    widget: Widget


class WidgetPreviewRequest(BaseModel):
    """Request for widget preview"""
    sample_data: Optional[Dict[str, Any]] = None
    theme: Optional[Literal["light", "dark"]] = "light"


class WidgetPreviewResponse(BaseModel):
    """Response for widget preview"""
    html: str
    css: Optional[str] = None
    js: Optional[str] = None


class ToolCallWidgetMeta(BaseModel):
    """Widget metadata for MCP tool call response"""
    outputTemplate: str = Field(..., alias="openai/outputTemplate")
    toolInvocationInvoking: Optional[str] = Field(None, alias="openai/toolInvocation/invoking")
    toolInvocationInvoked: Optional[str] = Field(None, alias="openai/toolInvocation/invoked")
    widgetAccessible: bool = Field(True, alias="openai/widgetAccessible")
    resultCanProduceWidget: bool = Field(True, alias="openai/resultCanProduceWidget")
    widget: Optional[Dict[str, Any]] = Field(None, alias="openai.com/widget")

    class Config:
        populate_by_name = True


class ToolOverrideWithWidget(BaseModel):
    """Tool override with widget attachment"""
    name: str
    description: str
    originalName: str
    originalDescription: str
    widget_id: Optional[str] = None
    widget_metadata: Optional[WidgetMetadata] = None


class WidgetResource(BaseModel):
    """Widget as MCP resource"""
    uri: str
    name: str
    description: str
    mimeType: str = "text/html+skybridge"
    text: Optional[str] = None
    _meta: Optional[ToolCallWidgetMeta] = None
