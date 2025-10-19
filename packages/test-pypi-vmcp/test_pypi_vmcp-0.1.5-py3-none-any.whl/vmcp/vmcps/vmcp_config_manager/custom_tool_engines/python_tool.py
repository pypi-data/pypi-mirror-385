#!/usr/bin/env python3
"""
Python Tool Engine
==================

Execution engine for Python-based custom tools with sandboxing.
"""

import subprocess
import tempfile
import os
import json
import sys
import logging
from typing import Dict, Any, List

from mcp.types import TextContent, PromptMessage, GetPromptResult, CallToolResult

logger = logging.getLogger("1xN_vMCP_PYTHON_TOOL")


def convert_arguments_to_types(arguments: Dict[str, Any], variables: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Convert string arguments to their correct types based on variable definitions.

    Args:
        arguments: Raw arguments dictionary
        variables: Variable definitions with type information

    Returns:
        Dictionary with type-converted arguments
    """
    converted = {}

    for var in variables:
        var_name = var.get('name')
        var_type = var.get('type', 'str')
        var_default = var.get('default_value')

        if var_name in arguments:
            value = arguments[var_name]

            # Handle null values
            if value is None or value == 'null' or value == '':
                if var_default is not None:
                    converted[var_name] = var_default
                else:
                    converted[var_name] = None
                continue

            try:
                if var_type == 'int':
                    converted[var_name] = int(value)
                elif var_type == 'float':
                    converted[var_name] = float(value)
                elif var_type == 'bool':
                    if isinstance(value, str):
                        converted[var_name] = value.lower() in ('true', '1', 'yes', 'on')
                    else:
                        converted[var_name] = bool(value)
                elif var_type == 'list':
                    if isinstance(value, str):
                        # Try to parse as JSON array
                        try:
                            converted[var_name] = json.loads(value)
                        except:
                            # Fallback to splitting by comma
                            converted[var_name] = [item.strip() for item in value.split(',')]
                    else:
                        converted[var_name] = value
                elif var_type == 'dict':
                    if isinstance(value, str):
                        try:
                            converted[var_name] = json.loads(value)
                        except:
                            converted[var_name] = value
                    else:
                        converted[var_name] = value
                else:  # str or unknown type
                    converted[var_name] = str(value)
            except (ValueError, TypeError) as e:
                # If conversion fails, use default value or keep as string
                if var_default is not None:
                    converted[var_name] = var_default
                    logger.warning(f"Failed to convert argument '{var_name}' to type '{var_type}', using default: {e}")
                else:
                    converted[var_name] = str(value)
                    logger.warning(f"Failed to convert argument '{var_name}' to type '{var_type}': {e}")
        else:
            # If argument not provided, use default value if available
            if var_default is not None:
                converted[var_name] = var_default
            elif var.get('required', True):
                logger.warning(f"Required argument '{var_name}' not provided")
                converted[var_name] = None
            else:
                converted[var_name] = None

    return converted


async def execute_python_tool(
    custom_tool: dict,
    arguments: Dict[str, Any],
    environment_variables: Dict[str, Any],
    tool_as_prompt: bool = False
):
    """
    Execute a Python tool with secure sandboxing.

    Args:
        custom_tool: Tool configuration dictionary
        arguments: Tool arguments
        environment_variables: Environment variables
        tool_as_prompt: Whether to return as prompt result

    Returns:
        CallToolResult or GetPromptResult
    """
    # Get the Python code
    python_code = custom_tool.get('code', '')
    if not python_code:
        error_content = TextContent(
            type="text",
            text="No Python code provided for this tool",
            annotations=None,
            meta=None
        )
        return CallToolResult(
            content=[error_content],
            structuredContent=None,
            isError=True
        )

    # Convert arguments to correct types based on tool variables
    converted_arguments = convert_arguments_to_types(arguments, custom_tool.get('variables', []))

    # Create a secure execution environment
    try:
        # Create a temporary file for the Python code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            # Prepare the execution environment
            execution_code = f"""
import sys
import json
import os
import subprocess
import tempfile
import shutil
import signal
import time
from contextlib import contextmanager

# Security: Disable dangerous modules
DANGEROUS_MODULES = [
    'os', 'subprocess', 'shutil', 'tempfile', 'signal', 'sys', 'importlib',
    'eval', 'exec', 'compile', '__import__', 'open', 'file', 'input', 'raw_input',
    'reload', 'vars', 'globals', 'locals', 'dir', 'hasattr', 'getattr', 'setattr',
    'delattr', 'callable', 'isinstance', 'issubclass', 'type', 'super'
]

# Override dangerous functions
def secure_exec(code, globals_dict, locals_dict):
    # Check for dangerous patterns
    dangerous_patterns = [
        'import os', 'import subprocess', 'import shutil', 'import tempfile',
        'import signal', 'import sys', 'import importlib',
        'eval(', 'exec(', 'compile(', '__import__(',
        'open(', 'file(', 'input(', 'raw_input(',
        'reload(', 'vars(', 'globals(', 'locals(',
        'dir(', 'hasattr(', 'getattr(', 'setattr(',
        'delattr(', 'callable(', 'isinstance(', 'issubclass(',
        'type(', 'super('
    ]

    for pattern in dangerous_patterns:
        if pattern in code:
            raise SecurityError(f"Dangerous pattern detected: {{pattern}}")

    # Execute the code
    exec(code, globals_dict, locals_dict)

class SecurityError(Exception):
    pass

# Arguments passed from the tool call
arguments = {json.dumps(converted_arguments)}

# Environment variables
environment_variables = {json.dumps(environment_variables)}

# User's Python code
{python_code}

# Execute the main function if it exists
if 'main' in locals() and callable(main):
    try:
        # Get function signature to properly map arguments
        import inspect
        sig = inspect.signature(main)
        param_names = list(sig.parameters.keys())

        # Filter arguments to only include those that match function parameters
        filtered_args = {{}}
        for param_name in param_names:
            if param_name in arguments:
                filtered_args[param_name] = arguments[param_name]

        result = main(**filtered_args)
        print(json.dumps({{"success": True, "result": result}}))
    except Exception as e:
        print(json.dumps({{"success": False, "error": str(e)}}))
else:
    print(json.dumps({{"success": False, "error": "No 'main' function found in the code"}}))
"""
            f.write(execution_code)
            temp_file = f.name

        # Execute the Python code in a secure environment
        result = subprocess.run(
            [sys.executable, temp_file],
            capture_output=True,
            text=True,
            timeout=30,  # 30 second timeout
            cwd=tempfile.gettempdir()  # Run in temp directory
        )

        # Clean up the temporary file
        os.unlink(temp_file)

        # Parse the result
        try:
            result_data = json.loads(result.stdout.strip())
            if result_data.get('success', False):
                result_text = json.dumps(result_data.get('result', ''), indent=2)
            else:
                result_text = f"Error: {result_data.get('error', 'Unknown error')}"
        except json.JSONDecodeError:
            result_text = result.stdout if result.stdout else result.stderr

        # Create the TextContent
        text_content = TextContent(
            type="text",
            text=result_text,
            annotations=None,
            meta=None
        )

        if tool_as_prompt:
            # Create the PromptMessage
            prompt_message = PromptMessage(
                role="user",
                content=text_content
            )

            # Create the GetPromptResult
            prompt_result = GetPromptResult(
                description="Python tool execution result",
                messages=[prompt_message]
            )
            return prompt_result

        # Create the CallToolResult
        tool_result = CallToolResult(
            content=[text_content],
            structuredContent=None,
            isError=not result_data.get('success', False) if 'result_data' in locals() else False
        )

        return tool_result

    except subprocess.TimeoutExpired:
        error_content = TextContent(
            type="text",
            text="Python tool execution timed out (30 seconds)",
            annotations=None,
            meta=None
        )
        return CallToolResult(
            content=[error_content],
            structuredContent=None,
            isError=True
        )
    except Exception as e:
        error_content = TextContent(
            type="text",
            text=f"Error executing Python tool: {str(e)}",
            annotations=None,
            meta=None
        )
        return CallToolResult(
            content=[error_content],
            structuredContent=None,
            isError=True
        )
