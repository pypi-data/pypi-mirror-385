"""
Wasapaso Python SDK

SDK oficial de Python para la API de Wasapaso.
Proporciona una interfaz sencilla y type-safe para gestionar sesiones de WhatsApp
y enviar mensajes a través de la plataforma Wasapaso.

Example:
    >>> from wasapaso import WasapasoClient
    >>> client = WasapasoClient(api_key="wsk_your_api_key")
    >>> session = client.sessions.create(name="Mi Sesión")
    >>> print(session.id)
"""

from wasapaso.client import WasapasoClient
from wasapaso.exceptions import (
    WasapasoError,
    AuthenticationError,
    ValidationError,
    RateLimitError,
    NotFoundError,
    PermissionError as WasapasoPermissionError,
)

__version__ = "0.1.0"
__all__ = [
    "WasapasoClient",
    "WasapasoError",
    "AuthenticationError",
    "ValidationError",
    "RateLimitError",
    "NotFoundError",
    "WasapasoPermissionError",
]
