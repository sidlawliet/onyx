"""Initial database schema migration.

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-08-07 22:20:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. tenants
    op.create_table(
        "tenants",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("slug", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("status", sa.String(length=24), server_default="ACTIVE", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("status IN ('ACTIVE', 'SUSPENDED')", name="valid_status"),
        sa.PrimaryKeyConstraint("id", name="pk_tenants"),
        sa.UniqueConstraint("slug", name="uq_tenants_slug"),
    )

    # 2. users
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("display_name", sa.String(length=200), nullable=False),
        sa.Column("status", sa.String(length=24), server_default="ACTIVE", nullable=False),
        sa.Column("mfa_enabled", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("is_service_principal", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("status IN ('ACTIVE', 'PENDING', 'SUSPENDED')", name="valid_status"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], name="fk_users_tenant", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_users"),
        sa.UniqueConstraint("tenant_id", "email", name="uq_users_tenant_email"),
        sa.UniqueConstraint("tenant_id", "id", name="uq_users_tenant_id"),
    )
    op.create_index("ix_users_tenant_status", "users", ["tenant_id", "status"], unique=False)

    # 3. roles
    op.create_table(
        "roles",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("permissions", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], name="fk_roles_tenant", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_roles"),
        sa.UniqueConstraint("tenant_id", "name", name="uq_roles_tenant_name"),
        sa.UniqueConstraint("tenant_id", "id", name="uq_roles_tenant_id"),
    )

    # 4. user_role_assignments
    op.create_table(
        "user_role_assignments",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("role_id", sa.Uuid(), nullable=False),
        sa.Column("assigned_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id", "role_id"], ["roles.tenant_id", "roles.id"], name="fk_user_role_assign_role", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tenant_id", "user_id"], ["users.tenant_id", "users.id"], name="fk_user_role_assign_user", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_user_role_assignments"),
        sa.UniqueConstraint("tenant_id", "user_id", "role_id", name="uq_user_role_assignment"),
    )

    # 5. portfolios
    op.create_table(
        "portfolios",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("code", sa.String(length=40), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("base_currency", sa.String(length=3), server_default="USD", nullable=False),
        sa.Column("status", sa.String(length=24), server_default="ACTIVE", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("length(base_currency) = 3", name="currency_length"),
        sa.CheckConstraint("status IN ('ACTIVE', 'CLOSED')", name="valid_status"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], name="fk_portfolios_tenant", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_portfolios"),
        sa.UniqueConstraint("tenant_id", "code", name="uq_portfolios_tenant_code"),
        sa.UniqueConstraint("tenant_id", "id", name="uq_portfolios_tenant_id"),
    )

    # 6. accounts
    op.create_table(
        "accounts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("portfolio_id", sa.Uuid(), nullable=False),
        sa.Column("account_number", sa.String(length=80), nullable=False),
        sa.Column("broker_name", sa.String(length=120), nullable=False),
        sa.Column("available_cash", sa.Numeric(precision=20, scale=4), nullable=False),
        sa.Column("currency", sa.String(length=3), server_default="USD", nullable=False),
        sa.Column("status", sa.String(length=24), server_default="ACTIVE", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("available_cash >= 0", name="nonnegative_cash"),
        sa.CheckConstraint("status IN ('ACTIVE', 'RESTRICTED', 'CLOSED')", name="valid_status"),
        sa.ForeignKeyConstraint(["tenant_id", "portfolio_id"], ["portfolios.tenant_id", "portfolios.id"], name="fk_accounts_portfolio", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_accounts"),
        sa.UniqueConstraint("tenant_id", "account_number", name="uq_accounts_tenant_number"),
        sa.UniqueConstraint("tenant_id", "id", name="uq_accounts_tenant_id"),
    )
    op.create_index("ix_accounts_portfolio", "accounts", ["tenant_id", "portfolio_id"], unique=False)

    # 7. instruments
    op.create_table(
        "instruments",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("symbol", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("asset_class", sa.String(length=40), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("exchange", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("asset_class IN ('EQUITY')", name="hackathon_asset_class"),
        sa.PrimaryKeyConstraint("id", name="pk_instruments"),
        sa.UniqueConstraint("symbol", "exchange", name="uq_instruments_symbol_exchange"),
    )

    # 8. workflows
    op.create_table(
        "workflows",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("portfolio_id", sa.Uuid(), nullable=False),
        sa.Column("created_by", sa.Uuid(), nullable=False),
        sa.Column("trace_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=240), nullable=False),
        sa.Column("stage", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("stage IN ('MARKET_INTELLIGENCE', 'PORTFOLIO_STRATEGY', 'HUMAN_APPROVAL', 'TRADE_EXECUTION', 'PORTFOLIO_MONITORING')", name="valid_stage"),
        sa.CheckConstraint("status IN ('DRAFT', 'RUNNING', 'AWAITING_REVIEW', 'APPROVED', 'REJECTED', 'FAILED', 'HALTED', 'COMPLETED')", name="valid_status"),
        sa.CheckConstraint("version > 0", name="positive_version"),
        sa.ForeignKeyConstraint(["tenant_id", "created_by"], ["users.tenant_id", "users.id"], name="fk_workflows_user", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["tenant_id", "portfolio_id"], ["portfolios.tenant_id", "portfolios.id"], name="fk_workflows_portfolio", ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id", name="pk_workflows"),
        sa.UniqueConstraint("tenant_id", "id", name="uq_workflows_tenant_id"),
        sa.UniqueConstraint("tenant_id", "trace_id", name="uq_workflows_tenant_trace"),
    )
    op.create_index("ix_workflows_portfolio_stage", "workflows", ["portfolio_id", "stage"], unique=False)
    op.create_index("ix_workflows_tenant_status", "workflows", ["tenant_id", "status"], unique=False)

    # 9. workflow_transitions
    op.create_table(
        "workflow_transitions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("workflow_id", sa.Uuid(), nullable=False),
        sa.Column("actor_id", sa.Uuid(), nullable=False),
        sa.Column("from_stage", sa.String(length=40), nullable=True),
        sa.Column("to_stage", sa.String(length=40), nullable=False),
        sa.Column("from_status", sa.String(length=32), nullable=True),
        sa.Column("to_status", sa.String(length=32), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id", "actor_id"], ["users.tenant_id", "users.id"], name="fk_wf_transitions_actor", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["tenant_id", "workflow_id"], ["workflows.tenant_id", "workflows.id"], name="fk_wf_transitions_workflow", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_workflow_transitions"),
    )
    op.create_index("ix_workflow_transitions_timeline", "workflow_transitions", ["workflow_id", "occurred_at"], unique=False)

    # 10. source_documents
    op.create_table(
        "source_documents",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("provider", sa.String(length=120), nullable=False),
        sa.Column("external_id", sa.String(length=200), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=True),
        sa.Column("classification", sa.String(length=32), server_default="INTERNAL", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("classification IN ('PUBLIC', 'INTERNAL', 'CONFIDENTIAL', 'RESTRICTED')", name="valid_classification"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], name="fk_source_docs_tenant", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_source_documents"),
        sa.UniqueConstraint("tenant_id", "provider", "external_id", name="uq_source_external"),
    )

    # 11. source_document_versions
    op.create_table(
        "source_document_versions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("document_id", sa.Uuid(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("retrieved_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("excerpt", sa.Text(), nullable=False),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.CheckConstraint("length(content_hash) = 64", name="hash_length"),
        sa.CheckConstraint("version > 0", name="positive_version"),
        sa.ForeignKeyConstraint(["document_id"], ["source_documents.id"], name="fk_src_doc_vers_doc", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_source_document_versions"),
        sa.UniqueConstraint("document_id", "version", name="uq_source_document_version"),
    )

    # 12. research_reports
    op.create_table(
        "research_reports",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("workflow_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("status", sa.String(length=24), server_default="DRAFT", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("status IN ('DRAFT', 'COMPLETED', 'VERIFIED', 'REJECTED')", name="valid_status"),
        sa.ForeignKeyConstraint(["tenant_id", "workflow_id"], ["workflows.tenant_id", "workflows.id"], name="fk_research_reports_workflow", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_research_reports"),
        sa.UniqueConstraint("tenant_id", "id", name="uq_research_reports_tenant_id"),
    )
    op.create_index("ix_research_reports_workflow", "research_reports", ["workflow_id", "status"], unique=False)

    # 13. research_report_versions
    op.create_table(
        "research_report_versions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("report_id", sa.Uuid(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("model_name", sa.String(length=120), nullable=False),
        sa.Column("model_version", sa.String(length=80), nullable=False),
        sa.Column("confidence", sa.Numeric(precision=5, scale=4), nullable=False),
        sa.Column("market_summary", sa.Text(), nullable=False),
        sa.Column("top_opportunities", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("top_risks", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("company_analysis", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("sector_analysis", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("artifact_uri", sa.Text(), nullable=False),
        sa.Column("artifact_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("length(artifact_hash) = 64", name="hash_length"),
        sa.CheckConstraint("confidence >= 0 AND confidence <= 1", name="confidence_range"),
        sa.CheckConstraint("version > 0", name="positive_version"),
        sa.ForeignKeyConstraint(["report_id"], ["research_reports.id"], name="fk_res_report_vers_report", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_research_report_versions"),
        sa.UniqueConstraint("artifact_hash", name="uq_research_report_artifact_hash"),
        sa.UniqueConstraint("report_id", "version", name="uq_research_report_version"),
    )

    # 14. research_claims
    op.create_table(
        "research_claims",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("report_version_id", sa.Uuid(), nullable=False),
        sa.Column("claim_text", sa.Text(), nullable=False),
        sa.Column("confidence", sa.Numeric(precision=5, scale=4), nullable=False),
        sa.CheckConstraint("confidence >= 0 AND confidence <= 1", name="confidence_range"),
        sa.ForeignKeyConstraint(["report_version_id"], ["research_report_versions.id"], name="fk_res_claims_report_version", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_research_claims"),
    )

    # 15. claim_citations
    op.create_table(
        "claim_citations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("claim_id", sa.Uuid(), nullable=False),
        sa.Column("source_document_version_id", sa.Uuid(), nullable=False),
        sa.Column("locator", sa.String(length=200), nullable=False),
        sa.ForeignKeyConstraint(["claim_id"], ["research_claims.id"], name="fk_claim_citations_claim", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["source_document_version_id"], ["source_document_versions.id"], name="fk_claim_citations_doc_version", ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id", name="pk_claim_citations"),
        sa.UniqueConstraint("claim_id", "source_document_version_id", "locator", name="uq_claim_citation"),
    )

    # 16. recommendations
    op.create_table(
        "recommendations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("workflow_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("status", sa.String(length=32), server_default="DRAFT", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("status IN ('DRAFT', 'READY', 'AWAITING_APPROVAL', 'APPROVED', 'REJECTED', 'SUPERSEDED')", name="valid_status"),
        sa.ForeignKeyConstraint(["tenant_id", "workflow_id"], ["workflows.tenant_id", "workflows.id"], name="fk_recommendations_workflow", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_recommendations"),
        sa.UniqueConstraint("tenant_id", "id", name="uq_recommendations_tenant_id"),
    )

    # 17. recommendation_versions
    op.create_table(
        "recommendation_versions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("recommendation_id", sa.Uuid(), nullable=False),
        sa.Column("research_report_version_id", sa.Uuid(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("expected_return", sa.Numeric(precision=9, scale=6), nullable=False),
        sa.Column("volatility", sa.Numeric(precision=9, scale=6), nullable=False),
        sa.Column("diversification_score", sa.Numeric(precision=5, scale=4), nullable=False),
        sa.Column("investment_horizon_days", sa.Integer(), nullable=False),
        sa.Column("confidence", sa.Numeric(precision=5, scale=4), nullable=False),
        sa.Column("reasoning", sa.Text(), nullable=False),
        sa.Column("artifact_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("length(artifact_hash) = 64", name="hash_length"),
        sa.CheckConstraint("confidence >= 0 AND confidence <= 1", name="confidence_range"),
        sa.CheckConstraint("diversification_score >= 0 AND diversification_score <= 1", name="diversification_range"),
        sa.CheckConstraint("expected_return >= -1", name="expected_return_floor"),
        sa.CheckConstraint("investment_horizon_days > 0", name="positive_horizon"),
        sa.CheckConstraint("version > 0", name="positive_version"),
        sa.CheckConstraint("volatility >= 0", name="nonnegative_volatility"),
        sa.ForeignKeyConstraint(["recommendation_id"], ["recommendations.id"], name="fk_rec_versions_recommendation", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["research_report_version_id"], ["research_report_versions.id"], name="fk_rec_versions_res_report", ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id", name="pk_recommendation_versions"),
        sa.UniqueConstraint("artifact_hash", name="uq_recommendation_artifact_hash"),
        sa.UniqueConstraint("recommendation_id", "version", name="uq_recommendation_version"),
    )

    # 18. recommendation_allocations
    op.create_table(
        "recommendation_allocations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("recommendation_version_id", sa.Uuid(), nullable=False),
        sa.Column("instrument_id", sa.Uuid(), nullable=False),
        sa.Column("target_weight", sa.Numeric(precision=9, scale=6), nullable=False),
        sa.Column("target_quantity", sa.Numeric(precision=20, scale=6), nullable=False),
        sa.Column("side", sa.String(length=8), nullable=False),
        sa.Column("rationale", sa.Text(), nullable=False),
        sa.CheckConstraint("target_quantity > 0", name="positive_quantity"),
        sa.CheckConstraint("side IN ('BUY', 'SELL', 'HOLD')", name="valid_side"),
        sa.CheckConstraint("target_weight >= 0 AND target_weight <= 1", name="target_weight_range"),
        sa.ForeignKeyConstraint(["instrument_id"], ["instruments.id"], name="fk_rec_allocations_instrument", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["recommendation_version_id"], ["recommendation_versions.id"], name="fk_rec_allocations_version", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_recommendation_allocations"),
        sa.UniqueConstraint("recommendation_version_id", "instrument_id", name="uq_recommendation_instrument"),
    )
    op.create_index("ix_recommendation_allocations_version", "recommendation_allocations", ["recommendation_version_id"], unique=False)

    # 19. validation_runs
    op.create_table(
        "validation_runs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("recommendation_version_id", sa.Uuid(), nullable=False),
        sa.Column("rule_set_version", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("status IN ('PASS', 'FAIL')", name="valid_status"),
        sa.ForeignKeyConstraint(["recommendation_version_id"], ["recommendation_versions.id"], name="fk_val_runs_rec_version", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_validation_runs"),
    )
    op.create_index("ix_validation_runs_recommendation", "validation_runs", ["recommendation_version_id", "completed_at"], unique=False)

    # 20. validation_results
    op.create_table(
        "validation_results",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("validation_run_id", sa.Uuid(), nullable=False),
        sa.Column("rule_code", sa.String(length=80), nullable=False),
        sa.Column("severity", sa.String(length=16), nullable=False),
        sa.Column("passed", sa.Boolean(), nullable=False),
        sa.Column("blocking", sa.Boolean(), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.CheckConstraint("severity IN ('INFO', 'WARNING', 'CRITICAL')", name="valid_severity"),
        sa.ForeignKeyConstraint(["validation_run_id"], ["validation_runs.id"], name="fk_val_results_val_run", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_validation_results"),
        sa.UniqueConstraint("validation_run_id", "rule_code", name="uq_validation_rule"),
    )

    # 21. artifact_manifests
    op.create_table(
        "artifact_manifests",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("workflow_id", sa.Uuid(), nullable=False),
        sa.Column("recommendation_version_id", sa.Uuid(), nullable=False),
        sa.Column("schema_version", sa.String(length=32), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("storage_uri", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=16), server_default="LOCKED", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("length(content_hash) = 64", name="hash_length"),
        sa.CheckConstraint("expires_at > created_at", name="valid_expiry"),
        sa.CheckConstraint("status IN ('LOCKED', 'SUPERSEDED', 'EXPIRED', 'REVOKED')", name="valid_status"),
        sa.ForeignKeyConstraint(["recommendation_version_id"], ["recommendation_versions.id"], name="fk_artifact_manifests_rec_version", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["tenant_id", "workflow_id"], ["workflows.tenant_id", "workflows.id"], name="fk_artifact_manifests_workflow", ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id", name="pk_artifact_manifests"),
        sa.UniqueConstraint("tenant_id", "content_hash", name="uq_artifact_tenant_hash"),
        sa.UniqueConstraint("tenant_id", "id", name="uq_artifact_manifests_tenant_id"),
    )
    op.create_index("ix_artifact_manifests_active", "artifact_manifests", ["tenant_id", "workflow_id"], unique=False, postgresql_where=sa.text("status = 'LOCKED'"))

    # 22. approval_tasks
    op.create_table(
        "approval_tasks",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("workflow_id", sa.Uuid(), nullable=False),
        sa.Column("artifact_manifest_id", sa.Uuid(), nullable=False),
        sa.Column("assigned_to", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=24), server_default="PENDING", nullable=False),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("status IN ('PENDING', 'APPROVED', 'REJECTED', 'MODIFIED', 'EXPIRED')", name="valid_status"),
        sa.ForeignKeyConstraint(["tenant_id", "artifact_manifest_id"], ["artifact_manifests.tenant_id", "artifact_manifests.id"], name="fk_app_tasks_manifest", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["tenant_id", "assigned_to"], ["users.tenant_id", "users.id"], name="fk_app_tasks_assignee", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["tenant_id", "workflow_id"], ["workflows.tenant_id", "workflows.id"], name="fk_app_tasks_workflow", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_approval_tasks"),
        sa.UniqueConstraint("tenant_id", "id", name="uq_approval_tasks_tenant_id"),
    )
    op.create_index("ix_approval_tasks_assignee_status", "approval_tasks", ["assigned_to", "status"], unique=False)
    op.create_index("uq_approval_tasks_active_artifact", "approval_tasks", ["artifact_manifest_id"], unique=True, postgresql_where=sa.text("status = 'PENDING'"))

    # 23. approval_decisions
    op.create_table(
        "approval_decisions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("approval_task_id", sa.Uuid(), nullable=False),
        sa.Column("decided_by", sa.Uuid(), nullable=False),
        sa.Column("artifact_hash", sa.String(length=64), nullable=False),
        sa.Column("decision", sa.String(length=16), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("attestation", sa.Text(), nullable=True),
        sa.Column("mfa_verified", sa.Boolean(), nullable=False),
        sa.Column("decided_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("length(artifact_hash) = 64", name="hash_length"),
        sa.CheckConstraint("decision IN ('APPROVE', 'REJECT', 'MODIFY')", name="valid_decision"),
        sa.CheckConstraint("(decision = 'APPROVE' AND attestation IS NOT NULL AND mfa_verified) OR (decision IN ('REJECT', 'MODIFY') AND reason IS NOT NULL)", name="decision_evidence"),
        sa.ForeignKeyConstraint(["tenant_id", "approval_task_id"], ["approval_tasks.tenant_id", "approval_tasks.id"], name="fk_app_decisions_task", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tenant_id", "decided_by"], ["users.tenant_id", "users.id"], name="fk_app_decisions_user", ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id", name="pk_approval_decisions"),
        sa.UniqueConstraint("tenant_id", "id", name="uq_approval_decisions_tenant_id"),
    )
    op.create_index("uq_approval_decisions_current_approval", "approval_decisions", ["approval_task_id"], unique=True, postgresql_where=sa.text("decision = 'APPROVE' AND revoked_at IS NULL"))

    # 24. integrations
    op.create_table(
        "integrations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("category", sa.String(length=32), nullable=False),
        sa.Column("environment", sa.String(length=16), server_default="SANDBOX", nullable=False),
        sa.Column("provider", sa.String(length=120), nullable=False),
        sa.Column("status", sa.String(length=24), server_default="ACTIVE", nullable=False),
        sa.Column("config", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("category IN ('MARKET_DATA', 'BROKER', 'CUSTODIAN', 'MODEL')", name="valid_category"),
        sa.CheckConstraint("environment IN ('SANDBOX', 'UAT', 'PRODUCTION')", name="valid_environment"),
        sa.CheckConstraint("status IN ('ACTIVE', 'DEGRADED', 'DISABLED')", name="valid_status"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], name="fk_integrations_tenant", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_integrations"),
        sa.UniqueConstraint("tenant_id", "id", name="uq_integrations_tenant_id"),
        sa.UniqueConstraint("tenant_id", "name", "environment", name="uq_integration_name_environment"),
    )

    # 25. execution_intents
    op.create_table(
        "execution_intents",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("workflow_id", sa.Uuid(), nullable=False),
        sa.Column("approval_decision_id", sa.Uuid(), nullable=False),
        sa.Column("artifact_manifest_id", sa.Uuid(), nullable=False),
        sa.Column("artifact_hash", sa.String(length=64), nullable=False),
        sa.Column("account_id", sa.Uuid(), nullable=False),
        sa.Column("integration_id", sa.Uuid(), nullable=False),
        sa.Column("idempotency_key", sa.String(length=120), nullable=False),
        sa.Column("status", sa.String(length=32), server_default="PENDING", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("length(artifact_hash) = 64", name="hash_length"),
        sa.CheckConstraint("status IN ('PENDING', 'VALIDATED', 'SUBMITTED', 'PARTIAL', 'EXECUTED', 'REJECTED', 'CANCELLED', 'RECONCILIATION_REQUIRED')", name="valid_status"),
        sa.ForeignKeyConstraint(["tenant_id", "account_id"], ["accounts.tenant_id", "accounts.id"], name="fk_exec_intents_account", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["tenant_id", "approval_decision_id"], ["approval_decisions.tenant_id", "approval_decisions.id"], name="fk_exec_intents_decision", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["tenant_id", "artifact_manifest_id"], ["artifact_manifests.tenant_id", "artifact_manifests.id"], name="fk_exec_intents_manifest", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["tenant_id", "integration_id"], ["integrations.tenant_id", "integrations.id"], name="fk_exec_intents_integration", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["tenant_id", "workflow_id"], ["workflows.tenant_id", "workflows.id"], name="fk_exec_intents_workflow", ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id", name="pk_execution_intents"),
        sa.UniqueConstraint("tenant_id", "id", name="uq_execution_intents_tenant_id"),
        sa.UniqueConstraint("tenant_id", "idempotency_key", name="uq_execution_intent_idempotency"),
    )
    op.create_index("ix_execution_intents_tenant_status", "execution_intents", ["tenant_id", "status"], unique=False)

    # 26. broker_orders
    op.create_table(
        "broker_orders",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("execution_intent_id", sa.Uuid(), nullable=False),
        sa.Column("instrument_id", sa.Uuid(), nullable=False),
        sa.Column("client_order_id", sa.String(length=120), nullable=False),
        sa.Column("provider_order_id", sa.String(length=120), nullable=True),
        sa.Column("side", sa.String(length=8), nullable=False),
        sa.Column("order_type", sa.String(length=16), nullable=False),
        sa.Column("quantity", sa.Numeric(precision=20, scale=6), nullable=False),
        sa.Column("limit_price", sa.Numeric(precision=20, scale=6), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("limit_price IS NULL OR limit_price > 0", name="positive_limit_price"),
        sa.CheckConstraint("order_type IN ('MARKET', 'LIMIT', 'VWAP')", name="valid_order_type"),
        sa.CheckConstraint("quantity > 0", name="positive_quantity"),
        sa.CheckConstraint("side IN ('BUY', 'SELL')", name="valid_side"),
        sa.CheckConstraint("status IN ('CREATED', 'QUEUED', 'SUBMITTED', 'PARTIAL', 'FILLED', 'REJECTED', 'CANCELLED')", name="valid_status"),
        sa.ForeignKeyConstraint(["instrument_id"], ["instruments.id"], name="fk_broker_orders_instrument", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["tenant_id", "execution_intent_id"], ["execution_intents.tenant_id", "execution_intents.id"], name="fk_broker_orders_intent", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_broker_orders"),
        sa.UniqueConstraint("tenant_id", "client_order_id", name="uq_broker_orders_client_order"),
        sa.UniqueConstraint("tenant_id", "provider_order_id", name="uq_broker_orders_provider_order"),
    )
    op.create_index("ix_broker_orders_execution_status", "broker_orders", ["execution_intent_id", "status"], unique=False)

    # 27. broker_order_events
    op.create_table(
        "broker_order_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("broker_order_id", sa.Uuid(), nullable=False),
        sa.Column("provider_message_id", sa.String(length=160), nullable=False),
        sa.Column("sequence_number", sa.BigInteger(), nullable=False),
        sa.Column("event_type", sa.String(length=40), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("received_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("sequence_number >= 0", name="nonnegative_sequence"),
        sa.ForeignKeyConstraint(["broker_order_id"], ["broker_orders.id"], name="fk_broker_events_order", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_broker_order_events"),
        sa.UniqueConstraint("broker_order_id", "sequence_number", name="uq_broker_event_sequence"),
        sa.UniqueConstraint("provider_message_id", name="uq_broker_event_provider_message"),
    )
    op.create_index("ix_broker_order_events_timeline", "broker_order_events", ["broker_order_id", "occurred_at"], unique=False)

    # 28. fills
    op.create_table(
        "fills",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("broker_order_id", sa.Uuid(), nullable=False),
        sa.Column("execution_id", sa.String(length=120), nullable=False),
        sa.Column("quantity", sa.Numeric(precision=20, scale=6), nullable=False),
        sa.Column("price", sa.Numeric(precision=20, scale=6), nullable=False),
        sa.Column("venue", sa.String(length=80), nullable=False),
        sa.Column("executed_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("price > 0", name="positive_price"),
        sa.CheckConstraint("quantity > 0", name="positive_quantity"),
        sa.ForeignKeyConstraint(["broker_order_id"], ["broker_orders.id"], name="fk_fills_broker_order", ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id", name="pk_fills"),
        sa.UniqueConstraint("execution_id", name="uq_fills_execution_id"),
    )
    op.create_index("ix_fills_order_executed", "fills", ["broker_order_id", "executed_at"], unique=False)

    # 29. holding_snapshots
    op.create_table(
        "holding_snapshots",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("portfolio_id", sa.Uuid(), nullable=False),
        sa.Column("instrument_id", sa.Uuid(), nullable=False),
        sa.Column("workflow_id", sa.Uuid(), nullable=True),
        sa.Column("quantity", sa.Numeric(precision=20, scale=6), nullable=False),
        sa.Column("market_price", sa.Numeric(precision=20, scale=6), nullable=False),
        sa.Column("market_value", sa.Numeric(precision=20, scale=4), nullable=False),
        sa.Column("weight", sa.Numeric(precision=9, scale=6), nullable=False),
        sa.Column("target_weight", sa.Numeric(precision=9, scale=6), nullable=False),
        sa.Column("pnl", sa.Numeric(precision=20, scale=4), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("market_price > 0", name="positive_market_price"),
        sa.CheckConstraint("quantity >= 0", name="nonnegative_quantity"),
        sa.CheckConstraint("target_weight >= 0 AND target_weight <= 1", name="target_weight_range"),
        sa.CheckConstraint("weight >= 0 AND weight <= 1", name="weight_range"),
        sa.ForeignKeyConstraint(["instrument_id"], ["instruments.id"], name="fk_holding_snapshots_instrument", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["tenant_id", "portfolio_id"], ["portfolios.tenant_id", "portfolios.id"], name="fk_holding_snapshots_portfolio", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tenant_id", "workflow_id"], ["workflows.tenant_id", "workflows.id"], name="fk_holding_snapshots_workflow", ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name="pk_holding_snapshots"),
        sa.UniqueConstraint("portfolio_id", "instrument_id", "observed_at", name="uq_holding_snapshot_point"),
    )
    op.create_index("ix_holding_snapshots_portfolio_time", "holding_snapshots", ["portfolio_id", "observed_at"], unique=False)

    # 30. alerts
    op.create_table(
        "alerts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("portfolio_id", sa.Uuid(), nullable=False),
        sa.Column("workflow_id", sa.Uuid(), nullable=True),
        sa.Column("alert_type", sa.String(length=48), nullable=False),
        sa.Column("severity", sa.String(length=16), nullable=False),
        sa.Column("title", sa.String(length=240), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("confidence", sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column("status", sa.String(length=24), server_default="OPEN", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("confidence IS NULL OR (confidence >= 0 AND confidence <= 1)", name="confidence_range"),
        sa.CheckConstraint("severity IN ('INFO', 'WARNING', 'CRITICAL')", name="valid_severity"),
        sa.CheckConstraint("status IN ('OPEN', 'ACKNOWLEDGED', 'RESOLVED')", name="valid_status"),
        sa.ForeignKeyConstraint(["tenant_id", "portfolio_id"], ["portfolios.tenant_id", "portfolios.id"], name="fk_alerts_portfolio", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tenant_id", "workflow_id"], ["workflows.tenant_id", "workflows.id"], name="fk_alerts_workflow", ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name="pk_alerts"),
    )
    op.create_index("ix_alerts_portfolio_status", "alerts", ["portfolio_id", "status", "severity"], unique=False)

    # 31. audit_events
    op.create_table(
        "audit_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("workflow_id", sa.Uuid(), nullable=True),
        sa.Column("trace_id", sa.Uuid(), nullable=False),
        sa.Column("actor_type", sa.String(length=24), nullable=False),
        sa.Column("actor_id", sa.Uuid(), nullable=True),
        sa.Column("action", sa.String(length=120), nullable=False),
        sa.Column("resource_type", sa.String(length=80), nullable=False),
        sa.Column("resource_id", sa.Uuid(), nullable=True),
        sa.Column("outcome", sa.String(length=24), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("previous_event_hash", sa.String(length=64), nullable=True),
        sa.Column("event_hash", sa.String(length=64), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("actor_type IN ('USER', 'AGENT', 'SYSTEM', 'PROVIDER')", name="valid_actor_type"),
        sa.CheckConstraint("char_length(event_hash) = 64", name="event_hash_length"),
        sa.CheckConstraint("outcome IN ('SUCCESS', 'DENIED', 'FAILED', 'PENDING')", name="valid_outcome"),
        sa.CheckConstraint("previous_event_hash IS NULL OR char_length(previous_event_hash) = 64", name="previous_hash_length"),
        sa.ForeignKeyConstraint(["tenant_id", "workflow_id"], ["workflows.tenant_id", "workflows.id"], name="fk_audit_events_workflow", ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name="pk_audit_events"),
    )
    op.create_index("ix_audit_events_resource", "audit_events", ["resource_type", "resource_id"], unique=False)
    op.create_index("ix_audit_events_tenant_time", "audit_events", ["tenant_id", sa.text("occurred_at DESC")], unique=False)
    op.create_index("ix_audit_events_trace_time", "audit_events", ["trace_id", "occurred_at"], unique=False)

    # 32. outbox_events
    op.create_table(
        "outbox_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("aggregate_type", sa.String(length=80), nullable=False),
        sa.Column("aggregate_id", sa.Uuid(), nullable=False),
        sa.Column("event_type", sa.String(length=160), nullable=False),
        sa.Column("event_version", sa.Integer(), server_default="1", nullable=False),
        sa.Column("trace_id", sa.Uuid(), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("attempts", sa.Integer(), server_default="0", nullable=False),
        sa.CheckConstraint("attempts >= 0", name="nonnegative_attempts"),
        sa.CheckConstraint("event_version > 0", name="positive_event_version"),
        sa.PrimaryKeyConstraint("id", name="pk_outbox_events"),
    )
    op.create_index("ix_outbox_events_unpublished", "outbox_events", ["occurred_at"], unique=False, postgresql_where=sa.text("published_at IS NULL"))

    # 33. inbox_messages
    op.create_table(
        "inbox_messages",
        sa.Column("consumer_name", sa.String(length=120), nullable=False),
        sa.Column("event_id", sa.Uuid(), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("consumer_name", "event_id", name="pk_inbox_messages"),
    )

    # 34. idempotency_records
    op.create_table(
        "idempotency_records",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("scope", sa.String(length=80), nullable=False),
        sa.Column("idempotency_key", sa.String(length=120), nullable=False),
        sa.Column("request_hash", sa.String(length=64), nullable=False),
        sa.Column("resource_type", sa.String(length=80), nullable=True),
        sa.Column("resource_id", sa.Uuid(), nullable=True),
        sa.Column("response_code", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("char_length(request_hash) = 64", name="request_hash_length"),
        sa.CheckConstraint("expires_at > created_at", name="valid_expiry"),
        sa.PrimaryKeyConstraint("id", name="pk_idempotency_records"),
        sa.UniqueConstraint("tenant_id", "scope", "idempotency_key", name="uq_idempotency_scope_key"),
    )
    op.create_index("ix_idempotency_records_expiry", "idempotency_records", ["expires_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_idempotency_records_expiry", table_name="idempotency_records")
    op.drop_table("idempotency_records")

    op.drop_table("inbox_messages")

    op.drop_index("ix_outbox_events_unpublished", table_name="outbox_events")
    op.drop_table("outbox_events")

    op.drop_index("ix_audit_events_resource", table_name="audit_events")
    op.drop_index("ix_audit_events_trace_time", table_name="audit_events")
    op.drop_index("ix_audit_events_tenant_time", table_name="audit_events")
    op.drop_table("audit_events")

    op.drop_index("ix_alerts_portfolio_status", table_name="alerts")
    op.drop_table("alerts")

    op.drop_index("ix_holding_snapshots_portfolio_time", table_name="holding_snapshots")
    op.drop_table("holding_snapshots")

    op.drop_index("ix_fills_order_executed", table_name="fills")
    op.drop_table("fills")

    op.drop_index("ix_broker_order_events_timeline", table_name="broker_order_events")
    op.drop_table("broker_order_events")

    op.drop_index("ix_broker_orders_execution_status", table_name="broker_orders")
    op.drop_table("broker_orders")

    op.drop_index("ix_execution_intents_tenant_status", table_name="execution_intents")
    op.drop_table("execution_intents")

    op.drop_table("integrations")

    op.drop_index("uq_approval_decisions_current_approval", table_name="approval_decisions")
    op.drop_table("approval_decisions")

    op.drop_index("uq_approval_tasks_active_artifact", table_name="approval_tasks")
    op.drop_index("ix_approval_tasks_assignee_status", table_name="approval_tasks")
    op.drop_table("approval_tasks")

    op.drop_index("ix_artifact_manifests_active", table_name="artifact_manifests")
    op.drop_table("artifact_manifests")

    op.drop_table("validation_results")

    op.drop_index("ix_validation_runs_recommendation", table_name="validation_runs")
    op.drop_table("validation_runs")

    op.drop_index("ix_recommendation_allocations_version", table_name="recommendation_allocations")
    op.drop_table("recommendation_allocations")

    op.drop_table("recommendation_versions")
    op.drop_table("recommendations")
    op.drop_table("claim_citations")
    op.drop_table("research_claims")
    op.drop_table("research_report_versions")

    op.drop_index("ix_research_reports_workflow", table_name="research_reports")
    op.drop_table("research_reports")

    op.drop_table("source_document_versions")
    op.drop_table("source_documents")

    op.drop_index("ix_workflow_transitions_timeline", table_name="workflow_transitions")
    op.drop_table("workflow_transitions")

    op.drop_index("ix_workflows_tenant_status", table_name="workflows")
    op.drop_index("ix_workflows_portfolio_stage", table_name="workflows")
    op.drop_table("workflows")

    op.drop_table("instruments")

    op.drop_index("ix_accounts_portfolio", table_name="accounts")
    op.drop_table("accounts")

    op.drop_table("portfolios")
    op.drop_table("user_role_assignments")
    op.drop_table("roles")

    op.drop_index("ix_users_tenant_status", table_name="users")
    op.drop_table("users")

    op.drop_table("tenants")
