"""Portfolio Strategy Agent for InvestOps AI.

Consumes verified Market Research Report versions, executes LLM strategy prompts,
constructs target asset allocations, and generates immutable recommendation artifacts with SHA-256 hashes.
"""

import hashlib
import logging
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID
from sqlalchemy.orm import Session

from apps.api.app.core.exceptions import NotFoundException
from apps.api.app.db.models import (
    Instrument,
    Recommendation,
    RecommendationAllocation,
    RecommendationVersion,
    ResearchReportVersion,
    Workflow,
)
from apps.api.app.llm.orchestrator import LLMOrchestrator, LLMOrchestrationResult
from apps.api.app.llm.schemas import PortfolioStrategyOutput

logger = logging.getLogger("investops.portfolio_strategy_agent")


class PortfolioStrategyAgent:
    @classmethod
    def execute(
        cls, db: Session, workflow: Workflow, actor_id: UUID
    ) -> tuple[Recommendation, RecommendationVersion, LLMOrchestrationResult]:
        """Execute the Portfolio Strategy Agent pipeline."""
        logger.info(f"PortfolioStrategyAgent executing for workflow {workflow.id}")

        # 1. Retrieve latest Research Report Version
        report_version = (
            db.query(ResearchReportVersion)
            .join(ResearchReportVersion.report)
            .filter(ResearchReportVersion.report.has(workflow_id=workflow.id))
            .order_by(ResearchReportVersion.version.desc())
            .first()
        )
        if not report_version:
            raise NotFoundException("ResearchReportVersion for workflow", workflow.id)

        # 2. Query available instruments
        instruments = db.query(Instrument).all()
        instr_map = {i.symbol: i for i in instruments}
        eligible_symbols = list(instr_map.keys())

        # 3. Run LLM Orchestration
        llm_result = LLMOrchestrator.execute_portfolio_strategy(
            market_summary=report_version.market_summary,
            company_analysis=str(report_version.company_analysis),
            available_cash="1,500,000.00",
            eligible_instruments=", ".join(eligible_symbols),
            max_single_stock=40.0,
            volatility_cap=25.0,
        )

        output: PortfolioStrategyOutput = llm_result.content

        # 4. Create Recommendation Header
        recommendation = Recommendation(
            tenant_id=workflow.tenant_id,
            workflow_id=workflow.id,
            title=f"Portfolio Strategy Recommendation - {workflow.title}",
            status="DRAFT",
            created_at=datetime.now(timezone.utc),
        )
        db.add(recommendation)
        db.flush()

        # Compute deterministic SHA-256 artifact content hash
        hash_payload = f"{workflow.tenant_id}:{workflow.id}:{recommendation.id}:v1:{output.reasoning}"
        artifact_hash = hashlib.sha256(hash_payload.encode("utf-8")).hexdigest()

        rec_version = RecommendationVersion(
            recommendation_id=recommendation.id,
            research_report_version_id=report_version.id,
            version=1,
            expected_return=output.expected_return,
            volatility=output.volatility,
            diversification_score=output.diversification_score,
            investment_horizon_days=output.investment_horizon_days,
            confidence=output.confidence,
            reasoning=output.reasoning,
            artifact_hash=artifact_hash,
            created_at=datetime.now(timezone.utc),
        )
        db.add(rec_version)
        db.flush()

        # 5. Create Recommendation Allocations
        for alloc_out in output.allocations:
            instr = instr_map.get(alloc_out.symbol)
            if instr:
                alloc = RecommendationAllocation(
                    recommendation_version_id=rec_version.id,
                    instrument_id=instr.id,
                    target_weight=alloc_out.target_weight,
                    target_quantity=alloc_out.target_quantity,
                    side=alloc_out.side,
                    rationale=alloc_out.rationale,
                )
                db.add(alloc)

        return recommendation, rec_version, llm_result
