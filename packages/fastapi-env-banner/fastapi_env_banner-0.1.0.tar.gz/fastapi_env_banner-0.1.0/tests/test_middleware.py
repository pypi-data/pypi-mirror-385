import pytest
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.testclient import TestClient

from fastapi_env_banner import Environment, EnvBannerConfig, EnvBannerMiddleware


class TestMiddlewareBasicFunctionality:
    def test_middleware_adds_banner_to_html(self, app, local_config):
        app.add_middleware(EnvBannerMiddleware, config=local_config)
        
        @app.get("/", response_class=HTMLResponse)
        async def root():
            return "<html><body><h1>Test</h1></body></html>"
        
        client = TestClient(app)
        response = client.get("/")
        
        assert response.status_code == 200
        assert "env-banner" in response.text
        assert "LOCAL ENVIRONMENT" in response.text
        assert local_config.get_banner_color() in response.text
    
    def test_middleware_does_not_modify_json(self, app, local_config):
        app.add_middleware(EnvBannerMiddleware, config=local_config)
        
        @app.get("/api")
        async def api():
            return {"message": "test"}
        
        client = TestClient(app)
        response = client.get("/api")
        
        assert response.status_code == 200
        assert "env-banner" not in response.text
        assert response.json() == {"message": "test"}
    
    def test_middleware_disabled(self, app, disabled_config):
        app.add_middleware(EnvBannerMiddleware, config=disabled_config)
        
        @app.get("/", response_class=HTMLResponse)
        async def root():
            return "<html><body><h1>Test</h1></body></html>"
        
        client = TestClient(app)
        response = client.get("/")
        
        assert response.status_code == 200
        assert "env-banner" not in response.text
    
    def test_middleware_production_disabled_by_default(self, app, production_config):
        app.add_middleware(EnvBannerMiddleware, config=production_config)
        
        @app.get("/", response_class=HTMLResponse)
        async def root():
            return "<html><body><h1>Test</h1></body></html>"
        
        client = TestClient(app)
        response = client.get("/")
        
        assert response.status_code == 200
        assert "env-banner" not in response.text


class TestMiddlewareBannerInjection:
    def test_banner_injected_after_body_tag(self, app, local_config):
        app.add_middleware(EnvBannerMiddleware, config=local_config)
        
        @app.get("/", response_class=HTMLResponse)
        async def root():
            return "<html><body><h1>Content</h1></body></html>"
        
        client = TestClient(app)
        response = client.get("/")
        
        body_pos = response.text.find("<body>")
        banner_pos = response.text.find("env-banner")
        
        assert body_pos != -1
        assert banner_pos != -1
        assert banner_pos > body_pos
    
    def test_banner_with_body_attributes(self, app, local_config):
        app.add_middleware(EnvBannerMiddleware, config=local_config)
        
        @app.get("/", response_class=HTMLResponse)
        async def root():
            return '<html><body class="main" id="app"><h1>Content</h1></body></html>'
        
        client = TestClient(app)
        response = client.get("/")
        
        assert "env-banner" in response.text
        assert "LOCAL ENVIRONMENT" in response.text
    
    def test_banner_without_body_tag(self, app, local_config):
        app.add_middleware(EnvBannerMiddleware, config=local_config)
        
        @app.get("/", response_class=HTMLResponse)
        async def root():
            return "<h1>Simple HTML without body tag</h1>"
        
        client = TestClient(app)
        response = client.get("/")
        
        assert "env-banner" in response.text
        assert response.text.startswith("\n<div id=\"env-banner\"")


class TestMiddlewareBannerCustomization:
    
    def test_custom_text(self, app, custom_config):
        app.add_middleware(EnvBannerMiddleware, config=custom_config)
        
        @app.get("/", response_class=HTMLResponse)
        async def root():
            return "<html><body><h1>Test</h1></body></html>"
        
        client = TestClient(app)
        response = client.get("/")
        
        assert custom_config.custom_text in response.text
        assert "DEVELOPMENT ENVIRONMENT" not in response.text
    
    def test_custom_color(self, app, custom_config):
        app.add_middleware(EnvBannerMiddleware, config=custom_config)
        
        @app.get("/", response_class=HTMLResponse)
        async def root():
            return "<html><body><h1>Test</h1></body></html>"
        
        client = TestClient(app)
        response = client.get("/")
        
        assert custom_config.custom_color in response.text
    
    def test_banner_position_top(self, app, local_config):
        local_config.position = "top"
        app.add_middleware(EnvBannerMiddleware, config=local_config)
        
        @app.get("/", response_class=HTMLResponse)
        async def root():
            return "<html><body><h1>Test</h1></body></html>"
        
        client = TestClient(app)
        response = client.get("/")
        
        assert "top: 0;" in response.text
        assert "padding-top: 40px" in response.text
    
    def test_banner_position_bottom(self, app, custom_config):
        custom_config.position = "bottom"
        app.add_middleware(EnvBannerMiddleware, config=custom_config)
        
        @app.get("/", response_class=HTMLResponse)
        async def root():
            return "<html><body><h1>Test</h1></body></html>"
        
        client = TestClient(app)
        response = client.get("/")
        
        assert "bottom: 0;" in response.text
        assert "padding-bottom: 40px" in response.text


