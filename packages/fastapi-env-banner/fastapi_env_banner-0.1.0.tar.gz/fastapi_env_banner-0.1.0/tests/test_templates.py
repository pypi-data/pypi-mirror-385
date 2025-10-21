"""Tests for templates module."""

import pytest

from fastapi_env_banner.templates import (
    get_banner_styles,
    get_swagger_banner_styles,
    render_banner,
    render_swagger_banner,
)


class TestGetBannerStyles:
    """Tests for get_banner_styles function."""
    
    def test_styles_with_top_position(self):
        """Test that styles include top position."""
        styles = get_banner_styles("#4CAF50", "top")
        
        assert "top: 0;" in styles
        assert "bottom: 0;" not in styles
        assert "background-color: #4CAF50;" in styles
        assert "position: fixed;" in styles
        assert "z-index: 999999;" in styles
    
    def test_styles_with_bottom_position(self):
        """Test that styles include bottom position."""
        styles = get_banner_styles("#FF9800", "bottom")
        
        assert "bottom: 0;" in styles
        assert "top: 0;" not in styles
        assert "background-color: #FF9800;" in styles
    
    def test_styles_include_all_required_properties(self):
        """Test that all required CSS properties are included."""
        styles = get_banner_styles("#123456", "top")
        
        required_properties = [
            "position: fixed;",
            "left: 0;",
            "right: 0;",
            "color: white;",
            "text-align: center;",
            "font-weight: 600;",
            "z-index: 999999;",
        ]
        
        for prop in required_properties:
            assert prop in styles
    
    def test_custom_color_is_applied(self):
        """Test that custom color is properly applied."""
        custom_color = "#ABCDEF"
        styles = get_banner_styles(custom_color, "top")
        
        assert f"background-color: {custom_color};" in styles


class TestGetSwaggerBannerStyles:
    """Tests for get_swagger_banner_styles function."""
    
    def test_swagger_styles_with_top_position(self):
        """Test Swagger styles with top position."""
        styles = get_swagger_banner_styles("#2196F3", "top")
        
        assert "top: 0;" in styles
        assert "bottom: 0;" not in styles
        assert "background-color: #2196F3;" in styles
    
    def test_swagger_styles_with_bottom_position(self):
        """Test Swagger styles with bottom position."""
        styles = get_swagger_banner_styles("#E91E63", "bottom")
        
        assert "bottom: 0;" in styles
        assert "top: 0;" not in styles
        assert "background-color: #E91E63;" in styles
    
    def test_swagger_styles_include_required_properties(self):
        """Test that Swagger styles include all required properties."""
        styles = get_swagger_banner_styles("#123456", "top")
        
        required_properties = [
            "position: fixed;",
            "left: 0;",
            "right: 0;",
            "color: white;",
            "text-align: center;",
            "z-index: 999999;",
        ]
        
        for prop in required_properties:
            assert prop in styles


class TestRenderBanner:
    """Tests for render_banner function."""
    
    def test_render_banner_basic(self):
        """Test basic banner rendering."""
        html = render_banner("TEST ENVIRONMENT", "#4CAF50", "top")
        
        assert "TEST ENVIRONMENT" in html
        assert "#4CAF50" in html
        assert "env-banner" in html
        assert "⚠️" in html
    
    def test_render_banner_top_position(self):
        """Test banner with top position."""
        html = render_banner("LOCAL", "#4CAF50", "top")
        
        assert "top: 0;" in html
        assert "padding-top: 40px !important;" in html
        assert "padding-bottom" not in html
    
    def test_render_banner_bottom_position(self):
        """Test banner with bottom position."""
        html = render_banner("STAGING", "#FF9800", "bottom")
        
        assert "bottom: 0;" in html
        assert "padding-bottom: 40px !important;" in html
        assert "padding-top" not in html
    
    def test_render_banner_contains_style_tag(self):
        """Test that rendered banner contains style tag."""
        html = render_banner("TEST", "#123456", "top")
        
        assert "<style>" in html
        assert "</style>" in html
        assert "body {" in html
    
    def test_render_banner_contains_div(self):
        """Test that rendered banner contains div element."""
        html = render_banner("TEST", "#123456", "top")
        
        assert '<div id="env-banner"' in html
        assert "</div>" in html
    
    def test_render_banner_with_special_characters(self):
        """Test banner rendering with special characters in text."""
        html = render_banner("TEST & DEVELOPMENT", "#4CAF50", "top")
        
        assert "TEST & DEVELOPMENT" in html
    
    def test_render_banner_with_custom_color(self):
        """Test banner with custom hex color."""
        custom_color = "#ABCDEF"
        html = render_banner("CUSTOM", custom_color, "top")
        
        assert custom_color in html


