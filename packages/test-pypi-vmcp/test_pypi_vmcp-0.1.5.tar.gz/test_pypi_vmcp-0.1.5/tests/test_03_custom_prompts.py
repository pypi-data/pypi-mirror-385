"""
Test Suite 3: Custom Prompts
Tests custom prompts with variables, tool calls, resources, and system variables
"""

import pytest
import requests
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


@pytest.mark.custom_prompts
class TestCustomPrompts:
    """Test custom prompts functionality"""

    def test_create_simple_prompt(self, base_url, create_vmcp, helpers):
        """Test 3.1: Create a simple custom prompt without variables"""
        vmcp = create_vmcp
        print(f"\n📦 Test 3.1 - Creating simple custom prompt: {vmcp['id']}")

        # Get vMCP data
        vmcp_data = helpers["get_vmcp"](vmcp["id"])

        # Add simple prompt
        simple_prompt = {
            "name": "simple_greeting",
            "description": "A simple greeting prompt",
            "text": "Say hello to the user in a friendly manner",
            "variables": [],
            "environment_variables": [],
            "tool_calls": []
        }

        vmcp_data["custom_prompts"].append(simple_prompt)

        # Update vMCP
        helpers["update_vmcp"](vmcp["id"], vmcp_data)

        # Verify
        updated_vmcp = helpers["get_vmcp"](vmcp["id"])
        assert len(updated_vmcp["custom_prompts"]) == 1
        assert updated_vmcp["custom_prompts"][0]["name"] == "simple_greeting"
        assert updated_vmcp["custom_prompts"][0]["text"] == "Say hello to the user in a friendly manner"

        print("✅ Simple prompt created successfully")

    @pytest.mark.asyncio
    async def test_list_custom_prompt(self, base_url, create_vmcp, helpers):
        """Test 3.2: List custom prompts via MCP"""
        vmcp = create_vmcp
        print(f"\n📦 Test 3.2 - Listing custom prompts via MCP: {vmcp['id']}")

        # Add a custom prompt
        vmcp_data = helpers["get_vmcp"](vmcp["id"])
        vmcp_data["custom_prompts"].append({
            "name": "test_prompt",
            "description": "Test prompt",
            "text": "This is a test prompt",
            "variables": [],
            "environment_variables": [],
            "tool_calls": []
        })
        helpers["update_vmcp"](vmcp["id"], vmcp_data)

        # Connect via MCP
        mcp_url = f"{base_url}private/{vmcp['name']}/vmcp"

        async with streamablehttp_client(mcp_url) as (read_stream, write_stream, _):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()

                # List prompts
                prompts_response = await session.list_prompts()
                prompt_names = [prompt.name for prompt in prompts_response.prompts]

                print(f"📋 Available prompts: {prompt_names}")

                assert "test_prompt" in prompt_names, "Custom prompt should be listed"

                print("✅ Custom prompt listed successfully")

    @pytest.mark.asyncio
    async def test_get_custom_prompt(self, base_url, create_vmcp, helpers):
        """Test 3.3: Get a custom prompt via MCP"""
        vmcp = create_vmcp
        print(f"\n📦 Test 3.3 - Getting custom prompt via MCP: {vmcp['id']}")

        # Add a custom prompt
        vmcp_data = helpers["get_vmcp"](vmcp["id"])
        vmcp_data["custom_prompts"].append({
            "name": "get_test_prompt",
            "description": "Prompt for testing get operation",
            "text": "Please analyze the following data carefully",
            "variables": [],
            "environment_variables": [],
            "tool_calls": []
        })
        helpers["update_vmcp"](vmcp["id"], vmcp_data)

        # Connect via MCP
        mcp_url = f"{base_url}private/{vmcp['name']}/vmcp"

        async with streamablehttp_client(mcp_url) as (read_stream, write_stream, _):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()

                # Get prompt
                result = await session.get_prompt("get_test_prompt")

                print(f"📋 Prompt result: {result}")

                # Verify
                assert len(result.messages) > 0
                prompt_text = result.messages[0].content.text
                assert "analyze" in prompt_text.lower()
                assert "data" in prompt_text.lower()

                print("✅ Custom prompt retrieved successfully")

    def test_create_prompt_with_variables(self, base_url, create_vmcp, helpers):
        """Test 3.4: Create prompt with @param variables"""
        vmcp = create_vmcp
        print(f"\n📦 Test 3.4 - Creating prompt with variables: {vmcp['id']}")

        # Get vMCP data
        vmcp_data = helpers["get_vmcp"](vmcp["id"])

        # Add prompt with variables
        prompt_with_vars = {
            "name": "greet_in_language",
            "description": "Greet user in specific language",
            "text": "Greet the user @param.name in @param.language language",
            "variables": [
                {"name": "name", "description": "User's name", "required": True},
                {"name": "language", "description": "Language for greeting", "required": True}
            ],
            "environment_variables": [],
            "tool_calls": []
        }

        vmcp_data["custom_prompts"].append(prompt_with_vars)
        helpers["update_vmcp"](vmcp["id"], vmcp_data)

        # Verify
        updated_vmcp = helpers["get_vmcp"](vmcp["id"])
        assert len(updated_vmcp["custom_prompts"]) == 1
        assert len(updated_vmcp["custom_prompts"][0]["variables"]) == 2

        print("✅ Prompt with variables created successfully")

    @pytest.mark.asyncio
    async def test_call_prompt_with_variables(self, base_url, create_vmcp, helpers):
        """Test 3.5: Call prompt with variable substitution"""
        vmcp = create_vmcp
        print(f"\n📦 Test 3.5 - Calling prompt with variables: {vmcp['id']}")

        # Add prompt with variables
        vmcp_data = helpers["get_vmcp"](vmcp["id"])
        vmcp_data["custom_prompts"].append({
            "name": "personalized_greeting",
            "description": "Personalized greeting",
            "text": "Hello @param.name, welcome to @param.location!",
            "variables": [
                {"name": "name", "description": "User's name", "required": True},
                {"name": "location", "description": "Location", "required": True}
            ],
            "environment_variables": [],
            "tool_calls": []
        })
        helpers["update_vmcp"](vmcp["id"], vmcp_data)

        # Connect via MCP
        mcp_url = f"{base_url}private/{vmcp['name']}/vmcp"

        async with streamablehttp_client(mcp_url) as (read_stream, write_stream, _):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()

                # Get prompt with arguments
                result = await session.get_prompt(
                    "personalized_greeting",
                    arguments={"name": "Alice", "location": "Wonderland"}
                )

                print(f"📋 Prompt result: {result}")

                # Verify variable substitution
                prompt_text = result.messages[0].content.text
                assert "Alice" in prompt_text, f"Expected 'Alice' in prompt, got: {prompt_text}"
                assert "Wonderland" in prompt_text, f"Expected 'Wonderland' in prompt, got: {prompt_text}"

                print("✅ Prompt with variable substitution successful")

    def test_create_prompt_with_config_variables(self, base_url, create_vmcp, helpers):
        """Test 3.6: Create prompt with @config system variables"""
        vmcp = create_vmcp
        print(f"\n📦 Test 3.6 - Creating prompt with config variables: {vmcp['id']}")

        # First, add environment variables to vMCP
        vmcp_data = helpers["get_vmcp"](vmcp["id"])
        vmcp_data["environment_variables"] = [
            {"name": "api_key", "value": "test-api-key-123"},
            {"name": "base_url", "value": "https://api.example.com"}
        ]

        # Add prompt with config variables
        prompt_with_config = {
            "name": "api_request_prompt",
            "description": "Prompt using API configuration",
            "text": "Make a request to @config.base_url using API key @config.api_key",
            "variables": [],
            "environment_variables": ["api_key", "base_url"],
            "tool_calls": []
        }

        vmcp_data["custom_prompts"].append(prompt_with_config)
        helpers["update_vmcp"](vmcp["id"], vmcp_data)

        # Verify
        updated_vmcp = helpers["get_vmcp"](vmcp["id"])
        assert len(updated_vmcp["custom_prompts"]) == 1
        assert len(updated_vmcp["custom_prompts"][0]["environment_variables"]) == 2

        print("✅ Prompt with config variables created successfully")

    @pytest.mark.asyncio
    async def test_call_prompt_with_config_variables(self, base_url, create_vmcp, helpers):
        """Test 3.7: Call prompt with config variable substitution"""
        vmcp = create_vmcp
        print(f"\n📦 Test 3.7 - Calling prompt with config variables: {vmcp['id']}")

        # Save environment variables using the proper endpoint
        helpers["save_env_vars"](vmcp["id"], [
            {"name": "service_name", "value": "TestService"},
            {"name": "version", "value": "1.0.0"}
        ])

        # Add prompt with config variables
        vmcp_data = helpers["get_vmcp"](vmcp["id"])
        vmcp_data["custom_prompts"].append({
            "name": "system_info_prompt",
            "description": "System info prompt",
            "text": "Connect to @config.service_name version @config.version",
            "variables": [],
            "environment_variables": ["service_name", "version"],
            "tool_calls": []
        })
        helpers["update_vmcp"](vmcp["id"], vmcp_data)

        # Connect via MCP
        mcp_url = f"{base_url}private/{vmcp['name']}/vmcp"

        async with streamablehttp_client(mcp_url) as (read_stream, write_stream, _):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()

                # Get prompt
                result = await session.get_prompt("system_info_prompt")

                print(f"📋 Prompt result: {result}")

                # Verify config variable substitution
                prompt_text = result.messages[0].content.text
                assert "TestService" in prompt_text, f"Expected 'TestService' in prompt, got: {prompt_text}"
                assert "1.0.0" in prompt_text, f"Expected '1.0.0' in prompt, got: {prompt_text}"

                print("✅ Prompt with config variable substitution successful")

    def test_create_prompt_with_tool_call(self, base_url, create_vmcp, mcp_servers, helpers):
        """Test 3.8: Create prompt with @tool call"""
        vmcp = create_vmcp
        print(f"\n📦 Test 3.8 - Creating prompt with tool call: {vmcp['id']}")

        # Add MCP server first
        helpers["add_server"](vmcp["id"], mcp_servers["allfeature"], "allfeature")

        # Get vMCP data
        vmcp_data = helpers["get_vmcp"](vmcp["id"])

        # Add prompt with tool call
        prompt_with_tool = {
            "name": "weather_analysis_prompt",
            "description": "Analyze weather data",
            "text": "Get the current weather: @tool.get_weather(city='London') and analyze it",
            "variables": [],
            "environment_variables": [],
            "tool_calls": [
                {"tool": "get_weather", "arguments": {"city": "London"}}
            ]
        }

        vmcp_data["custom_prompts"].append(prompt_with_tool)
        helpers["update_vmcp"](vmcp["id"], vmcp_data)

        # Verify
        updated_vmcp = helpers["get_vmcp"](vmcp["id"])
        assert len(updated_vmcp["custom_prompts"]) == 1
        assert len(updated_vmcp["custom_prompts"][0]["tool_calls"]) == 1

        print("✅ Prompt with tool call created successfully")

    def test_create_prompt_with_prompt_reference(self, base_url, create_vmcp, helpers):
        """Test 3.9: Create prompt that references another prompt"""
        vmcp = create_vmcp
        print(f"\n📦 Test 3.9 - Creating prompt with prompt reference: {vmcp['id']}")

        # Get vMCP data
        vmcp_data = helpers["get_vmcp"](vmcp["id"])

        # Add base prompt
        vmcp_data["custom_prompts"].append({
            "name": "base_greeting",
            "description": "Base greeting",
            "text": "Hello, welcome!",
            "variables": [],
            "environment_variables": [],
            "tool_calls": []
        })

        # Add prompt that references base prompt
        vmcp_data["custom_prompts"].append({
            "name": "extended_greeting",
            "description": "Extended greeting with base",
            "text": "@prompt.base_greeting Now let me help you with your questions.",
            "variables": [],
            "environment_variables": [],
            "tool_calls": []
        })

        helpers["update_vmcp"](vmcp["id"], vmcp_data)

        # Verify
        updated_vmcp = helpers["get_vmcp"](vmcp["id"])
        assert len(updated_vmcp["custom_prompts"]) == 2
        assert "@prompt.base_greeting" in updated_vmcp["custom_prompts"][1]["text"]

        print("✅ Prompt with prompt reference created successfully")

    def test_create_prompt_with_resource(self, base_url, create_vmcp, mcp_servers, helpers):
        """Test 3.10: Create prompt with @resource reference"""
        vmcp = create_vmcp
        print(f"\n📦 Test 3.10 - Creating prompt with resource reference: {vmcp['id']}")

        # Add MCP server
        helpers["add_server"](vmcp["id"], mcp_servers["everything"], "everything")

        # Get vMCP data
        vmcp_data = helpers["get_vmcp"](vmcp["id"])

        # Add prompt with resource
        prompt_with_resource = {
            "name": "dashboard_analysis_prompt",
            "description": "Analyze dashboard data",
            "text": "Analyze the following dashboard data: @resource.everything://dashboard",
            "variables": [],
            "environment_variables": [],
            "tool_calls": []
        }

        vmcp_data["custom_prompts"].append(prompt_with_resource)
        helpers["update_vmcp"](vmcp["id"], vmcp_data)

        # Verify
        updated_vmcp = helpers["get_vmcp"](vmcp["id"])
        assert len(updated_vmcp["custom_prompts"]) == 1
        assert "@resource.everything://dashboard" in updated_vmcp["custom_prompts"][0]["text"]

        print("✅ Prompt with resource reference created successfully")

    def test_create_complex_prompt(self, base_url, create_vmcp, mcp_servers, helpers):
        """Test 3.11: Create prompt with all features combined"""
        vmcp = create_vmcp
        print(f"\n📦 Test 3.11 - Creating complex prompt with all features: {vmcp['id']}")

        # Add MCP server
        helpers["add_server"](vmcp["id"], mcp_servers["allfeature"], "allfeature")

        # Add environment variables
        vmcp_data = helpers["get_vmcp"](vmcp["id"])
        vmcp_data["environment_variables"] = [
            {"name": "default_city", "value": "London"}
        ]

        # Add complex prompt
        complex_prompt = {
            "name": "comprehensive_analysis",
            "description": "Comprehensive analysis with all features",
            "text": """Analyze the following:
User: @param.user_name
City: @config.default_city
Weather: @tool.get_weather(city=@param.city)
Additional Info: @param.details""",
            "variables": [
                {"name": "user_name", "description": "User's name", "required": True},
                {"name": "city", "description": "City name", "required": False},
                {"name": "details", "description": "Additional details", "required": False}
            ],
            "environment_variables": ["default_city"],
            "tool_calls": [
                {"tool": "get_weather", "arguments": {"city": "@param.city"}}
            ]
        }

        vmcp_data["custom_prompts"].append(complex_prompt)
        helpers["update_vmcp"](vmcp["id"], vmcp_data)

        # Verify
        updated_vmcp = helpers["get_vmcp"](vmcp["id"])
        assert len(updated_vmcp["custom_prompts"]) == 1
        prompt = updated_vmcp["custom_prompts"][0]
        assert len(prompt["variables"]) == 3
        assert len(prompt["environment_variables"]) == 1
        assert len(prompt["tool_calls"]) == 1

        print("✅ Complex prompt with all features created successfully")
