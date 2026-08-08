from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    LargeBinary,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    Uuid,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from apps.api.app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


HASH_LENGTH = 64
JSONBType = JSONB().with_variant(JSON, "sqlite")



class Tenant(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "tenants"

    slug: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False, server_default="ACTIVE")

    users: Mapped[list["User"]] = relationship(back_populates="tenant")
    portfolios: Mapped[list["Portfolio"]] = relationship(back_populates="tenant")

    __table_args__ = (
        CheckConstraint("status IN ('ACTIVE', 'SUSPENDED')", name="valid_status"),
    )


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "users"

    tenant_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    email: Mapped[str] = mapped_column(String(320), nullable=False)
    display_name: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False, server_default="ACTIVE")
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    is_service_principal: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )

    tenant: Mapped[Tenant] = relationship(back_populates="users")
    role_assignments: Mapped[list["UserRoleAssignment"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("tenant_id", "email", name="uq_users_tenant_email"),
        UniqueConstraint("tenant_id", "id", name="uq_users_tenant_id"),
        CheckConstraint("status IN ('ACTIVE', 'PENDING', 'SUSPENDED')", name="valid_status"),
        Index("ix_users_tenant_status", "tenant_id", "status"),
    )


class Role(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "roles"

    tenant_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    permissions: Mapped[dict[str, Any]] = mapped_column(JSONBType, nullable=False, server_default=text("'{}'"))

    assignments: Mapped[list["UserRoleAssignment"]] = relationship(
        back_populates="role", cascade="all, delete-orphan", overlaps="role_assignments"
    )

    __table_args__ = (
        UniqueConstraint("tenant_id", "name", name="uq_roles_tenant_name"),
        UniqueConstraint("tenant_id", "id", name="uq_roles_tenant_id"),
    )


class UserRoleAssignment(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "user_role_assignments"

    tenant_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    user_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    role_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    user: Mapped[User] = relationship(back_populates="role_assignments", overlaps="assignments")
    role: Mapped[Role] = relationship(back_populates="assignments", overlaps="role_assignments,user")

    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "user_id"], ["users.tenant_id", "users.id"], ondelete="CASCADE"
        ),
        ForeignKeyConstraint(
            ["tenant_id", "role_id"], ["roles.tenant_id", "roles.id"], ondelete="CASCADE"
        ),
        UniqueConstraint("tenant_id", "user_id", "role_id", name="uq_user_role_assignment"),
    )


class Portfolio(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "portfolios"

    tenant_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    code: Mapped[str] = mapped_column(String(40), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    base_currency: Mapped[str] = mapped_column(String(3), nullable=False, server_default="USD")
    status: Mapped[str] = mapped_column(String(24), nullable=False, server_default="ACTIVE")

    tenant: Mapped[Tenant] = relationship(back_populates="portfolios")
    accounts: Mapped[list["Account"]] = relationship(back_populates="portfolio")
    workflows: Mapped[list["Workflow"]] = relationship(back_populates="portfolio")

    __table_args__ = (
        UniqueConstraint("tenant_id", "code", name="uq_portfolios_tenant_code"),
        UniqueConstraint("tenant_id", "id", name="uq_portfolios_tenant_id"),
        CheckConstraint("length(base_currency) = 3", name="currency_length"),
        CheckConstraint("status IN ('ACTIVE', 'CLOSED')", name="valid_status"),
    )


class Account(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "accounts"

    tenant_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    portfolio_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    account_number: Mapped[str] = mapped_column(String(80), nullable=False)
    broker_name: Mapped[str] = mapped_column(String(120), nullable=False)
    available_cash: Mapped[Decimal] = mapped_column(Numeric(20, 4), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, server_default="USD")
    status: Mapped[str] = mapped_column(String(24), nullable=False, server_default="ACTIVE")

    portfolio: Mapped[Portfolio] = relationship(back_populates="accounts")

    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "portfolio_id"],
            ["portfolios.tenant_id", "portfolios.id"],
            ondelete="CASCADE",
        ),
        UniqueConstraint("tenant_id", "account_number", name="uq_accounts_tenant_number"),
        UniqueConstraint("tenant_id", "id", name="uq_accounts_tenant_id"),
        CheckConstraint("available_cash >= 0", name="nonnegative_cash"),
        CheckConstraint("status IN ('ACTIVE', 'RESTRICTED', 'CLOSED')", name="valid_status"),
        Index("ix_accounts_portfolio", "tenant_id", "portfolio_id"),
    )


