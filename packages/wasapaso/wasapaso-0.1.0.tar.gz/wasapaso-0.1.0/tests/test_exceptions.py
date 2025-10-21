"""Tests para las excepciones personalizadas."""

import pytest
from wasapaso.exceptions import (
    WasapasoError,
    AuthenticationError,
    ValidationError,
    PermissionError,
    NotFoundError,
    RateLimitError,
    ServerError,
    handle_error_response,
)


def test_wasapaso_error():
    """Test de la excepción base."""
    error = WasapasoError("Test error", status_code=400)
    assert str(error) == "[400] Test error"
    assert error.status_code == 400
    assert error.message == "Test error"


def test_authentication_error():
    """Test de error de autenticación."""
    error = AuthenticationError()
    assert error.status_code == 401
    assert "Authentication failed" in error.message


def test_validation_error():
    """Test de error de validación."""
    error = ValidationError()
    assert error.status_code == 400
    assert "Validation error" in error.message


def test_permission_error():
    """Test de error de permisos."""
    error = PermissionError()
    assert error.status_code == 403
    assert "Permission denied" in error.message


def test_not_found_error():
    """Test de error 404."""
    error = NotFoundError()
    assert error.status_code == 404
    assert "not found" in error.message


def test_rate_limit_error():
    """Test de error de límite de tasa."""
    error = RateLimitError()
    assert error.status_code == 429
    assert "Rate limit" in error.message


def test_server_error():
    """Test de error del servidor."""
    error = ServerError()
    assert error.status_code == 500
    assert "Server error" in error.message


def test_handle_error_response_401():
    """Test de manejo de error 401."""
    response_data = {"message": "Invalid API key"}
    error = handle_error_response(401, response_data)
    assert isinstance(error, AuthenticationError)
    assert error.message == "Invalid API key"


def test_handle_error_response_403():
    """Test de manejo de error 403."""
    response_data = {"message": "Access denied"}
    error = handle_error_response(403, response_data)
    assert isinstance(error, PermissionError)


def test_handle_error_response_404():
    """Test de manejo de error 404."""
    response_data = {"message": "Session not found"}
    error = handle_error_response(404, response_data)
    assert isinstance(error, NotFoundError)


def test_handle_error_response_400():
    """Test de manejo de error 400."""
    response_data = {"message": "Invalid parameters"}
    error = handle_error_response(400, response_data)
    assert isinstance(error, ValidationError)


def test_handle_error_response_429():
    """Test de manejo de error 429."""
    response_data = {"message": "Too many requests"}
    error = handle_error_response(429, response_data)
    assert isinstance(error, RateLimitError)


def test_handle_error_response_500():
    """Test de manejo de error 500."""
    response_data = {"message": "Internal server error"}
    error = handle_error_response(500, response_data)
    assert isinstance(error, ServerError)


def test_error_repr():
    """Test de representación de error."""
    error = WasapasoError("Test", status_code=400)
    repr_str = repr(error)
    assert "WasapasoError" in repr_str
    assert "400" in repr_str
