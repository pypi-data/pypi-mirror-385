import re
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, StreamingResponse
from starlette.types import ASGIApp

from fastapi_env_banner.config import EnvBannerConfig, Environment
from fastapi_env_banner.templates import render_banner


class EnvBannerMiddleware(BaseHTTPMiddleware):
    """Middleware that injects an environment banner into HTML responses.
    
    This middleware automatically adds a visual banner to all HTML pages
    to indicate the current environment (local, staging, production, etc.).
    
    Args:
        app: The ASGI application
        config: Environment banner configuration
    """
    
    def __init__(self, app: ASGIApp, config: EnvBannerConfig):
        super().__init__(app)
        self.config = config
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if not self.config.enabled:
            return await call_next(request)
        
        if self.config.environment == Environment.PRODUCTION:
            return await call_next(request)
        
        response = await call_next(request)
        
        content_type = response.headers.get("content-type", "")
        if "text/html" not in content_type:
            return response
        
        if isinstance(response, StreamingResponse):
            return response
        
        body = b""
        async for chunk in response.body_iterator:
            body += chunk
        
        try:
            html_content = body.decode("utf-8")
            
            banner_html = self._get_banner_html()
            
            if "<body" in html_content:
                body_match = re.search(r"<body[^>]*>", html_content, re.IGNORECASE)
                if body_match:
                    insert_pos = body_match.end()
                    html_content = (
                        html_content[:insert_pos] +
                        banner_html +
                        html_content[insert_pos:]
                    )
            else:
                html_content = banner_html + html_content
            
            # Remove Content-Length header since we modified the content
            headers = dict(response.headers)
            headers.pop("content-length", None)
            
            return Response(
                content=html_content,
                status_code=response.status_code,
                headers=headers,
                media_type="text/html",
            )
        except UnicodeDecodeError:
            return response
    
    def _get_banner_html(self) -> str:
        return render_banner(
            text=self.config.get_banner_text(),
            color=self.config.get_banner_color(),
            position=self.config.position,
        )
