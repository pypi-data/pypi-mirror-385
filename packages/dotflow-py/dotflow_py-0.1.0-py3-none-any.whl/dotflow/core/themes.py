"""
Theme definitions for consistent styling.
"""

from enum import Enum
from typing import Dict, Any
from .models import NodeStyle, EdgeStyleConfig, EdgeStyle


class Theme(Enum):
    """Data models for ThemeManager"""

    DEFAULT = "default"
    DARK = "dark"
    COLORFUL = "colorful"
    MONOCHROME = "monochrome"
    BLUE = "blue"
    GREEN = "green"


class ThemeManager:
    """Manage theme configurations."""

    _themes: Dict[Theme, Dict[str, Any]] = {
        Theme.DEFAULT: {
            "bg_color": "white",
            "node_style": NodeStyle(
                color="black", fillcolor="white", fontcolor="black"
            ),
            "edge_style": EdgeStyleConfig(color="black", fontcolor="black"),
        },
        Theme.DARK: {
            "bg_color": "#1a202c",
            "node_style": NodeStyle(
                color="white", fillcolor="#2d3748", fontcolor="white"
            ),
            "edge_style": EdgeStyleConfig(color="#cbd5e0", fontcolor="#cbd5e0"),
        },
        Theme.COLORFUL: {
            "bg_color": "#f7fafc",
            "node_style": NodeStyle(
                color="#2d3748", fillcolor="#ecc94b", fontcolor="#2d3748"
            ),
            "edge_style": EdgeStyleConfig(color="#4a5568", fontcolor="#4a5568"),
        },
        Theme.BLUE: {
            "bg_color": "#f0f9ff",
            "node_style": NodeStyle(
                color="#1e40af", fillcolor="#dbeafe", fontcolor="#1e3a8a"
            ),
            "edge_style": EdgeStyleConfig(color="#3b82f6", fontcolor="#1e40af"),
        },
        Theme.GREEN: {
            "bg_color": "#f0fdf4",
            "node_style": NodeStyle(
                color="#166534", fillcolor="#dcfce7", fontcolor="#166534"
            ),
            "edge_style": EdgeStyleConfig(color="#22c55e", fontcolor="#166534"),
        },
        Theme.MONOCHROME: {
            "bg_color": "white",
            "node_style": NodeStyle(
                color="black", fillcolor="white", fontcolor="black"
            ),
            "edge_style": EdgeStyleConfig(color="black", fontcolor="black"),
        },
    }

    @classmethod
    def get_theme_config(cls, theme: Theme) -> Dict[str, Any]:
        """Get configuration for a specific theme."""
        return cls._themes.get(theme, cls._themes[Theme.DEFAULT])

    @classmethod
    def register_theme(cls, name: str, config: Dict[str, Any]) -> Theme:
        """Register a custom theme."""
        theme = Theme(name)
        cls._themes[theme] = config
        return theme
