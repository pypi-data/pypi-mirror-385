"""Advanced example with custom configuration."""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi_env_banner import (
    Environment,
    EnvBannerConfig,
    EnvBannerMiddleware,
    setup_swagger_ui
)

# Create FastAPI application
app = FastAPI(
    title="Custom Environment Banner Demo",
    description="Advanced example with custom configuration",
    version="1.0.0"
)

# Custom configuration
config = EnvBannerConfig(
    environment=Environment.STAGING,
    enabled=True,
    custom_text="⚠️ STAGING ENVIRONMENT - TEST DATA ONLY ⚠️",
    custom_color="#E91E63",  # Pink
    position="bottom",  # Banner at the bottom
    show_in_swagger=True
)

# Add middleware
app.add_middleware(EnvBannerMiddleware, config=config)

# Setup Swagger UI with banner
setup_swagger_ui(app, config)


@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with custom styled HTML."""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Custom Banner Demo</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 900px;
                margin: 0 auto;
                padding: 40px 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                min-height: 100vh;
            }}
            .container {{
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            }}
            h1 {{
                font-size: 2.5em;
                margin-bottom: 10px;
            }}
            .subtitle {{
                font-size: 1.2em;
                opacity: 0.9;
                margin-bottom: 30px;
            }}
            .feature-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }}
            .feature-card {{
                background: rgba(255, 255, 255, 0.15);
                padding: 20px;
                border-radius: 10px;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }}
            .feature-card h3 {{
                margin-top: 0;
                font-size: 1.3em;
            }}
            .config-info {{
                background: rgba(0, 0, 0, 0.2);
                padding: 20px;
                border-radius: 10px;
                margin: 20px 0;
            }}
            code {{
                background: rgba(0, 0, 0, 0.3);
                padding: 2px 8px;
                border-radius: 4px;
                font-family: 'Courier New', monospace;
            }}
            a {{
                color: #fff;
                text-decoration: underline;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎨 Custom Environment Banner</h1>
            <p class="subtitle">Advanced example with custom configuration</p>
            
            <div class="config-info">
                <h3>⚙️ Current Configuration</h3>
                <ul>
                    <li><strong>Environment:</strong> {config.environment.value}</li>
                    <li><strong>Banner Color:</strong> {config.get_banner_color()}</li>
                    <li><strong>Text:</strong> {config.get_banner_text()}</li>
                    <li><strong>Position:</strong> {config.position}</li>
                    <li><strong>Swagger UI:</strong> {'Enabled' if config.show_in_swagger else 'Disabled'}</li>
                </ul>
            </div>
            
            <div class="feature-grid">
                <div class="feature-card">
                    <h3>🎯 Custom Text</h3>
                    <p>Banner with personalized message for your environment</p>
                </div>
                
                <div class="feature-card">
                    <h3>🎨 Custom Color</h3>
                    <p>Choose any color in hexadecimal format</p>
                </div>
                
                <div class="feature-card">
                    <h3>📍 Flexible Position</h3>
                    <p>Banner at the top or bottom of the page</p>
                </div>
                
                <div class="feature-card">
                    <h3>📚 Swagger Integration</h3>
                    <p>Banner also appears in API documentation</p>
                </div>
            </div>
            
            <h2>🔗 Useful Links</h2>
            <ul>
                <li><a href="/docs">Swagger UI with Banner</a></li>
                <li><a href="/api/config">API Configuration</a></li>
                <li><a href="https://github.com/pinnlabs/fastapi-env-banner">GitHub Repository</a></li>
            </ul>
            
            <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid rgba(255,255,255,0.2); opacity: 0.8;">
                <p>💡 <strong>Tip:</strong> Notice the banner at the bottom of this page!</p>
            </div>
        </div>
    </body>
    </html>
    """


@app.get("/api/config")
async def get_config():
    """Get current banner configuration."""
    return {
        "environment": config.environment.value,
        "enabled": config.enabled,
        "custom_text": config.custom_text,
        "custom_color": config.custom_color,
        "position": config.position,
        "show_in_swagger": config.show_in_swagger,
        "banner_color": config.get_banner_color(),
        "banner_text": config.get_banner_text()
    }


if __name__ == "__main__":
    import uvicorn
    
    print("🎨 Starting Custom Environment Banner Demo")
    print(f"📍 Environment: {config.environment.value}")
    print(f"🎨 Custom Color: {config.custom_color}")
    print(f"📝 Custom Text: {config.custom_text}")
    print(f"📍 Position: {config.position}")
    print("\n🌐 Open your browser at: http://localhost:8001")
    print("📚 Swagger UI: http://localhost:8001/docs\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8001)
