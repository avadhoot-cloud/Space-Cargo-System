def application(environ, start_response):
    """Minimal WSGI application that responds instantly"""
    status = '200 OK'
    headers = [('Content-type', 'application/json')]
    start_response(status, headers)
    return [b'{"status":"online"}']

# This is a standalone WSGI app that responds immediately without Django 