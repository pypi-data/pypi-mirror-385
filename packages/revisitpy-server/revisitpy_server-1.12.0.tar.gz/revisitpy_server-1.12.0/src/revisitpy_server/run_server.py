from http.server import SimpleHTTPRequestHandler, HTTPServer
import os
from urllib.parse import urlparse


class ReactHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        # Serve index.html for all unknown paths
        static_dir = os.path.join(os.path.dirname(__file__), "static")
        parsed_path = urlparse(self.path)
        clean_path = parsed_path.path.lstrip("/")  # Remove leading slash
        requested_path = os.path.join(static_dir, clean_path)

        # Check if the requested path is a file
        print(requested_path)
        if not os.path.isfile(requested_path):
            self.path = "/index.html"
            print(self.path)

        return super().do_GET()


def run_server(port):
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    handler = ReactHandler
    os.chdir(static_dir)
    server = HTTPServer(("localhost", port), handler)
    server.serve_forever()


if __name__ == "__main__":
    run_server(port=8080)
