import hashlib
import uuid
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from apps.api.app.core.dependencies import get_current_tenant, get_db
from apps.api.app.db.models import AuditEvent, Tenant
from apps.api.app.schemas.audit import AuditEventRead, AuditExportRead, AuditExportRequest

router = APIRouter()


@router.get("/events", response_model=list[AuditEventRead])
def list_audit_events(
    trace_id: UUID | None = Query(None),
    workflow_id: UUID | None = Query(None),
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Query immutable audit event chain filterable by trace ID or workflow ID."""
    query = db.query(AuditEvent).filter(AuditEvent.tenant_id == tenant.id)
    if trace_id:
        query = query.filter(AuditEvent.trace_id == trace_id)
    if workflow_id:
        query = query.filter(AuditEvent.workflow_id == workflow_id)
    return query.order_by(AuditEvent.occurred_at.asc()).all()


@router.post("/export", response_model=AuditExportRead)
def export_audit_chain(
    request: AuditExportRequest,
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Export an audited hash-chained package with verification status."""
    query = db.query(AuditEvent).filter(AuditEvent.tenant_id == tenant.id)
    if request.trace_id:
        query = query.filter(AuditEvent.trace_id == request.trace_id)
    if request.workflow_id:
        query = query.filter(AuditEvent.workflow_id == request.workflow_id)

    events = query.order_by(AuditEvent.occurred_at.asc(), AuditEvent.id.asc()).all()

    # Validate hash chain integrity
    chain_valid = True
    for i in range(1, len(events)):
        if events[i].previous_event_hash != events[i - 1].event_hash:
            chain_valid = False
            break

    last_hash = events[-1].event_hash if events else "0" * 64
    manifest_hash = hashlib.sha256(f"{tenant.id}:{len(events)}:{last_hash}".encode("utf-8")).hexdigest()

    return AuditExportRead(
        export_id=uuid.uuid4(),
        total_events=len(events),
        chain_valid=chain_valid,
        manifest_hash=manifest_hash,
        events=events,
    )
