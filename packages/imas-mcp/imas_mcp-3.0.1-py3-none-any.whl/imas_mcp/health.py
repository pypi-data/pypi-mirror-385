"""Health endpoint integration for IMAS MCP server HTTP transports.

Provides a lightweight `/health` route exposing basic liveness plus
data dictionary version and document count metrics without introducing
an additional web framework dependency.

The previous `/ready` endpoint has been removed since embeddings and
documents are now initialized synchronously before the HTTP server binds.
If future deferred initialization is reintroduced, a readiness endpoint
can be restored using the historical pattern in version history.
"""

from __future__ import annotations

import importlib.metadata
import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from starlette.responses import JSONResponse

if TYPE_CHECKING:  # pragma: no cover - type checking only
    from imas_mcp.server import Server

logger = logging.getLogger(__name__)


@dataclass
class HealthEndpoint:
    """Attach a /health route to a FastMCP HTTP transport app.

    Usage:
        HealthEndpoint(server).attach("sse")
    """

    server: Server

    def _get_version(self) -> str:
        try:
            return importlib.metadata.version("imas-mcp")
        except Exception:  # pragma: no cover - defensive
            return "unknown"

    def attach(self) -> None:
        """Simple wrapper: replace the FastMCP factory once and inject /health.

        Wrapping targets the HTTP app factory.
        """

        # Always wrap http_app so that /health exists on base HTTP server even for SSE
        attr = "http_app"
        sentinel = "_health_wrapped_http"
        if getattr(self.server.mcp, sentinel, False):
            return
        original = getattr(self.server.mcp, attr)

        async def health_handler(request=None):  # type: ignore[unused-argument]
            ds = self.server.tools.document_store
            meta = ds.get_index_metadata()
            dd_version = meta.get("version") or "unknown"
            if dd_version == "unknown":
                # Use public accessor fallback if available
                try:  # pragma: no cover - defensive
                    dd_version = ds.get_dd_version()  # type: ignore[attr-defined]
                except Exception:
                    pass
            documents = meta.get("document_count") or 0
            ids_count = meta.get("ids_count") or 0
            emb = self.server.embeddings
            # Status without forcing build if deferred

            def _format_uptime(seconds: float) -> str:
                """Return a compact human-readable uptime string.

                Format: '<Xd> <Xh> <Xm> <Xs>' omitting leading zero units.
                Examples:
                    65 -> '1m 5s'
                    3661 -> '1h 1m 1s'
                    90061 -> '1d 1h 1m 1s'
                """
                try:
                    if seconds < 0:  # pragma: no cover - defensive
                        seconds = 0
                    remainder = int(seconds)
                    days, remainder = divmod(remainder, 86400)
                    hours, remainder = divmod(remainder, 3600)
                    minutes, secs = divmod(remainder, 60)
                    parts: list[str] = []
                    if days:
                        parts.append(f"{days}d")
                    if hours or days:
                        parts.append(f"{hours}h")
                    if minutes or hours or days:
                        parts.append(f"{minutes}m")
                    parts.append(f"{secs}s")
                    return " ".join(parts)
                except Exception:  # pragma: no cover - defensive
                    return f"{round(seconds, 3)}s"

            uptime_seconds = round(self.server.uptime_seconds(), 3)
            return JSONResponse(
                {
                    "status": "ok",
                    "mcp_server_version": self._get_version(),
                    "imas_dd_version": dd_version,
                    "ids_count": ids_count,
                    "document_count": documents,
                    "embedding_model_name": emb.model_name,
                    "started_at": self.server.started_at.isoformat(),
                    "uptime": _format_uptime(uptime_seconds),
                }
            )

        def wrapped(*args, **kwargs):  # type: ignore[override]
            app = original(*args, **kwargs)
            existing_paths = {
                getattr(r, "path", None) for r in getattr(app, "routes", [])
            }
            if "/health" not in existing_paths:
                if hasattr(app, "add_api_route"):
                    app.add_api_route(
                        "/health", health_handler, methods=["GET"], tags=["infra"]
                    )  # type: ignore[attr-defined]
                else:
                    app.add_route("/health", health_handler)  # type: ignore[attr-defined]
            return app

        setattr(self.server.mcp, attr, wrapped)
        setattr(self.server.mcp, sentinel, True)
