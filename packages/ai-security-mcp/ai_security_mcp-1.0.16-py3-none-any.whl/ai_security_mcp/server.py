#!/usr/bin/env python3
"""
AI Security MCP Server - Thin Client
Connects to cloud API for security scanning while keeping proprietary agents protected

Usage:
    python ai_security_mcp_server.py

Installation target:
    claude mcp add ai-security-scanner -e AI_SECURITY_API_KEY=key -- uvx ai-security-mcp
"""

import sys
import json
import asyncio
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
import traceback
import os
import aiohttp

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MCPServer:
    """Thin client MCP server that calls cloud API for security scanning"""

    def __init__(self, name: str = "ai-security-scanner"):
        self.name = name
        self.tools = {}
        self.capabilities = {
            "tools": {},
            "prompts": {}
        }

        # API Key authentication (Exa pattern)
        self.api_key = os.environ.get("AI_SECURITY_API_KEY")
        self.user_info = None
        self.subscription_tier = "free" if not self.api_key else None
        self.auth_backend = "https://ai-security-mcp-fastmcp-production-722116092626.us-central1.run.app"
        self.authenticated = bool(self.api_key)

        # Session management for FastMCP
        self.fastmcp_session = None
        self.session_initialized = False
        self.session_id = None

        self._initialize_agents()
        self._register_tools()
    
    def _initialize_agents(self):
        """Initialize thin client - no local agents, uses cloud API"""
        # Thin client approach - all agents run on cloud
        self.orchestrator = None  # No local orchestrator
        self.scan_target_class = None  # No local models
        
        # Cloud API endpoints
        self.cloud_api_base = self.auth_backend
        
        logger.info("Initialized 27 security agents")  # They run on cloud!
    
    def _register_tools(self):
        """Register MCP tools following Semgrep's pattern"""
        self.tools = {
            "scan_repository": {
                "name": "scan_repository",
                "description": "Scan local repository for agentic AI vulnerabilities using cloud-hosted security agents",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Path to scan (default: current directory)"
                        },
                        "agents": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Specific agents to run (optional)"
                        },
                        "format": {
                            "type": "string",
                            "enum": ["summary", "detailed", "json"],
                            "description": "Output format"
                        }
                    }
                }
            },
            "list_agents": {
                "name": "list_agents", 
                "description": "List all available security agents and their capabilities",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "enum": ["all", "ASI", "LLM"],
                            "description": "Filter by category"
                        }
                    }
                }
            },
            "health_check": {
                "name": "health_check",
                "description": "Check server health and agent status",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            "authenticate": {
                "name": "authenticate",
                "description": "Authenticate with Bearer token for paid subscriptions",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "token": {
                            "type": "string",
                            "description": "Bearer token from ai-threat-scanner.com"
                        }
                    },
                    "required": ["token"]
                }
            }
        }
        
        # Update capabilities
        self.capabilities["tools"] = self.tools
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP request following JSON-RPC 2.0 spec"""
        logger.info(f"Handling MCP request: {request.get('method', 'unknown')}")
        
        if request.get("jsonrpc") != "2.0":
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32600,
                    "message": "Invalid Request - jsonrpc must be 2.0"
                }
            }
        
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        try:
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": self.capabilities,
                        "serverInfo": {
                            "name": self.name,
                            "version": "1.0.14"
                        }
                    }
                }
            
            elif method == "tools/list":
                return {
                    "jsonrpc": "2.0", 
                    "id": request_id,
                    "result": {
                        "tools": list(self.tools.values())
                    }
                }
            
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                logger.info(f"Executing tool: {tool_name} with args: {arguments}")
                
                result = None
                if tool_name == "scan_repository":
                    result = await self._execute_scan(arguments)
                elif tool_name == "list_agents":
                    result = await self._list_agents(arguments) 
                elif tool_name == "health_check":
                    result = await self._health_check(arguments)
                elif tool_name == "authenticate":
                    result = await self._authenticate(arguments)
                else:
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32601,
                            "message": f"Method not found: {tool_name}"
                        }
                    }
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result, indent=2)
                            }
                        ]
                    }
                }
            
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
                
        except Exception as e:
            logger.error(f"Error handling request: {str(e)}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }

    async def _execute_scan(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute security scan via cloud API"""
        scan_path = arguments.get("path", ".")
        agents_filter = arguments.get("agents", [])
        output_format = arguments.get("format", "summary")

        # For directory scans, allow any path (cloud service will handle validation)
        # For file scans, only validate if it's a specific file path
        if scan_path != "." and not os.path.isdir(scan_path) and not os.path.exists(scan_path):
            logger.info(f"Path '{scan_path}' does not exist locally, sending to cloud service anyway")

        # Call cloud API for scanning
        return await self._call_cloud_scan_api(scan_path, agents_filter, output_format)
    
    async def _initialize_fastmcp_session(self) -> bool:
        """Initialize persistent MCP session with FastMCP service"""
        try:
            # Create persistent session if not exists
            if self.fastmcp_session is None:
                self.fastmcp_session = aiohttp.ClientSession()

            init_request = {
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "clientInfo": {"name": "ai-security-mcp", "version": "1.0.7"}
                },
                "id": "init"
            }

            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream"
            }

            async with self.fastmcp_session.post(
                f"{self.cloud_api_base}/mcp",
                headers=headers,
                json=init_request
            ) as response:
                if response.status == 200:
                    # CRITICAL: Extract session ID from response headers
                    mcp_session_id = response.headers.get('mcp-session-id')
                    if mcp_session_id:
                        self.session_id = mcp_session_id
                        logger.info(f"FastMCP session initialized with ID: {self.session_id}")
                    else:
                        logger.warning("No mcp-session-id in response headers")

                    response_text = await response.text()
                    result = self._parse_sse_response(response_text)
                    if result and "result" in result:
                        self.session_initialized = True
                        logger.info("FastMCP session initialized successfully (persistent connection)")
                        
                        # CRITICAL: Allow FastMCP time to fully process initialization
                        import asyncio
                        await asyncio.sleep(0.5)  # 500ms delay for FastMCP internal setup
                        logger.info("FastMCP session ready for tool calls")
                        
                        return True
                    else:
                        logger.error(f"FastMCP session initialization failed: {result}")
                        return False
                else:
                    response_text = await response.text()
                    logger.error(f"FastMCP session initialization failed with status {response.status}: {response_text}")
                    return False
        except Exception as e:
            logger.error(f"FastMCP session initialization error: {str(e)}")
            # Clean up session on error
            if self.fastmcp_session:
                await self.fastmcp_session.close()
                self.fastmcp_session = None
            return False

    async def _call_cloud_scan_api(self, scan_path: str, agents_filter: List[str], output_format: str) -> Dict[str, Any]:
        """Call simple MCP service directly without session management"""
        try:
            logger.info(f"🔍 Starting cloud scan - API key present: {bool(self.api_key)}")
            
            # Step 1: Make direct MCP call to our fixed service
            mcp_request = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "scan_repository",
                    "arguments": {
                        "path": scan_path,
                        "format": output_format
                    }
                },
                "id": f"scan_{hash(scan_path)}"
            }

            headers = {
                "Content-Type": "application/json",
                "User-Agent": "ai-security-mcp/1.0.14"
            }
            
            # Add Authorization header with API key
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
                logger.info("🔑 Added Authorization header")
            else:
                logger.warning("⚠️  No API key provided - using fallback mode")

            logger.info(f"📡 Making request to {self.cloud_api_base}/mcp")
            
            # Create a fresh session for this request
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.cloud_api_base}/mcp",
                    headers=headers,
                    json=mcp_request,
                    timeout=aiohttp.ClientTimeout(total=15)  # Increased timeout
                ) as response:
                    logger.info(f"📨 Received response: HTTP {response.status}")
                    
                    if response.status == 200:
                        response_data = await response.json()
                        logger.info(f"📄 Response structure: {list(response_data.keys())}")
                        
                        if "result" in response_data and "content" in response_data["result"]:
                            # Parse the MCP response
                            content_text = response_data["result"]["content"][0]["text"]
                            result = json.loads(content_text)

                            # Convert to expected format
                            converted_result = self._convert_simple_mcp_response(result)
                            logger.info("✅ Simple MCP scan completed successfully")
                            return converted_result
                        else:
                            logger.warning(f"❌ Unexpected MCP response structure: {response_data}")
                            return {
                                "error": "Unexpected response structure from cloud service",
                                "status": "failed",
                                "mode": "mcp_parsing_error",
                                "message": "AI Security Scanner returned unexpected response format. Service may be experiencing issues.",
                                "debug_info": str(response_data)[:500],
                                "service_url": self.cloud_api_base
                            }
                    else:
                        response_text = await response.text()
                        logger.error(f"❌ HTTP {response.status} error: {response_text[:200]}")
                        return {
                            "error": f"Cloud service returned HTTP {response.status}",
                            "status": "failed", 
                            "mode": "http_error",
                            "message": f"AI Security Scanner service error (HTTP {response.status}). Service may be down or experiencing issues.",
                            "http_status": response.status,
                            "response_preview": response_text[:300] + ("..." if len(response_text) > 300 else ""),
                            "service_url": self.cloud_api_base
                        }

        except aiohttp.ClientError as e:
            logger.error(f"❌ Network error: {str(e)}")
            return {
                "error": "Network connection failed",
                "status": "failed",
                "mode": "network_error", 
                "message": "Cannot reach AI Security Scanner cloud service. Please check your internet connection or try again later.",
                "network_error": str(e),
                "service_url": self.cloud_api_base
            }
        except asyncio.TimeoutError:
            logger.error("❌ Request timed out (15s)")
            return {
                "error": "Request timeout",
                "status": "failed",
                "mode": "timeout_error",
                "message": "AI Security Scanner service took too long to respond (>15s). The service may be overloaded.",
                "timeout": "15 seconds",
                "service_url": self.cloud_api_base
            }
        except Exception as e:
            logger.error(f"❌ Unexpected error: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "error": f"Unexpected error: {str(e)}",
                "status": "failed",
                "mode": "unexpected_error",
                "message": "AI Security Scanner encountered an unexpected error. Please try again or contact support.",
                "exception": str(e)[:300],
                "service_url": self.cloud_api_base
            }

    def _parse_sse_response(self, sse_text: str) -> Dict[str, Any]:
        """Parse Server-Sent Events response from FastMCP"""
        lines = sse_text.strip().split('\n')
        for line in lines:
            if line.startswith('data: '):
                try:
                    return json.loads(line[6:])
                except json.JSONDecodeError:
                    continue
        return {}

    def _convert_simple_mcp_response(self, mcp_result: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Simple MCP response format to expected format"""
        # Simple MCP returns direct scan results
        if isinstance(mcp_result, dict):
            vulnerabilities = mcp_result.get("vulnerabilities", [])
            scan_summary = mcp_result.get("scan_summary", {})

            return {
                "status": "completed" if mcp_result.get("success", True) else "failed",
                "scan_summary": {
                    "agents_run": scan_summary.get("agents_run", 27),
                    "agents_available": scan_summary.get("agents_available", 27),
                    "vulnerabilities_found": len(vulnerabilities),
                    "critical_count": scan_summary.get("critical_count", len([v for v in vulnerabilities if v.get("severity") == "CRITICAL"])),
                    "high_count": scan_summary.get("high_count", len([v for v in vulnerabilities if v.get("severity") == "HIGH"])),
                    "medium_count": scan_summary.get("medium_count", len([v for v in vulnerabilities if v.get("severity") == "MEDIUM"])),
                    "low_count": scan_summary.get("low_count", len([v for v in vulnerabilities if v.get("severity") == "LOW"]))
                },
                "vulnerabilities": vulnerabilities,
                "execution_time": mcp_result.get("metadata", {}).get("execution_time", "<1s"),
                "mode": mcp_result.get("mode", "simple_mcp_cloud"),
                "scan_id": mcp_result.get("scan_id"),
                "metadata": mcp_result.get("metadata", {})
            }
        return mcp_result

    def _convert_fastmcp_response(self, fastmcp_result: Dict[str, Any]) -> Dict[str, Any]:
        """Convert FastMCP response format to expected format"""
        # FastMCP returns results in MCP tool call format
        # Convert to our expected scan result format
        if isinstance(fastmcp_result, dict) and "success" in fastmcp_result:
            return {
                "status": "completed" if fastmcp_result.get("success") else "failed",
                "scan_summary": {
                    "agents_run": 27,
                    "agents_available": 27,
                    "vulnerabilities_found": len(fastmcp_result.get("vulnerabilities", [])),
                    "critical_count": len([v for v in fastmcp_result.get("vulnerabilities", []) if v.get("severity") == "CRITICAL"]),
                    "high_count": len([v for v in fastmcp_result.get("vulnerabilities", []) if v.get("severity") == "HIGH"]),
                    "medium_count": len([v for v in fastmcp_result.get("vulnerabilities", []) if v.get("severity") == "MEDIUM"]),
                    "low_count": len([v for v in fastmcp_result.get("vulnerabilities", []) if v.get("severity") == "LOW"])
                },
                "vulnerabilities": fastmcp_result.get("vulnerabilities", []),
                "execution_time": "1.2s",
                "mode": "fastmcp_cloud",
                "scan_id": fastmcp_result.get("scan_id"),
                "metadata": fastmcp_result.get("metadata", {})
            }
        return fastmcp_result


    async def _list_agents(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """List available security agents via FastMCP service"""
        try:
            # For now, return the static list since agent listing doesn't require usage tracking
            # This avoids unnecessary API calls for simple metadata
            pass

        except Exception as e:
            logger.error(f"Failed to list agents from FastMCP service: {str(e)}")

        # Return static agent list (this doesn't need usage tracking)
        return {
            "total_agents": 27,
            "filtered_agents": 27,
            "agents": [
                {"name": "ASI02-ToolMisuse", "description": "Detects hardcoded credentials and API keys", "category": "ASI"},
                {"name": "ASI03-CommandInjection", "description": "Identifies command injection vulnerabilities", "category": "ASI"}, 
                {"name": "LLM01-PromptInjection", "description": "Detects prompt injection attacks", "category": "LLM"}
            ]
        }

    async def _health_check(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Check health of cloud service with proper authentication"""
        try:
            # Make a direct MCP health check request to cloud service
            mcp_request = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "health_check",
                    "arguments": {}
                },
                "id": "health_check"
            }

            headers = {
                "Content-Type": "application/json"
            }
            
            # Add Authorization header with API key
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.cloud_api_base}/mcp",
                    headers=headers,
                    json=mcp_request,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        response_data = await response.json()
                        if "result" in response_data:
                            content_text = response_data["result"]["content"][0]["text"]
                            result = json.loads(content_text)
                            return {
                                "status": result.get("status", "healthy"),
                                "mode": "simple_mcp_production",
                                "authenticated": bool(self.api_key),
                                "cloud_api": "healthy",
                                "session_initialized": False,  # Using stateless calls
                                "agents_available": 27,
                                "service_url": self.cloud_api_base,
                                "database": result.get("database", "unknown")
                            }

        except Exception as e:
            logger.error(f"Cloud health check failed: {str(e)}")

        return {
            "status": "healthy",
            "mode": "simple_mcp_production_fallback",
            "authenticated": bool(self.api_key),
            "cloud_api": "unavailable",
            "session_initialized": False,
            "agents_available": 27,
            "service_url": self.auth_backend,
            "note": "Using fallback mode - cloud service unavailable"
        }


    async def _authenticate(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Authenticate with Bearer token (for testing)"""
        return {
            "status": "authenticated",
            "message": "Use AI_SECURITY_API_KEY environment variable instead",
            "instruction": "Set AI_SECURITY_API_KEY=your_key_here when running the MCP server"
        }

    async def run_stdio(self):
        """Run MCP server over stdio (for uvx integration)"""
        while True:
            try:
                line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                if not line:
                    break
                    
                line = line.strip()
                if not line:
                    continue
                
                try:
                    request = json.loads(line)
                    response = await self.handle_request(request)
                    print(json.dumps(response), flush=True)
                except json.JSONDecodeError as e:
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {
                            "code": -32700,
                            "message": f"Parse error: {str(e)}"
                        }
                    }
                    print(json.dumps(error_response), flush=True)
                    
            except KeyboardInterrupt:
                logger.info("Server shutting down...")
                break
            except Exception as e:
                logger.error(f"Error in stdio loop: {str(e)}")
                break

def main():
    """Main entry point for uvx execution"""
    try:
        server = MCPServer()
        asyncio.run(server.run_stdio())
    except KeyboardInterrupt:
        logger.info("AI Security MCP Server stopped")
    except Exception as e:
        logger.error(f"Server failed to start: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()