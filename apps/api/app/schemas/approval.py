from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class ArtifactManifestRead(BaseModel):
    id: UUID
    tenant_id: UUID
    workflow_id: UUID
    recommendation_version_id: UUID
    schema_version: str
    content_hash: str
    storage_uri: str
    status: str
    created_at: datetime
    expires_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ApprovalDecisionRequest(BaseModel):
    decision: str = Field(..., description="APPROVE, REJECT, or MODIFY")
    attestation: str | None = Field(None, description="Required for APPROVE")
    reason: str | None = Field(None, description="Required for REJECT or MODIFY")
    artifact_hash: str = Field(..., min_length=64, max_length=64, description="Canonical SHA-256 hash")
    mfa_verified: bool = Field(True, description="Must be true for APPROVE")


class ApprovalDecisionRead(BaseModel):
    id: UUID
    approval_task_id: UUID
    decided_by: UUID
    artifact_hash: str
    decision: str
    reason: str | None
    attestation: str | None
    mfa_verified: bool
    decided_at: datetime
    revoked_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class ApprovalTaskRead(BaseModel):
    id: UUID
    tenant_id: UUID
    workflow_id: UUID
    artifact_manifest_id: UUID
    assigned_to: UUID
    status: str
    due_at: datetime | None
    created_at: datetime
    decisions: list[ApprovalDecisionRead] = []

    model_config = ConfigDict(from_attributes=True)
