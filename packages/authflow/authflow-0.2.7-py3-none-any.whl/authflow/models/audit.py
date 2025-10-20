"""Audit log models and schemas."""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class AuditLogBase(BaseModel):
    """Base audit log schema."""

    model_config = ConfigDict(from_attributes=True)

    event_type: str = Field(..., description="Type of event (user.login, user.created, role.assigned, etc.)")
    resource_type: str = Field(..., description="Type of resource (user, role, organization, team, etc.)")
    resource_id: Optional[str] = Field(None, description="ID of the affected resource")
    action: str = Field(..., description="Action performed (create, update, delete, login, logout, etc.)")
    actor_id: Optional[str] = Field(None, description="ID of user who performed the action")
    actor_username: Optional[str] = Field(None, description="Username of actor")
    actor_ip: Optional[str] = Field(None, description="IP address of actor")
    actor_user_agent: Optional[str] = Field(None, description="User agent of actor")
    status: str = Field(..., description="Status of action (success, failure, pending)")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional event details")
    error_message: Optional[str] = Field(None, description="Error message if action failed")


class AuditLogCreate(AuditLogBase):
    """Schema for creating an audit log entry."""
    pass


class AuditLog(AuditLogBase):
    """Full audit log schema with metadata."""

    id: str
    timestamp: datetime
    organization_id: Optional[str] = None
    team_id: Optional[str] = None


class AuditLogFilters(BaseModel):
    """Filters for audit log queries."""

    model_config = ConfigDict(from_attributes=True)

    page: int = Field(1, ge=1)
    page_size: int = Field(50, ge=1, le=100)
    event_type: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    action: Optional[str] = None
    actor_id: Optional[str] = None
    actor_username: Optional[str] = None
    status: Optional[str] = None
    organization_id: Optional[str] = None
    team_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    search: Optional[str] = None


class AuditLogStats(BaseModel):
    """Audit log statistics."""

    total_events: int
    events_by_type: Dict[str, int]
    events_by_action: Dict[str, int]
    events_by_status: Dict[str, int]
    top_actors: list[Dict[str, Any]]
    recent_failures: int
