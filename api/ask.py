"""
Vercel Serverless Function for Connect Agent API

This is the main endpoint that handles agent queries via Vercel serverless functions.
"""

import sys
import os
import json
import asyncio
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agent_run import ConnectAgent

# Initialize agent globally (reused across invocations)
agent = ConnectAgent()


async def handle_request(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle the agent request asynchronously.
    
    Args:
        request_data: Request data with 'question' and optional 'conversation_id'
        
    Returns:
        Response dictionary with agent results
    """
    try:
        question = request_data.get('question', '')
        conversation_id = request_data.get('conversation_id')
        
        if not question:
            return {
                'success': False,
                'response': 'No question provided',
                'metadata': {}
            }
        
        # Execute agent query
        result = await agent.ask_detailed(
            question=question,
            conversation_id=conversation_id
        )
        
        return result
        
    except Exception as e:
        return {
            'success': False,
            'response': f'Error processing request: {str(e)}',
            'metadata': {
                'error': str(e)
            }
        }


def handler(request, context):
    """
    Vercel serverless function handler.
    
    This is the entry point that Vercel calls.
    """
    try:
        # Parse request body
        if hasattr(request, 'body'):
            body = request.body
            if isinstance(body, bytes):
                body = body.decode('utf-8')
            request_data = json.loads(body) if isinstance(body, str) else body
        else:
            request_data = request
        
        # Run async handler
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(handle_request(request_data))
        loop.close()
        
        # Return response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps(result)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': False,
                'response': f'Server error: {str(e)}',
                'metadata': {}
            })
        }
