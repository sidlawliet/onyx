from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class RecommendationAllocationRead(BaseModel):
    id: UUID
    recommendation_version_id: UUID
    instrument_id: UUID
    target_weight: Decimal
    target_quantity: Decimal
    side: str
    rationale: str

    model_config = ConfigDict(from_attributes=True)


class ValidationResultRead(BaseModel):
    id: UUID
    rule_code: str
    severity: str
    passed: bool
    blocking: bool
    explanation: str

    model_config = ConfigDict(from_attributes=True)


class ValidationRunRead(BaseModel):
    id: UUID
    recommendation_version_id: UUID
    rule_set_version: str
    status: str
    completed_at: datetime
    results: list[ValidationResultRead] = []

    model_config = ConfigDict(from_attributes=True)


class RecommendationVersionRead(BaseModel):
    id: UUID
    recommendation_id: UUID
    research_report_version_id: UUID
    version: int
    expected_return: Decimal
    volatility: Decimal
    diversification_score: Decimal
    investment_horizon_days: int
    confidence: Decimal
    reasoning: str
    artifact_hash: str
    created_at: datetime
    allocations: list[RecommendationAllocationRead] = []

    model_config = ConfigDict(from_attributes=True)


class RecommendationRead(BaseModel):
    id: UUID
    tenant_id: UUID
    workflow_id: UUID
    title: str
    status: str
    created_at: datetime
    versions: list[RecommendationVersionRead] = []

    model_config = ConfigDict(from_attributes=True)
