"""Pydantic Structured Output Models for LLM Responses in InvestOps AI."""

from decimal import Decimal
from typing import Any, Literal
from pydantic import BaseModel, Field


class ClaimCitationOutput(BaseModel):
    source_external_id: str = Field(..., description="External ID of source document")
    locator: str = Field(..., description="Locator, section or page number in source")
    excerpt: str = Field(..., description="Verbatim text excerpt from source")


class ResearchClaimOutput(BaseModel):
    claim_text: str = Field(..., description="Empirical research claim statement")
    confidence: Decimal = Field(..., ge=Decimal("0.0"), le=Decimal("1.0"), description="Confidence score")
    citations: list[ClaimCitationOutput] = Field(default_factory=list, description="Source citations")


class CompanyAnalysisItem(BaseModel):
    rating: Literal["OVERWEIGHT", "NEUTRAL", "UNDERWEIGHT"] = Field(..., description="Stock rating")
    target_price: str = Field(..., description="Target price")
    thesis: str = Field(..., description="Investment thesis")


class SectorAnalysisItem(BaseModel):
    weight_recommendation: Literal["OVERWEIGHT", "NEUTRAL", "UNDERWEIGHT"] = Field(...)
    momentum: Literal["POSITIVE", "NEUTRAL", "NEGATIVE"] = Field(...)


class MarketIntelligenceOutput(BaseModel):
    market_summary: str = Field(..., description="Executive market summary")
    top_opportunities: list[str] = Field(default_factory=list, description="Top opportunities")
    top_risks: list[str] = Field(default_factory=list, description="Top risks")
    company_analysis: dict[str, CompanyAnalysisItem] = Field(default_factory=dict, description="Per-company analysis")
    sector_analysis: dict[str, SectorAnalysisItem] = Field(default_factory=dict, description="Per-sector analysis")
    confidence: Decimal = Field(..., ge=Decimal("0.0"), le=Decimal("1.0"), description="Overall report confidence")
    claims: list[ResearchClaimOutput] = Field(default_factory=list, description="Sourced research claims")


class AllocationOutput(BaseModel):
    symbol: str = Field(..., description="Ticker symbol")
    target_weight: Decimal = Field(..., ge=Decimal("0.0"), le=Decimal("1.0"), description="Target portfolio weight")
    target_quantity: Decimal = Field(..., ge=Decimal("0.0"), description="Target share quantity")
    side: Literal["BUY", "SELL", "HOLD"] = Field(..., description="Trade side")
    rationale: str = Field(..., description="Trade rationale")


class PortfolioStrategyOutput(BaseModel):
    expected_return: Decimal = Field(..., description="Annualized expected return")
    volatility: Decimal = Field(..., description="Annualized volatility")
    diversification_score: Decimal = Field(..., ge=Decimal("0.0"), le=Decimal("1.0"), description="Diversification score")
    investment_horizon_days: int = Field(..., gt=0, description="Investment horizon in days")
    confidence: Decimal = Field(..., ge=Decimal("0.0"), le=Decimal("1.0"), description="Recommendation confidence")
    reasoning: str = Field(..., description="Strategy reasoning")
    allocations: list[AllocationOutput] = Field(default_factory=list, description="Target asset allocations")
    risk_scenarios: dict[str, Any] = Field(default_factory=dict, description="Scenario analysis")
