import hashlib
import json
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import delete
from sqlalchemy.orm import Session

from apps.api.app.db.models import (
    Account,
    Alert,
    ApprovalDecision,
    ApprovalTask,
    ArtifactManifest,
    AuditEvent,
    BrokerOrder,
    BrokerOrderEvent,
    ClaimCitation,
    ExecutionIntent,
    Fill,
    HoldingSnapshot,
    IdempotencyRecord,
    InboxMessage,
    Integration,
    Instrument,
    OutboxEvent,
    Portfolio,
    Recommendation,
    RecommendationAllocation,
    RecommendationVersion,
    ResearchClaim,
    ResearchReport,
    ResearchReportVersion,
    Role,
    SourceDocument,
    SourceDocumentVersion,
    Tenant,
    User,
    UserRoleAssignment,
    ValidationResult,
    ValidationRun,
    Workflow,
    WorkflowTransition,
)
from apps.api.app.db.session import SessionLocal

# Fixed Seed UUIDs for deterministic demo references
DEMO_TENANT_ID = UUID("00000000-0000-4000-a000-000000000001")
USER_ANALYST_ID = UUID("00000000-0000-4000-a000-000000000010")
USER_APPROVER_ID = UUID("00000000-0000-4000-a000-000000000011")
USER_TRADER_ID = UUID("00000000-0000-4000-a000-000000000012")
USER_AUDITOR_ID = UUID("00000000-0000-4000-a000-000000000013")

PORTFOLIO_ID = UUID("00000000-0000-4000-a000-000000000020")
ACCOUNT_ID = UUID("00000000-0000-4000-a000-000000000030")

WORKFLOW_ID = UUID("00000000-0000-4000-a000-000000000040")
TRACE_ID = UUID("11111111-1111-4111-a111-111111111111")

INST_AAPL_ID = UUID("00000000-0000-4000-a000-000000000101")
INST_MSFT_ID = UUID("00000000-0000-4000-a000-000000000102")
INST_NVDA_ID = UUID("00000000-0000-4000-a000-000000000103")
INST_GOOGL_ID = UUID("00000000-0000-4000-a000-000000000104")


