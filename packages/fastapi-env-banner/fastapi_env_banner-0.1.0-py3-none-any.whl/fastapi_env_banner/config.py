import os
from enum import Enum
from typing import Optional
from dataclasses import dataclass


class Environment(str, Enum):
    LOCAL = "local"
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


@dataclass
class EnvBannerConfig:
    """Configuration for the environment banner.
    
    Args:
        environment: The current environment (local, development, staging, production, testing)
        enabled: Whether to show the banner (default: True)
        custom_text: Custom text to display in the banner (optional)
        custom_color: Custom background color for the banner (optional, hex format)
        position: Banner position - 'top' or 'bottom' (default: 'top')
        show_in_swagger: Whether to show banner in Swagger UI (default: True)
    """
    
    environment: Environment = Environment.LOCAL
    enabled: bool = True
    custom_text: Optional[str] = None
    custom_color: Optional[str] = None
    position: str = "top"
    show_in_swagger: bool = True
    
    @classmethod
    def from_env(cls, env_var: str = "ENVIRONMENT") -> "EnvBannerConfig":
        env_value = os.getenv(env_var, "local").lower()
        
        env_mapping = {
            "local": Environment.LOCAL,
            "dev": Environment.DEVELOPMENT,
            "development": Environment.DEVELOPMENT,
            "stage": Environment.STAGING,
            "staging": Environment.STAGING,
            "prod": Environment.PRODUCTION,
            "production": Environment.PRODUCTION,
            "test": Environment.TESTING,
            "testing": Environment.TESTING,
        }
        
        environment = env_mapping.get(env_value, Environment.LOCAL)
        
        return cls(environment=environment)
    
    def get_banner_color(self) -> str:
        if self.custom_color:
            return self.custom_color
            
        color_map = {
            Environment.LOCAL: "#4CAF50",  # Green
            Environment.DEVELOPMENT: "#2196F3",  # Blue
            Environment.STAGING: "#FF9800",  # Orange
            Environment.PRODUCTION: "#F44336",  # Red
            Environment.TESTING: "#9C27B0",  # Purple
        }
        
        return color_map.get(self.environment, "#4CAF50")
    
    def get_banner_text(self) -> str:
        if self.custom_text:
            return self.custom_text
            
        text_map = {
            Environment.LOCAL: "LOCAL ENVIRONMENT",
            Environment.DEVELOPMENT: "DEVELOPMENT ENVIRONMENT",
            Environment.STAGING: "STAGING ENVIRONMENT",
            Environment.PRODUCTION: "PRODUCTION ENVIRONMENT",
            Environment.TESTING: "TESTING ENVIRONMENT",
        }
        
        return text_map.get(self.environment, "UNKNOWN ENVIRONMENT")
