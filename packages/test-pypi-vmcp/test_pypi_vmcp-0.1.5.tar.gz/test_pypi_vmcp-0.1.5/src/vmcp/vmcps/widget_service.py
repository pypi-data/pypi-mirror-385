"""
Widget Service for OpenAI Apps SDK Integration

This module provides widget management functions:
- Widget creation and storage
- Source file handling
- Build orchestration
- Widget retrieval and deletion
- Tool override integration
"""

import uuid
import os
import tempfile
import subprocess
import json
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path

from sqlalchemy.orm import Session
from vmcp.storage.models import Widget, Blob
from vmcp.vmcps.widget_models import (
    WidgetBuildStatus,
    WidgetMetadata,
    WidgetBuiltFiles
)
from vmcp.vmcps.widget_templates import (
    get_default_index_jsx,
    get_default_index_css,
    get_default_package_json,
    get_vite_config,
    get_widget_html_template,
    get_entry_wrapper
)
from vmcp.config import settings


class WidgetService:
    """Service class for widget operations"""

    @staticmethod
    def create_widget(
        db: Session,
        user_id: int,
        vmcp_id: str,
        name: str,
        description: Optional[str] = None
    ) -> Widget:
        """
        Create a new widget instance

        Args:
            db: Database session
            user_id: User ID
            vmcp_id: VMCP ID
            name: Widget name
            description: Widget description

        Returns:
            Created Widget instance
        """
        # Generate unique widget ID
        widget_id = f"widget_{uuid.uuid4().hex[:12]}"

        # Generate template URI
        template_uri = f"ui://widget/{name}.html"

        # Initialize widget data
        widget_data = {
            "source_files": [],
            "built_files": {},
            "metadata": {
                "invoking_message": "Loading widget...",
                "invoked_message": "Widget ready",
                "widget_accessible": True,
                "result_can_produce_widget": True,
                "annotations": {}
            }
        }

        # Create widget
        widget = Widget(
            widget_id=widget_id,
            user_id=user_id,
            vmcp_id=vmcp_id,
            name=name,
            description=description,
            template_uri=template_uri,
            build_status="pending",
            widget_data=widget_data
        )

        db.add(widget)
        db.commit()
        db.refresh(widget)

        return widget

    @staticmethod
    def add_source_file_to_widget(
        db: Session,
        widget: Widget,
        filename: str,
        path: str,
        blob_id: str,
        size: int,
        content_type: str,
        is_entry_point: bool = False
    ) -> Widget:
        """
        Add a source file reference to widget

        Args:
            db: Database session
            widget: Widget instance
            filename: Original filename
            path: Relative path in widget directory
            blob_id: Blob ID where file is stored
            size: File size in bytes
            content_type: MIME type
            is_entry_point: Whether this is the entry point file

        Returns:
            Updated Widget instance
        """
        widget.add_source_file(
            filename=filename,
            path=path,
            blob_id=blob_id,
            size=size,
            content_type=content_type,
            is_entry_point=is_entry_point
        )

        db.commit()
        db.refresh(widget)

        return widget

    @staticmethod
    def get_widget_by_id(db: Session, widget_id: str, user_id: int) -> Optional[Widget]:
        """Get widget by ID for specific user"""
        return db.query(Widget).filter(
            Widget.widget_id == widget_id,
            Widget.user_id == user_id
        ).first()

    @staticmethod
    def get_widgets_for_vmcp(db: Session, vmcp_id: str, user_id: int) -> List[Widget]:
        """Get all widgets for a specific vMCP"""
        return db.query(Widget).filter(
            Widget.vmcp_id == vmcp_id,
            Widget.user_id == user_id
        ).all()

    @staticmethod
    def delete_widget(db: Session, widget: Widget) -> bool:
        """Delete a widget and its associated source files"""
        try:
            # Get all source file blob IDs
            source_files = widget.source_files
            blob_ids = [f['blob_id'] for f in source_files]

            # Delete source file blobs
            db.query(Blob).filter(
                Blob.blob_id.in_(blob_ids)
            ).delete(synchronize_session=False)

            # Delete built file blobs if they exist
            built_files = widget.built_files
            built_blob_ids = [
                built_files.get(key) for key in ['html', 'css', 'js']
                if built_files.get(key) and built_files.get(key).startswith('blob_')
            ]

            if built_blob_ids:
                db.query(Blob).filter(
                    Blob.blob_id.in_(built_blob_ids)
                ).delete(synchronize_session=False)

            # Delete widget
            db.delete(widget)
            db.commit()

            return True
        except Exception as e:
            db.rollback()
            print(f"Error deleting widget: {e}")
            return False

    @staticmethod
    def update_widget_metadata(
        db: Session,
        widget: Widget,
        name: Optional[str] = None,
        description: Optional[str] = None,
        invoking_message: Optional[str] = None,
        invoked_message: Optional[str] = None
    ) -> Widget:
        """Update widget metadata"""
        if name is not None:
            widget.name = name
            widget.template_uri = f"ui://widget/{name}.html"

        if description is not None:
            widget.description = description

        if invoking_message is not None or invoked_message is not None:
            widget.update_metadata(
                invoking_message=invoking_message,
                invoked_message=invoked_message
            )

        db.commit()
        db.refresh(widget)

        return widget

    @staticmethod
    def validate_widget_files(files: List[Dict[str, Any]]) -> Tuple[bool, List[str], List[str]]:
        """
        Validate widget source files

        Returns:
            (valid, errors, warnings)
        """
        errors = []
        warnings = []

        # Check for entry point
        has_entry_point = any(
            f.get('filename') in ['index.jsx', 'index.tsx', 'index.js', 'index.ts']
            for f in files
        )

        if not has_entry_point:
            errors.append("No entry point found (index.jsx, index.tsx, index.js, or index.ts required)")

        # Check for package.json
        has_package_json = any(f.get('filename') == 'package.json' for f in files)
        if not has_package_json:
            warnings.append("No package.json found - default dependencies will be used")

        # Check total size
        total_size = sum(f.get('size', 0) for f in files)
        if total_size > 10 * 1024 * 1024:  # 10MB
            errors.append(f"Total size {total_size} exceeds 10MB limit")

        # Check individual file sizes
        for f in files:
            if f.get('size', 0) > 1024 * 1024:  # 1MB
                warnings.append(f"File {f.get('filename')} is larger than 1MB")

        valid = len(errors) == 0

        return valid, errors, warnings

    @staticmethod
    def is_valid_widget_name(name: str) -> Tuple[bool, Optional[str]]:
        """Validate widget name"""
        if not name or len(name.strip()) == 0:
            return False, "Widget name is required"

        if len(name) > 50:
            return False, "Widget name must be 50 characters or less"

        # Only allow alphanumeric, hyphens, and underscores
        import re
        if not re.match(r'^[a-zA-Z0-9-_]+$', name):
            return False, "Widget name can only contain letters, numbers, hyphens, and underscores"

        return True, None