class Instrument(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "instruments"

    symbol: Mapped[str] = mapped_column(String(32), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    asset_class: Mapped[str] = mapped_column(String(40), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    exchange: Mapped[str] = mapped_column(String(40), nullable=False)

    __table_args__ = (
        UniqueConstraint("symbol", "exchange", name="uq_instruments_symbol_exchange"),
        CheckConstraint("asset_class IN ('EQUITY')", name="hackathon_asset_class"),
    )


class Workflow(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "workflows"

    tenant_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    portfolio_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    created_by: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    trace_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    stage: Mapped[str] = mapped_column(String(40), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")

    portfolio: Mapped[Portfolio] = relationship(back_populates="workflows")
    transitions: Mapped[list["WorkflowTransition"]] = relationship(
        back_populates="workflow", cascade="all, delete-orphan", order_by="WorkflowTransition.occurred_at"
    )
    research_reports: Mapped[list["ResearchReport"]] = relationship(back_populates="workflow")
    recommendations: Mapped[list["Recommendation"]] = relationship(back_populates="workflow")

    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "portfolio_id"],
            ["portfolios.tenant_id", "portfolios.id"],
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["tenant_id", "created_by"], ["users.tenant_id", "users.id"], ondelete="RESTRICT"
        ),
        UniqueConstraint("tenant_id", "id", name="uq_workflows_tenant_id"),
        UniqueConstraint("tenant_id", "trace_id", name="uq_workflows_tenant_trace"),
        CheckConstraint(
            "stage IN ('MARKET_INTELLIGENCE', 'PORTFOLIO_STRATEGY', 'HUMAN_APPROVAL', "
            "'TRADE_EXECUTION', 'PORTFOLIO_MONITORING')",
            name="valid_stage",
        ),
        CheckConstraint(
            "status IN ('DRAFT', 'RUNNING', 'AWAITING_REVIEW', 'APPROVED', 'REJECTED', "
            "'FAILED', 'HALTED', 'COMPLETED')",
            name="valid_status",
        ),
        CheckConstraint("version > 0", name="positive_version"),
        Index("ix_workflows_tenant_status", "tenant_id", "status"),
        Index("ix_workflows_portfolio_stage", "portfolio_id", "stage"),
    )


class WorkflowTransition(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "workflow_transitions"

    tenant_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    workflow_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    actor_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    from_stage: Mapped[str | None] = mapped_column(String(40))
    to_stage: Mapped[str] = mapped_column(String(40), nullable=False)
    from_status: Mapped[str | None] = mapped_column(String(32))
    to_status: Mapped[str] = mapped_column(String(32), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    workflow: Mapped[Workflow] = relationship(back_populates="transitions")

    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "workflow_id"],
            ["workflows.tenant_id", "workflows.id"],
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["tenant_id", "actor_id"], ["users.tenant_id", "users.id"], ondelete="RESTRICT"
        ),
        Index("ix_workflow_transitions_timeline", "workflow_id", "occurred_at"),
    )


class SourceDocument(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "source_documents"

    tenant_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    provider: Mapped[str] = mapped_column(String(120), nullable=False)
    external_id: Mapped[str] = mapped_column(String(200), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    source_url: Mapped[str | None] = mapped_column(Text)
    classification: Mapped[str] = mapped_column(String(32), nullable=False, server_default="INTERNAL")

    versions: Mapped[list["SourceDocumentVersion"]] = relationship(
        back_populates="document", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("tenant_id", "provider", "external_id", name="uq_source_external"),
        CheckConstraint(
            "classification IN ('PUBLIC', 'INTERNAL', 'CONFIDENTIAL', 'RESTRICTED')",
            name="valid_classification",
        ),
    )


class SourceDocumentVersion(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "source_document_versions"

    document_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("source_documents.id", ondelete="CASCADE"), nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    retrieved_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    content_hash: Mapped[str] = mapped_column(String(HASH_LENGTH), nullable=False)
    excerpt: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSONBType, nullable=False, server_default=text("'{}'")
    )

    document: Mapped[SourceDocument] = relationship(back_populates="versions")

    __table_args__ = (
        UniqueConstraint("document_id", "version", name="uq_source_document_version"),
        CheckConstraint("version > 0", name="positive_version"),
        CheckConstraint("length(content_hash) = 64", name="hash_length"),
    )


class ResearchReport(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "research_reports"

    tenant_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    workflow_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False, server_default="DRAFT")

    workflow: Mapped[Workflow] = relationship(back_populates="research_reports")
    versions: Mapped[list["ResearchReportVersion"]] = relationship(
        back_populates="report", cascade="all, delete-orphan"
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "workflow_id"],
            ["workflows.tenant_id", "workflows.id"],
            ondelete="CASCADE",
        ),
        UniqueConstraint("tenant_id", "id", name="uq_research_reports_tenant_id"),
        CheckConstraint("status IN ('DRAFT', 'COMPLETED', 'VERIFIED', 'REJECTED')", name="valid_status"),
        Index("ix_research_reports_workflow", "workflow_id", "status"),
    )


class ResearchReportVersion(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "research_report_versions"

    report_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("research_reports.id", ondelete="CASCADE"), nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    model_name: Mapped[str] = mapped_column(String(120), nullable=False)
    model_version: Mapped[str] = mapped_column(String(80), nullable=False)
    confidence: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    market_summary: Mapped[str] = mapped_column(Text, nullable=False)
    top_opportunities: Mapped[list[Any]] = mapped_column(JSONBType, nullable=False)
    top_risks: Mapped[list[Any]] = mapped_column(JSONBType, nullable=False)
    company_analysis: Mapped[dict[str, Any]] = mapped_column(JSONBType, nullable=False)
    sector_analysis: Mapped[dict[str, Any]] = mapped_column(JSONBType, nullable=False)
    artifact_uri: Mapped[str] = mapped_column(Text, nullable=False)
    artifact_hash: Mapped[str] = mapped_column(String(HASH_LENGTH), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    report: Mapped[ResearchReport] = relationship(back_populates="versions")
    claims: Mapped[list["ResearchClaim"]] = relationship(
        back_populates="report_version", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("report_id", "version", name="uq_research_report_version"),
        UniqueConstraint("artifact_hash", name="uq_research_report_artifact_hash"),
        CheckConstraint("version > 0", name="positive_version"),
        CheckConstraint("confidence >= 0 AND confidence <= 1", name="confidence_range"),
        CheckConstraint("length(artifact_hash) = 64", name="hash_length"),
    )


class ResearchClaim(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "research_claims"

    report_version_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("research_report_versions.id", ondelete="CASCADE"), nullable=False
    )
    claim_text: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)

    report_version: Mapped[ResearchReportVersion] = relationship(back_populates="claims")
    citations: Mapped[list["ClaimCitation"]] = relationship(
        back_populates="claim", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("confidence >= 0 AND confidence <= 1", name="confidence_range"),
    )


class ClaimCitation(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "claim_citations"

    claim_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("research_claims.id", ondelete="CASCADE"), nullable=False
    )
    source_document_version_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("source_document_versions.id", ondelete="RESTRICT"), nullable=False
    )
    locator: Mapped[str] = mapped_column(String(200), nullable=False)

    claim: Mapped[ResearchClaim] = relationship(back_populates="citations")

    __table_args__ = (
        UniqueConstraint("claim_id", "source_document_version_id", "locator", name="uq_claim_citation"),
    )


class Recommendation(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "recommendations"

    tenant_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    workflow_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, server_default="DRAFT")

    workflow: Mapped[Workflow] = relationship(back_populates="recommendations")
    versions: Mapped[list["RecommendationVersion"]] = relationship(
        back_populates="recommendation", cascade="all, delete-orphan"
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "workflow_id"],
            ["workflows.tenant_id", "workflows.id"],
            ondelete="CASCADE",
        ),
        UniqueConstraint("tenant_id", "id", name="uq_recommendations_tenant_id"),
        CheckConstraint(
            "status IN ('DRAFT', 'READY', 'AWAITING_APPROVAL', 'APPROVED', 'REJECTED', 'SUPERSEDED')",
            name="valid_status",
        ),
    )


