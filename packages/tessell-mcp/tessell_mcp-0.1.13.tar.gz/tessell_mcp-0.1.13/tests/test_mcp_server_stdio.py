import os
import subprocess
import json
import pytest
import time
import sys
import logging

# Import shared configuration from conftest.py
from conftest import TEST_SERVICE_ID

# Configure logging for this test module
logger = logging.getLogger(__name__)

# NOTE: This test file is not yet fully tested or verified.

@pytest.fixture(scope="module")
def mcp_server_proc():
    """Start the MCP server process for testing."""
    # Environment variables are already loaded from test_config.env by conftest.py
    # The MCP server will use the environment variables directly
    
    # Start the MCP server process
    proc = subprocess.Popen([
        sys.executable, "-m", "tessell_mcp.main"
    ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # Print initial stderr output for debugging
    if proc.stderr:
        for _ in range(10):
            err_line = proc.stderr.readline()
            if err_line:
                logger.info(f"Server stderr: {err_line.rstrip()}")
            else:
                break
    
    logger.info(f"MCP server process started, pid={proc.pid}, alive={proc.poll() is None}")
    
    # Give the server a moment to start up
    time.sleep(1)
    
    try:
        yield proc
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()

def send_request(proc, request):
    """Send a JSON request to the MCP server and return the response."""
    request_str = json.dumps(request) + "\n"
    proc.stdin.write(request_str)
    proc.stdin.flush()
    
    # Read response with timeout
    for _ in range(30):
        line = proc.stdout.readline()
        if not line:
            time.sleep(0.5)
            continue
        try:
            return json.loads(line)
        except json.JSONDecodeError as e:
            logger.warning(f"JSON decode error: {e}, line: {line!r}")
            continue
    
    raise TimeoutError("No response received from MCP server")

def test_list_tools_stdio(mcp_server_proc):
    """Test that the MCP server responds to list_tools request."""
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list"
    }
    
    try:
        response = send_request(mcp_server_proc, request)
        logger.info(f"List tools response: {response}")
        
        # Check if we got a valid response
        assert response.get("jsonrpc") == "2.0"
        assert response.get("id") == 1
        
        # Check if we have tools in the response
        result = response.get("result", {})
        tools = result.get("tools", [])
        
        # Verify we have some expected tools
        tool_names = [tool.get("name") for tool in tools]
        logger.info(f"Available tools: {tool_names}")
        
        # Check for expected tools
        expected_tools = ["get_availability_machine_id", "create_snapshot", "list_snapshots"]
        for expected_tool in expected_tools:
            assert any(expected_tool in tool_name for tool_name in tool_names), f"Expected tool {expected_tool} not found"
            
    except Exception as e:
        logger.error(f"List tools test failed: {e}")
        raise

def test_invoke_tool_stdio(mcp_server_proc):
    """Test that the MCP server can invoke a tool."""
    # First, let's test with a simple tool that doesn't require real API credentials
    request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "list_services",
            "arguments": {
                "page_size": 1
            }
        }
    }
    
    try:
        response = send_request(mcp_server_proc, request)
        logger.info(f"Invoke tool response: {response}")
        
        # Check if we got a valid response
        assert response.get("jsonrpc") == "2.0"
        assert response.get("id") == 2
        
        # The response should have a result or error
        if "result" in response:
            result = response["result"]
            logger.info(f"Tool result: {result}")
            # Tool was called successfully
            assert "content" in result or "status_code" in result
        elif "error" in response:
            error = response["error"]
            logger.warning(f"Tool error: {error}")
            # This is expected if API credentials are not valid
            assert error.get("code") in [-32603, -32000]  # Internal error or server error
            
    except Exception as e:
        logger.error(f"Invoke tool test failed: {e}")
        raise