def compute_sha256(data: str | dict) -> str:
    """Helper to compute deterministic 64-char SHA256 hex string."""
    if isinstance(data, dict):
        raw = json.dumps(data, sort_keys=True)
    else:
        raw = str(data)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def reset_demo_data(session: Session) -> None:
    """Purge all existing records for the demo tenant to allow repeatable demo resets."""
    # Delete in reverse dependency order
    session.execute(delete(AuditEvent).where(AuditEvent.tenant_id == DEMO_TENANT_ID))
    session.execute(delete(OutboxEvent).where(OutboxEvent.tenant_id == DEMO_TENANT_ID))
    session.execute(delete(IdempotencyRecord).where(IdempotencyRecord.tenant_id == DEMO_TENANT_ID))
    session.execute(delete(Alert).where(Alert.tenant_id == DEMO_TENANT_ID))
    session.execute(delete(HoldingSnapshot).where(HoldingSnapshot.tenant_id == DEMO_TENANT_ID))

    # Execution & Fills
    session.execute(
        delete(Fill).where(
            Fill.broker_order_id.in_(
                session.query(BrokerOrder.id).filter(BrokerOrder.tenant_id == DEMO_TENANT_ID)
            )
        )
    )
    session.execute(
        delete(BrokerOrderEvent).where(
            BrokerOrderEvent.broker_order_id.in_(
                session.query(BrokerOrder.id).filter(BrokerOrder.tenant_id == DEMO_TENANT_ID)
            )
        )
    )
    session.execute(delete(BrokerOrder).where(BrokerOrder.tenant_id == DEMO_TENANT_ID))
    session.execute(delete(ExecutionIntent).where(ExecutionIntent.tenant_id == DEMO_TENANT_ID))

    # Approvals & Artifacts
    session.execute(delete(ApprovalDecision).where(ApprovalDecision.tenant_id == DEMO_TENANT_ID))
    session.execute(delete(ApprovalTask).where(ApprovalTask.tenant_id == DEMO_TENANT_ID))
    session.execute(delete(ArtifactManifest).where(ArtifactManifest.tenant_id == DEMO_TENANT_ID))

    # Validations & Recommendations
    session.execute(delete(ValidationResult).where(
        ValidationResult.validation_run_id.in_(
            session.query(ValidationRun.id).filter(ValidationRun.tenant_id == DEMO_TENANT_ID)
        )
    ))
    session.execute(delete(ValidationRun).where(ValidationRun.tenant_id == DEMO_TENANT_ID))
    session.execute(delete(RecommendationAllocation).where(
        RecommendationAllocation.recommendation_version_id.in_(
            session.query(RecommendationVersion.id).join(Recommendation).filter(Recommendation.tenant_id == DEMO_TENANT_ID)
        )
    ))
    session.execute(delete(RecommendationVersion).where(
        RecommendationVersion.recommendation_id.in_(
            session.query(Recommendation.id).filter(Recommendation.tenant_id == DEMO_TENANT_ID)
        )
    ))
    session.execute(delete(Recommendation).where(Recommendation.tenant_id == DEMO_TENANT_ID))

    # Research & Citations
    session.execute(delete(ClaimCitation).where(
        ClaimCitation.claim_id.in_(
            session.query(ResearchClaim.id).join(ResearchReportVersion).join(ResearchReport).filter(ResearchReport.tenant_id == DEMO_TENANT_ID)
        )
    ))
    session.execute(delete(ResearchClaim).where(
        ResearchClaim.report_version_id.in_(
            session.query(ResearchReportVersion.id).join(ResearchReport).filter(ResearchReport.tenant_id == DEMO_TENANT_ID)
        )
    ))
    session.execute(delete(ResearchReportVersion).where(
        ResearchReportVersion.report_id.in_(
            session.query(ResearchReport.id).filter(ResearchReport.tenant_id == DEMO_TENANT_ID)
        )
    ))
    session.execute(delete(ResearchReport).where(ResearchReport.tenant_id == DEMO_TENANT_ID))

    # Source documents
    session.execute(delete(SourceDocumentVersion).where(
        SourceDocumentVersion.document_id.in_(
            session.query(SourceDocument.id).filter(SourceDocument.tenant_id == DEMO_TENANT_ID)
        )
    ))
    session.execute(delete(SourceDocument).where(SourceDocument.tenant_id == DEMO_TENANT_ID))

    # Workflows
    session.execute(delete(WorkflowTransition).where(WorkflowTransition.tenant_id == DEMO_TENANT_ID))
    session.execute(delete(Workflow).where(Workflow.tenant_id == DEMO_TENANT_ID))

    # Accounts, Portfolios, Integrations
    session.execute(delete(Account).where(Account.tenant_id == DEMO_TENANT_ID))
    session.execute(delete(Portfolio).where(Portfolio.tenant_id == DEMO_TENANT_ID))
    session.execute(delete(Integration).where(Integration.tenant_id == DEMO_TENANT_ID))

    # Users, Roles, Assignments, Tenant
    session.execute(delete(UserRoleAssignment).where(UserRoleAssignment.tenant_id == DEMO_TENANT_ID))
    session.execute(delete(Role).where(Role.tenant_id == DEMO_TENANT_ID))
    session.execute(delete(User).where(User.tenant_id == DEMO_TENANT_ID))
    session.execute(delete(Tenant).where(Tenant.id == DEMO_TENANT_ID))

    session.commit()