class RecommendationVersion(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "recommendation_versions"

    recommendation_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("recommendations.id", ondelete="CASCADE"), nullable=False
    )
    research_report_version_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("research_report_versions.id", ondelete="RESTRICT"), nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    expected_return: Mapped[Decimal] = mapped_column(Numeric(9, 6), nullable=False)
    volatility: Mapped[Decimal] = mapped_column(Numeric(9, 6), nullable=False)
    diversification_score: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    investment_horizon_days: Mapped[int] = mapped_column(Integer, nullable=False)
    confidence: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    reasoning: Mapped[str] = mapped_column(Text, nullable=False)
    artifact_hash: Mapped[str] = mapped_column(String(HASH_LENGTH), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    recommendation: Mapped[Recommendation] = relationship(back_populates="versions")
    allocations: Mapped[list["RecommendationAllocation"]] = relationship(
        back_populates="recommendation_version", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("recommendation_id", "version", name="uq_recommendation_version"),
        UniqueConstraint("artifact_hash", name="uq_recommendation_artifact_hash"),
        CheckConstraint("version > 0", name="positive_version"),
        CheckConstraint("expected_return >= -1", name="expected_return_floor"),
        CheckConstraint("volatility >= 0", name="nonnegative_volatility"),
        CheckConstraint(
            "diversification_score >= 0 AND diversification_score <= 1",
            name="diversification_range",
        ),
        CheckConstraint("investment_horizon_days > 0", name="positive_horizon"),
        CheckConstraint("confidence >= 0 AND confidence <= 1", name="confidence_range"),
        CheckConstraint("length(artifact_hash) = 64", name="hash_length"),
    )


class RecommendationAllocation(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "recommendation_allocations"

    recommendation_version_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("recommendation_versions.id", ondelete="CASCADE"), nullable=False
    )
    instrument_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("instruments.id", ondelete="RESTRICT"), nullable=False
    )
    target_weight: Mapped[Decimal] = mapped_column(Numeric(9, 6), nullable=False)
    target_quantity: Mapped[Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    side: Mapped[str] = mapped_column(String(8), nullable=False)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)

    recommendation_version: Mapped[RecommendationVersion] = relationship(back_populates="allocations")

    __table_args__ = (
        UniqueConstraint("recommendation_version_id", "instrument_id", name="uq_recommendation_instrument"),
        CheckConstraint("target_weight >= 0 AND target_weight <= 1", name="target_weight_range"),
        CheckConstraint("target_quantity > 0", name="positive_quantity"),
        CheckConstraint("side IN ('BUY', 'SELL', 'HOLD')", name="valid_side"),
        Index("ix_recommendation_allocations_version", "recommendation_version_id"),
    )


