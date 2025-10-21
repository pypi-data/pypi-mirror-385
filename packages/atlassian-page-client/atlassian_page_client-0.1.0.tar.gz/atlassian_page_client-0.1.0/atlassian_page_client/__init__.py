"""
A Python client library for interacting with Atlassian Confluence pages.

This library provides a simple interface to read and modify Confluence pages
through the Atlassian REST API.
"""

from .client import AtlassianPageClient
from .page import AtlassianPage
from .content import AtlassianPageContent

__version__ = "0.1.0"
__author__ = "Yannick Zimmermann"
__email__ = "yannick.zimmermann@proton.me"

__all__ = ["AtlassianPageClient", "AtlassianPage", "AtlassianPageContent"]
