"""Clase base para todos los recursos de la API."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wasapaso._http_client import HTTPClient


class BaseResource:
    """Clase base para recursos de la API."""

    def __init__(self, http_client: "HTTPClient") -> None:
        """
        Inicializa el recurso.

        Args:
            http_client: Cliente HTTP para realizar peticiones
        """
        self._client = http_client
