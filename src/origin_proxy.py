"""Bounded loopback HTTP -> fixed Unix socket adapter; never a general proxy."""
import http.client
import http.server
import socket
import threading

LIMIT = 65536
REQUEST_DEADLINE_SECONDS = 12


class UnixConnection(http.client.HTTPConnection):
    def connect(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.settimeout(7)
        self.sock.connect("/ipc/mcp.sock")


class Handler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version, sys_version = "SandboxKit", ""

    def setup(self):
        super().setup()
        self.connection.settimeout(5)
        # Starts before request-line/header parsing; caps slow clients even when
        # individual reads make progress. Each response closes the connection.
        self.deadline = threading.Timer(REQUEST_DEADLINE_SECONDS, self.expire)
        self.deadline.daemon = True
        self.deadline.start()

    def expire(self):
        try:
            self.connection.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass

    def finish(self):
        self.deadline.cancel()
        try:
            super().finish()
        except OSError:
            pass

    def log_message(self, *args):
        pass

    def respond(self, status, body=b'{"error":"request_denied"}', content_type="application/json"):
        self.close_connection = True
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(body)

    def body(self):
        lengths = self.headers.get_all("Content-Length", [])
        encodings = self.headers.get_all("Transfer-Encoding", [])
        if len(lengths) > 1 or len(encodings) > 1 or (lengths and encodings):
            raise ValueError("Ambiguous body")
        if not encodings:
            length = int(lengths[0]) if lengths else 0
            if not 0 <= length <= LIMIT:
                raise OverflowError
            data = self.rfile.read(length)
            if len(data) != length:
                raise ValueError("Incomplete body")
            return data
        if encodings[0].lower() != "chunked":
            raise ValueError("Unsupported encoding")
        data = bytearray()
        while True:
            line = self.rfile.readline(256)
            if not line.endswith(b"\r\n"):
                raise ValueError("Invalid chunk")
            size = int(line.split(b";", 1)[0].strip(), 16)
            if size < 0 or len(data) + size > LIMIT:
                raise OverflowError
            if size == 0:
                # Reject trailers rather than allowing hidden authentication fields.
                if self.rfile.readline(256) != b"\r\n":
                    raise ValueError("Trailers not accepted")
                return bytes(data)
            chunk = self.rfile.read(size)
            if len(chunk) != size or self.rfile.read(2) != b"\r\n":
                raise ValueError("Incomplete chunk")
            data.extend(chunk)

    def relay(self):
        self.connection.settimeout(5)
        if self.path != "/mcp":
            return self.respond(404)
        if len(self.headers.get_all("Authorization", [])) != 1:
            return self.respond(401)
        connection = None
        try:
            data = self.body()
            headers = {"Host": "localhost", "Connection": "close"}
            for key in ("Authorization", "Accept", "Content-Type", "MCP-Protocol-Version", "MCP-Session-Id"):
                value = self.headers.get(key)
                if value is not None:
                    headers[key] = value
            connection = UnixConnection("localhost", timeout=7)
            connection.request(self.command, "/mcp", body=data, headers=headers)
            response = connection.getresponse()
            result = response.read(2097153)
            if len(result) > 2097152:
                return self.respond(502)
            return self.respond(response.status, result, response.getheader("Content-Type", "application/json"))
        except OverflowError:
            return self.respond(413)
        except (ValueError, TimeoutError):
            return self.respond(400)
        except (OSError, http.client.HTTPException):
            return self.respond(502)
        finally:
            if connection:
                connection.close()

    do_POST = relay
    do_GET = relay
    do_DELETE = relay


class Server(http.server.ThreadingHTTPServer):
    daemon_threads = True
    request_queue_size = 8
    def __init__(self):
        self.slots = threading.BoundedSemaphore(8)
        super().__init__(("127.0.0.1", 8767), Handler)

    def process_request(self, request, address):
        if not self.slots.acquire(blocking=False):
            self.shutdown_request(request)
            return
        return super().process_request(request, address)

    def process_request_thread(self, request, address):
        try:
            super().process_request_thread(request, address)
        finally:
            self.slots.release()


def start_proxy():
    server = Server()
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server
