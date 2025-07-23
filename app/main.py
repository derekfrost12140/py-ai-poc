from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our MCP agent
from .agent import MCPAgent

# Initialize FastAPI app
app = FastAPI(
    title="MCP Agent Orchestration System",
    description="AI Agent system that simulates MCP (Modular Control Point) architecture with dynamic tool selection",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for local development
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# Pydantic models for request/response
class QueryRequest(BaseModel):
    query: str
    security_password: Optional[str] = None

class QueryResponse(BaseModel):
    success: bool
    user_query: str
    tool_selected: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    result: Optional[Any] = None  # Accept list or string
    error: Optional[str] = None

# Initialize MCP Agent
try:
    mcp_agent = MCPAgent()
except Exception as e:
    print(f"Warning: Failed to initialize MCP Agent: {e}")
    mcp_agent = None

@app.get("/")
async def root():
    """Root endpoint with system information"""
    return {
        "message": "MCP Agent Orchestration System",
        "description": "AI-powered tool orchestration system simulating MCP architecture",
        "endpoints": {
            "POST /query": "Process natural language queries",
            "GET /docs": "OpenAPI documentation",
            "GET /health": "System health check"
        },
        "architecture": {
            "mcp_client": "LLM-based agent (OpenAI GPT-3.5)",
            "mcp_registry": "Tool manifest (manifest.json)",
            "mcp_server": "Tool executor (weather, SQL, GraphQL)"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agent_initialized": mcp_agent is not None,
        "openai_key_configured": bool(os.getenv('OPENAI_API_KEY')),
        "weather_key_configured": bool(os.getenv('WEATHER_API_KEY'))
    }

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Main endpoint for processing natural language queries
    
    This endpoint simulates the complete MCP orchestration flow:
    1. MCP Client receives user query
    2. LLM interprets intent and selects tool
    3. MCP Registry provides tool metadata
    4. MCP Server executes the selected tool
    5. Returns formatted response
    """
    if not mcp_agent:
        raise HTTPException(
            status_code=500,
            detail="MCP Agent not initialized. Check API keys and configuration."
        )
    
    try:
        # Process the query through our MCP-style agent
        result = mcp_agent.process_query(request.query, request.security_password)
        
        return QueryResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )

@app.get("/tools")
async def get_available_tools():
    """Get information about available tools (MCP Registry simulation)"""
    try:
        with open('app/manifest.json', 'r') as f:
            import json
            manifest = json.load(f)
        return {
            "message": "Available tools in MCP Registry",
            "tools": manifest['tools']
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error loading tool manifest: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 