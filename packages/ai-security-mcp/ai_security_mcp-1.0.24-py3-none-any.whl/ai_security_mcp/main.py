#!/usr/bin/env python3
"""
AI Security MCP Thin Client
Lightweight proxy that connects Claude Code to cloud MCP server
"""

import asyncio
import json
import logging
import os
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger(__name__)

# Cloud MCP server URL
CLOUD_MCP_URL = os.getenv(
    'AI_SECURITY_MCP_URL',
    'https://ai-security-mcp-fastmcp-production-722116092626.us-central1.run.app/mcp'
)

# User's API key from environment
API_KEY = os.getenv('AI_SECURITY_API_KEY')

class ThinMCPClient:
    """Thin MCP client that forwards requests to cloud server"""

    def __init__(self, cloud_url: str, api_key: str):
        self.cloud_url = cloud_url
        self.api_key = api_key
        self.session_id = None

    async def initialize_session(self):
        """Initialize MCP session with cloud server"""
        try:
            # Import MCP SDK dynamically to handle missing dependency gracefully
            try:
                from mcp.client.streamable_http import streamablehttp_client
                from mcp import ClientSession
            except ImportError:
                logger.error("MCP SDK not installed. Please install: pip install mcp")
                raise

            # Connect to cloud MCP server via streamable HTTP
            logger.info(f"Connecting to cloud MCP server: {self.cloud_url}")

            async with streamablehttp_client(
                self.cloud_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
            ) as (read_stream, write_stream, _):
                # Create MCP session
                async with ClientSession(read_stream, write_stream) as session:
                    # Don't initialize here - wait for JSON-RPC initialize request from Claude Code
                    logger.info("Cloud MCP session created, waiting for initialize request")

                    # Keep session alive and handle requests
                    await self.handle_stdio_loop(session)

        except Exception as e:
            logger.error(f"Failed to initialize cloud MCP session: {str(e)}")
            raise

    async def handle_stdio_loop(self, session):
        """Handle MCP protocol over stdio - read from stdin, write to stdout"""
        logger.info("Starting stdio loop for MCP protocol")

        try:
            while True:
                # Read JSON-RPC request from stdin (from Claude Code)
                line = await asyncio.get_event_loop().run_in_executor(
                    None, sys.stdin.readline
                )

                if not line:
                    logger.info("EOF received, closing connection")
                    break

                try:
                    request = json.loads(line.strip())
                    logger.debug(f"Received request: {request.get('method', 'unknown')}")

                    # Forward request to cloud MCP server via session
                    response = await self.forward_request(session, request)

                    # Return response to Claude Code via stdout
                    print(json.dumps(response), flush=True)

                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON received: {e}")
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {
                            "code": -32700,
                            "message": "Parse error",
                            "data": str(e)
                        }
                    }
                    print(json.dumps(error_response), flush=True)

                except Exception as e:
                    logger.error(f"Error handling request: {e}")
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": request.get("id") if 'request' in locals() else None,
                        "error": {
                            "code": -32603,
                            "message": "Internal error",
                            "data": str(e)
                        }
                    }
                    print(json.dumps(error_response), flush=True)

        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        except Exception as e:
            logger.error(f"Stdio loop error: {e}")
        finally:
            logger.info("Stdio loop terminated")

    async def forward_request(self, session, request: dict) -> dict:
        """Forward MCP request to cloud server and return response"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")

        try:
            # Handle different MCP methods
            if method == "initialize":
                result = await session.initialize()
            elif method == "tools/list":
                result = await session.list_tools()
            elif method == "tools/call":
                tool_name = params.get("name")
                tool_args = params.get("arguments", {})
                result = await session.call_tool(tool_name, tool_args)
            elif method == "prompts/list":
                result = await session.list_prompts()
            elif method == "resources/list":
                result = await session.list_resources()
            else:
                # Unknown method - return error
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }

            # Convert result to dict if it's a Pydantic model
            if hasattr(result, 'model_dump'):
                result_dict = result.model_dump()
            elif hasattr(result, 'dict'):
                result_dict = result.dict()
            else:
                result_dict = result

            # Return successful response
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result_dict
            }

        except Exception as e:
            logger.error(f"Error calling cloud MCP method {method}: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Cloud MCP error: {str(e)}"
                }
            }


def validate_environment():
    """Validate required environment variables"""
    if not API_KEY:
        logger.error("AI_SECURITY_API_KEY environment variable is required")
        print("\n" + "="*60, file=sys.stderr)
        print("ERROR: API Key Required", file=sys.stderr)
        print("="*60, file=sys.stderr)
        print("\nThe AI Security MCP thin client requires an API key.", file=sys.stderr)
        print("\nSteps to get your API key:", file=sys.stderr)
        print("1. Visit: https://app.ai-threat-scanner.com/dashboard/api-keys", file=sys.stderr)
        print("2. Generate a new API key", file=sys.stderr)
        print("3. Set environment variable:", file=sys.stderr)
        print("   export AI_SECURITY_API_KEY=ciso_live_your_key_here", file=sys.stderr)
        print("\nOr configure Claude Code:", file=sys.stderr)
        print("   claude mcp add ai-security-scanner \\", file=sys.stderr)
        print("     -e AI_SECURITY_API_KEY=ciso_live_your_key_here \\", file=sys.stderr)
        print("     -- uvx ai-security-mcp", file=sys.stderr)
        print("\n" + "="*60, file=sys.stderr)
        sys.exit(1)

    logger.info("Environment validation passed")
    logger.info(f"Using cloud MCP server: {CLOUD_MCP_URL}")
    logger.info(f"API key configured: {API_KEY[:15]}...")


def main():
    """Main entry point for the thin client"""
    logger.info("AI Security MCP Thin Client starting...")

    # Validate environment
    validate_environment()

    try:
        # Create thin client
        client = ThinMCPClient(
            cloud_url=CLOUD_MCP_URL,
            api_key=API_KEY
        )

        # Start async event loop
        asyncio.run(client.initialize_session())

    except KeyboardInterrupt:
        logger.info("Thin client stopped by user")
    except Exception as e:
        logger.error(f"Thin client failed: {str(e)}")
        sys.exit(1)

    logger.info("AI Security MCP Thin Client terminated")


if __name__ == "__main__":
    main()
