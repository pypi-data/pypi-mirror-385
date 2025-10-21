"""Cliente principal del SDK de Wasapaso."""

from typing import Optional

from wasapaso._http_client import HTTPClient
from wasapaso.resources.messages import MessagesResource
from wasapaso.resources.sessions import SessionsResource


class WasapasoClient:
    """
    Cliente principal para interactuar con la API de Wasapaso.

    Example:
        Uso básico:
        >>> from wasapaso import WasapasoClient
        >>> client = WasapasoClient(api_key="wsk_your_api_key_here")
        >>>
        >>> # Crear una sesión
        >>> session = client.sessions.create({"name": "Mi Sesión"})
        >>>
        >>> # Enviar un mensaje
        >>> result = client.messages.send_text(
        ...     session_id=session.id,
        ...     to="1234567890",
        ...     message="Hola desde Wasapaso!"
        ... )

        Uso asíncrono:
        >>> import asyncio
        >>> from wasapaso import WasapasoClient
        >>>
        >>> async def main():
        ...     client = WasapasoClient(api_key="wsk_your_api_key_here")
        ...     session = await client.sessions.create_async({"name": "Mi Sesión"})
        ...     result = await client.messages.send_text_async(
        ...         session_id=session.id,
        ...         to="1234567890",
        ...         message="Hola async!"
        ...     )
        >>>
        >>> asyncio.run(main())
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.wasapaso.com",
        timeout: float = 30.0,
    ) -> None:
        """
        Inicializa el cliente de Wasapaso.

        Args:
            api_key: Tu API key de Wasapaso (comienza con 'wsk_')
            base_url: URL base de la API (opcional, usa el default en producción)
            timeout: Timeout por defecto para las peticiones en segundos

        Raises:
            ValueError: Si la API key está vacía o es inválida
        """
        if not api_key or not isinstance(api_key, str):
            raise ValueError("API key is required and must be a string")

        if not api_key.startswith("wsk_"):
            raise ValueError(
                "Invalid API key format. API keys should start with 'wsk_'. "
                "Get your API key from https://wasapaso.com/dashboard/api-keys"
            )

        # Cliente HTTP
        self._http_client = HTTPClient(api_key=api_key, base_url=base_url, timeout=timeout)

        # Recursos de la API
        self.sessions = SessionsResource(self._http_client)
        self.messages = MessagesResource(self._http_client)

    @property
    def api_key(self) -> str:
        """Obtiene la API key (solo muestra los últimos 4 caracteres)."""
        key = self._http_client.api_key
        if len(key) > 8:
            return f"wsk_****{key[-4:]}"
        return "wsk_****"

    def health_check(self) -> dict:
        """
        Verifica el estado de la API.

        Returns:
            Información sobre el estado de la API

        Example:
            >>> status = client.health_check()
            >>> print(status["message"])
        """
        return self._http_client.get("health")

    async def health_check_async(self) -> dict:
        """Versión asíncrona de health_check()."""
        return await self._http_client.get_async("health")

    def get_status(self) -> dict:
        """
        Obtiene información sobre tu API key y permisos.

        Returns:
            Información sobre la API key autenticada

        Example:
            >>> info = client.get_status()
            >>> print(info["apiKey"]["name"])
            >>> print(info["apiKey"]["permissions"])
        """
        return self._http_client.get("status")

    async def get_status_async(self) -> dict:
        """Versión asíncrona de get_status()."""
        return await self._http_client.get_async("status")

    def __repr__(self) -> str:
        """Representación del cliente."""
        return f"WasapasoClient(api_key='{self.api_key}')"
