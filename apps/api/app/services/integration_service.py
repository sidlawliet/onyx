from uuid import UUID

from sqlalchemy.orm import Session

from apps.api.app.db.models import ApprovalTask, Integration, Workflow
from apps.api.app.schemas.integration import SystemHealthRead
from apps.api.app.services.agent_service import AgentService


class IntegrationService:
    @staticmethod
    def list_integrations(db: Session, tenant_id: UUID) -> list[Integration]:
        return db.query(Integration).filter(Integration.tenant_id == tenant_id).all()

    @staticmethod
    def get_system_health(db: Session, tenant_id: UUID) -> SystemHealthRead:
        active_workflows = db.query(Workflow).filter(Workflow.tenant_id == tenant_id, Workflow.status == "RUNNING").count()
        pending_approvals = db.query(ApprovalTask).filter(ApprovalTask.tenant_id == tenant_id, ApprovalTask.status == "PENDING").count()
        agents = AgentService.list_agent_statuses(db)

        return SystemHealthRead(
            status="HEALTHY",
            environment="SANDBOX",
            database_connected=True,
            active_workflows_count=active_workflows,
            pending_approvals_count=pending_approvals,
            agents=agents,
        )
