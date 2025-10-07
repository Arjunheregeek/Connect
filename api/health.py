"""
Health check endpoint for Vercel deployment
"""

import json


def handler(request, context):
    """
    Simple health check endpoint
    """
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'status': 'healthy',
            'service': 'Connect Agent API',
            'platform': 'Vercel Serverless'
        })
    }
