from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class SourceDocumentRead(BaseModel):
    id: UUID
    provider: str
    external_id: str
    title: str
    source_url: str | None
    classification: str

    model_config = ConfigDict(from_attributes=True)


class ClaimCitationRead(BaseModel):
    id: UUID
    claim_id: UUID
    source_document_version_id: UUID
    locator: str

    model_config = ConfigDict(from_attributes=True)


class ResearchClaimRead(BaseModel):
    id: UUID
    claim_text: str
    confidence: Decimal
    citations: list[ClaimCitationRead] = []

    model_config = ConfigDict(from_attributes=True)


class ResearchReportVersionRead(BaseModel):
    id: UUID
    report_id: UUID
    version: int
    model_name: str
    model_version: str
    confidence: Decimal
    market_summary: str
    top_opportunities: list[Any]
    top_risks: list[Any]
    company_analysis: dict[str, Any]
    sector_analysis: dict[str, Any]
    artifact_uri: str
    artifact_hash: str
    created_at: datetime
    claims: list[ResearchClaimRead] = []

    model_config = ConfigDict(from_attributes=True)


class ResearchReportRead(BaseModel):
    id: UUID
    tenant_id: UUID
    workflow_id: UUID
    title: str
    status: str
    created_at: datetime
    versions: list[ResearchReportVersionRead] = []

    model_config = ConfigDict(from_attributes=True)
