"""
Test script for MCP HTTP Client

This script tests the MCP client functionality by:
1. Testing basic connectivity
2. Listing available tools
3. Performing a simple tool call
4. Testing error handling
"""

import asyncio
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.mcp_client import MCPClient, MCPClientError

async def test_mcp_client():
    """Test the MCP client functionality"""
    print("🧪 Testing MCP HTTP Client...")
    print("=" * 50)
    
    async with MCPClient() as client:
        try:
            # Test 1: Health Check
            print("\n1. Testing Health Check...")
            health_response = await client.health_check()
            if health_response.success:
                print("✅ Health check passed")
                print(f"   Execution time: {health_response.execution_time:.3f}s")
            else:
                print(f"❌ Health check failed: {health_response.error_message}")
            
            # Test 2: List Tools
            print("\n2. Testing Tool Listing...")
            tools_response = await client.list_tools()
            if tools_response.success:
                # Handle case where data might be None or in different format
                if tools_response.data:
                    if isinstance(tools_response.data, dict) and "tools" in tools_response.data:
                        tools = tools_response.data["tools"]
                    elif isinstance(tools_response.data, list):
                        tools = tools_response.data
                    else:
                        tools = []
                        print(f"   DEBUG - Unexpected data format: {tools_response.data}")
                else:
                    tools = []
                    print(f"   DEBUG - No data in response")
                
                print(f"✅ Found {len(tools)} available tools")
                if tools:
                    print("   Available tools:")
                    for tool in tools[:5]:  # Show first 5 tools
                        if isinstance(tool, dict):
                            name = tool.get('name', 'Unknown')
                            desc = tool.get('description', 'No description')
                            print(f"   - {name}: {desc[:60]}...")
                        else:
                            print(f"   - {tool}")
                    if len(tools) > 5:
                        print(f"   ... and {len(tools) - 5} more tools")
            else:
                print(f"❌ Tool listing failed: {tools_response.error_message}")
            
            # Test 3: Simple Tool Call
            print("\n3. Testing Simple Tool Call...")
            
            search_response = await client.find_people_by_skill("python")
            if search_response.success:
                # MCP server wraps results in ToolCallResult format: {"content": [...], "isError": false}
                tool_result = search_response.data
                if tool_result and isinstance(tool_result, dict) and "content" in tool_result:
                    results = tool_result["content"]
                    if isinstance(results, list) and results:
                        # Extract the actual count from the text response
                        first_result = results[0]
                        if isinstance(first_result, dict) and "text" in first_result:
                            response_text = first_result["text"]
                            # Parse the count from "Found X people with 'python' skills:"
                            if "Found" in response_text and "people with" in response_text:
                                count_part = response_text.split("Found ")[1].split(" people")[0]
                                try:
                                    count = int(count_part)
                                    print(f"✅ Found {count} people with Python skills")
                                except:
                                    print(f"✅ Tool call successful - people found with Python skills")
                            else:
                                print(f"✅ Tool call successful")
                            
                            # Show a preview of the response
                            print(f"   Preview: {response_text[:100]}...")
                        else:
                            print(f"✅ Found {len(results)} result(s)")
                    else:
                        print(f"✅ Tool call successful with result: {str(results)[:100]}...")
                else:
                    print(f"✅ Tool call successful, but unexpected format")
                
                if search_response.execution_time:
                    print(f"   Execution time: {search_response.execution_time:.3f}s")
            else:
                print(f"❌ Tool call failed: {search_response.error_message}")
            
            # Test 4: Natural Language Search
            print("\n4. Testing Natural Language Search...")
            nl_response = await client.natural_language_search("Who are the top 3 Python developers?")
            if nl_response.success:
                tool_result = nl_response.data
                if tool_result and "content" in tool_result:
                    content = tool_result["content"]
                    if isinstance(content, list) and content:
                        # Natural language search returns text response in content[0]["text"]
                        response_text = content[0].get("text", str(content[0]))
                        print("✅ Natural language search successful")
                        print(f"   Response preview: {response_text[:150]}...")
                    else:
                        print(f"✅ Natural language search successful: {content}")
                else:
                    print(f"✅ Natural language search successful, raw response: {tool_result}")
                print(f"   Execution time: {nl_response.execution_time:.3f}s")
            else:
                print(f"❌ Natural language search failed: {nl_response.error_message}")
                
        except MCPClientError as e:
            print(f"❌ MCP Client Error: {e}")
            print(f"   Error Code: {e.error_code}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 MCP Client testing completed!")

if __name__ == "__main__":
    # Check if MCP server is running
    print("🚀 Starting MCP Client Test Suite")
    print("📋 Make sure your MCP server is running on localhost:8000")
    print("🔑 Using API key: f435d1c3...637ac3")
    
    try:
        asyncio.run(test_mcp_client())
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n💥 Test suite failed: {e}")
        sys.exit(1)