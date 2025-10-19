"""
Zentropy Client
A simple client for Zentropy server.
"""

from .client import Client
from .exceptions import AuthError, ConnectionError

__all__ = ["Client", "AuthError", "ConnectionError"]
__version__ = "0.1.0"