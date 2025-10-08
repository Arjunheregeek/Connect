#!/usr/bin/env python3
"""
Connect Agent API Server

FastAPI server that provides HTTP endpoints for the LangGraph Connect Agent.
This allows the React frontend to interact with the simplified agent system.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import uvicorn
from typing import Dict, Any, Optional
import sys
import os

# Add parent directory for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agent_run import ConnectAgent

# Initialize FastAPI app
app = FastAPI(
    title="Connect Agent API",
    description="LangGraph-based agent for people knowledge graph queries",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the agent
agent = ConnectAgent()

# Request/Response models
class QueryRequest(BaseModel):
    question: str
    conversation_id: Optional[str] = None

class QueryResponse(BaseModel):
    response: str
    success: bool
    metadata: Dict[str, Any]

class HealthResponse(BaseModel):
    status: str
    agent_info: Dict[str, Any]

@app.get("/", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    from app.agent_run import get_agent_info
    return HealthResponse(
        status="healthy",
        agent_info=get_agent_info()
    )

@app.post("/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    """
    Ask a question to the Connect Agent.
    
    This endpoint uses the simplified LangGraph workflow to process
    natural language queries about people in the knowledge graph.
    """
    try:
        result = await agent.ask_detailed(
            question=request.question,
            conversation_id=request.conversation_id
        )
        
        return QueryResponse(
            response=result['response'],
            success=result['success'],
            metadata=result['metadata']
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "message": "Failed to process question"
            }
        )

@app.get("/session/summary")
async def get_session_summary():
    """Get session statistics."""
    return agent.get_session_summary()

@app.post("/session/clear")
async def clear_session():
    """Clear session history."""
    agent.clear_history()
    return {"message": "Session history cleared"}

@app.get("/agent/info")
async def get_agent_information():
    """Get agent capabilities and information."""
    from app.agent_run import get_agent_info
    return get_agent_info()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Connect Agent API Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    
    args = parser.parse_args()
    
    print(f"""
🚀 Starting Connect Agent API Server
   
   URL: http://{args.host}:{args.port}
   Agent: SimplifiedConnectAgent (LangGraph)
   Workflow: Planning → Execution → Synthesis
   
   Endpoints:
   - GET  /           Health check
   - POST /ask        Ask questions  
   - GET  /agent/info Agent information
   
""")
    
    uvicorn.run(
        "app.api:app",
        host=args.host,
        port=args.port,
        reload=args.reload
    )