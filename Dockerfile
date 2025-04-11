import json

def application(environ, start_response):
    """Minimal WSGI application that responds to both health checks and placement API"""
    status = '200 OK'
    headers = [('Content-type', 'application/json')]
    
    # Handle different routes
    if environ['PATH_INFO'] == '/api/placement' and environ['REQUEST_METHOD'] == 'POST':
        # Read request body
        try:
            request_body_size = int(environ.get('CONTENT_LENGTH', 0))
        except ValueError:
            request_body_size = 0
            
        # Get request data (but we don't need to parse it for this mock)
        request_body = environ['wsgi.input'].read(request_body_size)
        
        # Mock successful placement response
        response = {
            "success": True,
            "message": "Items placed successfully",
            "placements": [
                {
                    "itemId": "test-item-1",
                    "containerId": "test-container-1",
                    "x": 0,
                    "y": 0,
                    "z": 0
                }
            ]
        }
        start_response(status, headers)
        return [json.dumps(response).encode('utf-8')]
    else:
        # Default health check response
        start_response(status, headers)
        return [b'{"status":"online"}']

# This is a standalone WSGI app that responds immediately without Django 