class TestRenderSwaggerBanner:
    """Tests for render_swagger_banner function."""
    
    def test_render_swagger_banner_basic(self):
        """Test basic Swagger banner rendering."""
        html = render_swagger_banner("DEVELOPMENT", "#2196F3", "top")
        
        assert "DEVELOPMENT" in html
        assert "#2196F3" in html
        assert "env-banner-swagger" in html
        assert "⚠️" in html
    
    def test_render_swagger_banner_top_position(self):
        """Test Swagger banner with top position."""
        html = render_swagger_banner("LOCAL", "#4CAF50", "top")
        
        assert "top: 0;" in html
        assert "padding-top: 50px;" in html
        assert "padding-bottom" not in html
    
    def test_render_swagger_banner_bottom_position(self):
        """Test Swagger banner with bottom position."""
        html = render_swagger_banner("STAGING", "#FF9800", "bottom")
        
        assert "bottom: 0;" in html
        assert "padding-bottom: 50px;" in html
        assert "padding-top" not in html
    
    def test_render_swagger_banner_contains_style_tag(self):
        """Test that Swagger banner contains style tag."""
        html = render_swagger_banner("TEST", "#123456", "top")
        
        assert "<style>" in html
        assert "</style>" in html
        assert ".swagger-ui {" in html
    
    def test_render_swagger_banner_contains_div(self):
        """Test that Swagger banner contains div element."""
        html = render_swagger_banner("TEST", "#123456", "top")
        
        assert '<div id="env-banner-swagger"' in html
        assert "</div>" in html
    
    def test_render_swagger_banner_different_padding(self):
        """Test that Swagger banner uses different padding than regular banner."""
        regular_html = render_banner("TEST", "#123456", "top")
        swagger_html = render_swagger_banner("TEST", "#123456", "top")
        
        assert "padding-top: 40px" in regular_html
        assert "padding-top: 50px" in swagger_html
    
    def test_render_swagger_banner_with_long_text(self):
        """Test Swagger banner with long text."""
        long_text = "THIS IS A VERY LONG ENVIRONMENT NAME FOR TESTING"
        html = render_swagger_banner(long_text, "#123456", "top")
        
        assert long_text in html


class TestTemplateEdgeCases:
    """Tests for edge cases in template rendering."""
    
    def test_empty_text(self):
        """Test rendering with empty text."""
        html = render_banner("", "#4CAF50", "top")
        
        assert "env-banner" in html
        assert "#4CAF50" in html
    
    def test_very_long_text(self):
        """Test rendering with very long text."""
        long_text = "A" * 200
        html = render_banner(long_text, "#4CAF50", "top")
        
        assert long_text in html
    
    def test_text_with_html_entities(self):
        """Test rendering with HTML entities in text."""
        html = render_banner("<script>alert('xss')</script>", "#4CAF50", "top")
        
        assert "<script>alert('xss')</script>" in html
    
    def test_invalid_position_defaults_to_bottom(self):
        """Test that invalid position is handled gracefully."""
        html = render_banner("TEST", "#4CAF50", "invalid")
        
        assert "bottom: 0;" in html
        assert "padding-bottom: 40px !important;" in html
    
    def test_color_without_hash(self):
        """Test color without # prefix."""
        html = render_banner("TEST", "4CAF50", "top")
        
        assert "4CAF50" in html
    
    def test_uppercase_position(self):
        """Test position with uppercase."""
        html = render_banner("TEST", "#4CAF50", "TOP")
        
        assert "bottom: 0;" in html


class TestTemplateConsistency:
    """Tests for consistency between regular and Swagger templates."""
    
    def test_both_templates_use_same_color(self):
        """Test that both templates use the same color."""
        color = "#123456"
        regular = render_banner("TEST", color, "top")
        swagger = render_swagger_banner("TEST", color, "top")
        
        assert color in regular
        assert color in swagger
    
    def test_both_templates_use_same_text(self):
        """Test that both templates use the same text."""
        text = "CUSTOM ENVIRONMENT"
        regular = render_banner(text, "#123456", "top")
        swagger = render_swagger_banner(text, "#123456", "top")
        
        assert text in regular
        assert text in swagger
    
    def test_both_templates_have_warning_emoji(self):
        """Test that both templates include warning emoji."""
        regular = render_banner("TEST", "#123456", "top")
        swagger = render_swagger_banner("TEST", "#123456", "top")
        
        assert "⚠️" in regular
        assert "⚠️" in swagger
    
    def test_different_banner_ids(self):
        """Test that regular and Swagger banners have different IDs."""
        regular = render_banner("TEST", "#123456", "top")
        swagger = render_swagger_banner("TEST", "#123456", "top")
        
        assert "env-banner" in regular
        assert "env-banner-swagger" in swagger
        assert regular != swagger
