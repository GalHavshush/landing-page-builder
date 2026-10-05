"""sitegen: turns a site document into static files. Must never import web or DB code."""

from sitegen.builder import BuildResult, build
from sitegen.renderer import AssetFile, Issue
from sitegen.schema import SiteDocument

__version__ = "0.0.0"
__all__ = ["AssetFile", "BuildResult", "Issue", "SiteDocument", "build"]
