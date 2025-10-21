"""ZnDraw communication package with physical-to-logical frame mapping."""

import logging

from zndraw.server import create_app
from zndraw.zndraw import ZnDraw
import importlib.metadata

__all__ = ["ZnDraw", "create_app"]

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
log.addHandler(handler)

__version__ = importlib.metadata.version("zndraw")