class ValidationRun(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "validation_runs"

    tenant_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    recommendation_version_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("recommendation_versions.id", ondelete="CASCADE"), nullable=False
    )
    rule_set_version: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    results: Mapped[list["ValidationResult"]] = relationship(cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("status IN ('PASS', 'FAIL')", name="valid_status"),
        Index("ix_validation_runs_recommendation", "recommendation_version_id", "completed_at"),
    )


class ValidationResult(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "validation_results"

    validation_run_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("validation_runs.id", ondelete="CASCADE"), nullable=False
    )
    rule_code: Mapped[str] = mapped_column(String(80), nullable=False)
    severity: Mapped[str] = mapped_column(String(16), nullable=False)
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    blocking: Mapped[bool] = mapped_column(Boolean, nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)

    __table_args__ = (
        UniqueConstraint("validation_run_id", "rule_code", name="uq_validation_rule"),
        CheckConstraint("severity IN ('INFO', 'WARNING', 'CRITICAL')", name="valid_severity"),
    )


class ArtifactManifest(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "artifact_manifests"

    tenant_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    workflow_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    recommendation_version_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("recommendation_versions.id", ondelete="RESTRICT"), nullable=False
    )
    schema_version: Mapped[str] = mapped_column(String(32), nullable=False)
    content_hash: Mapped[str] = mapped_column(String(HASH_LENGTH), nullable=False)
    storage_uri: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, server_default="LOCKED")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "workflow_id"],
            ["workflows.tenant_id", "workflows.id"],
            ondelete="RESTRICT",
        ),
        UniqueConstraint("tenant_id", "id", name="uq_artifact_manifests_tenant_id"),
        UniqueConstraint("tenant_id", "content_hash", name="uq_artifact_tenant_hash"),
        CheckConstraint("length(content_hash) = 64", name="hash_length"),
        CheckConstraint("status IN ('LOCKED', 'SUPERSEDED', 'EXPIRED', 'REVOKED')", name="valid_status"),
        CheckConstraint("expires_at > created_at", name="valid_expiry"),
        Index(
            "ix_artifact_manifests_active",
            "tenant_id",
            "workflow_id",
            postgresql_where=text("status = 'LOCKED'"),
        ),
    )


