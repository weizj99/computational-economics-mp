#!/usr/bin/env python3
"""Read-only loopback preview server with one byte range per request.

Usage: python serve_site.py --directory PATH --port 8765
QA may import make_handler(directory) and give the returned class to its own
loopback ThreadingHTTPServer. No model or script is executed by this server.
"""
from __future__ import annotations

import argparse
import datetime
import email.utils
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import ipaddress
import os
from pathlib import Path
import re
import socket
from urllib.parse import urlsplit, urlunsplit


def parse_byte_range(value: str, size: int) -> tuple[int, int]:
    """Return inclusive bounds for a single byte range, or raise ValueError.

    Multiple ranges are deliberately unsupported. End positions beyond EOF are
    clamped; an empty file, zero suffix, reversed or out-of-file range is 416.
    """
    match = re.fullmatch(r"bytes\s*=\s*([0-9]*)\s*-\s*([0-9]*)", value.strip(), re.IGNORECASE)
    if not match or size <= 0:
        raise ValueError("Invalid or unsatisfiable byte range")
    first, last = match.groups()
    if not first:
        if not last or int(last) <= 0:
            raise ValueError("Invalid suffix byte range")
        return max(0, size - int(last)), size - 1
    start = int(first)
    end = int(last) if last else size - 1
    if start >= size or end < start:
        raise ValueError("Unsatisfiable byte range")
    return start, min(end, size - 1)


def http_date_timestamp(value: str) -> float | None:
    try:
        parsed = email.utils.parsedate_to_datetime(value)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=datetime.timezone.utc)
        return parsed.timestamp()
    except (TypeError, ValueError, OverflowError, IndexError):
        return None


class RangeStaticHandler(SimpleHTTPRequestHandler):
    """Static GET/HEAD only, with a bounded streaming response and no listing."""

    protocol_version = "HTTP/1.1"
    server_version = "LessonPreview/1.0"
    extensions_map = {
        **SimpleHTTPRequestHandler.extensions_map,
        ".mp4": "video/mp4",
        ".vtt": "text/vtt; charset=utf-8",
        ".js": "text/javascript; charset=utf-8",
        ".css": "text/css; charset=utf-8",
        ".woff2": "font/woff2",
        ".svg": "image/svg+xml",
    }

    def __init__(self, *args, directory: str | os.PathLike[str], **kwargs):
        self._site_root = Path(directory).resolve(strict=True)
        if not self._site_root.is_dir():
            raise ValueError("Static directory is not a directory")
        self._bytes_to_send = 0
        super().__init__(*args, directory=str(self._site_root), **kwargs)

    def _inside_root(self, path: Path) -> bool:
        try:
            path.resolve().relative_to(self._site_root)
            return True
        except (ValueError, OSError, RuntimeError):
            return False

    def _file_headers(self, size: int, modified: float) -> None:
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Last-Modified", self.date_time_string(modified))

    def send_head(self):
        # A handler instance can serve several requests on one connection.
        self._bytes_to_send = 0
        parts = urlsplit(self.path)
        path = Path(self.translate_path(self.path))
        if not self._inside_root(path):
            self.send_error(HTTPStatus.FORBIDDEN, "Path is outside the static directory")
            return None
        if parts.path == "/favicon.ico" and not path.exists():
            self.send_response(HTTPStatus.NO_CONTENT)
            self.end_headers()
            return None
        if path.is_dir():
            if not parts.path.endswith(("/", "%2f", "%2F")):
                self.send_response(HTTPStatus.MOVED_PERMANENTLY)
                self.send_header("Location", urlunsplit(("", "", parts.path + "/", parts.query, parts.fragment)))
                self.send_header("Content-Length", "0")
                self.end_headers()
                return None
            index = next((path / name for name in ("index.html", "index.htm") if (path / name).is_file()), None)
            if index is None:
                self.send_error(HTTPStatus.NOT_FOUND, "No static index file")
                return None
            path = index
            if not self._inside_root(path):
                self.send_error(HTTPStatus.FORBIDDEN, "Path is outside the static directory")
                return None
        elif parts.path.endswith(("/", "%2f", "%2F")):
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")
            return None
        if not path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")
            return None
        try:
            handle = path.open("rb")
        except OSError:
            self.send_error(HTTPStatus.NOT_FOUND, "File could not be opened")
            return None
        try:
            info = os.fstat(handle.fileno())
            size = info.st_size
            if "If-Modified-Since" in self.headers and "If-None-Match" not in self.headers:
                since = http_date_timestamp(self.headers["If-Modified-Since"])
                if since is not None and int(info.st_mtime) <= since:
                    self.send_response(HTTPStatus.NOT_MODIFIED)
                    self._file_headers(size, info.st_mtime)
                    self.end_headers()
                    handle.close()
                    return None

            range_headers = self.headers.get_all("Range", [])
            use_range = bool(range_headers)
            if use_range and "If-Range" in self.headers:
                # No ETag is claimed. An entity-tag or invalid/old date asks for
                # the complete representation; valid date validators may range.
                since = http_date_timestamp(self.headers["If-Range"])
                use_range = since is not None and int(info.st_mtime) <= since
            if use_range:
                try:
                    if len(range_headers) != 1:
                        raise ValueError("Multiple Range fields")
                    start, end = parse_byte_range(range_headers[0], size)
                except ValueError:
                    self.send_response(HTTPStatus.REQUESTED_RANGE_NOT_SATISFIABLE)
                    self.send_header("Content-Range", f"bytes */{size}")
                    self.send_header("Content-Length", "0")
                    self._file_headers(size, info.st_mtime)
                    self.end_headers()
                    handle.close()
                    return None
                handle.seek(start)
                length = end - start + 1
                self.send_response(HTTPStatus.PARTIAL_CONTENT)
                self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
            else:
                length = size
                self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", self.guess_type(str(path)))
            self.send_header("Content-Length", str(length))
            self._file_headers(size, info.st_mtime)
            self.end_headers()
            self._bytes_to_send = length
            return handle
        except BaseException:
            handle.close()
            raise

    def copyfile(self, source, outputfile) -> None:
        remaining = self._bytes_to_send
        try:
            while remaining:
                block = source.read(min(256 * 1024, remaining))
                if not block:
                    self.close_connection = True
                    break
                outputfile.write(block)
                remaining -= len(block)
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            # Seeking/closing a tab cancels an earlier media response normally.
            self.close_connection = True


