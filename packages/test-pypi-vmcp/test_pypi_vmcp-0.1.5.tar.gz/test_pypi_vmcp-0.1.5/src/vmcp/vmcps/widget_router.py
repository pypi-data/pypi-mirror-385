"""
Widget Router for OpenAI Apps SDK Integration

API endpoints for widget management:
- Upload widget source files
- List widgets
- Get widget details
- Build widget
- Get build status
- Preview widget
- Update widget
- Delete widget
- Serve widget files
"""

import logging
import tempfile
import shutil
from typing import List, Optional
from pathlib import Path

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import HTMLResponse, Response
from sqlalchemy.orm import Session

from vmcp.storage.database import get_db
from vmcp.storage.dummy_user import UserContext
from vmcp.storage.dummy_user import get_user_context
from vmcp.storage.models import Widget, Blob

from vmcp.vmcps.widget_models import (
    Widget as WidgetResponse,
    WidgetListResponse,
    WidgetResponse as SingleWidgetResponse,
    WidgetBuildRequest,
    WidgetBuildResponse,
    WidgetUpdateRequest,
    WidgetPreviewResponse,
    WidgetBuildStatus
)
from vmcp.vmcps.widget_service import WidgetService, WidgetBuilder, generate_widget_meta

router = APIRouter(prefix="/vmcps/{vmcp_id}/widgets", tags=["Widgets"])

logger = logging.getLogger(__name__)


def is_entry_point_file(filename: str) -> bool:
    """Check if file is an entry point"""
    return filename.lower() in ['index.jsx', 'index.tsx', 'index.js', 'index.ts']


def is_valid_widget_file(filename: str) -> bool:
    """Check if file is a valid widget source file"""
    valid_extensions = ['.js', '.jsx', '.ts', '.tsx', '.css', '.scss', '.json']
    return any(filename.lower().endswith(ext) for ext in valid_extensions)


