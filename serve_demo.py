#!/usr/bin/env python
"""
Simple HTTP server for the Secure AI Agent web demo.
This script serves the web demo files and handles API requests.
"""

import os
import json
import http.server
import socketserver
import urllib.parse
from pathlib import Path

# Import the secure agent modules
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from secure_agent import config

# Constants
PORT = 8080
WEB_DEMO_DIR = Path(__file__).parent / 'web_demo'

class DemoRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom request handler for the demo server."""
    
    def __init__(self, *args, **kwargs):
        # Set the directory to serve files from
        self.directory = str(WEB_DEMO_DIR)
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests."""
        # Handle API requests
        if self.path.startswith('/api/'):
            self.handle_api_request()
            return
        
        # Serve static files
        return super().do_GET()
    
    def do_POST(self):
        """Handle POST requests."""
        # Handle API requests
        if self.path.startswith('/api/'):
            self.handle_api_request()
            return
        
        # Method not allowed for other paths
        self.send_error(405, "Method Not Allowed")
    
    def handle_api_request(self):
        """Handle API requests."""
        # Parse the path to get the API endpoint
        parsed_path = urllib.parse.urlparse(self.path)
        path_parts = parsed_path.path.split('/')
        
        # Remove 'api' from the path parts
        if len(path_parts) > 1 and path_parts[1] == 'api':
            path_parts = path_parts[2:]
        
        # Handle different API endpoints
        if len(path_parts) > 0:
            endpoint = path_parts[0]
            
            # Get API key endpoint
            if endpoint == 'key' and self.command == 'GET':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                response = {
                    'api_key': config.OPENAI_API_KEY or '',
                    'has_key': bool(config.OPENAI_API_KEY)
                }
                
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Process query endpoint
            elif endpoint == 'process' and self.command == 'POST':
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length).decode('utf-8')
                query_data = json.loads(post_data)
                
                # In a real implementation, this would process the query using the secure agent
                # For the demo, we'll just echo back the query
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                response = {
                    'success': True,
                    'query': query_data.get('query', ''),
                    'result': f"Processed query: {query_data.get('query', '')}"
                }
                
                self.wfile.write(json.dumps(response).encode())
                return
        
        # Unknown API endpoint
        self.send_error(404, "API endpoint not found")


def main():
    """Start the demo server."""
    # Create the server
    with socketserver.TCPServer(("localhost", PORT), DemoRequestHandler) as httpd:
        print(f"Serving at http://localhost:{PORT}")
        print(f"Web demo directory: {WEB_DEMO_DIR}")
        print(f"OpenAI API Key: {'Configured' if config.OPENAI_API_KEY else 'Not configured'}")
        
        # Serve until interrupted
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")


if __name__ == "__main__":
    main()
