import http.server
import socketserver
import json
from .subprocess_handler import PhicodeSubprocessHandler
from ..config.config import SERVER, ENGINE

class PhicodeHTTPServer(http.server.BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.handler = PhicodeSubprocessHandler()
        super().__init__(*args, **kwargs)

    def do_POST(self):
        if self.path == '/execute':
            self._handle_execute()
        elif self.path == '/convert':
            self._handle_convert()
        else:
            self._send_error(404, f"{SERVER} Endpoint not found")

    def do_GET(self):
        if self.path == '/info':
            self._handle_info()
        elif self.path == '/symbols':
            self._handle_symbols()
        else:
            self._send_error(404, f"{SERVER} Endpoint not found")

    def _handle_convert(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self._send_error(400, "Empty request body")
                return

            post_data = self.rfile.read(content_length).decode('utf-8')
            payload = json.loads(post_data)

            if 'code' not in payload or 'target' not in payload:
                self._send_error(400, "Missing 'code' or 'target' field")
                return

            result = self.handler.convert_code(payload['code'], payload['target'])
            self._send_json_response(result)

        except json.JSONDecodeError:
            self._send_error(400, "Invalid JSON")
        except Exception as e:
            self._send_error(500, f"{SERVER} error: {str(e)}")

    def _handle_symbols(self):
        result = self.handler.get_symbol_mappings()
        self._send_json_response(result)

    def _handle_execute(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self._send_error(400, "Empty request body")
                return

            post_data = self.rfile.read(content_length).decode('utf-8')
            payload = json.loads(post_data)

            if 'code' not in payload:
                self._send_error(400, "Missing 'code' field")
                return

            result = self.handler.execute_code(
                payload['code'],
                payload.get('type', 'auto')
            )
            self._send_json_response(result)

        except json.JSONDecodeError:
            self._send_error(400, "Invalid JSON")
        except Exception as e:
            self._send_error(500, f"{SERVER} error: {str(e)}")

    def _handle_info(self):
        result = self.handler.get_engine_info()
        self._send_json_response(result)

    def _send_json_response(self, data):
        response_body = json.dumps(data, ensure_ascii=False)
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(response_body.encode('utf-8'))))
        self.end_headers()
        self.wfile.write(response_body.encode('utf-8'))

    def _send_error(self, code, message):
        error_data = {"success": False, "error": message}
        response_body = json.dumps(error_data)
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(response_body)))
        self.end_headers()
        self.wfile.write(response_body.encode('utf-8'))

def start_server(host: str = "localhost", port: int = 8000):
    try:
        with socketserver.TCPServer((host, port), PhicodeHTTPServer) as httpd:
            print(f"🌐 {SERVER} running on http://{host}:{port}")
            print("📍 Endpoints:")
            print("   POST /execute - Execute φ or Python code")
            print("   POST /convert - Convert Python ↔ φ")
            print(f"   GET  /info    - {ENGINE} info")
            print("   GET  /symbols - Symbol mappings")
            print("🔄 Press Ctrl+C to stop")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print(f"\n⏹️  {SERVER} stopped")
    except Exception as e:
        print(f"❌ {SERVER} error: {e}")