from decimal import Decimal
from typing import Any
import uuid


class BrokerProvider:
    """FIX broker execution sandbox simulating broker order submission, fills, and status events."""

    @staticmethod
    def submit_fix_order(
        account_number: str,
        symbol: str,
        side: str,
        quantity: Decimal,
        limit_price: Decimal | None = None,
    ) -> dict[str, Any]:
        client_order_id = f"ORD-{uuid.uuid4().hex[:12].upper()}"
        provider_order_id = f"FIX-SANDBOX-{uuid.uuid4().hex[:8].upper()}"

        # Executed fill price
        exec_price = limit_price if limit_price else Decimal("150.000000")

        return {
            "client_order_id": client_order_id,
            "provider_order_id": provider_order_id,
            "status": "EXECUTED",
            "executed_quantity": str(quantity),
            "executed_price": str(exec_price),
            "executed_quantity_dec": quantity,
            "executed_price_dec": exec_price,
            "venue": "NASDAQ",
            "execution_id": f"EXEC-{uuid.uuid4().hex[:10].upper()}",
        }