class ApprovalTask(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "approval_tasks"

    tenant_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    workflow_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    artifact_manifest_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    assigned_to: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False, server_default="PENDING")
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    decisions: Mapped[list["ApprovalDecision"]] = relationship(
        back_populates="approval_task", cascade="all, delete-orphan"
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "workflow_id"],
            ["workflows.tenant_id", "workflows.id"],
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["tenant_id", "artifact_manifest_id"],
            ["artifact_manifests.tenant_id", "artifact_manifests.id"],
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["tenant_id", "assigned_to"], ["users.tenant_id", "users.id"], ondelete="RESTRICT"
        ),
        UniqueConstraint("tenant_id", "id", name="uq_approval_tasks_tenant_id"),
        CheckConstraint("status IN ('PENDING', 'APPROVED', 'REJECTED', 'MODIFIED', 'EXPIRED')", name="valid_status"),
        Index(
            "uq_approval_tasks_active_artifact",
            "artifact_manifest_id",
            unique=True,
            postgresql_where=text("status = 'PENDING'"),
        ),
        Index("ix_approval_tasks_assignee_status", "assigned_to", "status"),
    )


class ApprovalDecision(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "approval_decisions"

    tenant_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    approval_task_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    decided_by: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    artifact_hash: Mapped[str] = mapped_column(String(HASH_LENGTH), nullable=False)
    decision: Mapped[str] = mapped_column(String(16), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text)
    attestation: Mapped[str | None] = mapped_column(Text)
    mfa_verified: Mapped[bool] = mapped_column(Boolean, nullable=False)
    decided_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    approval_task: Mapped[ApprovalTask] = relationship(back_populates="decisions")
    execution_intents: Mapped[list["ExecutionIntent"]] = relationship(back_populates="approval_decision")

    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "approval_task_id"],
            ["approval_tasks.tenant_id", "approval_tasks.id"],
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["tenant_id", "decided_by"], ["users.tenant_id", "users.id"], ondelete="RESTRICT"
        ),
        UniqueConstraint("tenant_id", "id", name="uq_approval_decisions_tenant_id"),
        CheckConstraint("length(artifact_hash) = 64", name="hash_length"),
        CheckConstraint("decision IN ('APPROVE', 'REJECT', 'MODIFY')", name="valid_decision"),
        CheckConstraint(
            "(decision = 'APPROVE' AND attestation IS NOT NULL AND mfa_verified) OR "
            "(decision IN ('REJECT', 'MODIFY') AND reason IS NOT NULL)",
            name="decision_evidence",
        ),
        Index(
            "uq_approval_decisions_current_approval",
            "approval_task_id",
            unique=True,
            postgresql_where=text("decision = 'APPROVE' AND revoked_at IS NULL"),
        ),
    )


