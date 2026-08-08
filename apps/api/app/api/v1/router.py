from fastapi import APIRouter

from apps.api.app.api.v1.endpoints import (
    agents,
    approvals,
    audit,
    auth,
    execution,
    integrations,
    monitoring,
    notifications,
    portfolios,
    reports,
    research,
    strategy,
    system_health,
    tenants,
    workflows,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(tenants.router, prefix="/tenants", tags=["Tenants"])
api_router.include_router(portfolios.router, prefix="/portfolios", tags=["Portfolios"])
api_router.include_router(workflows.router, prefix="/workflows", tags=["Workflows"])
api_router.include_router(research.router, prefix="/research-reports", tags=["Market Intelligence"])
api_router.include_router(strategy.router, prefix="/recommendations", tags=["Portfolio Strategy"])
api_router.include_router(approvals.router, prefix="/approval-tasks", tags=["Human Approval Gate"])
api_router.include_router(execution.router, prefix="/execution-intents", tags=["Trade Execution"])
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["Portfolio Monitoring"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
api_router.include_router(audit.router, prefix="/audit-events", tags=["Audit Trail"])
api_router.include_router(agents.router, prefix="/agents", tags=["AI Agents"])
api_router.include_router(integrations.router, prefix="/integrations", tags=["Integrations"])
api_router.include_router(system_health.router, prefix="/system-health", tags=["System Health"])
