"""Excepciones personalizadas para el SDK de Wasapaso."""

from typing import Any, Dict, Optional


class WasapasoError(Exception):
    """Clase base para todas las excepciones del SDK de Wasapaso."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Inicializa una excepción de Wasapaso.

        Args:
            message: Mensaje de error descriptivo
            status_code: Código de estado HTTP (si aplica)
            response_data: Datos de la respuesta del servidor
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}

    def __str__(self) -> str:
        """Representación en string del error."""
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message

    def __repr__(self) -> str:
        """Representación técnica del error."""
        return (
            f"{self.__class__.__name__}("
            f"message={self.message!r}, "
            f"status_code={self.status_code!r})"
        )


class AuthenticationError(WasapasoError):
    """Error de autenticación - API key inválida o expirada."""

    def __init__(
        self,
        message: str = "Authentication failed. Check your API key.",
        status_code: int = 401,
        response_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Inicializa un error de autenticación."""
        super().__init__(message, status_code, response_data)


class ValidationError(WasapasoError):
    """Error de validación - parámetros inválidos o faltantes."""

    def __init__(
        self,
        message: str = "Validation error. Check your request parameters.",
        status_code: int = 400,
        response_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Inicializa un error de validación."""
        super().__init__(message, status_code, response_data)


class PermissionError(WasapasoError):
    """Error de permisos - la API key no tiene permisos suficientes."""

    def __init__(
        self,
        message: str = "Permission denied. Your API key lacks required permissions.",
        status_code: int = 403,
        response_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Inicializa un error de permisos."""
        super().__init__(message, status_code, response_data)


class NotFoundError(WasapasoError):
    """Error 404 - recurso no encontrado."""

    def __init__(
        self,
        message: str = "Resource not found.",
        status_code: int = 404,
        response_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Inicializa un error de recurso no encontrado."""
        super().__init__(message, status_code, response_data)


class RateLimitError(WasapasoError):
    """Error de límite de tasa - demasiadas peticiones."""

    def __init__(
        self,
        message: str = "Rate limit exceeded. Please try again later.",
        status_code: int = 429,
        response_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Inicializa un error de límite de tasa."""
        super().__init__(message, status_code, response_data)


class ServerError(WasapasoError):
    """Error del servidor (5xx)."""

    def __init__(
        self,
        message: str = "Server error. Please try again later.",
        status_code: int = 500,
        response_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Inicializa un error del servidor."""
        super().__init__(message, status_code, response_data)


class ConnectionError(WasapasoError):
    """Error de conexión con la API."""

    def __init__(
        self,
        message: str = "Failed to connect to Wasapaso API.",
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Inicializa un error de conexión."""
        super().__init__(message, status_code, response_data)


class TimeoutError(WasapasoError):
    """Error de timeout en la petición."""

    def __init__(
        self,
        message: str = "Request timed out.",
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Inicializa un error de timeout."""
        super().__init__(message, status_code, response_data)


def handle_error_response(status_code: int, response_data: Dict[str, Any]) -> WasapasoError:
    """
    Convierte una respuesta de error HTTP en la excepción apropiada.

    Args:
        status_code: Código de estado HTTP
        response_data: Datos de la respuesta de error

    Returns:
        La excepción apropiada según el código de estado
    """
    error_message = response_data.get("message", "An error occurred")

    if status_code == 401:
        return AuthenticationError(error_message, status_code, response_data)
    elif status_code == 403:
        return PermissionError(error_message, status_code, response_data)
    elif status_code == 404:
        return NotFoundError(error_message, status_code, response_data)
    elif status_code == 400 or status_code == 422:
        return ValidationError(error_message, status_code, response_data)
    elif status_code == 429:
        return RateLimitError(error_message, status_code, response_data)
    elif 500 <= status_code < 600:
        return ServerError(error_message, status_code, response_data)
    else:
        return WasapasoError(error_message, status_code, response_data)