def seed_demo_data(session: Session) -> dict[str, UUID]:
    """Seed full single-tenant demo state for InvestOps AI."""
    # Reset existing demo tenant data first to guarantee idempotent seed execution
    reset_demo_data(session)

    now = datetime.now(timezone.utc)

    # 1. Tenant
    tenant = Tenant(
        id=DEMO_TENANT_ID,
        slug="demo-tenant",
        name="InvestOps Institutional Demo",
        status="ACTIVE",
    )
    session.add(tenant)
    session.flush()

    # 2. Roles & Users
    roles = {
        "Analyst": Role(
            tenant_id=DEMO_TENANT_ID,
            name="Analyst",
            permissions={"market_intelligence": ["read", "write"], "strategy": ["read", "create"]},
        ),
        "Portfolio Manager": Role(
            tenant_id=DEMO_TENANT_ID,
            name="Portfolio Manager",
            permissions={"strategy": ["read", "publish"], "approval": ["decide"]},
        ),
        "Trader": Role(
            tenant_id=DEMO_TENANT_ID,
            name="Trader",
            permissions={"execution": ["read", "submit", "cancel"]},
        ),
        "Auditor": Role(
            tenant_id=DEMO_TENANT_ID,
            name="Auditor",
            permissions={"audit": ["read", "export"]},
        ),
    }
    for r in roles.values():
        session.add(r)
    session.flush()

    users = {
        "analyst": User(
            id=USER_ANALYST_ID,
            tenant_id=DEMO_TENANT_ID,
            email="analyst@investops.ai",
            display_name="Market Research Analyst",
            status="ACTIVE",
            mfa_enabled=True,
        ),
        "approver": User(
            id=USER_APPROVER_ID,
            tenant_id=DEMO_TENANT_ID,
            email="approver@investops.ai",
            display_name="Senior Portfolio Manager / Approver",
            status="ACTIVE",
            mfa_enabled=True,
        ),
        "trader": User(
            id=USER_TRADER_ID,
            tenant_id=DEMO_TENANT_ID,
            email="trader@investops.ai",
            display_name="Head of Execution",
            status="ACTIVE",
            mfa_enabled=True,
        ),
        "auditor": User(
            id=USER_AUDITOR_ID,
            tenant_id=DEMO_TENANT_ID,
            email="auditor@investops.ai",
            display_name="Compliance Auditor",
            status="ACTIVE",
            mfa_enabled=False,
        ),
    }
    for u in users.values():
        session.add(u)
    session.flush()

    # User Role Assignments
    assignments = [
        UserRoleAssignment(tenant_id=DEMO_TENANT_ID, user_id=USER_ANALYST_ID, role_id=roles["Analyst"].id),
        UserRoleAssignment(tenant_id=DEMO_TENANT_ID, user_id=USER_APPROVER_ID, role_id=roles["Portfolio Manager"].id),
        UserRoleAssignment(tenant_id=DEMO_TENANT_ID, user_id=USER_TRADER_ID, role_id=roles["Trader"].id),
        UserRoleAssignment(tenant_id=DEMO_TENANT_ID, user_id=USER_AUDITOR_ID, role_id=roles["Auditor"].id),
    ]
    for a in assignments:
        session.add(a)

    # 3. Portfolio & Account
    portfolio = Portfolio(
        id=PORTFOLIO_ID,
        tenant_id=DEMO_TENANT_ID,
        code="GROWTH-01",
        name="Global Tech & Growth Core Fund",
        base_currency="USD",
        status="ACTIVE",
    )
    session.add(portfolio)
    session.flush()

    account = Account(
        id=ACCOUNT_ID,
        tenant_id=DEMO_TENANT_ID,
        portfolio_id=PORTFOLIO_ID,
        account_number="BROKER-ACCT-9921",
        broker_name="Apex Clearing / FIX Sandbox",
        available_cash=Decimal("1500000.00"),
        currency="USD",
        status="ACTIVE",
    )
    session.add(account)

    # 4. Instruments
    instruments_data = [
        (INST_AAPL_ID, "AAPL", "Apple Inc.", "EQUITY", "USD", "NASDAQ"),
        (INST_MSFT_ID, "MSFT", "Microsoft Corp.", "EQUITY", "USD", "NASDAQ"),
        (INST_NVDA_ID, "NVDA", "NVIDIA Corp.", "EQUITY", "USD", "NASDAQ"),
        (INST_GOOGL_ID, "GOOGL", "Alphabet Inc.", "EQUITY", "USD", "NASDAQ"),
    ]
    inst_objs = {}
    for i_id, sym, name, ac, curr, ex in instruments_data:
        existing = session.query(Instrument).filter_by(symbol=sym, exchange=ex).first()
        if existing:
            inst_objs[sym] = existing
        else:
            inst = Instrument(id=i_id, symbol=sym, name=name, asset_class=ac, currency=curr, exchange=ex)
            session.add(inst)
            inst_objs[sym] = inst
    session.flush()

    # 5. Integrations
    integrations = [
        Integration(
            tenant_id=DEMO_TENANT_ID,
            name="Market Data Sandbox",
            category="MARKET_DATA",
            environment="SANDBOX",
            provider="Finnhub/Polygon Mock",
            status="ACTIVE",
            config={"rate_limit_per_min": 600, "polling_interval_sec": 5},
        ),
        Integration(
            tenant_id=DEMO_TENANT_ID,
            name="Broker FIX Sandbox",
            category="BROKER",
            environment="SANDBOX",
            provider="Apex FIX Gateway",
            status="ACTIVE",
            config={"fix_version": "FIX.4.4", "sender_comp_id": "INVESTOPS_DEMO"},
        ),
    ]
    for integ in integrations:
        session.add(integ)

    # 6. Source Documents & Versions
    src_doc = SourceDocument(
        tenant_id=DEMO_TENANT_ID,
        provider="SEC EDGAR",
        external_id="10K-2025-TECH-SECTOR",
        title="Big Tech Q4 2025 Financial Performance & Capital Allocation Analysis",
        source_url="https://sec.gov/edgar/mock/10k-2025",
        classification="PUBLIC",
    )
    session.add(src_doc)
    session.flush()

    doc_content = "Q4 2025 earnings show strong enterprise cloud growth (+26% YoY). Generative AI infrastructure capex accelerated."
    src_version = SourceDocumentVersion(
        document_id=src_doc.id,
        version=1,
        published_at=now - timedelta(days=5),
        retrieved_at=now - timedelta(days=4),
        content_hash=compute_sha256(doc_content),
        excerpt=doc_content,
        metadata_json={"pages": 124, "filing_type": "10-K"},
    )
    session.add(src_version)
    session.flush()

    # 7. Workflow Instance
    workflow = Workflow(
        id=WORKFLOW_ID,
        tenant_id=DEMO_TENANT_ID,
        portfolio_id=PORTFOLIO_ID,
        created_by=USER_ANALYST_ID,
        trace_id=TRACE_ID,
        title="Q1 2026 Tech & Growth Rebalance Strategy",
        stage="PORTFOLIO_STRATEGY",
        status="AWAITING_REVIEW",
        version=1,
    )
    session.add(workflow)
    session.flush()

    # Workflow Transitions
    t1 = WorkflowTransition(
        tenant_id=DEMO_TENANT_ID,
        workflow_id=WORKFLOW_ID,
        actor_id=USER_ANALYST_ID,
        from_stage=None,
        to_stage="MARKET_INTELLIGENCE",
        from_status=None,
        to_status="RUNNING",
        reason="Initiated Q1 2026 Tech Market Intelligence research job.",
        occurred_at=now - timedelta(hours=3),
    )
    t2 = WorkflowTransition(
        tenant_id=DEMO_TENANT_ID,
        workflow_id=WORKFLOW_ID,
        actor_id=USER_ANALYST_ID,
        from_stage="MARKET_INTELLIGENCE",
        to_stage="PORTFOLIO_STRATEGY",
        from_status="RUNNING",
        to_status="AWAITING_REVIEW",
        reason="Market Research Report completed. Generated Portfolio Recommendation Report v1.",
        occurred_at=now - timedelta(hours=1),
    )
    session.add_all([t1, t2])

    # 8. Research Report
    research_report = ResearchReport(
        tenant_id=DEMO_TENANT_ID,
        workflow_id=WORKFLOW_ID,
        title="Market Intelligence Report - Q1 2026 Tech Growth Sector",
        status="COMPLETED",
    )
    session.add(research_report)
    session.flush()

    rr_payload = {
        "summary": "Enterprise cloud and AI compute demand remain robust. Semiconductors show strong order backlogs.",
        "top_opportunities": ["AI Accelerator Hardware", "Enterprise Cloud Migration", "Custom Silicon Design"],
        "top_risks": ["Supply Chain Bottlenecks", "Valuation Multiples Expansion"],
    }
    rr_hash = compute_sha256(rr_payload)

    rr_version = ResearchReportVersion(
        report_id=research_report.id,
        version=1,
        model_name="InvestOps-Claude-3.5-Sonnet",
        model_version="v2.1",
        confidence=Decimal("0.9200"),
        market_summary=rr_payload["summary"],
        top_opportunities=rr_payload["top_opportunities"],
        top_risks=rr_payload["top_risks"],
        company_analysis={
            "NVDA": "Strong demand for Blackwell GPU architecture.",
            "MSFT": "Azure AI revenue contribution up 31% YoY.",
        },
        sector_analysis={
            "Semiconductors": "Overweight",
            "Software & Services": "Neutral-Positive",
        },
        artifact_uri=f"s3://investops-reports/{DEMO_TENANT_ID}/{WORKFLOW_ID}/rr_v1.json",
        artifact_hash=rr_hash,
    )
    session.add(rr_version)
    session.flush()

    # Research Claim & Citation
    claim = ResearchClaim(
        report_version_id=rr_version.id,
        claim_text="Cloud infrastructure capex accelerated driven by AI compute demand (+26% YoY).",
        confidence=Decimal("0.9500"),
    )
    session.add(claim)
    session.flush()

    citation = ClaimCitation(
        claim_id=claim.id,
        source_document_version_id=src_version.id,
        locator="SEC EDGAR 10-K p.44",
    )
    session.add(citation)

    # 9. Recommendation & Allocations
    rec = Recommendation(
        tenant_id=DEMO_TENANT_ID,
        workflow_id=WORKFLOW_ID,
        title="Recommended Allocation - Tech Growth Core",
        status="AWAITING_APPROVAL",
    )
    session.add(rec)
    session.flush()

    rec_payload = {
        "expected_return": "0.145000",
        "volatility": "0.128000",
        "diversification_score": "0.8800",
        "allocations": [
            {"symbol": "NVDA", "weight": "0.350000", "quantity": "500.000000"},
            {"symbol": "MSFT", "weight": "0.300000", "quantity": "400.000000"},
            {"symbol": "AAPL", "weight": "0.200000", "quantity": "300.000000"},
            {"symbol": "GOOGL", "weight": "0.150000", "quantity": "250.000000"},
        ],
    }
    rec_hash = compute_sha256(rec_payload)

    rec_version = RecommendationVersion(
        recommendation_id=rec.id,
        research_report_version_id=rr_version.id,
        version=1,
        expected_return=Decimal("0.145000"),
        volatility=Decimal("0.128000"),
        diversification_score=Decimal("0.8800"),
        investment_horizon_days=90,
        confidence=Decimal("0.8900"),
        reasoning="Overweight NVDA and MSFT based on validated Q4 earnings expansion and 10-K capex citations.",
        artifact_hash=rec_hash,
    )
    session.add(rec_version)
    session.flush()

    allocations = [
        RecommendationAllocation(
            recommendation_version_id=rec_version.id,
            instrument_id=inst_objs["NVDA"].id,
            target_weight=Decimal("0.350000"),
            target_quantity=Decimal("500.000000"),
            side="BUY",
            rationale="High growth conviction in AI hardware.",
        ),
        RecommendationAllocation(
            recommendation_version_id=rec_version.id,
            instrument_id=inst_objs["MSFT"].id,
            target_weight=Decimal("0.300000"),
            target_quantity=Decimal("400.000000"),
            side="BUY",
            rationale="Enterprise cloud leadership.",
        ),
        RecommendationAllocation(
            recommendation_version_id=rec_version.id,
            instrument_id=inst_objs["AAPL"].id,
            target_weight=Decimal("0.200000"),
            target_quantity=Decimal("300.000000"),
            side="BUY",
            rationale="Stable free cash flow anchor.",
        ),
        RecommendationAllocation(
            recommendation_version_id=rec_version.id,
            instrument_id=inst_objs["GOOGL"].id,
            target_weight=Decimal("0.150000"),
            target_quantity=Decimal("250.000000"),
            side="BUY",
            rationale="Valuation buffer and search ecosystem.",
        ),
    ]
    for alloc in allocations:
        session.add(alloc)

    # 10. Pre-trade Validation Run (Passing)
    val_run = ValidationRun(
        tenant_id=DEMO_TENANT_ID,
        recommendation_version_id=rec_version.id,
        rule_set_version="MANDATE-POLICY-v2026.1",
        status="PASS",
        completed_at=now - timedelta(minutes=30),
    )
    session.add(val_run)
    session.flush()

    val_results = [
        ValidationResult(
            validation_run_id=val_run.id,
            rule_code="RULE_SINGLE_STOCK_MAX_35",
            severity="INFO",
            passed=True,
            blocking=True,
            explanation="Max single position NVDA at 35.00% meets the mandatory <= 35% threshold.",
        ),
        ValidationResult(
            validation_run_id=val_run.id,
            rule_code="RULE_CASH_SUFFICIENT",
            severity="INFO",
            passed=True,
            blocking=True,
            explanation="Estimated trade cost $485,000.00 is fully covered by available cash $1,500,000.00.",
        ),
    ]
    for vr in val_results:
        session.add(vr)

    # 11. Artifact Manifest & Approval Task
    manifest = ArtifactManifest(
        tenant_id=DEMO_TENANT_ID,
        workflow_id=WORKFLOW_ID,
        recommendation_version_id=rec_version.id,
        schema_version="v1.0",
        content_hash=rec_hash,
        storage_uri=f"s3://investops-artifacts/{DEMO_TENANT_ID}/{rec_hash}.json",
        status="LOCKED",
        expires_at=now + timedelta(days=7),
    )
    session.add(manifest)
    session.flush()

    app_task = ApprovalTask(
        tenant_id=DEMO_TENANT_ID,
        workflow_id=WORKFLOW_ID,
        artifact_manifest_id=manifest.id,
        assigned_to=USER_APPROVER_ID,
        status="PENDING",
        due_at=now + timedelta(hours=24),
    )
    session.add(app_task)

    # 12. Seeded Audit Event
    audit_evt = AuditEvent(
        tenant_id=DEMO_TENANT_ID,
        workflow_id=WORKFLOW_ID,
        trace_id=TRACE_ID,
        actor_type="USER",
        actor_id=USER_ANALYST_ID,
        action="RECOMMENDATION_SUBMITTED_FOR_APPROVAL",
        resource_type="RecommendationVersion",
        resource_id=rec_version.id,
        outcome="SUCCESS",
        payload={"artifact_hash": rec_hash, "recommendation_version": 1},
        event_hash=compute_sha256(f"AUDIT_{WORKFLOW_ID}_{rec_hash}"),
        occurred_at=now - timedelta(minutes=25),
    )
    session.add(audit_evt)

    session.commit()

    return {
        "tenant_id": DEMO_TENANT_ID,
        "workflow_id": WORKFLOW_ID,
        "trace_id": TRACE_ID,
        "portfolio_id": PORTFOLIO_ID,
        "account_id": ACCOUNT_ID,
    }


if __name__ == "__main__":
    db = SessionLocal()
    try:
        res = seed_demo_data(db)
        print(f"Successfully seeded InvestOps demo database: {res}")
    finally:
        db.close()
