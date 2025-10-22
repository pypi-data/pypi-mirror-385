# chuk_mcp_runtime/server/request_context.py
"""
Request context management for MCP tools.

Provides access to the current MCP request context including session,
progress token, and other request metadata.
"""

from __future__ import annotations

from contextvars import ContextVar
from typing import Any, Optional

from chuk_mcp_runtime.server.logging_config import get_logger

logger = get_logger("chuk_mcp_runtime.request_context")

# ───────────────────────── Context Variables ──────────────────────────
_request_context: ContextVar[Optional["MCPRequestContext"]] = ContextVar(
    "request_context", default=None
)


# ───────────────────────── Request Context ─────────────────────────────
class MCPRequestContext:
    """
    Container for MCP request context information.

    Provides access to session, progress token, and other request metadata
    that tools may need during execution.
    """

    def __init__(
        self,
        session: Any = None,
        progress_token: str | int | None = None,
        meta: Any = None,
    ):
        """
        Initialize request context.

        Args:
            session: The MCP session object
            progress_token: Progress token from client (if provided)
            meta: Request metadata
        """
        self.session = session
        self.progress_token = progress_token
        self.meta = meta

    async def send_progress(
        self,
        progress: float,
        total: float | None = None,
        message: str | None = None,
    ) -> None:
        """
        Send a progress notification to the client.

        Args:
            progress: Current progress value
            total: Total progress value (optional)
            message: Progress message (optional)

        Example:
            # Report 50% progress
            await ctx.send_progress(progress=0.5, total=1.0, message="Processing...")

            # Report step progress
            await ctx.send_progress(progress=3, total=10, message="Step 3 of 10")
        """
        if not self.session:
            logger.warning("No session available for progress notifications")
            return

        if not self.progress_token:
            logger.debug("No progress token provided by client, skipping notification")
            return

        try:
            await self.session.send_progress_notification(
                progress_token=self.progress_token,
                progress=progress,
                total=total,
                message=message,
            )
            logger.debug(f"Sent progress: {progress}/{total or '?'} - {message or 'no message'}")
        except Exception as e:
            logger.error(f"Failed to send progress notification: {e}")


# ───────────────────────── Global Context Access ───────────────────────
def get_request_context() -> Optional[MCPRequestContext]:
    """
    Get the current request context.

    Returns:
        The current MCPRequestContext or None if not in a request context.

    Example:
        ctx = get_request_context()
        if ctx:
            await ctx.send_progress(0.5, 1.0, "Half done")
    """
    return _request_context.get()


def set_request_context(context: Optional[MCPRequestContext]) -> None:
    """
    Set the current request context.

    This is typically called by the server infrastructure and should not
    be called directly by tool implementations.

    Args:
        context: The request context to set
    """
    _request_context.set(context)


async def send_progress(
    progress: float,
    total: float | None = None,
    message: str | None = None,
) -> None:
    """
    Convenience function to send progress from the current context.

    Args:
        progress: Current progress value
        total: Total progress value (optional)
        message: Progress message (optional)

    Example:
        from chuk_mcp_runtime.server.request_context import send_progress

        @mcp_tool()
        async def long_task(items: list[str]):
            total = len(items)
            for i, item in enumerate(items):
                await send_progress(
                    progress=i + 1,
                    total=total,
                    message=f"Processing {item}"
                )
                # ... do work ...

    Raises:
        RuntimeError: If no request context is available
    """
    ctx = get_request_context()
    if not ctx:
        logger.warning("send_progress() called outside of request context - ignoring")
        return

    await ctx.send_progress(progress=progress, total=total, message=message)


# ───────────────────────── Context Manager ─────────────────────────────
class RequestContext:
    """
    Async context manager for request context lifecycle.

    Example:
        async with RequestContext(session, progress_token):
            # Tools called here will have access to the context
            await some_tool()
    """

    def __init__(
        self,
        session: Any = None,
        progress_token: str | int | None = None,
        meta: Any = None,
    ):
        self.context = MCPRequestContext(
            session=session,
            progress_token=progress_token,
            meta=meta,
        )
        self.previous_context: MCPRequestContext | None = None

    async def __aenter__(self) -> MCPRequestContext:
        """Enter the request context."""
        self.previous_context = get_request_context()
        set_request_context(self.context)
        logger.debug(f"Entered request context (progress_token={self.context.progress_token})")
        return self.context

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the request context."""
        set_request_context(self.previous_context)
        logger.debug("Exited request context")
        return False
