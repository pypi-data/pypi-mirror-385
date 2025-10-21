"""HTML templates for environment banners."""

from string import Template
from typing import Dict


BANNER_TEMPLATE = Template("""
<div id="$banner_id" style="$styles">
    ⚠️ $text ⚠️
</div>
<style>
    body {
        $body_padding
    }
</style>
""")

SWAGGER_BANNER_TEMPLATE = Template("""
<div id="$banner_id" style="$styles">
    ⚠️ $text ⚠️
</div>
<style>
    .swagger-ui {
        $swagger_padding
    }
</style>
""")


def get_banner_styles(color: str, position: str) -> str:
    """Generate inline styles for the banner.
    
    Args:
        color: Background color in hex format
        position: Banner position ('top' or 'bottom')
    
    Returns:
        CSS inline styles as string
    """
    position_style = "top: 0;" if position == "top" else "bottom: 0;"
    
    styles = [
        "position: fixed;",
        position_style,
        "left: 0;",
        "right: 0;",
        f"background-color: {color};",
        "color: white;",
        "text-align: center;",
        "padding: 8px 16px;",
        "font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;",
        "font-size: 14px;",
        "font-weight: 600;",
        "z-index: 999999;",
        "box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);",
        "letter-spacing: 0.5px;",
    ]
    
    return " ".join(styles)


def get_swagger_banner_styles(color: str, position: str) -> str:
    """Generate inline styles for Swagger UI banner.
    
    Args:
        color: Background color in hex format
        position: Banner position ('top' or 'bottom')
    
    Returns:
        CSS inline styles as string
    """
    position_style = "top: 0;" if position == "top" else "bottom: 0;"
    
    styles = [
        "position: fixed;",
        position_style,
        "left: 0;",
        "right: 0;",
        f"background-color: {color};",
        "color: white;",
        "text-align: center;",
        "padding: 10px 16px;",
        "font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;",
        "font-size: 14px;",
        "font-weight: 600;",
        "z-index: 999999;",
        "box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);",
        "letter-spacing: 0.5px;",
    ]
    
    return " ".join(styles)


def render_banner(text: str, color: str, position: str = "top") -> str:
    """Render HTML banner for regular pages.
    
    Args:
        text: Banner text to display
        color: Background color in hex format
        position: Banner position ('top' or 'bottom')
    
    Returns:
        Rendered HTML string
    """
    body_padding = (
        "padding-top: 40px !important;" 
        if position == "top" 
        else "padding-bottom: 40px !important;"
    )
    
    return BANNER_TEMPLATE.substitute(
        banner_id="env-banner",
        styles=get_banner_styles(color, position),
        text=text,
        body_padding=body_padding,
    )


def render_swagger_banner(text: str, color: str, position: str = "top") -> str:
    """Render HTML banner for Swagger UI.
    
    Args:
        text: Banner text to display
        color: Background color in hex format
        position: Banner position ('top' or 'bottom')
    
    Returns:
        Rendered HTML string
    """
    swagger_padding = (
        "padding-top: 50px;" 
        if position == "top" 
        else "padding-bottom: 50px;"
    )
    
    return SWAGGER_BANNER_TEMPLATE.substitute(
        banner_id="env-banner-swagger",
        styles=get_swagger_banner_styles(color, position),
        text=text,
        swagger_padding=swagger_padding,
    )
