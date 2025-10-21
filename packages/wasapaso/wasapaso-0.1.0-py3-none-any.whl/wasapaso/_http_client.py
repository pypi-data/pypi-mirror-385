"""Cliente HTTP base para comunicación con la API de Wasapaso."""

import json
from typing import Any, Dict, Optional, Union

import httpx

from wasapaso.exceptions import (
    ConnectionError,
    TimeoutError,
    WasapasoError,
    handle_error_response,
)


class HTTPClient:
    """Cliente HTTP base para realizar peticiones a la API."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.wasapaso.com",
        timeout: float = 30.0,
    ) -> None:
        """
        Inicializa el cliente HTTP.

        Args:
            api_key: API key para autenticación
            base_url: URL base de la API
            timeout: Timeout por defecto para las peticiones (en segundos)
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

        # Headers por defecto
        self._headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "wasapaso-python/0.1.0",
        }

    def _get_url(self, path: str) -> str:
        """Construye la URL completa."""
        return f"{self.base_url}/api/v1/{path.lstrip('/')}"

    def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """
        Procesa la respuesta HTTP y maneja errores.

        Args:
            response: Respuesta HTTP de httpx

        Returns:
            Datos de la respuesta como diccionario

        Raises:
            WasapasoError: Si hay un error en la respuesta
        """
        try:
            data = response.json()
        except json.JSONDecodeError:
            data = {"error": "Invalid JSON response", "raw": response.text}

        # Si el status code indica error
        if response.status_code >= 400:
            raise handle_error_response(response.status_code, data)

        return data

    def request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Realiza una petición HTTP síncrona.

        Args:
            method: Método HTTP (GET, POST, PUT, DELETE, etc.)
            path: Path del endpoint (relativo a /api/v1/)
            params: Parámetros de query string
            json_data: Datos JSON para el body
            timeout: Timeout específico para esta petición

        Returns:
            Datos de la respuesta

        Raises:
            WasapasoError: Si hay un error en la petición
        """
        url = self._get_url(path)
        timeout_value = timeout or self.timeout

        try:
            with httpx.Client(timeout=timeout_value) as client:
                response = client.request(
                    method=method,
                    url=url,
                    headers=self._headers,
                    params=params,
                    json=json_data,
                )
                return self._handle_response(response)

        except httpx.TimeoutException as e:
            raise TimeoutError(f"Request timed out after {timeout_value}s") from e
        except httpx.ConnectError as e:
            raise ConnectionError(f"Failed to connect to {url}") from e
        except httpx.HTTPError as e:
            raise WasapasoError(f"HTTP error occurred: {str(e)}") from e

    async def request_async(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Realiza una petición HTTP asíncrona.

        Args:
            method: Método HTTP (GET, POST, PUT, DELETE, etc.)
            path: Path del endpoint (relativo a /api/v1/)
            params: Parámetros de query string
            json_data: Datos JSON para el body
            timeout: Timeout específico para esta petición

        Returns:
            Datos de la respuesta

        Raises:
            WasapasoError: Si hay un error en la petición
        """
        url = self._get_url(path)
        timeout_value = timeout or self.timeout

        try:
            async with httpx.AsyncClient(timeout=timeout_value) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=self._headers,
                    params=params,
                    json=json_data,
                )
                return self._handle_response(response)

        except httpx.TimeoutException as e:
            raise TimeoutError(f"Request timed out after {timeout_value}s") from e
        except httpx.ConnectError as e:
            raise ConnectionError(f"Failed to connect to {url}") from e
        except httpx.HTTPError as e:
            raise WasapasoError(f"HTTP error occurred: {str(e)}") from e

    # Métodos de conveniencia para HTTP
    def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Realiza una petición GET síncrona."""
        return self.request("GET", path, params=params, timeout=timeout)

    async def get_async(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Realiza una petición GET asíncrona."""
        return await self.request_async("GET", path, params=params, timeout=timeout)

    def post(
        self,
        path: str,
        json_data: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Realiza una petición POST síncrona."""
        return self.request("POST", path, json_data=json_data, timeout=timeout)

    async def post_async(
        self,
        path: str,
        json_data: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Realiza una petición POST asíncrona."""
        return await self.request_async("POST", path, json_data=json_data, timeout=timeout)

    def put(
        self,
        path: str,
        json_data: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Realiza una petición PUT síncrona."""
        return self.request("PUT", path, json_data=json_data, timeout=timeout)

    async def put_async(
        self,
        path: str,
        json_data: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Realiza una petición PUT asíncrona."""
        return await self.request_async("PUT", path, json_data=json_data, timeout=timeout)

    def patch(
        self,
        path: str,
        json_data: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Realiza una petición PATCH síncrona."""
        return self.request("PATCH", path, json_data=json_data, timeout=timeout)

    async def patch_async(
        self,
        path: str,
        json_data: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Realiza una petición PATCH asíncrona."""
        return await self.request_async("PATCH", path, json_data=json_data, timeout=timeout)

    def delete(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Realiza una petición DELETE síncrona."""
        return self.request("DELETE", path, params=params, timeout=timeout)

    async def delete_async(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Realiza una petición DELETE asíncrona."""
        return await self.request_async("DELETE", path, params=params, timeout=timeout)