class WidgetBuilder:
    """Widget build orchestration"""


    @staticmethod
    def generate_html_with_references(widget_id: str, widget_name: str) -> str:
        """Generate HTML that references separate CSS and JS files via URLs"""
        css_url = f"{settings.base_url}/api/widgets/{widget_id}/serve/css"
        js_url = f"{settings.base_url}/api/widgets/{widget_id}/serve/js"

        return get_widget_html_template(widget_name, css_url, js_url)

    @staticmethod
    def build_widget(
        db: Session,
        widget: Widget,
        temp_dir: str
    ) -> Tuple[bool, Optional[str], Optional[str], Optional[Dict[str, str]]]:
        """
        Build widget in temporary directory

        Args:
            db: Database session
            widget: Widget instance
            temp_dir: Temporary directory path

        Returns:
            (success, error_message, build_log, built_files)
        """
        build_log = []

        try:
            # Create source directory
            src_dir = Path(temp_dir)
            src_dir.mkdir(parents=True, exist_ok=True)

            build_log.append(f"Created build directory: {src_dir}")

            # Extract source files from blobs
            for source_file in widget.source_files:
                blob = db.query(Blob).filter(
                    Blob.blob_id == source_file['blob_id']
                ).first()

                if not blob:
                    raise Exception(f"Blob not found: {source_file['blob_id']}")

                file_path = src_dir / source_file['path']
                file_path.parent.mkdir(parents=True, exist_ok=True)

                # Write file
                with open(file_path, 'wb') as f:
                    f.write(blob.file_data)

                build_log.append(f"Extracted: {source_file['path']}")

            # Find entry point
            entry_point = None
            for source_file in widget.source_files:
                filename = source_file['filename']
                if filename in ['index.jsx', 'index.tsx', 'index.js', 'index.ts']:
                    entry_point = source_file['path']
                    break

            if not entry_point:
                raise Exception("No entry point found (index.jsx, index.tsx, index.js, or index.ts)")

            build_log.append(f"Entry point: {entry_point}")

            # Generate package.json if not exists
            package_json_path = src_dir / "package.json"
            if not package_json_path.exists():
                package_json = get_default_package_json(widget.name)
                with open(package_json_path, 'w') as f:
                    f.write(package_json)
                build_log.append("Generated package.json")

            # Generate entry wrapper that mounts the React component
            entry_wrapper_path = src_dir / "_entry.js"
            entry_wrapper = get_entry_wrapper(widget.name, entry_point)
            with open(entry_wrapper_path, 'w') as f:
                f.write(entry_wrapper)
            build_log.append("Generated _entry.js wrapper")

            # Generate vite.config.mts
            vite_config_path = src_dir / "vite.config.mts"
            vite_config = get_vite_config(widget.name)
            with open(vite_config_path, 'w') as f:
                f.write(vite_config)
            build_log.append("Generated vite.config.mts")

            # Run npm install
            build_log.append("Running npm install...")
            npm_install = subprocess.run(
                ['npm', 'install'],
                cwd=src_dir,
                capture_output=True,
                text=True,
                timeout=300
            )

            build_log.append(npm_install.stdout)
            if npm_install.returncode != 0:
                build_log.append(f"npm install stderr: {npm_install.stderr}")
                raise Exception(f"npm install failed: {npm_install.stderr}")

            # Run build
            build_log.append("Running npm run build...")
            npm_build = subprocess.run(
                ['npm', 'run', 'build'],
                cwd=src_dir,
                capture_output=True,
                text=True,
                timeout=300
            )

            build_log.append(npm_build.stdout)
            if npm_build.returncode != 0:
                build_log.append(f"npm build stderr: {npm_build.stderr}")
                raise Exception(f"Build failed: {npm_build.stderr}")

            # Read built files
            dist_dir = src_dir / "dist"
            js_path = dist_dir / f"{widget.name}.js"
            css_path = dist_dir / f"{widget.name}.css"

            if not js_path.exists():
                raise Exception(f"Built JS file not found: {js_path}")

            with open(js_path, 'r') as f:
                js_content = f.read()

            css_content = ""
            if css_path.exists():
                with open(css_path, 'r') as f:
                    css_content = f.read()

            # Generate HTML with references to separate CSS/JS files
            html_content = WidgetBuilder.generate_html_with_references(
                widget.widget_id,
                widget.name
            )

            # Generate hash based on combined content
            combined_content = f"{html_content}{css_content}{js_content}"
            hash_value = hashlib.sha256(combined_content.encode()).hexdigest()[:8]

            built_files = {
                'html': html_content,
                'css': css_content if css_content else "",
                'js': js_content,
                'hash': hash_value
            }

            build_log.append("Build completed successfully")

            return True, None, "\n".join(build_log), built_files

        except subprocess.TimeoutExpired:
            error_msg = "Build timeout (exceeded 5 minutes)"
            build_log.append(error_msg)
            return False, error_msg, "\n".join(build_log), None

        except Exception as e:
            error_msg = str(e)
            build_log.append(f"Build failed: {error_msg}")
            return False, error_msg, "\n".join(build_log), None


def generate_widget_meta(widget: Widget, custom_metadata: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Generate widget metadata for MCP tool call response

    Args:
        widget: Widget instance
        custom_metadata: Optional custom metadata override

    Returns:
        Widget metadata dictionary
    """
    metadata = widget.metadata

    return {
        "openai/outputTemplate": widget.template_uri,
        "openai/toolInvocation/invoking": custom_metadata.get('invoking_message') if custom_metadata else metadata.get('invoking_message', 'Loading widget...'),
        "openai/toolInvocation/invoked": custom_metadata.get('invoked_message') if custom_metadata else metadata.get('invoked_message', 'Widget ready'),
        "openai/widgetAccessible": metadata.get('widget_accessible', True),
        "openai/resultCanProduceWidget": metadata.get('result_can_produce_widget', True),
        "openai.com/widget": {
            "uri": widget.template_uri,
            "name": widget.name,
            "description": widget.description or f"{widget.name} widget",
            "mimeType": "text/html+skybridge"
        }
    }