@router.post("/init", response_model=SingleWidgetResponse, status_code=201)
async def initialize_widget(
    vmcp_id: str,
    name: str = Form(...),
    description: Optional[str] = Form(None),
    user_context: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """
    Initialize a new widget with default template files

    Creates a production-grade widget following OpenAI Apps SDK patterns with:
    - index.jsx with window.openai hooks
    - index.css with modern styling
    - package.json with React 19 and Vite 7
    """
    logger.info("=" * 80)
    logger.info("🎨 WIDGET INITIALIZATION REQUEST")
    logger.info("=" * 80)
    logger.info(f"   vmcp_id: {vmcp_id}")
    logger.info(f"   name: {name}")
    logger.info(f"   description: {description}")
    logger.info(f"   user_id: {user_context.user_id}")

    try:
        # Validate widget name
        is_valid, error_msg = WidgetService.is_valid_widget_name(name)
        if not is_valid:
            logger.error(f"❌ Invalid widget name: {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)

        # Check if widget with same name already exists
        existing = db.query(Widget).filter(
            Widget.user_id == user_context.user_id,
            Widget.vmcp_id == vmcp_id,
            Widget.name == name
        ).first()

        if existing:
            logger.warning(f"⚠️  Widget '{name}' already exists for this vMCP")
            raise HTTPException(
                status_code=409,
                detail=f"Widget with name '{name}' already exists for this vMCP"
            )

        # Create widget
        logger.info(f"🔨 Creating widget in database...")
        widget = WidgetService.create_widget(
            db=db,
            user_id=user_context.user_id,
            vmcp_id=vmcp_id,
            name=name,
            description=description
        )
        logger.info(f"✅ Widget created with ID: {widget.widget_id}")

        # Import template functions
        from vmcps.widget_templates import (
            get_default_index_jsx,
            get_default_index_css,
            get_default_package_json
        )

        # Create default template files
        template_files = {
            'index.jsx': get_default_index_jsx(name),
            'index.css': get_default_index_css(name),
            'package.json': get_default_package_json(name)
        }

        logger.info(f"💾 Creating {len(template_files)} template files...")
        for filename, content in template_files.items():
            # Create blob
            blob_id = f"blob_{widget.widget_id}_{filename}"
            content_bytes = content.encode('utf-8')

            blob = Blob(
                blob_id=blob_id,
                user_id=user_context.user_id,
                original_filename=filename,
                filename=filename,
                content_type="text/plain",
                size=len(content_bytes),
                file_data=content_bytes,
                vmcp_id=vmcp_id
            )

            db.add(blob)
            logger.info(f"   ✅ Created blob: {blob_id}")

            # Add file reference to widget
            is_entry = is_entry_point_file(filename)
            widget = WidgetService.add_source_file_to_widget(
                db=db,
                widget=widget,
                filename=filename,
                path=filename,
                blob_id=blob_id,
                size=len(content_bytes),
                content_type="text/plain",
                is_entry_point=is_entry
            )
            logger.info(f"   ✅ Added {filename} to widget")

        db.commit()
        db.refresh(widget)

        logger.info(f"✅ Widget initialized successfully with {len(template_files)} template files")
        logger.info("=" * 80)

        return SingleWidgetResponse(
            success=True,
            widget=widget.to_dict()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error initializing widget: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to initialize widget: {str(e)}")


@router.post("", response_model=SingleWidgetResponse, status_code=201)
async def upload_widget(
    vmcp_id: str,
    name: str = Form(...),
    description: Optional[str] = Form(None),
    files: List[UploadFile] = File(...),
    user_context: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """
    Upload widget source files

    Creates a new widget with uploaded source files.
    Files are stored in blob storage and widget metadata is saved.
    """
    logger.info("=" * 80)
    logger.info("📤 WIDGET UPLOAD REQUEST")
    logger.info("=" * 80)
    logger.info(f"   vmcp_id: {vmcp_id}")
    logger.info(f"   name: {name}")
    logger.info(f"   description: {description}")
    logger.info(f"   user_id: {user_context.user_id}")
    logger.info(f"   files count: {len(files) if files else 0}")
    if files:
        logger.info(f"   file names: {[f.filename for f in files]}")

    try:
        # Validate widget name
        is_valid, error_msg = WidgetService.is_valid_widget_name(name)
        if not is_valid:
            logger.error(f"❌ Invalid widget name: {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)

        # Check if widget with same name already exists
        existing = db.query(Widget).filter(
            Widget.user_id == user_context.user_id,
            Widget.vmcp_id == vmcp_id,
            Widget.name == name
        ).first()

        if existing:
            logger.warning(f"⚠️  Widget '{name}' already exists for this vMCP")
            raise HTTPException(
                status_code=409,
                detail=f"Widget with name '{name}' already exists for this vMCP"
            )

        # Validate files
        if not files:
            logger.error("❌ No files provided")
            raise HTTPException(status_code=400, detail="No files provided")

        logger.info(f"📁 Files to upload: {[f.filename for f in files]}")

        # Check file validity
        invalid_files = [f.filename for f in files if not is_valid_widget_file(f.filename)]
        if invalid_files:
            logger.error(f"❌ Invalid file types: {invalid_files}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file types: {', '.join(invalid_files)}"
            )

        # Create widget
        logger.info(f"🔨 Creating widget in database...")
        widget = WidgetService.create_widget(
            db=db,
            user_id=user_context.user_id,
            vmcp_id=vmcp_id,
            name=name,
            description=description
        )
        logger.info(f"✅ Widget created with ID: {widget.widget_id}")

        # Save files to blob storage
        logger.info(f"💾 Saving {len(files)} files to blob storage...")
        for idx, file in enumerate(files, 1):
            # Read file content
            content = await file.read()
            logger.info(f"   [{idx}/{len(files)}] {file.filename} - {len(content)} bytes")

            # Create blob
            blob_id = f"blob_{widget.widget_id}_{file.filename}"
            blob = Blob(
                blob_id=blob_id,
                user_id=user_context.user_id,
                original_filename=file.filename,
                filename=file.filename,
                content_type=file.content_type or "application/octet-stream",
                size=len(content),
                file_data=content,
                vmcp_id=vmcp_id
            )

            db.add(blob)
            logger.info(f"      ✅ Blob created: {blob_id}")

            # Add file reference to widget
            is_entry = is_entry_point_file(file.filename)
            logger.info(f"      📝 Adding to widget (entry_point={is_entry})")
            widget = WidgetService.add_source_file_to_widget(
                db=db,
                widget=widget,
                filename=file.filename,
                path=file.filename,
                blob_id=blob_id,
                size=len(content),
                content_type=file.content_type or "application/octet-stream",
                is_entry_point=is_entry
            )
            logger.info(f"      ✅ File added to widget")

        logger.info(f"💾 Committing to database...")
        db.commit()
        db.refresh(widget)
        logger.info(f"✅ Database commit successful")

        # Validate files
        logger.info(f"🔍 Validating widget files...")
        logger.info(f"   source_files count: {len(widget.source_files)}")
        logger.info(f"   source_files: {widget.source_files}")
        valid, errors, warnings = WidgetService.validate_widget_files(widget.source_files)

        if not valid:
            logger.error(f"❌ Widget validation failed!")
            logger.error(f"   Errors: {errors}")
            logger.error(f"   Warnings: {warnings}")
            # Delete widget if validation fails
            WidgetService.delete_widget(db, widget)
            raise HTTPException(
                status_code=400,
                detail={"errors": errors, "warnings": warnings}
            )

        logger.info(f"✅ Widget validation successful")
        if warnings:
            logger.warning(f"⚠️  Warnings: {warnings}")

        logger.info("=" * 80)
        logger.info(f"✅ WIDGET UPLOAD COMPLETE: {widget.widget_id}")
        logger.info("=" * 80)

        return {"widget": widget.to_dict()}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading widget: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to upload widget: {str(e)}")


@router.get("", response_model=WidgetListResponse)
async def list_widgets(
    vmcp_id: str,
    user_context: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """List all widgets for a vMCP"""
    try:
        widgets = WidgetService.get_widgets_for_vmcp(
            db=db,
            vmcp_id=vmcp_id,
            user_id=user_context.user_id
        )

        return {
            "widgets": [widget.to_dict() for widget in widgets]
        }

    except Exception as e:
        logger.error(f"Error listing widgets: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list widgets: {str(e)}")


@router.get("/{widget_id}", response_model=SingleWidgetResponse)
async def get_widget(
    vmcp_id: str,
    widget_id: str,
    user_context: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """Get specific widget details"""
    try:
        widget = WidgetService.get_widget_by_id(
            db=db,
            widget_id=widget_id,
            user_id=user_context.user_id
        )

        if not widget or widget.vmcp_id != vmcp_id:
            raise HTTPException(status_code=404, detail="Widget not found")

        return {"widget": widget.to_dict()}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting widget: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get widget: {str(e)}")


async def build_widget_task(widget_id: str, user_id: int, db_session):
    """Background task to build widget"""
    logger.info(f"Starting build for widget {widget_id}")

    try:
        # Get widget
        widget = db_session.query(Widget).filter(
            Widget.widget_id == widget_id,
            Widget.user_id == user_id
        ).first()

        if not widget:
            logger.error(f"Widget {widget_id} not found")
            return

        # Update status to building
        widget.update_build_status("building")
        db_session.commit()

        # Create temp directory
        with tempfile.TemporaryDirectory() as temp_dir:
            logger.info(f"Building widget in {temp_dir}")

            # Build widget
            success, error, build_log, built_files = WidgetBuilder.build_widget(
                db=db_session,
                widget=widget,
                temp_dir=temp_dir
            )

            if success and built_files:
                # Save built files to blobs (HTML, CSS, JS)
                html_blob_id = f"blob_{widget_id}_built_html"
                css_blob_id = f"blob_{widget_id}_built_css"
                js_blob_id = f"blob_{widget_id}_built_js"

                # Save HTML blob
                existing_html_blob = db_session.query(Blob).filter(
                    Blob.blob_id == html_blob_id
                ).first()

                if existing_html_blob:
                    existing_html_blob.original_filename = f"{widget.name}.html"
                    existing_html_blob.filename = f"{widget.name}.html"
                    existing_html_blob.content_type = "text/html"
                    existing_html_blob.size = len(built_files['html'].encode())
                    existing_html_blob.file_data = built_files['html'].encode()
                    logger.info(f"Updated existing HTML blob {html_blob_id}")
                else:
                    html_blob = Blob(
                        blob_id=html_blob_id,
                        user_id=user_id,
                        original_filename=f"{widget.name}.html",
                        filename=f"{widget.name}.html",
                        content_type="text/html",
                        size=len(built_files['html'].encode()),
                        file_data=built_files['html'].encode(),
                        vmcp_id=widget.vmcp_id
                    )
                    db_session.add(html_blob)
                    logger.info(f"Created new HTML blob {html_blob_id}")

                # Save CSS blob (if exists)
                css_content = built_files.get('css', '')
                if css_content:
                    existing_css_blob = db_session.query(Blob).filter(
                        Blob.blob_id == css_blob_id
                    ).first()

                    if existing_css_blob:
                        existing_css_blob.original_filename = f"{widget.name}.css"
                        existing_css_blob.filename = f"{widget.name}.css"
                        existing_css_blob.content_type = "text/css"
                        existing_css_blob.size = len(css_content.encode())
                        existing_css_blob.file_data = css_content.encode()
                        logger.info(f"Updated existing CSS blob {css_blob_id}")
                    else:
                        css_blob = Blob(
                            blob_id=css_blob_id,
                            user_id=user_id,
                            original_filename=f"{widget.name}.css",
                            filename=f"{widget.name}.css",
                            content_type="text/css",
                            size=len(css_content.encode()),
                            file_data=css_content.encode(),
                            vmcp_id=widget.vmcp_id
                        )
                        db_session.add(css_blob)
                        logger.info(f"Created new CSS blob {css_blob_id}")

                # Save JS blob
                js_content = built_files.get('js', '')
                if js_content:
                    existing_js_blob = db_session.query(Blob).filter(
                        Blob.blob_id == js_blob_id
                    ).first()

                    if existing_js_blob:
                        existing_js_blob.original_filename = f"{widget.name}.js"
                        existing_js_blob.filename = f"{widget.name}.js"
                        existing_js_blob.content_type = "application/javascript"
                        existing_js_blob.size = len(js_content.encode())
                        existing_js_blob.file_data = js_content.encode()
                        logger.info(f"Updated existing JS blob {js_blob_id}")
                    else:
                        js_blob = Blob(
                            blob_id=js_blob_id,
                            user_id=user_id,
                            original_filename=f"{widget.name}.js",
                            filename=f"{widget.name}.js",
                            content_type="application/javascript",
                            size=len(js_content.encode()),
                            file_data=js_content.encode(),
                            vmcp_id=widget.vmcp_id
                        )
                        db_session.add(js_blob)
                        logger.info(f"Created new JS blob {js_blob_id}")

                # Update widget with built file references
                widget.update_built_files(
                    html=html_blob_id,
                    css=css_blob_id if css_content else None,
                    js=js_blob_id if js_content else None,
                    hash=built_files.get('hash')
                )

                widget.update_build_status("built", log=build_log)
                logger.info(f"Widget {widget_id} built successfully")

            else:
                widget.update_build_status("failed", error=error, log=build_log)
                logger.error(f"Widget {widget_id} build failed: {error}")

            db_session.commit()

    except Exception as e:
        logger.error(f"Error in build task for widget {widget_id}: {str(e)}")
        try:
            widget = db_session.query(Widget).filter(Widget.widget_id == widget_id).first()
            if widget:
                widget.update_build_status("failed", error=str(e))
                db_session.commit()
        except:
            pass


@router.post("/{widget_id}/build", response_model=WidgetBuildResponse)
async def build_widget(
    vmcp_id: str,
    widget_id: str,
    background_tasks: BackgroundTasks,
    build_request: Optional[WidgetBuildRequest] = None,
    user_context: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """
    Trigger widget build process

    Starts an asynchronous build process for the widget.
    """
    try:
        widget = WidgetService.get_widget_by_id(
            db=db,
            widget_id=widget_id,
            user_id=user_context.user_id
        )

        if not widget or widget.vmcp_id != vmcp_id:
            raise HTTPException(status_code=404, detail="Widget not found")

        # Allow force rebuild - if already building, this will restart the build
        if widget.is_building:
            logger.info(f"Force rebuilding widget {widget_id} (was in building state)")
        elif widget.is_built:
            logger.info(f"Rebuilding widget {widget_id}")

        # Start background build task
        from auth_service.database import SessionLocal
        background_tasks.add_task(
            build_widget_task,
            widget_id=widget_id,
            user_id=user_context.user_id,
            db_session=SessionLocal()
        )

        # Update status immediately
        widget.update_build_status("building")
        db.commit()

        logger.info(f"Build started for widget {widget_id}")

        return WidgetBuildResponse(
            success=True,
            widget_id=widget_id,
            build_status=WidgetBuildStatus.BUILDING,
            build_error=None,
            build_log=None,
            built_files=None
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting build: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start build: {str(e)}")


@router.get("/{widget_id}/build/status", response_model=WidgetBuildResponse)
async def get_build_status(
    vmcp_id: str,
    widget_id: str,
    user_context: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """Get current build status"""
    try:
        widget = WidgetService.get_widget_by_id(
            db=db,
            widget_id=widget_id,
            user_id=user_context.user_id
        )

        if not widget or widget.vmcp_id != vmcp_id:
            raise HTTPException(status_code=404, detail="Widget not found")

        from vmcps.widget_models import WidgetBuiltFiles as BuiltFilesModel

        built_files = None
        if widget.is_built:
            built_files = BuiltFilesModel(**widget.built_files)

        return WidgetBuildResponse(
            success=widget.is_built,
            widget_id=widget_id,
            build_status=WidgetBuildStatus(widget.build_status),
            build_error=widget.build_error,
            build_log=widget.build_log,
            built_files=built_files
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting build status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get build status: {str(e)}")


@router.get("/{widget_id}/preview", response_model=WidgetPreviewResponse)
async def get_widget_preview(
    vmcp_id: str,
    widget_id: str,
    sample_data: Optional[str] = None,
    theme: Optional[str] = "light",
    user_context: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """Get widget preview HTML"""
    try:
        widget = WidgetService.get_widget_by_id(
            db=db,
            widget_id=widget_id,
            user_id=user_context.user_id
        )

        if not widget or widget.vmcp_id != vmcp_id:
            raise HTTPException(status_code=404, detail="Widget not found")

        if not widget.is_built:
            raise HTTPException(status_code=400, detail="Widget is not built yet")

        # Get HTML from blob
        html_blob_id = widget.get_html_url()
        if not html_blob_id:
            raise HTTPException(status_code=404, detail="Widget HTML not found")

        html_blob = db.query(Blob).filter(Blob.blob_id == html_blob_id).first()
        if not html_blob:
            raise HTTPException(status_code=404, detail="Widget HTML blob not found")

        html_content = html_blob.file_data.decode('utf-8')

        return WidgetPreviewResponse(
            html=html_content,
            css=None,
            js=None
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting preview: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get preview: {str(e)}")


@router.patch("/{widget_id}", response_model=SingleWidgetResponse)
async def update_widget(
    vmcp_id: str,
    widget_id: str,
    update_request: WidgetUpdateRequest,
    user_context: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """Update widget metadata"""
    try:
        widget = WidgetService.get_widget_by_id(
            db=db,
            widget_id=widget_id,
            user_id=user_context.user_id
        )

        if not widget or widget.vmcp_id != vmcp_id:
            raise HTTPException(status_code=404, detail="Widget not found")

        # Extract metadata if provided
        invoking_msg = None
        invoked_msg = None
        if update_request.metadata:
            invoking_msg = update_request.metadata.invoking_message
            invoked_msg = update_request.metadata.invoked_message

        widget = WidgetService.update_widget_metadata(
            db=db,
            widget=widget,
            name=update_request.name,
            description=update_request.description,
            invoking_message=invoking_msg,
            invoked_message=invoked_msg
        )

        logger.info(f"Widget {widget_id} updated by user {user_context.user_id}")

        return {"widget": widget.to_dict()}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating widget: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update widget: {str(e)}")


@router.get("/{widget_id}/files")
async def list_widget_files(
    vmcp_id: str,
    widget_id: str,
    user_context: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """List all source files for a widget"""
    try:
        widget = WidgetService.get_widget_by_id(
            db=db,
            widget_id=widget_id,
            user_id=user_context.user_id
        )

        if not widget or widget.vmcp_id != vmcp_id:
            raise HTTPException(status_code=404, detail="Widget not found")

        return {"files": widget.source_files}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing widget files: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")


@router.post("/{widget_id}/files")
async def create_widget_file(
    vmcp_id: str,
    widget_id: str,
    filename: str = Form(...),
    content: str = Form(""),
    user_context: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """Create a new source file for a widget"""
    try:
        import uuid
        from sqlalchemy.orm import attributes

        widget = WidgetService.get_widget_by_id(
            db=db,
            widget_id=widget_id,
            user_id=user_context.user_id
        )

        if not widget or widget.vmcp_id != vmcp_id:
            raise HTTPException(status_code=404, detail="Widget not found")

        # Check if filename already exists
        existing_file = next((f for f in widget.source_files if f['filename'] == filename), None)
        if existing_file:
            raise HTTPException(status_code=400, detail=f"File '{filename}' already exists")

        # Create blob for the file
        file_data = content.encode('utf-8')
        blob = Blob(
            blob_id=str(uuid.uuid4()),
            user_id=user_context.user_id,
            original_filename=filename,
            filename=filename,
            file_data=file_data,
            size=len(file_data),
            content_type="text/plain"
        )
        db.add(blob)
        db.flush()

        # Create file info
        file_info = {
            'id': str(uuid.uuid4()),
            'filename': filename,
            'path': filename,
            'blob_id': blob.blob_id,
            'size': len(file_data),
            'content_type': 'text/plain',
            'is_entry_point': False
        }

        # Add to widget source_files
        source_files = widget.source_files.copy()
        source_files.append(file_info)
        widget.widget_data = {
            **widget.widget_data,
            'source_files': source_files
        }
        attributes.flag_modified(widget, 'widget_data')

        db.commit()

        logger.info(f"Created file {filename} for widget {widget_id}")

        return {
            "success": True,
            "file": file_info,
            "message": "File created successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating widget file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create file: {str(e)}")


@router.get("/{widget_id}/files/{file_id}")
async def get_widget_file(
    vmcp_id: str,
    widget_id: str,
    file_id: str,
    user_context: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """Get content of a specific widget source file"""
    try:
        widget = WidgetService.get_widget_by_id(
            db=db,
            widget_id=widget_id,
            user_id=user_context.user_id
        )

        if not widget or widget.vmcp_id != vmcp_id:
            raise HTTPException(status_code=404, detail="Widget not found")

        # Find the file
        file_info = next((f for f in widget.source_files if f['id'] == file_id), None)
        if not file_info:
            raise HTTPException(status_code=404, detail="File not found")

        # Get blob content
        blob = db.query(Blob).filter(Blob.blob_id == file_info['blob_id']).first()
        if not blob:
            raise HTTPException(status_code=404, detail="File content not found")

        content = blob.file_data.decode('utf-8')

        return {
            "file": file_info,
            "content": content
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting widget file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get file: {str(e)}")


@router.put("/{widget_id}/files/{file_id}")
async def update_widget_file(
    vmcp_id: str,
    widget_id: str,
    file_id: str,
    content: str = Form(...),
    user_context: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """Update content of a specific widget source file"""
    try:
        widget = WidgetService.get_widget_by_id(
            db=db,
            widget_id=widget_id,
            user_id=user_context.user_id
        )

        if not widget or widget.vmcp_id != vmcp_id:
            raise HTTPException(status_code=404, detail="Widget not found")

        # Find the file
        file_info = next((f for f in widget.source_files if f['id'] == file_id), None)
        if not file_info:
            raise HTTPException(status_code=404, detail="File not found")

        # Update blob content
        blob = db.query(Blob).filter(Blob.blob_id == file_info['blob_id']).first()
        if not blob:
            raise HTTPException(status_code=404, detail="File content not found")

        # Update the blob
        blob.file_data = content.encode('utf-8')
        blob.size = len(content.encode('utf-8'))
        db.commit()

        logger.info(f"Updated file {file_id} in widget {widget_id}")

        return {
            "success": True,
            "file": file_info,
            "message": "File updated successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating widget file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update file: {str(e)}")


@router.delete("/{widget_id}/files/{file_id}")
async def delete_widget_file(
    vmcp_id: str,
    widget_id: str,
    file_id: str,
    user_context: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """Delete a specific widget source file"""
    try:
        widget = WidgetService.get_widget_by_id(
            db=db,
            widget_id=widget_id,
            user_id=user_context.user_id
        )

        if not widget or widget.vmcp_id != vmcp_id:
            raise HTTPException(status_code=404, detail="Widget not found")

        # Find the file
        file_info = next((f for f in widget.source_files if f['id'] == file_id), None)
        if not file_info:
            raise HTTPException(status_code=404, detail="File not found")

        # Check if it's the entry point
        if file_info.get('is_entry_point'):
            raise HTTPException(status_code=400, detail="Cannot delete entry point file")

        # Delete the blob
        db.query(Blob).filter(Blob.blob_id == file_info['blob_id']).delete()

        # Remove from widget_data
        from sqlalchemy.orm import attributes
        source_files = [f for f in widget.source_files if f['id'] != file_id]
        widget.widget_data = {
            **widget.widget_data,
            'source_files': source_files
        }
        attributes.flag_modified(widget, 'widget_data')

        db.commit()

        logger.info(f"Deleted file {file_id} from widget {widget_id}")

        return {"success": True, "message": "File deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting widget file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")


@router.get("/{widget_id}/serve/js")
async def serve_widget_js(
    vmcp_id: str,
    widget_id: str,
    db: Session = Depends(get_db)
):
    """Serve the built widget JavaScript module - Public endpoint, no auth required"""
    try:
        # Query widget without user_id filtering since this is a public endpoint
        from auth_service.models import Widget
        widget = db.query(Widget).filter(
            Widget.widget_id == widget_id,
            Widget.vmcp_id == vmcp_id
        ).first()

        if not widget:
            raise HTTPException(status_code=404, detail="Widget not found")

        if widget.build_status != 'built':
            raise HTTPException(status_code=400, detail="Widget is not built yet")

        # Get the built JS file from blob storage
        built_files = widget.widget_data.get('built_files', {})
        js_blob_id = built_files.get('js')

        if not js_blob_id:
            raise HTTPException(status_code=404, detail="Widget JS not found")

        # Fetch the blob
        from auth_service.models import Blob
        blob = db.query(Blob).filter(Blob.blob_id == js_blob_id).first()

        if not blob or not blob.file_data:
            raise HTTPException(status_code=404, detail="Widget JS file not found")

        # Decode bytes to string
        if isinstance(blob.file_data, bytes):
            js_content = blob.file_data.decode('utf-8')
        else:
            js_content = str(blob.file_data)

        logger.info(f"Serving widget JS for {widget_id}, size: {len(js_content)} bytes")

        # Return as JavaScript module
        return Response(
            content=js_content,
            media_type="application/javascript",
            headers={
                "Cache-Control": "public, max-age=3600",
                "Access-Control-Allow-Origin": "*"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving widget JS: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to serve widget JS: {str(e)}")


@router.get("/{widget_id}/serve/css")
async def serve_widget_css(
    vmcp_id: str,
    widget_id: str,
    db: Session = Depends(get_db)
):
    """Serve the built widget CSS - Public endpoint, no auth required"""
    try:
        # Query widget without user_id filtering since this is a public endpoint
        from auth_service.models import Widget
        widget = db.query(Widget).filter(
            Widget.widget_id == widget_id,
            Widget.vmcp_id == vmcp_id
        ).first()

        if not widget:
            raise HTTPException(status_code=404, detail="Widget not found")

        if widget.build_status != 'built':
            raise HTTPException(status_code=400, detail="Widget is not built yet")

        # Get the built CSS file from blob storage
        built_files = widget.widget_data.get('built_files', {})
        css_blob_id = built_files.get('css')

        if not css_blob_id:
            # CSS is optional, return empty stylesheet
            return Response(
                content="",
                media_type="text/css",
                headers={
                    "Cache-Control": "public, max-age=3600",
                    "Access-Control-Allow-Origin": "*"
                }
            )

        # Fetch the blob
        from auth_service.models import Blob
        blob = db.query(Blob).filter(Blob.blob_id == css_blob_id).first()

        if not blob or not blob.file_data:
            # Return empty stylesheet if not found
            return Response(
                content="",
                media_type="text/css",
                headers={
                    "Cache-Control": "public, max-age=3600",
                    "Access-Control-Allow-Origin": "*"
                }
            )

        # Decode bytes to string
        if isinstance(blob.file_data, bytes):
            css_content = blob.file_data.decode('utf-8')
        else:
            css_content = str(blob.file_data)

        logger.info(f"Serving widget CSS for {widget_id}, size: {len(css_content)} bytes")

        # Return as CSS
        return Response(
            content=css_content,
            media_type="text/css",
            headers={
                "Cache-Control": "public, max-age=3600",
                "Access-Control-Allow-Origin": "*"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving widget bundle: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to serve widget bundle: {str(e)}")


@router.delete("/{widget_id}", status_code=204)
async def delete_widget(
    vmcp_id: str,
    widget_id: str,
    user_context: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """Delete a widget"""
    try:
        widget = WidgetService.get_widget_by_id(
            db=db,
            widget_id=widget_id,
            user_id=user_context.user_id
        )

        if not widget or widget.vmcp_id != vmcp_id:
            raise HTTPException(status_code=404, detail="Widget not found")

        success = WidgetService.delete_widget(db=db, widget=widget)

        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete widget")

        logger.info(f"Widget {widget_id} deleted by user {user_context.user_id}")

        return Response(status_code=204)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting widget: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete widget: {str(e)}")


# Separate router for serving widget files (no vmcp_id in path)
serve_router = APIRouter(prefix="/widgets", tags=["Widget Files"])


@serve_router.get("/{widget_id}/serve/{file_type}")
async def serve_widget_file(
    widget_id: str,
    file_type: str,
    db: Session = Depends(get_db)
):
    """
    Serve widget files (HTML, CSS, JS)

    Public endpoint for serving built widget files.
    No authentication required for serving.
    """
    try:
        if file_type not in ['html', 'css', 'js']:
            raise HTTPException(status_code=400, detail="Invalid file type")

        # Get widget
        widget = db.query(Widget).filter(Widget.widget_id == widget_id).first()

        if not widget:
            raise HTTPException(status_code=404, detail="Widget not found")

        if widget.build_status != 'built':
            raise HTTPException(status_code=400, detail="Widget not built")

        # Get file blob_id from built_files
        built_files = widget.widget_data.get('built_files', {})
        file_blob_id = built_files.get(file_type)

        # CSS is optional - return empty if not found
        if not file_blob_id and file_type == 'css':
            return Response(
                content="",
                media_type="text/css",
                headers={
                    "Cache-Control": "public, max-age=3600",
                    "Access-Control-Allow-Origin": "*"
                }
            )

        if not file_blob_id:
            raise HTTPException(status_code=404, detail=f"{file_type.upper()} file not found")

        # Get blob
        blob = db.query(Blob).filter(Blob.blob_id == file_blob_id).first()

        if not blob or not blob.file_data:
            if file_type == 'css':
                # Return empty CSS if not found
                return Response(
                    content="",
                    media_type="text/css",
                    headers={
                        "Cache-Control": "public, max-age=3600",
                        "Access-Control-Allow-Origin": "*"
                    }
                )
            raise HTTPException(status_code=404, detail="File blob not found")

        # Decode bytes to string
        if isinstance(blob.file_data, bytes):
            file_content = blob.file_data.decode('utf-8')
        else:
            file_content = str(blob.file_data)

        logger.info(f"Serving widget {file_type} for {widget_id}, size: {len(file_content)} bytes")

        # Determine content type
        content_types = {
            'html': 'text/html',
            'css': 'text/css',
            'js': 'application/javascript'
        }

        return Response(
            content=file_content,
            media_type=content_types.get(file_type, 'application/octet-stream'),
            headers={
                "Cache-Control": "public, max-age=3600",
                "Access-Control-Allow-Origin": "*"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving widget {file_type}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to serve file: {str(e)}")
