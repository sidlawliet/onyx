# PROJECT CONTEXT

You are working on an enterprise software project called **InvestOps AI**.

InvestOps AI is an enterprise investment operations platform that automates the institutional investment lifecycle while ensuring that humans retain complete control over investment decisions.

This application is NOT:

- a stock prediction app
- an autonomous trading bot
- a retail investing application
- a crypto trading platform

The objective is to automate repetitive investment operations performed by investment firms while maintaining complete transparency, auditability and human oversight.

------------------------------------------------------------

# Primary Business Workflow

The application follows this workflow exactly.

1. Market Intelligence Agent

Responsibilities

- Research financial markets in real time
- Collect live market data
- Collect company fundamentals
- Collect financial news
- Collect earnings reports
- Collect analyst ratings
- Collect macroeconomic indicators
- Analyze market sentiment
- Generate a detailed Market Research Report

The report contains

- Market Summary
- Top Opportunities
- Top Risks
- Company Analysis
- Sector Analysis
- Confidence Scores
- Source References

The report is automatically passed to the Portfolio Strategy Agent.

------------------------------------------------------------

2. Portfolio Strategy Agent

Reads the Market Research Report.

Generates a Portfolio Recommendation Report containing

- Recommended companies
- Allocation percentages
- Risk analysis
- Expected return
- Volatility
- Diversification analysis
- Investment horizon
- Confidence score
- Detailed reasoning

The Portfolio Recommendation Report is sent to a human decision maker.

------------------------------------------------------------

3. Human Approval

The human may

- Approve
- Reject
- Modify allocations

No investment can be executed without explicit human approval.

Human approval is mandatory.

------------------------------------------------------------

4. Trade Execution Agent

Receives ONLY the approved portfolio.

Responsibilities

- Validate approved allocations
- Verify available funds
- Execute trades through broker APIs
- Store transactions
- Generate execution logs

The Execution Agent must never

- generate portfolios
- perform research
- modify allocations

------------------------------------------------------------

5. Portfolio Monitoring Agent

Continuously monitors

- Portfolio holdings
- Live prices
- Profit and Loss
- Portfolio drift
- Sector allocation
- Performance
- Alerts
- Reports
- Historical investments

Generates

- Daily reports
- Weekly reports
- Monthly reports
- Performance dashboards

------------------------------------------------------------

# Core Principles

The workflow above is fixed.

Do not redesign it.

Do not merge agents.

Do not introduce autonomous investing.

Do not bypass human approval.

Every important action must be traceable.

Every decision must be auditable.

Every generated report must be stored.

Every service should be modular.

The architecture must support future expansion without major refactoring.

------------------------------------------------------------

# Technology Stack

Frontend

- Next.js
- TypeScript
- TailwindCSS
- shadcn/ui

Backend

- FastAPI

Database

- PostgreSQL

Caching

- Redis

Deployment

- Docker

Authentication

- Better Auth (or equivalent)

Broker Integration

Abstracted through provider interfaces.

Market Data

Abstracted through provider interfaces.

------------------------------------------------------------

# Existing Project Files

The following files already exist and must be treated as the source of truth.

business-brief.md

Contains the validated business opportunity.

design.md

Contains the finalized UI and UX.

Never redesign the interface.

Never recreate screens.

Use design.md as the canonical design specification.

------------------------------------------------------------

# Development Philosophy

Follow the BMAD methodology.

Every artifact must build upon previous artifacts.

Never contradict

- business-brief.md
- design.md
- previously approved architecture

Always preserve architectural consistency throughout the project.
InvestOps AI is NOT attempting to replace Bloomberg,
Aladdin, Charles River or FactSet.

Instead it acts as an AI orchestration layer
that sits above existing institutional systems.

The platform connects

Market Research

↓

Portfolio Construction

↓

Human Approval

↓

Execution

↓

Monitoring

while preserving every decision,
every report,
every approval,
and every investment as a complete auditable chain.

The competitive advantage is not better market data.

The competitive advantage is
workflow continuity,
AI-assisted decision support,
and end-to-end auditability.