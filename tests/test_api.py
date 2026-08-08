from decimal import Decimal
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from apps.api.app.core.security import hash_token
from apps.api.app.db.base import Base
from apps.api.app.db.seed import seed_demo_data
from apps.api.app.db.session import get_db
from apps.api.app.main import app

from sqlalchemy.pool import StaticPool

# Setup test SQLite in-memory engine
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    seed_demo_data(db)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


def test_auth_login(client):
    response = client.post("/api/v1/auth/login", json={"email": "analyst@investops.ai", "password": "demo-password"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["email"] == "analyst@investops.ai"


def test_get_current_user_profile(client):
    login_res = client.post("/api/v1/auth/login", json={"email": "analyst@investops.ai"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "analyst@investops.ai"


def test_list_tenants_and_portfolios(client):
    response = client.get("/api/v1/tenants")
    assert response.status_code == 200
    tenants = response.json()
    assert len(tenants) >= 1

    portfolios_res = client.get("/api/v1/portfolios")
    assert portfolios_res.status_code == 200
    portfolios = portfolios_res.json()
    assert len(portfolios) >= 1
    assert portfolios[0]["code"] == "GROWTH-01"


def test_full_5_stage_workflow_and_approval_safety_gate(client):
    """Test the complete 5-stage institutional workflow:
    Market Intelligence -> Portfolio Strategy -> Validation -> Human Approval Gate -> Execution -> Monitoring
    """
    # 1. Fetch Portfolio ID
    portfolios_res = client.get("/api/v1/portfolios")
    portfolio_id = portfolios_res.json()[0]["id"]
    accounts_res = client.get("/api/v1/portfolios/accounts")
    account_id = accounts_res.json()[0]["id"]
    integrations_res = client.get("/api/v1/integrations")
    integration_id = integrations_res.json()[0]["id"]

    # 2. Stage 1: Create Workflow
    wf_res = client.post(
        "/api/v1/workflows",
        json={"portfolio_id": portfolio_id, "title": "Q3 Growth Rebalance Strategy"},
    )
    assert wf_res.status_code == 201
    wf_data = wf_res.json()
    workflow_id = wf_data["id"]
    trace_id = wf_data["trace_id"]
    assert wf_data["stage"] == "MARKET_INTELLIGENCE"

    # 3. Stage 1: Run Market Intelligence Agent
    intel_res = client.post(f"/api/v1/research-reports/workflows/{workflow_id}/run")
    assert intel_res.status_code == 200
    report_data = intel_res.json()
    assert report_data["status"] == "COMPLETED"
    assert len(report_data["versions"]) >= 1
    claims = report_data["versions"][0]["claims"]
    assert len(claims) >= 1
    assert len(claims[0]["citations"]) >= 1

    # 4. Stage 2: Generate Portfolio Strategy Recommendation
    strat_res = client.post(f"/api/v1/recommendations/workflows/{workflow_id}/generate")
    assert strat_res.status_code == 200
    rec_data = strat_res.json()
    rec_version_id = rec_data["versions"][0]["id"]
    artifact_hash = rec_data["versions"][0]["artifact_hash"]
    assert len(artifact_hash) == 64

    # 5. Stage 2: Validate Recommendation against Mandates & Risk Rules
    val_res = client.post(f"/api/v1/recommendations/versions/{rec_version_id}/validate")
    assert val_res.status_code == 200
    val_data = val_res.json()
    assert val_data["status"] == "PASS"

    # 6. SAFETY GATE NEGATIVE TEST 1: Reject Execution attempt BEFORE human approval
    fake_intent_res = client.post(
        "/api/v1/execution-intents",
        json={
            "approved_artifact_id": rec_version_id,
            "approved_artifact_hash": artifact_hash,
            "account_id": account_id,
            "integration_id": integration_id,
            "idempotency_key": "IDEM-TEST-PREMATURE-01",
        },
    )
    # Should fail because rec_version_id is not an approved ArtifactManifest ID
    assert fake_intent_res.status_code in (404, 422)

    # 7. Stage 3: Submit to Human Approval Gate
    submit_res = client.post(f"/api/v1/approval-tasks/recommendation-versions/{rec_version_id}/submit")
    assert submit_res.status_code == 200
    task_data = submit_res.json()
    task_id = task_data["id"]
    manifest_id = task_data["artifact_manifest_id"]

    # 8. SAFETY GATE NEGATIVE TEST 2: Reject Execution attempt with Mismatched/Tampered Artifact Hash
    tampered_hash_res = client.post(
        "/api/v1/execution-intents",
        json={
            "approved_artifact_id": manifest_id,
            "approved_artifact_hash": "f" * 64,  # Tampered hash
            "account_id": account_id,
            "integration_id": integration_id,
            "idempotency_key": "IDEM-TEST-TAMPERED-01",
        },
    )
    assert tampered_hash_res.status_code in (409, 422)

    # 9. Stage 3: Record Human Approval Decision (APPROVE with Attestation & MFA)
    decision_res = client.post(
        f"/api/v1/approval-tasks/tasks/{task_id}/decision",
        json={
            "decision": "APPROVE",
            "attestation": "I attest that I have reviewed the SEC 10-K research report and approve this allocation.",
            "artifact_hash": artifact_hash,
            "mfa_verified": True,
        },
    )
    assert decision_res.status_code == 200
    decision_data = decision_res.json()
    assert decision_data["decision"] == "APPROVE"

    # 10. Stage 4: Submit Pre-Approved Trade Execution Intent
    exec_res = client.post(
        "/api/v1/execution-intents",
        json={
            "approved_artifact_id": manifest_id,
            "approved_artifact_hash": artifact_hash,
            "account_id": account_id,
            "integration_id": integration_id,
            "idempotency_key": "IDEM-TEST-VALID-EXEC-01",
        },
    )
    assert exec_res.status_code == 201
    exec_data = exec_res.json()
    assert exec_data["status"] == "EXECUTED"
    assert len(exec_data["orders"]) >= 1
    assert len(exec_data["orders"][0]["fills"]) >= 1

    # 11. IDEMPOTENCY TEST: Duplicate command execution resubmission
    dup_exec_res = client.post(
        "/api/v1/execution-intents",
        json={
            "approved_artifact_id": manifest_id,
            "approved_artifact_hash": artifact_hash,
            "account_id": account_id,
            "integration_id": integration_id,
            "idempotency_key": "IDEM-TEST-VALID-EXEC-01",
        },
    )
    assert dup_exec_res.status_code == 409

    # 12. Stage 5: Portfolio Monitoring & Holding Snapshots
    mon_res = client.post(f"/api/v1/monitoring/portfolios/{portfolio_id}/capture-snapshots")
    assert mon_res.status_code == 200
    snapshots = mon_res.json()
    assert len(snapshots) >= 1

    # 13. Audit Chain Query by Trace ID
    audit_res = client.get(f"/api/v1/audit-events/events?trace_id={trace_id}")
    assert audit_res.status_code == 200
    audit_events = audit_res.json()
    assert len(audit_events) >= 5

    # 14. Audit Export Verification
    export_res = client.post("/api/v1/audit-events/export", json={"trace_id": trace_id})
    assert export_res.status_code == 200
    export_data = export_res.json()
    assert export_data["chain_valid"] is True


def test_system_health_and_agents(client):
    health_res = client.get("/api/v1/system-health")
    assert health_res.status_code == 200
    assert health_res.json()["status"] == "HEALTHY"

    agents_res = client.get("/api/v1/agents/status")
    assert agents_res.status_code == 200
    assert len(agents_res.json()) == 5


def test_agent_orchestration_and_outbox_events(client):
    """Test LLM Orchestrator, Prompt Management, Agent Pipeline, and Outbox Event publication."""
    from apps.api.app.db.models import OutboxEvent
    from apps.api.app.llm.orchestrator import LLMOrchestrator

    # 1. Test LLM Orchestrator direct call
    intel_res = LLMOrchestrator.execute_market_intelligence(
        workflow_title="Test Orchestration",
        portfolio_name="GROWTH-01",
        context_documents="Test excerpt",
        market_snapshots="AAPL: 235.50",
    )
    assert intel_res.model_name == "Claude 3.5 Sonnet"
    assert intel_res.prompt_version == "v1.0.0"
    assert intel_res.total_tokens > 0
    assert intel_res.content.confidence >= Decimal("0.90")

    # 2. Test Outbox event creation after running research report via API endpoint
    portfolios_res = client.get("/api/v1/portfolios")
    portfolio_id = portfolios_res.json()[0]["id"]

    wf_res = client.post(
        "/api/v1/workflows",
        json={"portfolio_id": portfolio_id, "title": "Agent Orchestration Pipeline Test Workflow"},
    )
    assert wf_res.status_code == 201
    workflow_id = wf_res.json()["id"]

    # Run Market Intelligence Agent via endpoint (delegates to AgentExecutionPipeline)
    run_res = client.post(f"/api/v1/research-reports/workflows/{workflow_id}/run")
    assert run_res.status_code == 200

    # Run Portfolio Strategy Agent via endpoint
    strat_res = client.post(f"/api/v1/recommendations/workflows/{workflow_id}/generate")
    assert strat_res.status_code == 200

    # Query DB session to verify Outbox Events published
    db = TestingSessionLocal()
    try:
        outbox_events = (
            db.query(OutboxEvent)
            .filter(OutboxEvent.payload.op("->>")("workflow_id") == workflow_id)
            .all()
        )
        assert len(outbox_events) >= 2
        event_types = [e.event_type for e in outbox_events]
        assert "intelligence.report-completed.v1" in event_types
        assert "strategy.recommendation-published.v1" in event_types
    finally:
        db.close()

