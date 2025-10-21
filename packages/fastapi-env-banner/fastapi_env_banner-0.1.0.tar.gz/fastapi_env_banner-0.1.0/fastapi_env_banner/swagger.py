from typing import Optional
from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from starlette.responses import HTMLResponse

from fastapi_env_banner.config import EnvBannerConfig, Environment
from fastapi_env_banner.templates import render_swagger_banner


def setup_swagger_ui(
    app: FastAPI,
    config: EnvBannerConfig,
    openapi_url: str = "/openapi.json",
    docs_url: str = "/docs",
    title: Optional[str] = None,
) -> None:
    """
    This function overrides the default Swagger UI endpoint to include
    an environment banner at the top of the documentation page.
    
    Args:
        app: FastAPI application instance
        config: Environment banner configuration
        openapi_url: URL where OpenAPI schema is served
        docs_url: URL where Swagger UI is served
        title: Custom title for the Swagger UI page
    """
    if not config.show_in_swagger or not config.enabled:
        return
    
    if config.environment == Environment.PRODUCTION:
        return
    
    @app.get(docs_url, include_in_schema=False)
    async def custom_swagger_ui_html() -> HTMLResponse:
        swagger_title = title or app.title
        
        html = get_swagger_ui_html(
            openapi_url=openapi_url,
            title=f"{swagger_title} - Swagger UI",
        )
        
        banner_html = _get_swagger_banner_html(config)
        
        html_content = html.body.decode("utf-8")
        
        if "<body>" in html_content:
            html_content = html_content.replace(
                "<body>",
                f"<body>{banner_html}",
                1
            )
        
        return HTMLResponse(content=html_content)


def _get_swagger_banner_html(config: EnvBannerConfig) -> str:
    return render_swagger_banner(
        text=config.get_banner_text(),
        color=config.get_banner_color(),
        position=config.position,
    )
