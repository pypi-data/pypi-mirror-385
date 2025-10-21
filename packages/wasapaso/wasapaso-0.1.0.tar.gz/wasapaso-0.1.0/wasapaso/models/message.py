"""Modelos relacionados con mensajes de WhatsApp."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class MessageType(str, Enum):
    """Tipos de mensajes soportados."""

    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    FILE = "file"
    LOCATION = "location"
    CONTACT = "contact"
    POLL = "poll"
    BUTTONS = "buttons"


class Message(BaseModel):
    """Información de un mensaje."""

    id: str
    session_id: str = Field(alias="sessionId")
    message_id: str = Field(alias="messageId")
    from_: str = Field(alias="from")
    to: str
    body: Optional[str] = None
    type: str
    timestamp: datetime
    from_me: bool = Field(alias="fromMe")

    class Config:
        populate_by_name = True


class MessageList(BaseModel):
    """Lista paginada de mensajes."""

    data: List[Message]
    pagination: Dict[str, Any]


class MessageSend(BaseModel):
    """Datos base para enviar un mensaje."""

    session_id: str = Field(alias="sessionId")
    to: str
    reply_to: Optional[str] = Field(None, alias="replyTo")

    class Config:
        populate_by_name = True


class TextMessage(MessageSend):
    """Datos para enviar un mensaje de texto."""

    message: str
    type: MessageType = MessageType.TEXT


class MediaContent(BaseModel):
    """Contenido de media (imagen, video, audio, archivo)."""

    url: Optional[str] = None
    data: Optional[str] = None  # Base64
    mimetype: str
    filename: Optional[str] = None


class MediaMessage(MessageSend):
    """Datos para enviar un mensaje con media."""

    type: MessageType
    media: MediaContent
    caption: Optional[str] = None


class Location(BaseModel):
    """Coordenadas de ubicación."""

    latitude: float
    longitude: float
    title: Optional[str] = None


class LocationMessage(MessageSend):
    """Datos para enviar una ubicación."""

    type: MessageType = MessageType.LOCATION
    location: Location


class Contact(BaseModel):
    """Información de un contacto."""

    full_name: str = Field(alias="fullName")
    phone_number: str = Field(alias="phoneNumber")
    organization: Optional[str] = None

    class Config:
        populate_by_name = True


class ContactMessage(MessageSend):
    """Datos para enviar contactos."""

    type: MessageType = MessageType.CONTACT
    contacts: List[Contact]


class Poll(BaseModel):
    """Configuración de una encuesta."""

    name: str
    options: List[str]
    multiple_answers: bool = Field(False, alias="multipleAnswers")

    class Config:
        populate_by_name = True


class PollMessage(MessageSend):
    """Datos para enviar una encuesta."""

    type: MessageType = MessageType.POLL
    poll: Poll


class ButtonType(str, Enum):
    """Tipos de botones soportados."""

    REPLY = "reply"
    CALL = "call"
    URL = "url"
    COPY = "copy"


class Button(BaseModel):
    """Configuración de un botón."""

    type: ButtonType
    text: str
    url: Optional[str] = None
    phone_number: Optional[str] = Field(None, alias="phoneNumber")
    copy_code: Optional[str] = Field(None, alias="copyCode")

    class Config:
        populate_by_name = True


class ButtonsContent(BaseModel):
    """Contenido de un mensaje con botones."""

    header: str
    body: str
    footer: Optional[str] = None
    buttons: List[Button]


class ButtonsMessage(MessageSend):
    """Datos para enviar un mensaje con botones."""

    type: MessageType = MessageType.BUTTONS
    buttons: ButtonsContent
