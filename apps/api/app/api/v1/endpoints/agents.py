from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from apps.api.app.core.dependencies import get_db
from apps.api.app.schemas.integration import AgentStatusRead
from apps.api.app.services.agent_service import AgentService

router = APIRouter()


@router.get("/status", response_model=list[AgentStatusRead])
def list_agent_statuses(db: Session = Depends(get_db)):
    """List operational status and execution metrics for all 5 AI Agents."""
    return AgentService.list_agent_statuses(db)
