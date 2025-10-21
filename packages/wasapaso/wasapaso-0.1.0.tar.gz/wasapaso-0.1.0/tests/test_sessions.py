"""Tests para el recurso de sesiones."""

import pytest
import respx
import httpx
from wasapaso import WasapasoClient
from wasapaso.models.session import Session, SessionStatus


@pytest.fixture
def client():
    """Fixture del cliente de Wasapaso."""
    return WasapasoClient(api_key="wsk_test_key_1234567890abcdef")


@pytest.fixture
def mock_session_response():
    """Fixture con respuesta simulada de sesión."""
    return {
        "success": True,
        "message": "Session created successfully",
        "data": {
            "id": "64abc123def456",
            "name": "Test Session",
            "sessionName": "session_user123_1234567890",
            "status": "STOPPED",
            "messageCount": 0,
            "isPaid": False,
            "metadata": {},
            "customWebhook": None,
            "webhookEvents": [],
            "createdAt": "2024-01-01T00:00:00.000Z",
            "updatedAt": "2024-01-01T00:00:00.000Z"
        }
    }


@respx.mock
def test_create_session(client, mock_session_response):
    """Test de creación de sesión."""
    route = respx.post("https://api.wasapaso.com/api/v1/sessions").mock(
        return_value=httpx.Response(200, json=mock_session_response)
    )

    session = client.sessions.create({"name": "Test Session"})

    assert route.called
    assert isinstance(session, Session)
    assert session.name == "Test Session"
    assert session.status == SessionStatus.STOPPED


@respx.mock
def test_list_sessions(client):
    """Test de listado de sesiones."""
    list_response = {
        "success": True,
        "data": [
            {
                "id": "64abc123",
                "name": "Session 1",
                "sessionName": "session_1",
                "status": "WORKING",
                "messageCount": 10,
                "isPaid": True,
                "metadata": {},
                "createdAt": "2024-01-01T00:00:00.000Z",
                "updatedAt": "2024-01-01T00:00:00.000Z"
            }
        ],
        "pagination": {
            "page": 1,
            "limit": 20,
            "total": 1,
            "pages": 1
        }
    }

    route = respx.get("https://api.wasapaso.com/api/v1/sessions").mock(
        return_value=httpx.Response(200, json=list_response)
    )

    sessions = client.sessions.list()

    assert route.called
    assert len(sessions.data) == 1
    assert sessions.data[0].name == "Session 1"
    assert sessions.pagination["total"] == 1


@respx.mock
def test_get_session(client, mock_session_response):
    """Test de obtención de sesión específica."""
    route = respx.get("https://api.wasapaso.com/api/v1/sessions/64abc123").mock(
        return_value=httpx.Response(200, json=mock_session_response)
    )

    session = client.sessions.get("64abc123")

    assert route.called
    assert isinstance(session, Session)
    assert session.id == "64abc123def456"


@respx.mock
def test_start_session(client, mock_session_response):
    """Test de inicio de sesión."""
    # Modificar la respuesta para mostrar estado STARTING
    starting_response = mock_session_response.copy()
    starting_response["data"]["status"] = "STARTING"

    route = respx.post("https://api.wasapaso.com/api/v1/sessions/64abc123/start").mock(
        return_value=httpx.Response(200, json=starting_response)
    )

    session = client.sessions.start("64abc123")

    assert route.called
    assert session.status == SessionStatus.STARTING


@respx.mock
def test_stop_session(client, mock_session_response):
    """Test de detención de sesión."""
    route = respx.post("https://api.wasapaso.com/api/v1/sessions/64abc123/stop").mock(
        return_value=httpx.Response(200, json=mock_session_response)
    )

    session = client.sessions.stop("64abc123")

    assert route.called
    assert session.status == SessionStatus.STOPPED


@respx.mock
def test_delete_session(client):
    """Test de eliminación de sesión."""
    delete_response = {
        "success": True,
        "message": "Session deleted successfully"
    }

    route = respx.delete("https://api.wasapaso.com/api/v1/sessions/64abc123").mock(
        return_value=httpx.Response(200, json=delete_response)
    )

    result = client.sessions.delete("64abc123")

    assert route.called
    assert result["success"] is True


@pytest.mark.asyncio
@respx.mock
async def test_create_session_async(client, mock_session_response):
    """Test asíncrono de creación de sesión."""
    route = respx.post("https://api.wasapaso.com/api/v1/sessions").mock(
        return_value=httpx.Response(200, json=mock_session_response)
    )

    session = await client.sessions.create_async({"name": "Test Session"})

    assert route.called
    assert isinstance(session, Session)
    assert session.name == "Test Session"
