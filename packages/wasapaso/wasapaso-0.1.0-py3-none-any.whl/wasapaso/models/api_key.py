"""Modelos relacionados con API Keys."""

from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel, Field


class SessionPermissions(BaseModel):
    """Permisos relacionados con sesiones."""

    create: bool = True
    read: bool = True
    update: bool = True
    delete: bool = True


class MessagePermissions(BaseModel):
    """Permisos relacionados con mensajes."""

    send: bool = True
    read: bool = True
    delete: bool = False


class ContactPermissions(BaseModel):
    """Permisos relacionados con contactos."""

    read: bool = True
    manage: bool = False


class WebhookPermissions(BaseModel):
    """Permisos relacionados con webhooks."""

    manage: bool = False


class Permissions(BaseModel):
    """Permisos de una API key."""

    sessions: SessionPermissions
    messages: MessagePermissions
    contacts: ContactPermissions
    webhooks: WebhookPermissions


class RateLimit(BaseModel):
    """Límites de tasa de una API key."""

    requests_per_minute: int = Field(alias="requestsPerMinute")
    requests_per_hour: int = Field(alias="requestsPerHour")
    requests_per_day: int = Field(alias="requestsPerDay")

    class Config:
        populate_by_name = True


class Usage(BaseModel):
    """Estadísticas de uso de una API key."""

    last_used: Optional[datetime] = Field(None, alias="lastUsed")
    total_requests: int = Field(alias="totalRequests")
    requests_today: int = Field(alias="requestsToday")
    last_reset_date: datetime = Field(alias="lastResetDate")

    class Config:
        populate_by_name = True


class ApiKeyInfo(BaseModel):
    """Información sobre una API key."""

    name: str
    display_key: str = Field(alias="displayKey")
    permissions: Permissions
    rate_limit: RateLimit = Field(alias="rateLimit")
    usage: Usage
    is_active: bool = Field(alias="isActive", default=True)
    expires_at: Optional[datetime] = Field(None, alias="expiresAt")
    created_at: datetime = Field(alias="createdAt")
    metadata: Optional[Dict[str, str]] = None

    class Config:
        populate_by_name = True
