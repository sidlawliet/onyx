from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from apps.api.app.core.dependencies import get_current_tenant, get_current_user, get_db
from apps.api.app.core.exceptions import NotFoundException
from apps.api.app.db.models import Recommendation, Tenant, User
from apps.api.app.schemas.strategy import RecommendationRead, ValidationRunRead
from apps.api.app.services.strategy_service import StrategyService
from apps.api.app.services.validation_service import ValidationService

router = APIRouter()


@router.post("/workflows/{workflow_id}/generate", response_model=RecommendationRead)
def generate_recommendation(
    workflow_id: UUID,
    user: User = Depends(get_current_user),
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Run Portfolio Strategy Agent to generate a Portfolio Recommendation with target weights."""
    return StrategyService.generate_recommendation(db=db, workflow_id=workflow_id, actor_id=user.id)


@router.post("/versions/{recommendation_version_id}/validate", response_model=ValidationRunRead)
def validate_recommendation(
    recommendation_version_id: UUID,
    user: User = Depends(get_current_user),
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Validate a recommendation version against pre-trade mandate & risk rules."""
    return ValidationService.validate_recommendation(
        db=db, recommendation_version_id=recommendation_version_id, actor_id=user.id
    )


@router.get("/recommendations/{recommendation_id}", response_model=RecommendationRead)
def get_recommendation(
    recommendation_id: UUID,
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Get recommendation details including allocations and artifact hashes."""
    rec = (
        db.query(Recommendation)
        .filter(Recommendation.id == recommendation_id, Recommendation.tenant_id == tenant.id)
        .first()
    )
    if not rec:
        raise NotFoundException("Recommendation", recommendation_id)
    return rec
