"""
AstroGeo - Professional Multi-Agent Space & Environmental Intelligence System
"""

__version__ = "1.0.0"
__author__ = "AstroGeo Development Team"

# Import core modules for package initialization
try:
    from .crew import AstroGeoCrew
    from .utils.config_loader import ConfigLoader
    __all__ = ['AstroGeoCrew', 'ConfigLoader']
except ImportError:
    # Graceful handling if dependencies aren't available yet
    __all__ = []
