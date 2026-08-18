import http.server
import os

PORT = 3000
DIR = "/Users/sanghuisim/Desktop/claude/tbm-auto-app"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIR, **kwargs)

with http.server.HTTPServer(("", PORT), Handler) as httpd:
    print(f"Serving {DIR} at http://localhost:{PORT}")
    httpd.serve_forever()
