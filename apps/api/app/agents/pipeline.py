"""Agent Execution Pipeline for InvestOps AI.

Manages agent execution lifecycle, workflow state transitions, audit trail recording,
and transactional outbox event publishing for event-driven agent orchestration.
"""

import logging
from datetime import datetime, timezone
from uuid import UUID
from sqlalchemy.orm import Session

from apps.api.app.agents.market_intelligence_agent import MarketIntelligenceAgent
from apps.api.app.agents.portfolio_strategy_agent import PortfolioStrategyAgent
from apps.api.app.core.exceptions import NotFoundException
from apps.api.app.db.models import OutboxEvent, ResearchReport, Recommendation, Workflow
from apps.api.app.services.audit_service import AuditService
from apps.api.app.services.workflow_service import WorkflowService

logger = logging.getLogger("investops.agent_pipeline")


class AgentExecutionPipeline:
    @classmethod
    def run_market_intelligence_agent(
        cls, db: Session, workflow_id: UUID, actor_id: UUID
    ) -> ResearchReport:
        """Run Market Intelligence Agent pipeline, update workflow state, and publish outbox events."""
        workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
        if not workflow:
            raise NotFoundException("Workflow", workflow_id)

        # Execute Market Intelligence Agent
        report, report_version, llm_result = MarketIntelligenceAgent.execute(
            db=db, workflow=workflow, actor_id=actor_id
        )

        # Transition workflow stage
        WorkflowService.transition_stage(
            db=db,
            workflow=workflow,
            actor_id=actor_id,
            to_stage="PORTFOLIO_STRATEGY",
            to_status="AWAITING_REVIEW",
            reason="Market Research Report published with verified citations",
        )

        # Record Audit Event
        AuditService.record_audit_event(
            db=db,
            tenant_id=workflow.tenant_id,
            trace_id=workflow.trace_id,
            workflow_id=workflow.id,
            actor_type="AGENT",
            actor_id=actor_id,
            action="research.report_published",
            resource_type="research_report",
            resource_id=report.id,
            outcome="SUCCESS",
            payload={
                "report_id": str(report.id),
                "artifact_hash": report_version.artifact_hash,
                "model_name": llm_result.model_name,
                "latency_ms": llm_result.latency_ms,
                "tokens": llm_result.total_tokens,
            },
        )

        # Publish Transactional Outbox Event
        AuditService.publish_outbox_event(
            db=db,
            tenant_id=workflow.tenant_id,
            trace_id=workflow.trace_id,
            aggregate_type="ResearchReport",
            aggregate_id=report.id,
            event_type="intelligence.report-completed.v1",
            payload={
                "workflow_id": str(workflow.id),
                "report_id": str(report.id),
                "version": report_version.version,
                "artifact_hash": report_version.artifact_hash,
                "confidence": str(report_version.confidence),
            },
        )

        db.commit()
        db.refresh(report)
        return report

    @classmethod
    def run_portfolio_strategy_agent(
        cls, db: Session, workflow_id: UUID, actor_id: UUID
    ) -> Recommendation:
        """Run Portfolio Strategy Agent pipeline, generate recommendations, and publish outbox events."""
        workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
        if not workflow:
            raise NotFoundException("Workflow", workflow_id)

        # Execute Portfolio Strategy Agent
        recommendation, rec_version, llm_result = PortfolioStrategyAgent.execute(
            db=db, workflow=workflow, actor_id=actor_id
        )

        # Record Audit Event
        AuditService.record_audit_event(
            db=db,
            tenant_id=workflow.tenant_id,
            trace_id=workflow.trace_id,
            workflow_id=workflow.id,
            actor_type="AGENT",
            actor_id=actor_id,
            action="strategy.recommendation_generated",
            resource_type="recommendation",
            resource_id=recommendation.id,
            outcome="SUCCESS",
            payload={
                "recommendation_id": str(recommendation.id),
                "artifact_hash": rec_version.artifact_hash,
                "model_name": llm_result.model_name,
                "latency_ms": llm_result.latency_ms,
                "tokens": llm_result.total_tokens,
            },
        )

        # Publish Transactional Outbox Event
        AuditService.publish_outbox_event(
            db=db,
            tenant_id=workflow.tenant_id,
            trace_id=workflow.trace_id,
            aggregate_type="Recommendation",
            aggregate_id=recommendation.id,
            event_type="strategy.recommendation-published.v1",
            payload={
                "workflow_id": str(workflow.id),
                "recommendation_id": str(recommendation.id),
                "recommendation_version_id": str(rec_version.id),
                "artifact_hash": rec_version.artifact_hash,
                "expected_return": str(rec_version.expected_return),
                "volatility": str(rec_version.volatility),
            },
        )

        db.commit()
        db.refresh(recommendation)
        return recommendation
