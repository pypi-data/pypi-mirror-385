import os
import pytest

from fastapi_env_banner import Environment, EnvBannerConfig


class TestEnvironmentEnum: 
    def test_environment_values(self):
        assert Environment.LOCAL.value == "local"
        assert Environment.DEVELOPMENT.value == "development"
        assert Environment.STAGING.value == "staging"
        assert Environment.PRODUCTION.value == "production"
        assert Environment.TESTING.value == "testing"
    
    def test_environment_is_string(self):
        assert isinstance(Environment.LOCAL, str)
        assert isinstance(Environment.PRODUCTION, str)


class TestEnvBannerConfigDefaults: 
    def test_default_values(self):
        config = EnvBannerConfig()
        
        assert config.environment == Environment.LOCAL
        assert config.enabled is True
        assert config.custom_text is None
        assert config.custom_color is None
        assert config.position == "top"
        assert config.show_in_swagger is True
    
    def test_custom_values(self):
        config = EnvBannerConfig(
            environment=Environment.STAGING,
            enabled=False,
            custom_text="Test Banner",
            custom_color="#FF0000",
            position="bottom",
            show_in_swagger=False
        )
        
        assert config.environment == Environment.STAGING
        assert config.enabled is False
        assert config.custom_text == "Test Banner"
        assert config.custom_color == "#FF0000"
        assert config.position == "bottom"
        assert config.show_in_swagger is False


class TestEnvBannerConfigFromEnv: 
    def test_from_env_local(self, monkeypatch):
        monkeypatch.setenv("ENVIRONMENT", "local")
        config = EnvBannerConfig.from_env()
        assert config.environment == Environment.LOCAL
    
    def test_from_env_dev(self, monkeypatch):
        monkeypatch.setenv("ENVIRONMENT", "dev")
        config = EnvBannerConfig.from_env()
        assert config.environment == Environment.DEVELOPMENT
    
    def test_from_env_development(self, monkeypatch):
        monkeypatch.setenv("ENVIRONMENT", "development")
        config = EnvBannerConfig.from_env()
        assert config.environment == Environment.DEVELOPMENT
    
    def test_from_env_stage(self, monkeypatch):
        monkeypatch.setenv("ENVIRONMENT", "stage")
        config = EnvBannerConfig.from_env()
        assert config.environment == Environment.STAGING
    
    def test_from_env_staging(self, monkeypatch):
        monkeypatch.setenv("ENVIRONMENT", "staging")
        config = EnvBannerConfig.from_env()
        assert config.environment == Environment.STAGING
    
    def test_from_env_prod(self, monkeypatch):
        monkeypatch.setenv("ENVIRONMENT", "prod")
        config = EnvBannerConfig.from_env()
        assert config.environment == Environment.PRODUCTION
    
    def test_from_env_production(self, monkeypatch):
        monkeypatch.setenv("ENVIRONMENT", "production")
        config = EnvBannerConfig.from_env()
        assert config.environment == Environment.PRODUCTION
    
    def test_from_env_test(self, monkeypatch):
        monkeypatch.setenv("ENVIRONMENT", "test")
        config = EnvBannerConfig.from_env()
        assert config.environment == Environment.TESTING
    
    def test_from_env_testing(self, monkeypatch):
        monkeypatch.setenv("ENVIRONMENT", "testing")
        config = EnvBannerConfig.from_env()
        assert config.environment == Environment.TESTING
    
    def test_from_env_case_insensitive(self, monkeypatch):
        monkeypatch.setenv("ENVIRONMENT", "STAGING")
        config = EnvBannerConfig.from_env()
        assert config.environment == Environment.STAGING
    
    def test_from_env_default_when_not_set(self, monkeypatch):
        monkeypatch.delenv("ENVIRONMENT", raising=False)
        config = EnvBannerConfig.from_env()
        assert config.environment == Environment.LOCAL
    
    def test_from_env_unknown_value(self, monkeypatch):
        monkeypatch.setenv("ENVIRONMENT", "unknown")
        config = EnvBannerConfig.from_env()
        assert config.environment == Environment.LOCAL
    
    def test_from_env_custom_var_name(self, monkeypatch):
        monkeypatch.setenv("CUSTOM_ENV", "staging")
        config = EnvBannerConfig.from_env(env_var="CUSTOM_ENV")
        assert config.environment == Environment.STAGING


class TestGetBannerColor: 
    def test_local_color(self):
        config = EnvBannerConfig(environment=Environment.LOCAL)
        assert config.get_banner_color() == "#4CAF50"
    
    def test_development_color(self):
        config = EnvBannerConfig(environment=Environment.DEVELOPMENT)
        assert config.get_banner_color() == "#2196F3"
    
    def test_staging_color(self):
        config = EnvBannerConfig(environment=Environment.STAGING)
        assert config.get_banner_color() == "#FF9800"
    
    def test_production_color(self):
        config = EnvBannerConfig(environment=Environment.PRODUCTION)
        assert config.get_banner_color() == "#F44336"
    
    def test_testing_color(self):
        config = EnvBannerConfig(environment=Environment.TESTING)
        assert config.get_banner_color() == "#9C27B0"
    
    def test_custom_color_overrides_default(self):
        config = EnvBannerConfig(
            environment=Environment.LOCAL,
            custom_color="#123456"
        )
        assert config.get_banner_color() == "#123456"


class TestGetBannerText: 
    def test_local_text(self):
        config = EnvBannerConfig(environment=Environment.LOCAL)
        assert config.get_banner_text() == "LOCAL ENVIRONMENT"
    
    def test_development_text(self):
        config = EnvBannerConfig(environment=Environment.DEVELOPMENT)
        assert config.get_banner_text() == "DEVELOPMENT ENVIRONMENT"
    
    def test_staging_text(self):
        config = EnvBannerConfig(environment=Environment.STAGING)
        assert config.get_banner_text() == "STAGING ENVIRONMENT"
    
    def test_production_text(self):
        config = EnvBannerConfig(environment=Environment.PRODUCTION)
        assert config.get_banner_text() == "PRODUCTION ENVIRONMENT"
    
    def test_testing_text(self):
        config = EnvBannerConfig(environment=Environment.TESTING)
        assert config.get_banner_text() == "TESTING ENVIRONMENT"
    
    def test_custom_text_overrides_default(self):
        config = EnvBannerConfig(
            environment=Environment.LOCAL,
            custom_text="CUSTOM BANNER TEXT"
        )
        assert config.get_banner_text() == "CUSTOM BANNER TEXT"