class Integration(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "integrations"

    tenant_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    category: Mapped[str] = mapped_column(String(32), nullable=False)
    environment: Mapped[str] = mapped_column(String(16), nullable=False, server_default="SANDBOX")
    provider: Mapped[str] = mapped_column(String(120), nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False, server_default="ACTIVE")
    config: Mapped[dict[str, Any]] = mapped_column(JSONBType, nullable=False, server_default=text("'{}'"))

    __table_args__ = (
        UniqueConstraint("tenant_id", "name", "environment", name="uq_integration_name_environment"),
        UniqueConstraint("tenant_id", "id", name="uq_integrations_tenant_id"),
        CheckConstraint("category IN ('MARKET_DATA', 'BROKER', 'CUSTODIAN', 'MODEL')", name="valid_category"),
        CheckConstraint("environment IN ('SANDBOX', 'UAT', 'PRODUCTION')", name="valid_environment"),
        CheckConstraint("status IN ('ACTIVE', 'DEGRADED', 'DISABLED')", name="valid_status"),
    )


class ExecutionIntent(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "execution_intents"

    tenant_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    workflow_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    approval_decision_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    artifact_manifest_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    artifact_hash: Mapped[str] = mapped_column(String(HASH_LENGTH), nullable=False)
    account_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    integration_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(120), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, server_default="PENDING")

    approval_decision: Mapped[ApprovalDecision] = relationship(back_populates="execution_intents")
    orders: Mapped[list["BrokerOrder"]] = relationship(
        back_populates="execution_intent", cascade="all, delete-orphan"
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "workflow_id"],
            ["workflows.tenant_id", "workflows.id"],
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["tenant_id", "approval_decision_id"],
            ["approval_decisions.tenant_id", "approval_decisions.id"],
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["tenant_id", "artifact_manifest_id"],
            ["artifact_manifests.tenant_id", "artifact_manifests.id"],
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["tenant_id", "account_id"], ["accounts.tenant_id", "accounts.id"], ondelete="RESTRICT"
        ),
        ForeignKeyConstraint(
            ["tenant_id", "integration_id"],
            ["integrations.tenant_id", "integrations.id"],
            ondelete="RESTRICT",
        ),
        UniqueConstraint("tenant_id", "id", name="uq_execution_intents_tenant_id"),
        UniqueConstraint("tenant_id", "idempotency_key", name="uq_execution_intent_idempotency"),
        CheckConstraint("length(artifact_hash) = 64", name="hash_length"),
        CheckConstraint(
            "status IN ('PENDING', 'VALIDATED', 'SUBMITTED', 'PARTIAL', 'EXECUTED', "
            "'REJECTED', 'CANCELLED', 'RECONCILIATION_REQUIRED')",
            name="valid_status",
        ),
        Index("ix_execution_intents_tenant_status", "tenant_id", "status"),
    )


class BrokerOrder(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "broker_orders"

    tenant_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    execution_intent_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    instrument_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("instruments.id", ondelete="RESTRICT"), nullable=False
    )
    client_order_id: Mapped[str] = mapped_column(String(120), nullable=False)
    provider_order_id: Mapped[str | None] = mapped_column(String(120))
    side: Mapped[str] = mapped_column(String(8), nullable=False)
    order_type: Mapped[str] = mapped_column(String(16), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    limit_price: Mapped[Decimal | None] = mapped_column(Numeric(20, 6))
    status: Mapped[str] = mapped_column(String(32), nullable=False)

    execution_intent: Mapped[ExecutionIntent] = relationship(back_populates="orders")
    events: Mapped[list["BrokerOrderEvent"]] = relationship(
        back_populates="broker_order", cascade="all, delete-orphan"
    )
    fills: Mapped[list["Fill"]] = relationship(back_populates="broker_order", cascade="all, delete-orphan")

    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "execution_intent_id"],
            ["execution_intents.tenant_id", "execution_intents.id"],
            ondelete="CASCADE",
        ),
        UniqueConstraint("tenant_id", "client_order_id", name="uq_broker_orders_client_order"),
        UniqueConstraint("tenant_id", "provider_order_id", name="uq_broker_orders_provider_order"),
        CheckConstraint("side IN ('BUY', 'SELL')", name="valid_side"),
        CheckConstraint("order_type IN ('MARKET', 'LIMIT', 'VWAP')", name="valid_order_type"),
        CheckConstraint("quantity > 0", name="positive_quantity"),
        CheckConstraint("limit_price IS NULL OR limit_price > 0", name="positive_limit_price"),
        CheckConstraint(
            "status IN ('CREATED', 'QUEUED', 'SUBMITTED', 'PARTIAL', 'FILLED', 'REJECTED', 'CANCELLED')",
            name="valid_status",
        ),
        Index("ix_broker_orders_execution_status", "execution_intent_id", "status"),
    )


