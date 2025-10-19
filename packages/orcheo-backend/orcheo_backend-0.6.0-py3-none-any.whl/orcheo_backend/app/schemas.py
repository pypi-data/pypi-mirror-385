"""Pydantic request schemas for the FastAPI service."""

from __future__ import annotations
from datetime import datetime
from typing import Any
from uuid import UUID
from pydantic import BaseModel, Field, field_validator
from orcheo.graph.ingestion import DEFAULT_SCRIPT_SIZE_LIMIT
from orcheo.models import (
    CredentialHealthStatus,
    CredentialKind,
    GovernanceAlertKind,
    SecretGovernanceAlertSeverity,
)


class WorkflowCreateRequest(BaseModel):
    """Payload for creating a new workflow."""

    name: str
    slug: str | None = None
    description: str | None = None
    tags: list[str] = Field(default_factory=list)
    actor: str = Field(default="system")


class WorkflowUpdateRequest(BaseModel):
    """Payload for updating an existing workflow."""

    name: str | None = None
    description: str | None = None
    tags: list[str] | None = None
    is_archived: bool | None = None
    actor: str = Field(default="system")


class WorkflowVersionCreateRequest(BaseModel):
    """Payload for creating a workflow version."""

    graph: dict[str, Any]
    metadata: dict[str, Any] = Field(default_factory=dict)
    notes: str | None = None
    created_by: str


class WorkflowVersionIngestRequest(BaseModel):
    """Payload for ingesting a LangGraph Python script."""

    script: str
    entrypoint: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    notes: str | None = None
    created_by: str

    @field_validator("script")
    @classmethod
    def _enforce_script_size(cls, value: str) -> str:
        size = len(value.encode("utf-8"))
        if size > DEFAULT_SCRIPT_SIZE_LIMIT:
            msg = (
                "LangGraph script exceeds the maximum allowed size of "
                f"{DEFAULT_SCRIPT_SIZE_LIMIT} bytes"
            )
            raise ValueError(msg)
        return value


class WorkflowRunCreateRequest(BaseModel):
    """Payload for creating a new workflow execution run."""

    workflow_version_id: UUID
    triggered_by: str
    input_payload: dict[str, Any] = Field(default_factory=dict)


class RunActionRequest(BaseModel):
    """Base payload for run lifecycle transitions."""

    actor: str


class RunSucceedRequest(RunActionRequest):
    """Payload for marking a run as succeeded."""

    output: dict[str, Any] | None = None


class RunFailRequest(RunActionRequest):
    """Payload for marking a run as failed."""

    error: str


class RunCancelRequest(RunActionRequest):
    """Payload for cancelling a run."""

    reason: str | None = None


class RunHistoryStepResponse(BaseModel):
    """Response payload describing a single run history step."""

    index: int
    at: datetime
    payload: dict[str, Any]


class RunHistoryResponse(BaseModel):
    """Execution history response returned by the API."""

    execution_id: str
    workflow_id: str
    status: str
    started_at: datetime
    completed_at: datetime | None = None
    error: str | None = None
    inputs: dict[str, Any] = Field(default_factory=dict)
    steps: list[RunHistoryStepResponse] = Field(default_factory=list)


class RunReplayRequest(BaseModel):
    """Request body for replaying a run from a given step index."""

    from_step: int = Field(default=0, ge=0)


class WorkflowVersionDiffResponse(BaseModel):
    """Response payload for workflow version diffs."""

    base_version: int
    target_version: int
    diff: list[str]


class CronDispatchRequest(BaseModel):
    """Request body for dispatching cron triggers."""

    now: datetime | None = None


class CredentialValidationRequest(BaseModel):
    """Request body for on-demand credential validation."""

    actor: str = Field(default="system")


class CredentialHealthItem(BaseModel):
    """Represents the health state for an individual credential."""

    credential_id: str
    name: str
    provider: str
    status: CredentialHealthStatus
    last_checked_at: datetime | None = None
    failure_reason: str | None = None


class CredentialHealthResponse(BaseModel):
    """Response payload describing workflow credential health."""

    workflow_id: str
    status: CredentialHealthStatus
    checked_at: datetime | None = None
    credentials: list[CredentialHealthItem] = Field(default_factory=list)


class CredentialScopePayload(BaseModel):
    """Schema describing credential scoping configuration."""

    workflow_ids: list[UUID] = Field(default_factory=list)
    workspace_ids: list[UUID] = Field(default_factory=list)
    roles: list[str] = Field(default_factory=list)


class CredentialIssuancePolicyPayload(BaseModel):
    """Schema describing issuance policy defaults for a template."""

    require_refresh_token: bool = False
    rotation_period_days: int | None = Field(default=None, ge=1)
    expiry_threshold_minutes: int = Field(default=60, ge=1)


class OAuthTokenRequest(BaseModel):
    """Plaintext OAuth token payload submitted by clients."""

    access_token: str | None = None
    refresh_token: str | None = None
    expires_at: datetime | None = None


class CredentialTemplateCreateRequest(BaseModel):
    """Request payload for creating a credential template."""

    name: str
    provider: str
    scopes: list[str] = Field(default_factory=list)
    description: str | None = None
    kind: CredentialKind = CredentialKind.SECRET
    scope: CredentialScopePayload | None = None
    issuance_policy: CredentialIssuancePolicyPayload | None = None
    actor: str = Field(default="system")


class CredentialTemplateUpdateRequest(BaseModel):
    """Request payload for mutating credential template metadata."""

    name: str | None = None
    scopes: list[str] | None = None
    description: str | None = None
    kind: CredentialKind | None = None
    scope: CredentialScopePayload | None = None
    issuance_policy: CredentialIssuancePolicyPayload | None = None
    actor: str = Field(default="system")


class CredentialTemplateResponse(BaseModel):
    """Response schema describing a credential template."""

    id: str
    name: str
    provider: str
    scopes: list[str]
    description: str | None
    kind: CredentialKind
    scope: CredentialScopePayload
    issuance_policy: CredentialIssuancePolicyPayload
    created_at: datetime
    updated_at: datetime


class CredentialIssuanceRequest(BaseModel):
    """Request payload for issuing a credential from a template."""

    template_id: UUID
    secret: str
    actor: str = Field(default="system")
    name: str | None = None
    scopes: list[str] | None = None
    workflow_id: UUID | None = None
    oauth_tokens: OAuthTokenRequest | None = None


class CredentialIssuanceResponse(BaseModel):
    """Response describing the issued credential metadata."""

    credential_id: str
    name: str
    provider: str
    kind: CredentialKind
    template_id: str | None
    created_at: datetime
    updated_at: datetime


class GovernanceAlertResponse(BaseModel):
    """Response payload describing a governance alert."""

    id: str
    kind: GovernanceAlertKind
    severity: SecretGovernanceAlertSeverity
    message: str
    credential_id: str | None
    template_id: str | None
    is_acknowledged: bool
    acknowledged_at: datetime | None
    created_at: datetime
    updated_at: datetime


class AlertAcknowledgeRequest(BaseModel):
    """Request payload for acknowledging a governance alert."""

    actor: str = Field(default="system")
