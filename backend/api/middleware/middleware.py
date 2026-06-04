import time
from collections import defaultdict
from starlette.types import ASGIApp, Scope, Receive, Send
from starlette.responses import JSONResponse

from utils.logger import get_logger, generate_trace_id, trace_id_var

logger = get_logger(__name__)


class RequestLoggingMiddleware:
    """Logs every request with trace ID, method, path, status, and duration."""

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return

        trace_id = generate_trace_id()
        trace_id_var.set(trace_id)
        start = time.perf_counter()

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                duration = (time.perf_counter() - start) * 1000
                headers = list(message.get("headers", []))
                headers.append((b"x-trace-id", trace_id.encode()))
                headers.append((b"x-response-time", f"{duration:.1f}ms".encode()))
                message["headers"] = headers
                logger.info(
                    f"{scope.get('method', 'WS')} {scope.get('path', '/')} → {message.get('status', 200)} "
                    f"({duration:.1f}ms)"
                )
            await send(message)

        await self.app(scope, receive, send_wrapper)


class RateLimitMiddleware:
    """Simple in-memory rate limiter (per-client-IP, per-minute) designed for high concurrency."""

    def __init__(self, app: ASGIApp, max_requests: int = 60, window_seconds: int = 60):
        self.app = app
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._request_counts: dict[str, list[float]] = defaultdict(list)
        self._last_clean = time.time()

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        now = time.time()
        # Periodically clean the entire dictionary to avoid memory growth under high loads
        if now - self._last_clean > 300:
            self._clean_all_ips(now)

        client = scope.get("client")
        client_ip = client[0] if client else "unknown"

        # Clean current client IP entries
        self._request_counts[client_ip] = [
            t for t in self._request_counts[client_ip]
            if now - t < self.window_seconds
        ]

        if len(self._request_counts[client_ip]) >= self.max_requests:
            logger.warning(f"🚫 Rate limit exceeded for {client_ip}")
            response = JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Please try again later."},
            )
            await response(scope, receive, send)
            return

        self._request_counts[client_ip].append(now)
        await self.app(scope, receive, send)

    def _clean_all_ips(self, now: float):
        to_delete = []
        for ip, times in self._request_counts.items():
            valid_times = [t for t in times if now - t < self.window_seconds]
            if not valid_times:
                to_delete.append(ip)
            else:
                self._request_counts[ip] = valid_times
        for ip in to_delete:
            del self._request_counts[ip]
        self._last_clean = now

