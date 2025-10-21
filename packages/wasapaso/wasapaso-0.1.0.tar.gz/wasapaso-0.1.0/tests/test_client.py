"""Tests para el cliente principal de Wasapaso."""

import pytest
from wasapaso import WasapasoClient
from wasapaso.exceptions import WasapasoError


def test_client_initialization():
    """Test de inicialización del cliente."""
    client = WasapasoClient(api_key="wsk_test_key_1234567890abcdef")
    assert client is not None
    assert "wsk_" in client.api_key


def test_client_invalid_api_key_empty():
    """Test con API key vacía."""
    with pytest.raises(ValueError, match="API key is required"):
        WasapasoClient(api_key="")


def test_client_invalid_api_key_format():
    """Test con formato de API key inválido."""
    with pytest.raises(ValueError, match="Invalid API key format"):
        WasapasoClient(api_key="invalid_key_format")


def test_client_has_resources():
    """Test que el cliente tiene los recursos necesarios."""
    client = WasapasoClient(api_key="wsk_test_key_1234567890abcdef")
    assert hasattr(client, "sessions")
    assert hasattr(client, "messages")


def test_client_repr():
    """Test de representación del cliente."""
    client = WasapasoClient(api_key="wsk_test_key_1234567890abcdef")
    repr_str = repr(client)
    assert "WasapasoClient" in repr_str
    assert "wsk_****" in repr_str
