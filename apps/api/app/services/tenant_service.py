from uuid import UUID

from sqlalchemy.orm import Session

from apps.api.app.db.models import Account, Instrument, Portfolio, Tenant, User


class TenantService:
    @staticmethod
    def get_tenant(db: Session, tenant_id: UUID) -> Tenant | None:
        return db.query(Tenant).filter(Tenant.id == tenant_id).first()

    @staticmethod
    def list_tenants(db: Session) -> list[Tenant]:
        return db.query(Tenant).all()

    @staticmethod
    def list_users(db: Session, tenant_id: UUID) -> list[User]:
        return db.query(User).filter(User.tenant_id == tenant_id).all()

    @staticmethod
    def list_portfolios(db: Session, tenant_id: UUID) -> list[Portfolio]:
        return db.query(Portfolio).filter(Portfolio.tenant_id == tenant_id).all()

    @staticmethod
    def list_accounts(db: Session, tenant_id: UUID) -> list[Account]:
        return db.query(Account).filter(Account.tenant_id == tenant_id).all()

    @staticmethod
    def list_instruments(db: Session) -> list[Instrument]:
        return db.query(Instrument).all()
