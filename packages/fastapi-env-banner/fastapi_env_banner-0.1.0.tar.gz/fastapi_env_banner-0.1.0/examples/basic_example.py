"""Basic example of using fastapi-env-banner."""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi_env_banner import EnvBannerConfig, EnvBannerMiddleware, setup_swagger_ui

# Create FastAPI application
app = FastAPI(
    title="FastAPI Environment Banner Demo",
    description="Demonstration of the fastapi-env-banner library",
    version="1.0.0"
)

# Configure environment banner (auto-detect from ENVIRONMENT variable)
config = EnvBannerConfig.from_env()

# Add middleware to inject banner in HTML responses
app.add_middleware(EnvBannerMiddleware, config=config)

# Setup custom Swagger UI with banner
setup_swagger_ui(app, config)


@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with HTML response."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>FastAPI Environment Banner Demo</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                line-height: 1.6;
            }
            h1 {
                color: #333;
            }
            .info-box {
                background-color: #f5f5f5;
                border-left: 4px solid #2196F3;
                padding: 15px;
                margin: 20px 0;
            }
            code {
                background-color: #f4f4f4;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
            }
            a {
                color: #2196F3;
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <h1>🎉 FastAPI Environment Banner Demo</h1>
        
        <div class="info-box">
            <p><strong>You should see a banner at the top of this page!</strong></p>
            <p>The banner indicates the current application environment.</p>
        </div>
        
        <h2>📚 Resources</h2>
        <ul>
            <li><a href="/docs">Swagger UI</a> - API documentation with banner</li>
            <li><a href="/redoc">ReDoc</a> - Alternative documentation</li>
            <li><a href="/api/info">API Info</a> - JSON information</li>
        </ul>
        
        <h2>⚙️ Configuration</h2>
        <p>To change the environment, set the environment variable:</p>
        <code>export ENVIRONMENT=staging</code>
        
        <h2>🎨 Available Environments</h2>
        <ul>
            <li><strong>local</strong> - Green</li>
            <li><strong>development</strong> - Blue</li>
            <li><strong>staging</strong> - Orange</li>
            <li><strong>production</strong> - Red (banner disabled by default)</li>
            <li><strong>testing</strong> - Purple</li>
        </ul>
        
        <footer style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #666;">
            <p>Built with ❤️ using <a href="https://fastapi.tiangolo.com/">FastAPI</a></p>
        </footer>
    </body>
    </html>
    """


@app.get("/api/info")
async def api_info():
    """API endpoint returning JSON (no banner)."""
    return {
        "app": "FastAPI Environment Banner Demo",
        "version": "1.0.0",
        "environment": config.environment.value,
        "banner_enabled": config.enabled,
        "message": "This JSON response won't have a banner - only HTML pages do!"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting FastAPI Environment Banner Demo")
    print(f"📍 Environment: {config.environment.value}")
    print(f"🎨 Banner Color: {config.get_banner_color()}")
    print(f"📝 Banner Text: {config.get_banner_text()}")
    print("\n🌐 Open your browser at: http://localhost:8000")
    print("📚 Swagger UI: http://localhost:8000/docs\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
