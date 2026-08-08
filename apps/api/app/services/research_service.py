from uuid import UUID
from sqlalchemy.orm import Session

from apps.api.app.agents.pipeline import AgentExecutionPipeline
from apps.api.app.db.models import ResearchReport


class ResearchService:
    @staticmethod
    def run_market_intelligence(db: Session, workflow_id: UUID, actor_id: UUID) -> ResearchReport:
        """Run Market Intelligence Agent to generate a sourced Market Research Report."""
        return AgentExecutionPipeline.run_market_intelligence_agent(
            db=db, workflow_id=workflow_id, actor_id=actor_id
        )
