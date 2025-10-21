"""Modelos relacionados con sesiones de WhatsApp."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SessionStatus(str, Enum):
    """Estados posibles de una sesión."""

    STOPPED = "STOPPED"
    STARTING = "STARTING"
    SCAN_QR_CODE = "SCAN_QR_CODE"
    WORKING = "WORKING"
    FAILED = "FAILED"


class Session(BaseModel):
    """Información completa de una sesión de WhatsApp."""

    id: str
    name: str
    session_name: str = Field(alias="sessionName")
    status: SessionStatus
    message_count: int = Field(0, alias="messageCount")
    is_paid: bool = Field(False, alias="isPaid")
    metadata: Optional[Dict[str, Any]] = None
    custom_webhook: Optional[str] = Field(None, alias="customWebhook")
    webhook_events: List[str] = Field(default_factory=list, alias="webhookEvents")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")

    class Config:
        populate_by_name = True
        use_enum_values = False


class SessionCreate(BaseModel):
    """Datos para crear una nueva sesión."""

    name: str
    webhook_url: Optional[str] = Field(None, alias="webhookUrl")
    webhook_events: Optional[List[str]] = Field(None, alias="webhookEvents")
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        populate_by_name = True


class SessionUpdate(BaseModel):
    """Datos para actualizar una sesión existente."""

    name: Optional[str] = None
    webhook_url: Optional[str] = Field(None, alias="webhookUrl")
    webhook_events: Optional[List[str]] = Field(None, alias="webhookEvents")
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        populate_by_name = True


class SessionList(BaseModel):
    """Lista paginada de sesiones."""

    data: List[Session]
    pagination: Dict[str, Any]


class QRCode(BaseModel):
    """Código QR para autenticar una sesión."""

    session_id: str = Field(alias="sessionId")
    session_name: str = Field(alias="sessionName")
    qr: Any  # Puede ser string (base64) o dict con más info

    class Config:
        populate_by_name = True


class PairingCode(BaseModel):
    """Código de emparejamiento para autenticar por teléfono."""

    session_id: str = Field(alias="sessionId")
    session_name: str = Field(alias="sessionName")
    phone_number: str = Field(alias="phoneNumber")
    code: str

    class Config:
        populate_by_name = True
