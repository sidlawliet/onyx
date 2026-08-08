import pytest
import hashlib
from decimal import Decimal
from apps.api.app.schemas.workflow import WorkflowRead, WorkflowCreateRequest
from apps.api.app.schemas.approval import ApprovalDecisionRequest
from apps.api.app.schemas.execution import ExecutionIntentCreateRequest
from apps.api.app.llm.schemas import MarketIntelligenceOutput, PortfolioStrategyOutput, AllocationOutput

def test_workflow_schemas():
    req = WorkflowCreateRequest(portfolio_id="11111111-1111-4111-a111-111111111111", title="Q4 Tech Rebalance")
    assert req.title == "Q4 Tech Rebalance"

def test_approval_decision_request_schema():
    req = ApprovalDecisionRequest(
        decision="APPROVE",
        attestation="I approve this recommendation.",
        artifact_hash="a" * 64,
        mfa_verified=True
    )
    assert req.decision == "APPROVE"
    assert req.mfa_verified is True

def test_execution_intent_request_schema():
    req = ExecutionIntentCreateRequest(
        approved_artifact_id="22222222-2222-4222-a222-222222222222",
        approved_artifact_hash="b" * 64,
        account_id="33333333-3333-4333-a333-333333333333",
        integration_id="44444444-4444-4444-a444-444444444444",
        idempotency_key="IDEM-TEST-01"
    )
    assert req.idempotency_key == "IDEM-TEST-01"

def test_pydantic_llm_structured_output_parsing():
    alloc = AllocationOutput(
        symbol="AAPL",
        target_weight=Decimal("0.25"),
        target_quantity=Decimal("150.0"),
        side="BUY",
        rationale="Strong Q4 earnings and robust cash flow"
    )
    assert alloc.symbol == "AAPL"
    assert alloc.target_weight == Decimal("0.25")
    assert alloc.side == "BUY"

    strategy = PortfolioStrategyOutput(
        allocations=[alloc],
        expected_return=Decimal("0.145"),
        volatility=Decimal("0.18"),
        diversification_score=Decimal("0.88"),
        investment_horizon_days=90,
        confidence=Decimal("0.92"),
        reasoning="Overweight high-quality mega-cap tech equities"
    )
    assert len(strategy.allocations) == 1
    assert strategy.expected_return == Decimal("0.145")
    assert strategy.diversification_score == Decimal("0.88")
    assert strategy.confidence == Decimal("0.92")

def test_sha256_hash_integrity():
    data = "test-investops-payload-data"
    expected_hash = hashlib.sha256(data.encode("utf-8")).hexdigest()
    assert len(expected_hash) == 64
    assert hashlib.sha256(data.encode("utf-8")).hexdigest() == expected_hash