class TestMiddlewareEnvironments:
    def test_local_environment(self, app):
        config = EnvBannerConfig(environment=Environment.LOCAL)
        app.add_middleware(EnvBannerMiddleware, config=config)
        
        @app.get("/", response_class=HTMLResponse)
        async def root():
            return "<html><body><h1>Test</h1></body></html>"
        
        client = TestClient(app)
        response = client.get("/")
        
        assert "#4CAF50" in response.text  # Green
        assert "LOCAL ENVIRONMENT" in response.text
    
    def test_development_environment(self, app):
        config = EnvBannerConfig(environment=Environment.DEVELOPMENT)
        app.add_middleware(EnvBannerMiddleware, config=config)
        
        @app.get("/", response_class=HTMLResponse)
        async def root():
            return "<html><body><h1>Test</h1></body></html>"
        
        client = TestClient(app)
        response = client.get("/")
        
        assert "#2196F3" in response.text  # Blue
        assert "DEVELOPMENT ENVIRONMENT" in response.text
    
    def test_staging_environment(self, app, staging_config):
        app.add_middleware(EnvBannerMiddleware, config=staging_config)
        
        @app.get("/", response_class=HTMLResponse)
        async def root():
            return "<html><body><h1>Test</h1></body></html>"
        
        client = TestClient(app)
        response = client.get("/")
        
        assert "#FF9800" in response.text  # Orange
        assert "STAGING ENVIRONMENT" in response.text
    
    def test_testing_environment(self, app):
        config = EnvBannerConfig(environment=Environment.TESTING)
        app.add_middleware(EnvBannerMiddleware, config=config)
        
        @app.get("/", response_class=HTMLResponse)
        async def root():
            return "<html><body><h1>Test</h1></body></html>"
        
        client = TestClient(app)
        response = client.get("/")
        
        assert "#9C27B0" in response.text  # Purple
        assert "TESTING ENVIRONMENT" in response.text


class TestMiddlewareEdgeCases:
    def test_empty_html_response(self, app, local_config):
        app.add_middleware(EnvBannerMiddleware, config=local_config)
        
        @app.get("/", response_class=HTMLResponse)
        async def root():
            return ""
        
        client = TestClient(app)
        response = client.get("/")
        
        assert response.status_code == 200
        assert "env-banner" in response.text
    
    def test_malformed_html(self, app, local_config):
        app.add_middleware(EnvBannerMiddleware, config=local_config)
        
        @app.get("/", response_class=HTMLResponse)
        async def root():
            return "<html><body><h1>Unclosed tag"
        
        client = TestClient(app)
        response = client.get("/")
        
        assert response.status_code == 200
        assert "env-banner" in response.text
    
    def test_multiple_body_tags(self, app, local_config):
        app.add_middleware(EnvBannerMiddleware, config=local_config)
        
        @app.get("/", response_class=HTMLResponse)
        async def root():
            return "<html><body><h1>First</h1></body><body><h1>Second</h1></body></html>"
        
        client = TestClient(app)
        response = client.get("/")
        
        assert response.status_code == 200
        assert "env-banner" in response.text
    
    def test_case_insensitive_body_tag(self, app, local_config):
        app.add_middleware(EnvBannerMiddleware, config=local_config)
        
        @app.get("/", response_class=HTMLResponse)
        async def root():
            return "<HTML><BODY><H1>Test</H1></BODY></HTML>"
        
        client = TestClient(app)
        response = client.get("/")
        
        assert response.status_code == 200
        assert "env-banner" in response.text
    
    def test_non_html_content_type(self, app, local_config):
        app.add_middleware(EnvBannerMiddleware, config=local_config)
        
        @app.get("/xml")
        async def xml_endpoint():
            return HTMLResponse(
                content="<xml><data>test</data></xml>",
                media_type="application/xml"
            )
        
        client = TestClient(app)
        response = client.get("/xml")
        
        assert response.status_code == 200
        assert "env-banner" not in response.text
