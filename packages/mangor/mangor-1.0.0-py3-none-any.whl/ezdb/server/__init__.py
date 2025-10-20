"""
EzDB REST API Server
"""
from .app import create_app
from .models import *

__all__ = ["create_app"]