def make_handler(directory: str | os.PathLike[str]) -> type[RangeStaticHandler]:
    """Return a directory-bound class for a loopback QA HTTPServer."""
    root = Path(directory).resolve(strict=True)
    if not root.is_dir():
        raise ValueError("--directory must be an existing directory")

    class BoundRangeStaticHandler(RangeStaticHandler):
        def __init__(self, *args, **kwargs):
            if "directory" in kwargs:
                raise TypeError("The handler factory already fixes its directory")
            super().__init__(*args, directory=root, **kwargs)

    return BoundRangeStaticHandler


def create_server(host: str, port: int, directory: str | os.PathLike[str]) -> ThreadingHTTPServer:
    """Bind a loopback address only; hostnames and wildcard/public IPs fail."""
    address = ipaddress.ip_address(host)
    if not address.is_loopback:
        raise ValueError("Only a numeric loopback IP address may be bound")
    if not 0 <= port <= 65535:
        raise ValueError("Port must be between 0 and 65535")

    class LoopbackServer(ThreadingHTTPServer):
        address_family = socket.AF_INET6 if address.version == 6 else socket.AF_INET
        daemon_threads = True

    return LoopbackServer((str(address), port), make_handler(directory))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", required=True, type=Path)
    parser.add_argument("--host", default="127.0.0.1", help="Numeric loopback IP only (default: 127.0.0.1)")
    parser.add_argument("--port", default=8765, type=int)
    args = parser.parse_args()
    try:
        server = create_server(args.host, args.port, args.directory)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    host, port = server.server_address[:2]
    display_host = f"[{host}]" if ":" in host else host
    print(f"Static preview: http://{display_host}:{port}/ (GET/HEAD, byte ranges; no script execution)", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
