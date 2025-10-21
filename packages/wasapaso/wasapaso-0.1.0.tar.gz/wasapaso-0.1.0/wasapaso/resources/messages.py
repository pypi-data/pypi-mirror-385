"""Recurso para gestionar mensajes de WhatsApp."""

from typing import Any, Dict, List, Optional, Union

from wasapaso.models.message import (
    ButtonsMessage,
    ContactMessage,
    LocationMessage,
    MediaMessage,
    Message,
    MessageList,
    PollMessage,
    TextMessage,
)
from wasapaso.resources.base import BaseResource


class MessagesResource(BaseResource):
    """Gestión de mensajes de WhatsApp."""

    def send(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Envía un mensaje genérico (usa los métodos específicos cuando sea posible).

        Args:
            data: Datos del mensaje

        Returns:
            Información del mensaje enviado

        Example:
            >>> result = client.messages.send({
            ...     "sessionId": "64abc123...",
            ...     "to": "1234567890",
            ...     "message": "Hola!",
            ...     "type": "text"
            ... })
        """
        return self._client.post("messages/send", json_data=data)

    async def send_async(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Versión asíncrona de send()."""
        return await self._client.post_async("messages/send", json_data=data)

    def send_text(
        self,
        session_id: str,
        to: str,
        message: str,
        reply_to: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Envía un mensaje de texto.

        Args:
            session_id: ID de la sesión
            to: Número de teléfono del destinatario
            message: Texto del mensaje
            reply_to: ID del mensaje al que se responde (opcional)

        Returns:
            Información del mensaje enviado

        Example:
            >>> result = client.messages.send_text(
            ...     session_id="64abc123...",
            ...     to="1234567890",
            ...     message="Hola! ¿Cómo estás?"
            ... )
            >>> print(result["data"]["messageId"])
        """
        msg = TextMessage(
            sessionId=session_id,
            to=to,
            message=message,
            replyTo=reply_to,
        )
        payload = msg.model_dump(by_alias=True, exclude_none=True)
        return self._client.post("messages/text", json_data=payload)

    async def send_text_async(
        self,
        session_id: str,
        to: str,
        message: str,
        reply_to: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Versión asíncrona de send_text()."""
        msg = TextMessage(
            sessionId=session_id,
            to=to,
            message=message,
            replyTo=reply_to,
        )
        payload = msg.model_dump(by_alias=True, exclude_none=True)
        return await self._client.post_async("messages/text", json_data=payload)

    def send_media(
        self,
        session_id: str,
        to: str,
        media_type: str,
        media_url: Optional[str] = None,
        media_data: Optional[str] = None,
        mimetype: str = "image/jpeg",
        caption: Optional[str] = None,
        filename: Optional[str] = None,
        reply_to: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Envía un archivo multimedia (imagen, video, audio, archivo).

        Args:
            session_id: ID de la sesión
            to: Número de teléfono del destinatario
            media_type: Tipo de media (image, video, audio, file)
            media_url: URL del archivo multimedia (opcional)
            media_data: Datos en base64 del archivo (opcional)
            mimetype: Tipo MIME del archivo
            caption: Texto de caption (opcional)
            filename: Nombre del archivo (opcional)
            reply_to: ID del mensaje al que se responde (opcional)

        Returns:
            Información del mensaje enviado

        Example:
            >>> result = client.messages.send_media(
            ...     session_id="64abc123...",
            ...     to="1234567890",
            ...     media_type="image",
            ...     media_url="https://example.com/image.jpg",
            ...     caption="Mira esta imagen!"
            ... )
        """
        from wasapaso.models.message import MediaContent, MessageType

        media = MediaContent(
            url=media_url,
            data=media_data,
            mimetype=mimetype,
            filename=filename,
        )

        msg = MediaMessage(
            sessionId=session_id,
            to=to,
            type=MessageType(media_type),
            media=media,
            caption=caption,
            replyTo=reply_to,
        )
        payload = msg.model_dump(by_alias=True, exclude_none=True)
        return self._client.post("messages/media", json_data=payload)

    async def send_media_async(
        self,
        session_id: str,
        to: str,
        media_type: str,
        media_url: Optional[str] = None,
        media_data: Optional[str] = None,
        mimetype: str = "image/jpeg",
        caption: Optional[str] = None,
        filename: Optional[str] = None,
        reply_to: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Versión asíncrona de send_media()."""
        from wasapaso.models.message import MediaContent, MessageType

        media = MediaContent(
            url=media_url,
            data=media_data,
            mimetype=mimetype,
            filename=filename,
        )

        msg = MediaMessage(
            sessionId=session_id,
            to=to,
            type=MessageType(media_type),
            media=media,
            caption=caption,
            replyTo=reply_to,
        )
        payload = msg.model_dump(by_alias=True, exclude_none=True)
        return await self._client.post_async("messages/media", json_data=payload)

    def send_location(
        self,
        session_id: str,
        to: str,
        latitude: float,
        longitude: float,
        title: Optional[str] = None,
        reply_to: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Envía una ubicación.

        Args:
            session_id: ID de la sesión
            to: Número de teléfono del destinatario
            latitude: Latitud
            longitude: Longitud
            title: Título de la ubicación (opcional)
            reply_to: ID del mensaje al que se responde (opcional)

        Returns:
            Información del mensaje enviado

        Example:
            >>> result = client.messages.send_location(
            ...     session_id="64abc123...",
            ...     to="1234567890",
            ...     latitude=40.7128,
            ...     longitude=-74.0060,
            ...     title="Nueva York"
            ... )
        """
        from wasapaso.models.message import Location

        location = Location(latitude=latitude, longitude=longitude, title=title)

        msg = LocationMessage(
            sessionId=session_id,
            to=to,
            location=location,
            replyTo=reply_to,
        )
        payload = msg.model_dump(by_alias=True, exclude_none=True)
        return self._client.post("messages/send", json_data=payload)

    async def send_location_async(
        self,
        session_id: str,
        to: str,
        latitude: float,
        longitude: float,
        title: Optional[str] = None,
        reply_to: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Versión asíncrona de send_location()."""
        from wasapaso.models.message import Location

        location = Location(latitude=latitude, longitude=longitude, title=title)

        msg = LocationMessage(
            sessionId=session_id,
            to=to,
            location=location,
            replyTo=reply_to,
        )
        payload = msg.model_dump(by_alias=True, exclude_none=True)
        return await self._client.post_async("messages/send", json_data=payload)

    def list(
        self,
        session_id: str,
        chat_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        from_me: Optional[bool] = None,
    ) -> MessageList:
        """
        Lista los mensajes de una sesión.

        Args:
            session_id: ID de la sesión
            chat_id: ID del chat para filtrar (opcional)
            limit: Cantidad de resultados
            offset: Offset para paginación
            from_me: Filtrar por mensajes enviados (True) o recibidos (False)

        Returns:
            Lista paginada de mensajes

        Example:
            >>> messages = client.messages.list(
            ...     session_id="64abc123...",
            ...     limit=20
            ... )
            >>> for msg in messages.data:
            ...     print(msg.body)
        """
        params: Dict[str, Any] = {
            "sessionId": session_id,
            "limit": limit,
            "offset": offset,
        }
        if chat_id:
            params["chatId"] = chat_id
        if from_me is not None:
            params["fromMe"] = str(from_me).lower()

        response = self._client.get("messages", params=params)
        return MessageList(**response)

    async def list_async(
        self,
        session_id: str,
        chat_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        from_me: Optional[bool] = None,
    ) -> MessageList:
        """Versión asíncrona de list()."""
        params: Dict[str, Any] = {
            "sessionId": session_id,
            "limit": limit,
            "offset": offset,
        }
        if chat_id:
            params["chatId"] = chat_id
        if from_me is not None:
            params["fromMe"] = str(from_me).lower()

        response = await self._client.get_async("messages", params=params)
        return MessageList(**response)

    def get(self, message_id: str) -> Message:
        """
        Obtiene un mensaje específico.

        Args:
            message_id: ID del mensaje

        Returns:
            Datos del mensaje

        Example:
            >>> message = client.messages.get("64xyz789...")
            >>> print(message.body)
        """
        response = self._client.get(f"messages/{message_id}")
        return Message(**response["data"])

    async def get_async(self, message_id: str) -> Message:
        """Versión asíncrona de get()."""
        response = await self._client.get_async(f"messages/{message_id}")
        return Message(**response["data"])

    def mark_as_read(self, message_id: str) -> Dict[str, Any]:
        """
        Marca un mensaje como leído.

        Args:
            message_id: ID del mensaje

        Returns:
            Respuesta de confirmación

        Example:
            >>> result = client.messages.mark_as_read("64xyz789...")
        """
        return self._client.post(f"messages/{message_id}/read")

    async def mark_as_read_async(self, message_id: str) -> Dict[str, Any]:
        """Versión asíncrona de mark_as_read()."""
        return await self._client.post_async(f"messages/{message_id}/read")

    def react(self, message_id: str, reaction: str) -> Dict[str, Any]:
        """
        Reacciona a un mensaje con un emoji.

        Args:
            message_id: ID del mensaje
            reaction: Emoji de reacción

        Returns:
            Respuesta de confirmación

        Example:
            >>> result = client.messages.react("64xyz789...", "👍")
        """
        payload = {"reaction": reaction}
        return self._client.post(f"messages/{message_id}/react", json_data=payload)

    async def react_async(self, message_id: str, reaction: str) -> Dict[str, Any]:
        """Versión asíncrona de react()."""
        payload = {"reaction": reaction}
        return await self._client.post_async(f"messages/{message_id}/react", json_data=payload)

    def delete(self, message_id: str, delete_for_everyone: bool = False) -> Dict[str, Any]:
        """
        Elimina un mensaje.

        Args:
            message_id: ID del mensaje
            delete_for_everyone: Si es True, elimina el mensaje para todos

        Returns:
            Respuesta de confirmación

        Example:
            >>> result = client.messages.delete("64xyz789...", delete_for_everyone=True)
        """
        params = {"deleteForEveryone": str(delete_for_everyone).lower()}
        return self._client.delete(f"messages/{message_id}", params=params)

    async def delete_async(
        self, message_id: str, delete_for_everyone: bool = False
    ) -> Dict[str, Any]:
        """Versión asíncrona de delete()."""
        params = {"deleteForEveryone": str(delete_for_everyone).lower()}
        return await self._client.delete_async(f"messages/{message_id}", params=params)
