from datetime import datetime, timezone
from sqlalchemy.orm import Session

from apps.api.app.schemas.integration import AgentStatusRead


class AgentService:
    @staticmethod
    def list_agent_statuses(db: Session) -> list[AgentStatusRead]:
        """Return operational status of the 5 institutional agents."""
        now = datetime.now(timezone.utc)
        return [
            AgentStatusRead(
                agent_id="agent-intel-01",
                name="Market Intelligence Agent",
                stage="MARKET_INTELLIGENCE",
                status="IDLE",
                last_execution_at=now,
            ),
            AgentStatusRead(
                agent_id="agent-strat-01",
                name="Portfolio Strategy Agent",
                stage="PORTFOLIO_STRATEGY",
                status="IDLE",
                last_execution_at=now,
            ),
            AgentStatusRead(
                agent_id="agent-val-01",
                name="Mandate Validation Agent",
                stage="PORTFOLIO_STRATEGY",
                status="IDLE",
                last_execution_at=now,
            ),
            AgentStatusRead(
                agent_id="agent-exec-01",
                name="Trade Execution Agent",
                stage="TRADE_EXECUTION",
                status="IDLE",
                last_execution_at=now,
            ),
            AgentStatusRead(
                agent_id="agent-mon-01",
                name="Portfolio Monitoring Agent",
                stage="PORTFOLIO_MONITORING",
                status="RUNNING",
                last_execution_at=now,
            ),
        ]
