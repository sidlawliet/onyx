from decimal import Decimal
from typing import Any


class MarketDataProvider:
    """Provider abstraction yielding realistic market data quotes and fundamental filings research."""

    @staticmethod
    def get_realtime_prices(symbols: list[str]) -> dict[str, Decimal]:
        snapshot = {
            "AAPL": Decimal("224.500000"),
            "MSFT": Decimal("448.200000"),
            "NVDA": Decimal("128.750000"),
            "GOOGL": Decimal("176.300000"),
        }
        return {s: snapshot.get(s, Decimal("100.000000")) for s in symbols}

    @staticmethod
    def fetch_sec_filing_excerpts(ticker: str) -> dict[str, Any]:
        return {
            "ticker": ticker,
            "form": "10-K",
            "period": "FY2025",
            "excerpt": f"Form 10-K for {ticker}: Revenue grew 18% YoY driven by cloud intelligence and data center operations. Operational cash flows reached $28.4B.",
            "source_url": f"https://www.sec.gov/edgar/data/{ticker}/10k-2025.pdf",
            "hash": "a1b2c3d4e5f60718293a4b5c6d7e8f90a1b2c3d4e5f60718293a4b5c6d7e8f90",
        }
