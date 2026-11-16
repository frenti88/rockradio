#!/usr/bin/env python3
"""
Threaded HTTP Server with Range request support for Rock Radio on port 8080.
Supports audio seeking/streaming and safely proxies /api/* to localhost:5055.
"""
import os
import re
import urllib.parse
import urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

HOST = os.environ.get('ROCKRADIO_HOST', '127.0.0.1')
PORT = int(os.environ.get('ROCKRADIO_PORT', '8080'))
DIRECTORY = os.path.abspath(os.path.dirname(__file__))
MAX_PROXY_BODY_BYTES = 65536
ALLOWED_PUBLIC_EXTENSIONS = {
    '.html', '.mp3', '.png', '.jpg', '.jpeg', '.webp', '.svg',
    '.ico', '.js', '.webmanifest', '.txt'
}
BLOCKED_TOP_DIRS = {'api', 'data', 'scripts', '.git'}


class RangeRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def _allowed_origin(self):
        origin = self.headers.get('Origin', '')
        if re.match(r'^http://(localhost|127\.0\.0\.1)(:\d+)?$', origin):
            return origin
        if origin in ('https://www.rockradio.lat', 'https://rockradio.lat'):
            return origin
        return None

    def _is_safe_public_path(self):
        parsed = urllib.parse.urlsplit(self.path)
        clean_path = urllib.parse.unquote(parsed.path)
        if clean_path in ('', '/'):
            return True
        rel = clean_path.lstrip('/')
        parts = [p for p in rel.split('/') if p]
        if any(p.startswith('.') or p == '..' for p in parts):
            return False
        if parts and parts[0] in BLOCKED_TOP_DIRS:
            return False
        fs_path = os.path.abspath(os.path.join(DIRECTORY, rel))
        if not (fs_path == DIRECTORY or fs_path.startswith(DIRECTORY + os.sep)):
            return False
        if os.path.isdir(fs_path):
            return False
        _, ext = os.path.splitext(fs_path)
        return ext.lower() in ALLOWED_PUBLIC_EXTENSIONS

    def send_head(self):
        if not self._is_safe_public_path():
            self.send_error(403, "Forbidden")
            return None

        if 'Range' not in self.headers:
            return super().send_head()

        path = self.translate_path(self.path)
        if not os.path.exists(path) or os.path.isdir(path):
            return super().send_head()

        file_size = os.path.getsize(path)
        range_header = self.headers['Range']
        match = re.match(r'bytes=(\d+)-(\d*)', range_header)
        if not match:
            return super().send_head()

        start = int(match.group(1))
        end = int(match.group(2)) if match.group(2) else file_size - 1
        if start >= file_size or end >= file_size or start > end:
            self.send_error(416, "Requested Range Not Satisfiable")
            return None

        self.send_response(206)
        ctype = self.guess_type(path)
        self.send_header("Content-Type", ctype)
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
        self.send_header("Content-Length", str(end - start + 1))
        self.send_header("Last-Modified", self.date_time_string(os.path.getmtime(path)))
        self.end_headers()

        f = open(path, 'rb')
        f.seek(start)

        class BoundedFile:
            def __init__(self, fh, length):
                self.f = fh
                self.remaining = length

            def read(self, size=-1):
                if self.remaining <= 0:
                    return b""
                if size < 0 or size > self.remaining:
                    size = self.remaining
                data = self.f.read(size)
                self.remaining -= len(data)
                return data

            def close(self):
                self.f.close()

        return BoundedFile(f, end - start + 1)

    def end_headers(self):
        allowed_origin = self._allowed_origin()
        if allowed_origin:
            self.send_header("Access-Control-Allow-Origin", allowed_origin)
            self.send_header("Vary", "Origin")
        self.send_header("Access-Control-Allow-Methods", "GET, HEAD, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Accept")
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("X-Content-Type-Options", "nosniff")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def _proxy_to_api(self):
        try:
            length = int(self.headers.get('Content-Length', '0') or '0')
        except ValueError:
            self.send_error(400, "Invalid Content-Length")
            return
        if length < 0 or length > MAX_PROXY_BODY_BYTES:
            self.send_error(413, "Payload Too Large")
            return

        target_url = f"http://127.0.0.1:5055{self.path}"
        body = self.rfile.read(length) if length > 0 else None
        headers = {
            k: v for k, v in self.headers.items()
            if k.lower() in ('content-type', 'accept')
        }
        req = urllib.request.Request(target_url, data=body, headers=headers, method=self.command)
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                resp_body = resp.read()
                self.send_response(resp.status)
                for k, v in resp.getheaders():
                    if k.lower() not in ('transfer-encoding', 'content-length', 'access-control-allow-origin', 'vary'):
                        self.send_header(k, v)
                self.send_header('Content-Length', str(len(resp_body)))
                self.end_headers()
                self.wfile.write(resp_body)
        except Exception:
            self.send_response(502)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"error": "API gateway unavailable"}')

    def do_POST(self):
        if self.path.startswith('/api/'):
            return self._proxy_to_api()
        self.send_error(405, "Method Not Allowed")

    def do_GET(self):
        if self.path.startswith('/api/'):
            return self._proxy_to_api()
        return super().do_GET()


if __name__ == '__main__':
    server = ThreadingHTTPServer((HOST, PORT), RangeRequestHandler)
    print(f"Serving Rock Radio at http://{HOST}:{PORT} (Threaded + Range requests enabled)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
