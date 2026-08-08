from uuid import UUID
from sqlalchemy.orm import Session

from apps.api.app.agents.pipeline import AgentExecutionPipeline
from apps.api.app.db.models import Recommendation


class StrategyService:
    @staticmethod
    def generate_recommendation(db: Session, workflow_id: UUID, actor_id: UUID) -> Recommendation:
        """Run Portfolio Strategy Agent to generate a Portfolio Recommendation with target asset allocations."""
        return AgentExecutionPipeline.run_portfolio_strategy_agent(
            db=db, workflow_id=workflow_id, actor_id=actor_id
        )
