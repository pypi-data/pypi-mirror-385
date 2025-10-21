# envbanner/middleware.py
import re
import os
from typing import Optional, Dict, Any
from .core import classify_env, build_banner_html, is_prod

def _inject_before(html: str, snippet: str, needle: str) -> str:
    i = html.lower().rfind(needle)
    if i == -1: return ""
    return html[:i] + snippet + html[i:]

def _get_header(headers, name_bytes: bytes):
    for k, v in headers:
        if k.lower() == name_bytes.lower(): return v
    return None

def _set_or_replace_header(headers, name: bytes, value: bytes):
    lname = name.lower()
    out = [(k, v) for k, v in headers if k.lower() != lname]
    out.append((name, value))
    return out

def _charset_from_content_type(ct: bytes) -> str:
    if not ct: return "utf-8"
    m = re.search(br"charset=([A-Za-z0-9_\-]+)", ct)
    return m.group(1).decode("ascii", "ignore") if m else "utf-8"

class WSGIBannerMiddleware:
    def __init__(self, app, env_var_name: str = "APP_ENV", **options):
        """
        WSGI middleware to inject environment banner.

        Args:
            app: WSGI application
            env_var_name: Primary environment variable to check (default: "APP_ENV")
            **options: Additional banner options:
                - text: Custom banner text
                - background: Custom background color (hex)
                - color: Custom text color (hex)
                - position: Banner position ('top', 'bottom', 'top-left', 'top-right',
                           'bottom-left', 'bottom-right', 'diagonal', 'diagonal-tlbr', 'diagonal-bltr')
                - show_host: Whether to show hostname (default: True)
                - opacity: Banner opacity 0.0-1.0
        """
        self.app = app
        self.env_var_name = env_var_name
        self.options = options

    def __call__(self, environ, start_response):
        # Buffer response to inject HTML
        buffer = []
        status_headers = {}
        def _start_response(status, headers, exc_info=None):
            status_headers.update(status=status, headers=headers)
            return buffer.append

        app_iter = self.app(environ, _start_response)
        body = b"".join(app_iter)
        if hasattr(app_iter, 'close'): app_iter.close()

        status = status_headers.get("status", "200 OK")
        headers = status_headers.get("headers", [])
        ct = _get_header(headers, b"Content-Type")

        if not (ct and b"text/html" in ct and status.startswith("2")):
            start_response(status, headers)
            return [body]

        host = environ.get("HTTP_HOST", "") or environ.get("SERVER_NAME", "")
        path = environ.get("PATH_INFO", "") or "/"
        env_var = environ.get(self.env_var_name) or environ.get("ENVBANNER_ENV")
        env = classify_env(env_var=env_var, host=host, path=path)

        if is_prod(env):
            start_response(status, headers)
            return [body]

        # Build banner options
        banner_options = {**self.options, "env": env, "host": host}
        snippet = build_banner_html(banner_options)
        charset = _charset_from_content_type(ct)
        html = body.decode(charset, errors="replace")
        html_out = _inject_before(html, snippet, "</body>") or (html + snippet)
        body_out = html_out.encode(charset, errors="replace")

        headers = _set_or_replace_header(headers, b"Content-Length", str(len(body_out)).encode())
        start_response(status, headers)
        return [body_out]

class ASGIBannerMiddleware:
    def __init__(self, app, env_var_name: str = "APP_ENV", **options):
        """
        ASGI middleware to inject environment banner.

        Args:
            app: ASGI application
            env_var_name: Primary environment variable to check (default: "APP_ENV")
            **options: Additional banner options:
                - text: Custom banner text
                - background: Custom background color (hex)
                - color: Custom text color (hex)
                - position: Banner position ('top', 'bottom', 'top-left', 'top-right',
                           'bottom-left', 'bottom-right', 'diagonal', 'diagonal-tlbr', 'diagonal-bltr')
                - show_host: Whether to show hostname (default: True)
                - opacity: Banner opacity 0.0-1.0
        """
        self.app = app
        self.env_var_name = env_var_name
        self.options = options

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        response_started = False
        response_body = b""
        original_send = send

        async def send_wrapper(message):
            nonlocal response_started, response_body
            if message["type"] == "http.response.start":
                response_started = message
            elif message["type"] == "http.response.body":
                response_body += message.get("body", b"")
                if not message.get("more_body", False):
                    await self.finalize_response(scope, original_send, response_started, response_body)
            else:
                 await original_send(message)

        await self.app(scope, receive, send_wrapper)

    async def finalize_response(self, scope, send, start_msg, body):
        if not start_msg: return
        headers = start_msg.get("headers", [])
        ct = _get_header(headers, b"content-type")
        status = start_msg.get("status", 200)

        if not (ct and b"text/html" in ct and status // 100 == 2):
            await send(start_msg)
            await send({"type": "http.response.body", "body": body})
            return

        host = dict(scope.get("headers", [])).get(b"host", b"").decode()
        path = scope.get("path", "/")
        env_var = os.getenv(self.env_var_name) or os.getenv("ENVBANNER_ENV")
        env = classify_env(env_var=env_var, host=host, path=path)

        if is_prod(env):
            await send(start_msg)
            await send({"type": "http.response.body", "body": body})
            return

        # Build banner options
        banner_options = {**self.options, "env": env, "host": host}
        snippet = build_banner_html(banner_options)
        charset = _charset_from_content_type(ct)
        html = body.decode(charset, "replace")
        html_out = _inject_before(html, snippet, "</body>") or (html + snippet)
        body_out = html_out.encode(charset, "replace")

        final_headers = _set_or_replace_header(headers, b"content-length", str(len(body_out)).encode())
        start_msg["headers"] = final_headers
        await send(start_msg)
        await send({"type": "http.response.body", "body": body_out})
