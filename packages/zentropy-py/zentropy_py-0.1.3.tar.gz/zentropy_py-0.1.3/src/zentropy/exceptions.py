class ZentropyError(Exception):
    """Base exception for zentropy client"""

class AuthError(ZentropyError):
    """Authentication failed"""

class ConnectionError(ZentropyError):
    """Connection related errors"""