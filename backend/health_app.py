import json

def application(environ, start_response):
    """Minimal WSGI application that responds to both health checks and placement API"""
    status = '200 OK'
    headers = [('Content-type', 'application/json')]
    
    # Handle different routes
    if environ['PATH_INFO'] == '/api/placement' and environ['REQUEST_METHOD'] == 'POST':
        # Mock response with dummy data
        response = {
            "success": True,
            "placements": [
                {
                    "itemId": "test-item-1",
                    "containerId": "test-container-1",
                    "position": {
                        "startCoordinates": {
                            "width": 0,
                            "depth": 0,
                            "height": 0
                        },
                        "endCoordinates": {
                            "width": 10,
                            "depth": 10,
                            "height": 10
                        }
                    }
                }
            ],
            "rearrangements": [
                {
                    "step": 1,
                    "action": "move",
                    "itemId": "test-item-1",
                    "fromContainer": "test-container-0",
                    "fromPosition": {
                        "startCoordinates": {
                            "width": 5,
                            "depth": 5,
                            "height": 5
                        },
                        "endCoordinates": {
                            "width": 15,
                            "depth": 15,
                            "height": 15
                        }
                    },
                    "toContainer": "test-container-1",
                    "toPosition": {
                        "startCoordinates": {
                            "width": 0,
                            "depth": 0,
                            "height": 0
                        },
                        "endCoordinates": {
                            "width": 10,
                            "depth": 10,
                            "height": 10
                        }
                    }
                }
            ]
        }
        start_response(status, headers)
        return [json.dumps(response).encode('utf-8')]
    else:
        # Default health check response
        start_response(status, headers)
        return [b'{"status":"online"}']