class BrokerOrderEvent(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "broker_order_events"

    broker_order_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("broker_orders.id", ondelete="CASCADE"), nullable=False
    )
    provider_message_id: Mapped[str] = mapped_column(String(160), nullable=False)
    sequence_number: Mapped[int] = mapped_column(BigInteger, nullable=False)
    event_type: Mapped[str] = mapped_column(String(40), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONBType, nullable=False, server_default=text("'{}'"))
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    broker_order: Mapped[BrokerOrder] = relationship(back_populates="events")

    __table_args__ = (
        UniqueConstraint("provider_message_id", name="uq_broker_event_provider_message"),
        UniqueConstraint("broker_order_id", "sequence_number", name="uq_broker_event_sequence"),
        CheckConstraint("sequence_number >= 0", name="nonnegative_sequence"),
        Index("ix_broker_order_events_timeline", "broker_order_id", "occurred_at"),
    )


class Fill(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "fills"

    broker_order_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("broker_orders.id", ondelete="RESTRICT"), nullable=False
    )
    execution_id: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    quantity: Mapped[Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    venue: Mapped[str] = mapped_column(String(80), nullable=False)
    executed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    broker_order: Mapped[BrokerOrder] = relationship(back_populates="fills")

    __table_args__ = (
        CheckConstraint("quantity > 0", name="positive_quantity"),
        CheckConstraint("price > 0", name="positive_price"),
        Index("ix_fills_order_executed", "broker_order_id", "executed_at"),
    )


class HoldingSnapshot(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "holding_snapshots"

    tenant_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    portfolio_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    instrument_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("instruments.id", ondelete="RESTRICT"), nullable=False
    )
    workflow_id: Mapped[UUID | None] = mapped_column(Uuid)
    quantity: Mapped[Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    market_price: Mapped[Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    market_value: Mapped[Decimal] = mapped_column(Numeric(20, 4), nullable=False)
    weight: Mapped[Decimal] = mapped_column(Numeric(9, 6), nullable=False)
    target_weight: Mapped[Decimal] = mapped_column(Numeric(9, 6), nullable=False)
    pnl: Mapped[Decimal] = mapped_column(Numeric(20, 4), nullable=False)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "portfolio_id"],
            ["portfolios.tenant_id", "portfolios.id"],
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["tenant_id", "workflow_id"],
            ["workflows.tenant_id", "workflows.id"],
            ondelete="SET NULL",
        ),
        UniqueConstraint(
            "portfolio_id", "instrument_id", "observed_at", name="uq_holding_snapshot_point"
        ),
        CheckConstraint("quantity >= 0", name="nonnegative_quantity"),
        CheckConstraint("market_price > 0", name="positive_market_price"),
        CheckConstraint("weight >= 0 AND weight <= 1", name="weight_range"),
        CheckConstraint("target_weight >= 0 AND target_weight <= 1", name="target_weight_range"),
        Index("ix_holding_snapshots_portfolio_time", "portfolio_id", "observed_at"),
    )


