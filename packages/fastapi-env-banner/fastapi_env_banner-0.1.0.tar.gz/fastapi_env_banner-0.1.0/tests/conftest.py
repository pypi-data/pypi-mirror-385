import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from fastapi_env_banner import Environment, EnvBannerConfig, EnvBannerMiddleware


@pytest.fixture
def app():
    return FastAPI(title="Bananada", version="0.1.0")


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture
def local_config():
    return EnvBannerConfig(
        environment=Environment.LOCAL,
        enabled=True,
        position="top",
        show_in_swagger=True
    )


@pytest.fixture
def staging_config():
    return EnvBannerConfig(
        environment=Environment.STAGING,
        enabled=True,
        position="top",
        show_in_swagger=True
    )


@pytest.fixture
def production_config():
    return EnvBannerConfig(
        environment=Environment.PRODUCTION,
        enabled=True,
        position="top",
        show_in_swagger=True
    )


@pytest.fixture
def custom_config():
    return EnvBannerConfig(
        environment=Environment.DEVELOPMENT,
        enabled=True,
        custom_text="CUSTOM TEST ENVIRONMENT",
        custom_color="#123456",
        position="bottom",
        show_in_swagger=False
    )


@pytest.fixture
def disabled_config():
    return EnvBannerConfig(
        environment=Environment.LOCAL,
        enabled=False,
        position="top",
        show_in_swagger=True
    )


@pytest.fixture
def app_with_middleware(app, local_config):
    app.add_middleware(EnvBannerMiddleware, config=local_config)
    return app


@pytest.fixture
def client_with_middleware(app_with_middleware):
    return TestClient(app_with_middleware)
