"""Recurso para gestionar sesiones de WhatsApp."""

from typing import Any, Dict, List, Optional, Union

from wasapaso.models.session import (
    PairingCode,
    QRCode,
    Session,
    SessionCreate,
    SessionList,
    SessionUpdate,
)
from wasapaso.resources.base import BaseResource


class SessionsResource(BaseResource):
    """Gestión de sesiones de WhatsApp."""

    def create(self, data: Union[SessionCreate, Dict[str, Any]]) -> Session:
        """
        Crea una nueva sesión de WhatsApp.

        Args:
            data: Datos de la sesión a crear

        Returns:
            La sesión creada

        Example:
            >>> session = client.sessions.create(
            ...     SessionCreate(
            ...         name="Mi Sesión",
            ...         webhook_url="https://myapp.com/webhook"
            ...     )
            ... )
        """
        if isinstance(data, SessionCreate):
            payload = data.model_dump(by_alias=True, exclude_none=True)
        else:
            payload = data

        response = self._client.post("sessions", json_data=payload)
        return Session(**response["data"])

    async def create_async(self, data: Union[SessionCreate, Dict[str, Any]]) -> Session:
        """Versión asíncrona de create()."""
        if isinstance(data, SessionCreate):
            payload = data.model_dump(by_alias=True, exclude_none=True)
        else:
            payload = data

        response = await self._client.post_async("sessions", json_data=payload)
        return Session(**response["data"])

    def list(
        self, page: int = 1, limit: int = 20, status: Optional[str] = None
    ) -> SessionList:
        """
        Lista todas las sesiones del usuario.

        Args:
            page: Número de página
            limit: Cantidad de resultados por página
            status: Filtrar por estado (opcional)

        Returns:
            Lista paginada de sesiones

        Example:
            >>> sessions = client.sessions.list(page=1, limit=10)
            >>> for session in sessions.data:
            ...     print(session.name)
        """
        params = {"page": page, "limit": limit}
        if status:
            params["status"] = status

        response = self._client.get("sessions", params=params)
        return SessionList(**response)

    async def list_async(
        self, page: int = 1, limit: int = 20, status: Optional[str] = None
    ) -> SessionList:
        """Versión asíncrona de list()."""
        params = {"page": page, "limit": limit}
        if status:
            params["status"] = status

        response = await self._client.get_async("sessions", params=params)
        return SessionList(**response)

    def get(self, session_id: str) -> Session:
        """
        Obtiene los detalles de una sesión específica.

        Args:
            session_id: ID de la sesión

        Returns:
            Datos de la sesión

        Example:
            >>> session = client.sessions.get("64abc123...")
            >>> print(session.status)
        """
        response = self._client.get(f"sessions/{session_id}")
        return Session(**response["data"])

    async def get_async(self, session_id: str) -> Session:
        """Versión asíncrona de get()."""
        response = await self._client.get_async(f"sessions/{session_id}")
        return Session(**response["data"])

    def get_qr(self, session_id: str, format: str = "json") -> QRCode:
        """
        Obtiene el código QR para autenticar la sesión.

        Args:
            session_id: ID de la sesión
            format: Formato del QR (json, image)

        Returns:
            Código QR

        Example:
            >>> qr = client.sessions.get_qr("64abc123...")
            >>> print(qr.qr)  # String base64 o datos del QR
        """
        params = {"format": format}
        response = self._client.get(f"sessions/{session_id}/qr", params=params)
        return QRCode(**response["data"])

    async def get_qr_async(self, session_id: str, format: str = "json") -> QRCode:
        """Versión asíncrona de get_qr()."""
        params = {"format": format}
        response = await self._client.get_async(f"sessions/{session_id}/qr", params=params)
        return QRCode(**response["data"])

    def request_pairing_code(self, session_id: str, phone_number: str) -> PairingCode:
        """
        Solicita un código de emparejamiento para autenticar con número de teléfono.

        Args:
            session_id: ID de la sesión
            phone_number: Número de teléfono

        Returns:
            Código de emparejamiento

        Example:
            >>> code = client.sessions.request_pairing_code("64abc123...", "+1234567890")
            >>> print(code.code)
        """
        payload = {"phoneNumber": phone_number}
        response = self._client.post(f"sessions/{session_id}/pair", json_data=payload)
        return PairingCode(**response["data"])

    async def request_pairing_code_async(
        self, session_id: str, phone_number: str
    ) -> PairingCode:
        """Versión asíncrona de request_pairing_code()."""
        payload = {"phoneNumber": phone_number}
        response = await self._client.post_async(f"sessions/{session_id}/pair", json_data=payload)
        return PairingCode(**response["data"])

    def start(self, session_id: str) -> Session:
        """
        Inicia una sesión de WhatsApp.

        Args:
            session_id: ID de la sesión

        Returns:
            Sesión actualizada

        Example:
            >>> session = client.sessions.start("64abc123...")
            >>> print(session.status)  # STARTING
        """
        response = self._client.post(f"sessions/{session_id}/start")
        return Session(**response["data"])

    async def start_async(self, session_id: str) -> Session:
        """Versión asíncrona de start()."""
        response = await self._client.post_async(f"sessions/{session_id}/start")
        return Session(**response["data"])

    def stop(self, session_id: str) -> Session:
        """
        Detiene una sesión de WhatsApp.

        Args:
            session_id: ID de la sesión

        Returns:
            Sesión actualizada

        Example:
            >>> session = client.sessions.stop("64abc123...")
            >>> print(session.status)  # STOPPED
        """
        response = self._client.post(f"sessions/{session_id}/stop")
        return Session(**response["data"])

    async def stop_async(self, session_id: str) -> Session:
        """Versión asíncrona de stop()."""
        response = await self._client.post_async(f"sessions/{session_id}/stop")
        return Session(**response["data"])

    def update(self, session_id: str, data: Union[SessionUpdate, Dict[str, Any]]) -> Session:
        """
        Actualiza los datos de una sesión.

        Args:
            session_id: ID de la sesión
            data: Datos a actualizar

        Returns:
            Sesión actualizada

        Example:
            >>> session = client.sessions.update(
            ...     "64abc123...",
            ...     SessionUpdate(name="Nuevo Nombre")
            ... )
        """
        if isinstance(data, SessionUpdate):
            payload = data.model_dump(by_alias=True, exclude_none=True)
        else:
            payload = data

        response = self._client.patch(f"sessions/{session_id}", json_data=payload)
        return Session(**response["data"])

    async def update_async(
        self, session_id: str, data: Union[SessionUpdate, Dict[str, Any]]
    ) -> Session:
        """Versión asíncrona de update()."""
        if isinstance(data, SessionUpdate):
            payload = data.model_dump(by_alias=True, exclude_none=True)
        else:
            payload = data

        response = await self._client.patch_async(f"sessions/{session_id}", json_data=payload)
        return Session(**response["data"])

    def delete(self, session_id: str) -> Dict[str, Any]:
        """
        Elimina una sesión de WhatsApp.

        Args:
            session_id: ID de la sesión

        Returns:
            Respuesta de confirmación

        Example:
            >>> result = client.sessions.delete("64abc123...")
            >>> print(result["message"])
        """
        return self._client.delete(f"sessions/{session_id}")

    async def delete_async(self, session_id: str) -> Dict[str, Any]:
        """Versión asíncrona de delete()."""
        return await self._client.delete_async(f"sessions/{session_id}")
