"""
Test Suite 2: MCP Server Integration
Tests adding MCP servers and verifying tools, resources, and prompts
"""

import pytest
import requests
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


@pytest.mark.mcp_server
class TestMCPServerIntegration:
    """Test MCP server integration functionality"""

    def test_add_everything_server(self, base_url, create_vmcp, mcp_servers, helpers):
        """Test 2.1: Add Everything MCP server to vMCP"""
        vmcp = create_vmcp
        print(f"\n📦 Test 2.1 - Adding Everything server to vMCP: {vmcp['id']}")

        result = helpers["add_server"](
            vmcp["id"],
            mcp_servers["everything"],
            "everything"
        )

        assert result is not None
        print("✅ Everything server added successfully")

    def test_add_allfeature_server(self, base_url, create_vmcp, mcp_servers, helpers):
        """Test 2.2: Add AllFeature MCP server to vMCP"""
        vmcp = create_vmcp
        print(f"\n📦 Test 2.2 - Adding AllFeature server to vMCP: {vmcp['id']}")

        result = helpers["add_server"](
            vmcp["id"],
            mcp_servers["allfeature"],
            "allfeature"
        )

        assert result is not None
        print("✅ AllFeature server added successfully")

    @pytest.mark.asyncio
    async def test_verify_tools_from_mcp_server(self, base_url, create_vmcp, mcp_servers, helpers):
        """Test 2.3: Verify tools are accessible from MCP server"""
        vmcp = create_vmcp
        print(f"\n📦 Test 2.3 - Verifying tools from MCP server: {vmcp['id']}")

        # Add server
        helpers["add_server"](vmcp["id"], mcp_servers["everything"], "everything")

        # Connect via MCP client
        mcp_url = f"{base_url}private/{vmcp['name']}/vmcp"

        async with streamablehttp_client(mcp_url) as (read_stream, write_stream, _):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()

                # List tools
                tools_response = await session.list_tools()
                tool_names = [tool.name for tool in tools_response.tools]

                print(f"🔧 Available tools: {tool_names}")

                # Verify some expected tools exist (tools are prefixed with server name)
                expected_tools = ["everything_create_task", "everything_search_everything", "everything_generate_report"]
                for expected_tool in expected_tools:
                    assert expected_tool in tool_names, f"Expected tool '{expected_tool}' not found"

                print(f"✅ Verified {len(tool_names)} tools available")

    @pytest.mark.asyncio
    async def test_verify_prompts_from_mcp_server(self, base_url, create_vmcp, mcp_servers, helpers):
        """Test 2.4: Verify prompts are accessible from MCP server"""
        vmcp = create_vmcp
        print(f"\n📦 Test 2.4 - Verifying prompts from MCP server: {vmcp['id']}")

        # Add server
        helpers["add_server"](vmcp["id"], mcp_servers["everything"], "everything")

        # Connect via MCP client
        mcp_url = f"{base_url}private/{vmcp['name']}/vmcp"

        async with streamablehttp_client(mcp_url) as (read_stream, write_stream, _):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()

                # List prompts
                prompts_response = await session.list_prompts()
                prompt_names = [prompt.name for prompt in prompts_response.prompts]

                print(f"📋 Available prompts: {prompt_names}")

                # Verify some expected prompts exist (prompts are prefixed with server name)
                expected_prompts = ["everything_system_administration_prompt", "everything_data_analysis_prompt"]
                for expected_prompt in expected_prompts:
                    assert expected_prompt in prompt_names, f"Expected prompt '{expected_prompt}' not found"

                print(f"✅ Verified {len(prompt_names)} prompts available")

    @pytest.mark.asyncio
    async def test_verify_resources_from_mcp_server(self, base_url, create_vmcp, mcp_servers, helpers):
        """Test 2.5: Verify resources are accessible from MCP server"""
        vmcp = create_vmcp
        print(f"\n📦 Test 2.5 - Verifying resources from MCP server: {vmcp['id']}")

        # Add server
        helpers["add_server"](vmcp["id"], mcp_servers["everything"], "everything")

        # Connect via MCP client
        mcp_url = f"{base_url}private/{vmcp['name']}/vmcp"

        async with streamablehttp_client(mcp_url) as (read_stream, write_stream, _):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()

                # List resources
                resources_response = await session.list_resources()
                resource_uris = [resource.uri for resource in resources_response.resources]

                print(f"📚 Available resources: {resource_uris}")

                # Verify we have some resources
                assert len(resource_uris) > 0, "Expected at least one resource"

                print(f"✅ Verified {len(resource_uris)} resources available")

    @pytest.mark.asyncio
    async def test_call_mcp_tool(self, base_url, create_vmcp, mcp_servers, helpers):
        """Test 2.6: Call a tool from MCP server"""
        vmcp = create_vmcp
        print(f"\n📦 Test 2.6 - Calling MCP tool: {vmcp['id']}")

        # Add server
        helpers["add_server"](vmcp["id"], mcp_servers["allfeature"], "allfeature")

        # Connect via MCP client
        mcp_url = f"{base_url}private/{vmcp['name']}/vmcp"

        async with streamablehttp_client(mcp_url) as (read_stream, write_stream, _):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()

                # Call add tool (tool names are prefixed with server name)
                result = await session.call_tool("allfeature_add", arguments={"a": 5, "b": 3})

                print(f"🔧 Tool result: {result}")

                # Verify result
                assert len(result.content) > 0
                result_text = result.content[0].text
                assert "8" in result_text, f"Expected result to contain '8', got: {result_text}"

                print("✅ Tool call successful")

    @pytest.mark.asyncio
    async def test_get_mcp_prompt(self, base_url, create_vmcp, mcp_servers, helpers):
        """Test 2.7: Get a prompt from MCP server"""
        vmcp = create_vmcp
        print(f"\n📦 Test 2.7 - Getting MCP prompt: {vmcp['id']}")

        # Add server
        helpers["add_server"](vmcp["id"], mcp_servers["allfeature"], "allfeature")

        # Connect via MCP client
        mcp_url = f"{base_url}private/{vmcp['name']}/vmcp"

        async with streamablehttp_client(mcp_url) as (read_stream, write_stream, _):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()

                # Get prompt (prompt names are prefixed with server name)
                result = await session.get_prompt("allfeature_greet_user", arguments={"name": "Alice", "style": "friendly"})

                print(f"📋 Prompt result: {result}")

                # Verify result
                assert len(result.messages) > 0
                prompt_text = result.messages[0].content.text
                assert "Alice" in prompt_text, f"Expected prompt to contain 'Alice', got: {prompt_text}"
                assert "friendly" in prompt_text or "warm" in prompt_text

                print("✅ Prompt retrieval successful")
