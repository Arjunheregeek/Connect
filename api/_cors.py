"""
CORS preflight handler for Vercel deployment
"""

def handler(request, context):
    """
    Handle OPTIONS requests for CORS preflight
    """
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            'Access-Control-Max-Age': '86400'
        },
        'body': ''
    }
