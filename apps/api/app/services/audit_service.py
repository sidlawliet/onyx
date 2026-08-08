import hashlib
import json
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from apps.api.app.db.models import AuditEvent, OutboxEvent


class AuditService:
    @staticmethod
    def record_audit_event(
        db: Session,
        tenant_id: UUID,
        trace_id: UUID,
        actor_type: str,
        actor_id: UUID,
        action: str,
        resource_type: str,
        resource_id: UUID | None,
        outcome: str,
        payload: dict[str, Any],
        workflow_id: UUID | None = None,
    ) -> AuditEvent:
        """Record an immutable, hash-chained audit event in the database."""
        # Flush pending session objects so previous audit events are visible
        db.flush()
        prev_event = (
            db.query(AuditEvent)
            .filter(AuditEvent.tenant_id == tenant_id)
            .order_by(AuditEvent.occurred_at.desc(), AuditEvent.id.desc())
            .first()
        )
        prev_hash = prev_event.event_hash if prev_event else "0" * 64

        # Compute SHA-256 hash for current event
        hash_input = f"{tenant_id}:{trace_id}:{actor_id}:{action}:{resource_type}:{resource_id}:{outcome}:{prev_hash}"
        event_hash = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()

        audit_event = AuditEvent(
            tenant_id=tenant_id,
            workflow_id=workflow_id,
            trace_id=trace_id,
            actor_type=actor_type,
            actor_id=actor_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            outcome=outcome,
            payload=payload,
            previous_event_hash=prev_hash,
            event_hash=event_hash,
            occurred_at=datetime.now(timezone.utc),
        )
        db.add(audit_event)
        return audit_event

    @staticmethod
    def publish_outbox_event(
        db: Session,
        tenant_id: UUID,
        trace_id: UUID,
        aggregate_type: str,
        aggregate_id: UUID,
        event_type: str,
        payload: dict[str, Any],
    ) -> OutboxEvent:
        """Publish a transactional outbox event for asynchronous agent orchestration."""
        outbox_event = OutboxEvent(
            tenant_id=tenant_id,
            trace_id=trace_id,
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            event_type=event_type,
            event_version=1,
            payload=payload,
            occurred_at=datetime.now(timezone.utc),
            published_at=None,
            attempts=0,
        )
        db.add(outbox_event)
        return outbox_event