class Alert(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "alerts"

    tenant_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    portfolio_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    workflow_id: Mapped[UUID | None] = mapped_column(Uuid)
    alert_type: Mapped[str] = mapped_column(String(48), nullable=False)
    severity: Mapped[str] = mapped_column(String(16), nullable=False)
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[Decimal | None] = mapped_column(Numeric(5, 4))
    status: Mapped[str] = mapped_column(String(24), nullable=False, server_default="OPEN")

    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "portfolio_id"],
            ["portfolios.tenant_id", "portfolios.id"],
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["tenant_id", "workflow_id"],
            ["workflows.tenant_id", "workflows.id"],
            ondelete="SET NULL",
        ),
        CheckConstraint("severity IN ('INFO', 'WARNING', 'CRITICAL')", name="valid_severity"),
        CheckConstraint("status IN ('OPEN', 'ACKNOWLEDGED', 'RESOLVED')", name="valid_status"),
        CheckConstraint("confidence IS NULL OR (confidence >= 0 AND confidence <= 1)", name="confidence_range"),
        Index("ix_alerts_portfolio_status", "portfolio_id", "status", "severity"),
    )


class AuditEvent(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "audit_events"

    tenant_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    workflow_id: Mapped[UUID | None] = mapped_column(Uuid)
    trace_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    actor_type: Mapped[str] = mapped_column(String(24), nullable=False)
    actor_id: Mapped[UUID | None] = mapped_column(Uuid)
    action: Mapped[str] = mapped_column(String(120), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(80), nullable=False)
    resource_id: Mapped[UUID | None] = mapped_column(Uuid)
    outcome: Mapped[str] = mapped_column(String(24), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONBType, nullable=False, server_default=text("'{}'"))
    previous_event_hash: Mapped[str | None] = mapped_column(String(HASH_LENGTH))
    event_hash: Mapped[str] = mapped_column(String(HASH_LENGTH), nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "workflow_id"],
            ["workflows.tenant_id", "workflows.id"],
            ondelete="SET NULL",
        ),
        CheckConstraint("actor_type IN ('USER', 'AGENT', 'SYSTEM', 'PROVIDER')", name="valid_actor_type"),
        CheckConstraint("outcome IN ('SUCCESS', 'DENIED', 'FAILED', 'PENDING')", name="valid_outcome"),
        CheckConstraint("previous_event_hash IS NULL OR length(previous_event_hash) = 64", name="previous_hash_length"),
        CheckConstraint("length(event_hash) = 64", name="event_hash_length"),
        Index("ix_audit_events_tenant_time", "tenant_id", text("occurred_at DESC")),
        Index("ix_audit_events_trace_time", "trace_id", "occurred_at"),
        Index("ix_audit_events_resource", "resource_type", "resource_id"),
    )


class OutboxEvent(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "outbox_events"

    tenant_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    aggregate_type: Mapped[str] = mapped_column(String(80), nullable=False)
    aggregate_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    event_type: Mapped[str] = mapped_column(String(160), nullable=False)
    event_version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    trace_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONBType, nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")

    __table_args__ = (
        CheckConstraint("event_version > 0", name="positive_event_version"),
        CheckConstraint("attempts >= 0", name="nonnegative_attempts"),
        Index(
            "ix_outbox_events_unpublished",
            "occurred_at",
            postgresql_where=text("published_at IS NULL"),
        ),
    )


class InboxMessage(Base):
    __tablename__ = "inbox_messages"

    consumer_name: Mapped[str] = mapped_column(String(120), primary_key=True)
    event_id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    processed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class IdempotencyRecord(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "idempotency_records"

    tenant_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    scope: Mapped[str] = mapped_column(String(80), nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(120), nullable=False)
    request_hash: Mapped[str] = mapped_column(String(HASH_LENGTH), nullable=False)
    resource_type: Mapped[str | None] = mapped_column(String(80))
    resource_id: Mapped[UUID | None] = mapped_column(Uuid)
    response_code: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        UniqueConstraint("tenant_id", "scope", "idempotency_key", name="uq_idempotency_scope_key"),
        CheckConstraint("length(request_hash) = 64", name="request_hash_length"),
        CheckConstraint("expires_at > created_at", name="valid_expiry"),
        Index("ix_idempotency_records_expiry", "expires_at"),
    )
