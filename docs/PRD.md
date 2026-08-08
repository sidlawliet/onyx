# Onyx Product Requirements Document

**Status:** Draft for stakeholder review  
**Product:** InvestOps AI  
**Date:** August 7, 2026  
**Canonical inputs:** `project-context.md`, `business-brief.md`, and the complete Stitch export in `ui/`

## Executive Summary
Onyx AI is an enterprise orchestration platform for institutional investment operations. It connects market research, portfolio construction, mandatory human approval, trade execution, and portfolio monitoring into one traceable workflow while leaving existing market-data, broker, custodian, and system-of-record platforms in place.

The product addresses a documented market problem: institutional firms have capable specialist systems, but evidence, decisions, controls, orders, and outcomes remain fragmented across terminals, portfolio and order management systems, spreadsheets, documents, and communications. InvestOps AI improves continuity across that installed stack. AI performs preparatory, analytical, and monitoring work; named professionals retain authority for investment decisions. No portfolio may reach execution without explicit human approval.

The MVP will implement the fixed lifecycle defined in `project-context.md`:

1. Market Intelligence Agent generates a sourced Market Research Report.
2. Portfolio Strategy Agent consumes that report and generates a Portfolio Recommendation Report.
3. A human decision maker approves, rejects, or modifies the recommendation.
4. Trade Execution Agent validates and executes only the approved portfolio through broker interfaces.
5. Portfolio Monitoring Agent monitors holdings and outcomes and generates alerts and periodic reports.

Every input, generated report, model version, decision, approval, modification, order, execution event, and monitoring outcome will form a reproducible audit chain. The Stitch export under `ui/` is the canonical interface specification. This PRD defines product behavior within those screens and does not authorize any redesign or new layout.

## Vision

Enable institutional investment teams to move from evidence to monitored outcome with less manual searching, rekeying, and reconciliation, while making human accountability and auditability stronger than in fragmented workflows.

The product will become the governed context and orchestration layer above existing institutional systems, not a replacement for Bloomberg, Aladdin, Charles River, FactSet, brokers, custodians, compliance controls, or books of record. Its durable advantage will be workflow continuity, proprietary decision history, AI-assisted decision support, and end-to-end evidence preservation.

## Product Positioning

### Category

Governed AI orchestration for institutional investment operations.

### Target Customers

- Institutional asset managers and asset owners
- Hedge funds
- Wealth platforms with institutional operating requirements
- Outsourced investment operations providers
- Public-market teams initially, with controlled expansion to additional asset classes

### Core Value Proposition

InvestOps AI reduces the effort required to gather evidence, produce reviewable analysis, hand work between specialist functions, investigate exceptions, and reconstruct decisions. It does so without replacing systems of record or transferring fiduciary accountability to AI.

### Differentiation

- One continuous evidence chain from market research through monitoring
- Source-linked and versioned AI outputs rather than generic chat responses
- Mandatory, substantive human approval before execution
- Strict separation of research, strategy, execution, and monitoring responsibilities
- Provider-agnostic integration with the installed institutional stack
- Searchable, exportable audit records covering both agent and human actions

### Explicit Non-Goals

- Stock prediction for retail users
- Autonomous portfolio approval, allocation changes, or trading
- Crypto trading
- Replacement of market-data terminals, OMS/PMS, accounting, risk, compliance, broker, or custodian systems
- Final interpretation of ambiguous legal, regulatory, mandate, or compliance rules by AI
- Autonomous control overrides, breach closure, valuation approval, or external communications

**Business justification:** The brief identifies fragmented context, manual synthesis, approval friction, and weak decision memory as core pain points. It also concludes that adoption will favor governed augmentation of installed systems, while autonomous security selection, allocation changes, trade release, and control overrides carry materially higher fiduciary and operational risk (`business-brief.md`, Executive Summary; Pain Points; Strategic Conclusions).

## Business Requirements

| ID | Requirement | Business justification | Canonical UI reference |
|---|---|---|---|
| BR-01 | Preserve the five-stage workflow in order: Market Intelligence, Portfolio Strategy, Human Approval, Trade Execution, and Portfolio Monitoring. Stages may not be merged, skipped, or reordered. | Institutional investing relies on specialized roles and separated decision rights; continuity between those roles is the unmet need (`business-brief.md`, Executive Summary; Industry Operating Model; Strategic Conclusions 1). | Persistent stage navigation in `onyx_market_intelligence_refined`, `onyx_decision_workspace_refined`, and related screens; pipeline state in `onyx_workflow_engine_refined`. |
| BR-02 | Require explicit human approval of the final allocations before any order can be released. Rejection terminates the execution path; modification creates a revised recommendation requiring approval. | Meaningful human review requires evidence, authority to reject, and recorded rationale; unsupervised order release and autonomous target-weight changes are high-risk uses (`business-brief.md`, High-Risk Uses; Strategic Conclusion 5). | `Approve Allocation`, `Modify`, and `Reject` controls in `onyx_decision_workspace_refined`; `Approved` as the first execution milestone in `onyx_trade_execution_refined`. |
| BR-03 | Preserve a complete, searchable, exportable chain linking source evidence, reports, recommendation versions, approvals, orders, execution events, and monitoring outcomes. | Firms struggle to reconstruct why decisions were made, while books-and-records obligations and model governance demand reproducible evidence (`business-brief.md`, Approval Friction and Weak Decision Memory; Regulatory and Control Considerations). | `onyx_audit_trail_refined` event table, event details, JSON payload, chain of custody, search, filters, and export controls. |
| BR-04 | Operate as an integration and orchestration layer over existing providers and systems of record through abstract provider interfaces. | Institutions remain multi-vendor, implementation risk limits replacement, and buyers favor augmentation (`business-brief.md`, Competitive Implications 2 and 5; Strategic Conclusion 7). | `onyx_integrations_refined` connection grid, active connections, connection details, health, scopes, and event stream. |
| BR-05 | Apply least-privilege, role-based access with strong authentication and separation of sensitive permissions. | Firms remain responsible for data privacy, cybersecurity, information barriers, supervision, and independent control functions (`business-brief.md`, Regulatory and Control Considerations; Cross-Jurisdiction Control Baseline). | `onyx_access_control_refined` user directory, roles, MFA state, and granular Market Intelligence, Trade Execution, override, and Audit permissions. |
| BR-06 | Make AI outputs reviewable by showing sources, confidence, assumptions/reasoning, model identity/version, and uncertainty where applicable. | The strongest AI opportunities preserve source evidence and assist a named professional; generated research remains unverified until checked (`business-brief.md`, Market Research; Opportunities for AI Automation; Strategic Conclusions 2 and 5). | Evidence links and confidence in `onyx_market_intelligence_refined`; evidence, version compare, confidence, scenario analysis, risks, and reasoning in `onyx_decision_workspace_refined`. |
| BR-07 | Use deterministic controls outside generative models for hard limits, funds checks, execution eligibility, and workflow gates. | Consequential models require independent validation and deterministic controls; AI scores are not substitutes for compliance or best-execution review (`business-brief.md`, High-Risk Uses; Cross-Jurisdiction Control Baseline 7). | Validation milestone and emergency controls in `onyx_trade_execution_refined`; disabled override permission in `onyx_access_control_refined`. |
| BR-08 | Support operational resilience through health monitoring, alerting, safe halt/cancel controls, retry handling, and manual fallback. | T+1 compresses repair windows, while DORA and cross-jurisdiction guidance require resilience, incident management, continuity, and fallback (`business-brief.md`, Trade Execution; DORA; Cross-Jurisdiction Control Baseline 11). | `onyx_system_health_refined`, broker health and `Emergency Halt`/`Cancel All` in `onyx_trade_execution_refined`, connectivity testing and warnings in `onyx_integrations_refined`. |
| BR-09 | Enforce data entitlements, permitted-use restrictions, confidentiality controls, and retention policies for every provider and generated artifact. | Data rights, MNPI, privacy, licensing, and retention determine whether AI use is deployable (`business-brief.md`, Competitive Implication 3; MNPI and Market Abuse; GDPR; Strategic Conclusion 3). | Permission scopes and credential controls in `onyx_integrations_refined`; user and role configuration in `onyx_access_control_refined`; document metadata in `onyx_knowledge_center_refined`. |
| BR-10 | Reduce manual research synthesis, handoff effort, and exception investigation without removing accountable professional review. | Search, reading, extraction, comparison, drafting, and triage are the largest appropriate AI workloads and are under cost and talent pressure (`business-brief.md`, Manual Information Processing; Cost and Talent Pressure; Strategic Conclusion 2). | Research synthesis, workflow queues, agent job queue, command/search surfaces, and context rails across the Stitch export. |

## Functional Requirements

### Workflow Orchestration

| ID | Requirement | Business justification | Canonical UI reference |
|---|---|---|---|
| FR-WF-01 | Create a unique workflow ID and trace ID for each investment lifecycle instance and propagate them through every stage and artifact. | Cross-system fragmentation makes reconstruction difficult; records must reproduce and explain decisions (`business-brief.md`, Fragmented Data and Context; Cross-Jurisdiction Control Baseline 12). | Workflow IDs and timeline in `onyx_workflow_engine_refined`; trace IDs in `onyx_audit_trail_refined`. |
| FR-WF-02 | Represent workflow states at minimum as queued, running, awaiting review, approved, rejected, failed, completed, and halted, with actor and timestamp for each transition. | Exception-driven operations require rapid prioritization and accountability (`business-brief.md`, Exception-Driven Operations; Approval Governance). | Active/completed tabs, status filters, expanded timeline, and review action in `onyx_workflow_engine_refined`. |
| FR-WF-03 | Automatically pass only the completed, stored Market Research Report to the Portfolio Strategy Agent. | Continuity between evidence and decisions is the central unmet need, but source lineage must remain intact (`business-brief.md`, Strategic Conclusions 1 and 6). | Workflow pipeline and context rail in `onyx_workflow_engine_refined`; related reports in `onyx_market_intelligence_refined`. |
| FR-WF-04 | Pass only an explicitly approved recommendation version to Trade Execution. The backend must reject all other execution requests regardless of client behavior. | Unsupervised order release is high risk; controls must be independent of the generative model and UI (`business-brief.md`, High-Risk Uses; Cross-Jurisdiction Control Baseline 7-8). | `Approved` execution milestone in `onyx_trade_execution_refined`; approval controls in `onyx_decision_workspace_refined`. |
| FR-WF-05 | On failure, preserve intermediate artifacts, expose failure details, notify the responsible role, and allow authorized retry or termination without duplicating downstream actions. | Residual exceptions are low-volume but high-consequence; continuity and safe recovery are required (`business-brief.md`, Exception-Driven Operations; DORA). | Failed jobs and `Abort Job` in `onyx_ai_agents_workspace_refined`; retry and event stream in `onyx_integrations_refined`. |

### Market Intelligence Agent

| ID | Requirement | Business justification | Canonical UI reference |
|---|---|---|---|
| FR-MI-01 | Ingest authorized live market data, company fundamentals, financial news, earnings reports, analyst ratings, macroeconomic indicators, and sentiment inputs through provider interfaces. | Institutional research combines structured data, primary documents, market data, news, and portfolio context (`business-brief.md`, Market Research and Idea Generation). | Sector heatmap, real-time flow, asset-class controls, indices variance, and watchlist in `onyx_market_intelligence_refined`; provider cards in `onyx_integrations_refined`. |
| FR-MI-02 | Generate and store a versioned Market Research Report containing Market Summary, Top Opportunities, Top Risks, Company Analysis, Sector Analysis, Confidence Scores, and Source References. | AI is appropriate for reviewable synthesis when sources and assumptions remain available (`business-brief.md`, Research Ingestion and Retrieval; Market Research). | `Onyx AI Synthesis`, core thesis, evidence links, confidence, and related reports in `onyx_market_intelligence_refined`; repository metadata in `onyx_knowledge_center_refined`. |
| FR-MI-03 | Attach source identifier, provider, publication/effective timestamp, retrieval timestamp, entitlement context, and source link or retained excerpt to each material claim. | Date/version awareness, entitlement enforcement, citations, and provenance are required controls (`business-brief.md`, High-Value Opportunities; Cross-Jurisdiction Control Baseline 3 and 5). | Evidence Links and Context Rail in `onyx_market_intelligence_refined`; document version/author metadata in `onyx_knowledge_center_refined`. |
| FR-MI-04 | Display confidence and clearly flag missing, stale, conflicting, or low-confidence evidence for analyst review; the agent must not silently correct source data. | Data-quality triage must use deterministic validation and logged human disposition, with no silent correction (`business-brief.md`, Data-Quality Triage). | Confidence badges, real-time status, and agent warnings/logs in `onyx_market_intelligence_refined` and `onyx_ai_agents_workspace_refined`. |
| FR-MI-05 | Support analyst search, filtering, source inspection, and generation of deeper research from the existing market intelligence workspace. | Analysts currently lose time moving among fragmented tools and manually synthesizing evidence (`business-brief.md`, Market Research; Fragmented Data and Context). | Search/command palette, asset-class tabs, time-range controls, watchlist, evidence links, and `Generate Deep Dive` in `onyx_market_intelligence_refined`. |

### Portfolio Strategy Agent

| ID | Requirement | Business justification | Canonical UI reference |
|---|---|---|---|
| FR-PS-01 | Consume the exact version of the Market Research Report linked to the workflow and record that input version. | Decisions must be reproducible from retained inputs and model versions (`business-brief.md`, High-Risk Uses; Cross-Jurisdiction Control Baseline 5 and 12). | Version and compare controls plus evidence sources in `onyx_decision_workspace_refined`. |
| FR-PS-02 | Generate and store a versioned Portfolio Recommendation Report containing recommended companies, allocation percentages, risk analysis, expected return, volatility, diversification analysis, investment horizon, confidence score, and detailed reasoning. | Portfolio construction requires sizing under constraints, risk/scenario analysis, and accountable assumptions (`business-brief.md`, Portfolio Construction). | Portfolio Recommendation, proposed allocation, expected return, scenario analysis, confidence, impact summary, and reasoning in `onyx_decision_workspace_refined`. |
| FR-PS-03 | Compare proposed allocations with current holdings, benchmark, mandate constraints, cash, concentration, liquidity, and applicable risk limits before submission for approval. | Portfolio teams inspect constraint utilization and iterate; optimization cannot remove professional judgment (`business-brief.md`, Portfolio Construction). | Current/proposed comparison, net change, sector impact, risk factors, and scenario analysis in `onyx_decision_workspace_refined`. |
| FR-PS-04 | Flag hard-limit breaches as non-approvable and ambiguous constraints for independent risk/compliance review; the agent must not interpret or override them conclusively. | Final rule interpretation and control overrides are high-risk; compliance and risk must independently challenge limits (`business-brief.md`, Human Approval and Governance; High-Risk Uses). | Risk factors and "remains within established risk limits" impact state in `onyx_decision_workspace_refined`; override control in `onyx_access_control_refined`. |
| FR-PS-05 | Permit iterative recommendation versions while retaining diffs, prior versions, source lineage, author/agent identity, and timestamps. | Spreadsheets create version and lineage risk; approval records must identify later changes (`business-brief.md`, Spreadsheet Risk; Human Approval and Governance). | `v2.1 / v2.0` and `Compare` in `onyx_decision_workspace_refined`; version column in `onyx_knowledge_center_refined`. |

### Human Approval

| ID | Requirement | Business justification | Canonical UI reference |
|---|---|---|---|
| FR-HA-01 | Present the assigned approver with the thesis, evidence, risks, recommendation, scenario analysis, current-versus-proposed impact, confidence, model/version metadata, and prior changes in one review context. | Substantive review requires competence, evidence, uncertainty, changed assumptions, and authority to reject (`business-brief.md`, High-Risk Uses; Strategic Conclusion 5). | Three-column decision workspace in `onyx_decision_workspace_refined`. |
| FR-HA-02 | Allow an authorized human to approve, reject, or request/perform allocation modification using the existing controls. | Accountable professionals remain responsible for final positioning, assumptions, and overrides (`business-brief.md`, Portfolio Construction; Human Approval and Governance). | `Approve Allocation`, `Modify`, and `Reject` in `onyx_decision_workspace_refined`. |
| FR-HA-03 | Require a reason for rejection and modification, and require an approval attestation confirming review of evidence and authority to decide. | Effective records identify evidence considered, decision, conditions, approver, timestamp, and changes (`business-brief.md`, Human Approval and Governance). | Behavior attached to the canonical action controls in `onyx_decision_workspace_refined`; no new layout is authorized. |
| FR-HA-04 | Treat a modification as a new recommendation version, rerun deterministic validations, and require fresh explicit approval before execution. | Autonomous target-weight changes are high-risk, and later changes must be captured (`business-brief.md`, High-Risk Uses; Human Approval and Governance). | `Modify`, version compare, and impact summary in `onyx_decision_workspace_refined`. |
| FR-HA-05 | Enforce role, mandate, delegated authority, MFA, and separation-of-duties checks before accepting an approval or exception disposition. | Strong governance separates proposal, exception, valuation, and operational override rights (`business-brief.md`, Human Approval and Governance; Cross-Jurisdiction Control Baseline). | Assignee in `onyx_decision_workspace_refined`; roles, MFA, and granular permissions in `onyx_access_control_refined`. |

### Trade Execution Agent

| ID | Requirement | Business justification | Canonical UI reference |
|---|---|---|---|
| FR-TE-01 | Accept only a locked, approved portfolio artifact and validate approval identity, timestamp, version, allocations, available funds, account eligibility, and broker connectivity before order creation. | Execution begins after approval and includes cash checks, allocation, pre-trade controls, and connectivity (`business-brief.md`, Trade Execution and Post-Trade Processing). | Approved-to-validation pipeline and broker/API health in `onyx_trade_execution_refined`. |
| FR-TE-02 | Prevent the Trade Execution Agent from researching securities, generating portfolios, changing allocations, or bypassing limits. | Traders do not own the investment thesis; autonomous allocation changes and overrides are high-risk (`business-brief.md`, Human Approval and Governance; High-Risk Uses). | Execution screen is limited to queue, status, strategy, progress, broker health, modification/cancel, and logs in `onyx_trade_execution_refined`. |
| FR-TE-03 | Route orders through abstract broker interfaces and record order, account allocation, broker, venue, execution strategy, timestamps, acknowledgements, fills, rejects, cancellations, and settlement state. | Best execution and books-and-records duties require routing logic, broker selection, execution evidence, and exceptions (`business-brief.md`, Trade Execution; U.S. Best Execution and Allocation). | Execution queue, order details, pipeline milestones, and live audit trail in `onyx_trade_execution_refined`; FIX integration details in `onyx_integrations_refined`. |
| FR-TE-04 | Show queue and order states including validation, queued, submitted, partial fill, executed, rejected, cancelled, and settled, with real-time progress and error detail. | T+1 increases the importance of same-day processing and rapid exception resolution (`business-brief.md`, Trade Execution and Post-Trade Processing). | Pipeline progress, execution queue, details drawer, progress, and logs in `onyx_trade_execution_refined`. |
| FR-TE-05 | Provide authorized cancel-order, cancel-all, emergency-halt, and safe retry capabilities; all such actions must be idempotent and audited. | Operational resilience requires failure containment, manual fallback, and records; execution errors are high consequence (`business-brief.md`, DORA; Cross-Jurisdiction Control Baseline 11-12). | `Cancel Order`, `Cancel All`, `Emergency Halt`, and live audit trail in `onyx_trade_execution_refined`. |
| FR-TE-06 | Any execution-side "Modify" action that changes investment quantity or allocation must stop execution and return the proposal to strategy validation and human approval. It may not mutate the approved artifact in place. | Autonomous target-weight changes and unsupervised corrections are explicitly high-risk (`business-brief.md`, High-Risk Uses). | `Modify` in `onyx_trade_execution_refined`, behavior constrained by the approval workflow; layout remains unchanged. |

### Portfolio Monitoring Agent

| ID | Requirement | Business justification | Canonical UI reference |
|---|---|---|---|
| FR-PM-01 | Continuously ingest authorized holdings, prices, cash, transactions, benchmark, and risk data and reconcile them against authoritative systems. | The same figure can differ across systems, creating recurring reconciliation work (`business-brief.md`, Portfolio Monitoring). | Live portfolio KPIs, holdings table, activity log, and integration status in `onyx_portfolio_monitoring_refined`. |
| FR-PM-02 | Monitor holdings, live prices, P&L, target drift, sector allocation, performance, risk, alerts, and historical investments. | These are core institutional monitoring domains connecting thesis, mandate, and actual portfolio (`business-brief.md`, Portfolio Monitoring). | KPI row, performance-versus-benchmark, risk alerts, holdings and drift, activity, and news in `onyx_portfolio_monitoring_refined`. |
| FR-PM-03 | Rank and display alerts by severity, impact, recency, confidence, related positions, and reasoning while requiring human disposition for breaches or corrective investment actions. | Static alerting causes overload; AI may prioritize evidence, but final breach determinations and overrides remain with professionals (`business-brief.md`, Alert Overload; Medium-Risk Opportunities). | AI Risk Alerts with confidence and `View Reasoning` in `onyx_portfolio_monitoring_refined`. |
| FR-PM-04 | Generate, store, and export daily, weekly, and monthly reports and on-demand performance reports from reconciled data. | Reporting demand is increasing, and generated commentary must reconcile to approved source data (`business-brief.md`, Portfolio Monitoring; Operational and Client Commentary). | `Export Report`, reports navigation, activity log, and Knowledge Center repository. |
| FR-PM-05 | Treat `Rebalance` as initiation of a new strategy recommendation workflow requiring validation and explicit approval, never as direct autonomous execution. | Autonomous changes to target weights or unsupervised order release are high-risk (`business-brief.md`, High-Risk Uses). | Existing `Rebalance` control in `onyx_portfolio_monitoring_refined`; subsequent review uses `onyx_decision_workspace_refined`. |
| FR-PM-06 | Interpret any "Auto-Rebalance Executed" activity text as an execution of a previously approved rebalance, and link it to that approval and order trace. | Approval must be substantive and records must reproduce a decision; UI wording cannot bypass governance (`business-brief.md`, Human Approval and Governance; Cross-Jurisdiction Control Baseline 12). | Activity Log in `onyx_portfolio_monitoring_refined` and chain of custody in `onyx_audit_trail_refined`. |

### Reports, Knowledge, Audit, and Administration

| ID | Requirement | Business justification | Canonical UI reference |
|---|---|---|---|
| FR-GV-01 | Store every generated report and approved artifact in a searchable repository with title, category, owner/agent, version, effective date, update time, tags, source lineage, and retention class. | Institutional memory is difficult to search; access, effective-date logic, citation, and retention are required (`business-brief.md`, Knowledge Discovery; Books and Records). | Collections, repository, search, filters, document metadata, recent activity, and tags in `onyx_knowledge_center_refined`. |
| FR-GV-02 | Record immutable audit events for authentication, data access, agent jobs, report generation, recommendation changes, approval actions, validations, orders, executions, alerts, configuration changes, exports, and failures. | Firms need records sufficient to reproduce decisions and supervise consequential AI (`business-brief.md`, Supervision and Model Governance; Cross-Jurisdiction Control Baseline). | Forensic event log, agent/user action KPIs, event details, and chain of custody in `onyx_audit_trail_refined`. |
| FR-GV-03 | Support audit search and filters by time, severity, category, actor, entity/resource, action, status, workflow ID, and trace ID, plus controlled export. | Evidence is often scattered, and books-and-records obligations require retrievable records (`business-brief.md`, Approval Friction; Books and Records). | Search, time selector, filters, trace IDs, detail drawer, and export actions in `onyx_audit_trail_refined`. |
| FR-GV-04 | Provision and suspend users; manage role-based permissions for research, strategy, approval, execution, overrides, audit, integrations, and administration; require MFA for privileged and approval roles. | Least privilege, access control, accountability, and information barriers are foundational controls (`business-brief.md`, Privacy and Cybersecurity; Cross-Jurisdiction Control Baseline 4). | User directory, status/MFA fields, provisioning, role configuration, granular toggles, and save/reset actions in `onyx_access_control_refined`. |
| FR-GV-05 | Inventory agent versions and jobs; expose status, task, duration, logs, warnings, confidence, inputs, outputs, and authorized abort/export actions. | Consequential AI requires inventory, validation, limitations, change control, monitoring, and incident evidence (`business-brief.md`, Supervision and Model Governance). | Status cards, job queue, execution console, `Abort Job`, and `Export` in `onyx_ai_agents_workspace_refined`. |
| FR-GV-06 | The phrase "autonomous agents" in the canonical AI workspace is operational status copy only; agents remain bounded by the permissions and human-decision rules in this PRD. | The market direction is governed augmentation, not unbounded autonomy (`business-brief.md`, Executive Summary; High-Risk Uses). | Existing page copy in `onyx_ai_agents_workspace_refined`; no visual redesign required. |
| FR-GV-07 | Manage market-data, broker, and custodian connections through provider interfaces, including environment, protocol, health, throughput, credentials, scopes, expiry, rotation, test, disable, and event history. | Multi-vendor integration, data rights, vendor oversight, resilience, and exit planning are adoption requirements (`business-brief.md`, Competitive Implications; Cross-Jurisdiction Control Baseline 10). | Entire `onyx_integrations_refined` workspace. |
| FR-GV-08 | Monitor service uptime, latency, compute, database health, topology, errors, alerts, and capacity; support diagnostics and report export. | Firms remain accountable for operational resilience and third-party concentration (`business-brief.md`, DORA; Privacy and Cybersecurity). | `onyx_system_health_refined` health pulse, topology, active alerts, diagnostics, logs, and export. |

## Non Functional Requirements

| ID | Requirement | Target / acceptance threshold | Business justification |
|---|---|---|---|
| NFR-01 | Security | TLS 1.2+ in transit, AES-256 or platform-equivalent encryption at rest, secrets held outside application code, MFA for privileged roles, least privilege, and environment isolation. | Privacy, cybersecurity, vendor, and data-leakage risks expand with model and retrieval services (`business-brief.md`, Privacy and Cybersecurity; Cross-Jurisdiction Control Baseline 4). |
| NFR-02 | Authorization integrity | All permissions and workflow gates enforced server-side; zero successful execution attempts without a valid approved artifact in security testing. | Human approval and independent controls cannot rely on a ceremonial click or client UI (`business-brief.md`, High-Risk Uses; Strategic Conclusion 5). |
| NFR-03 | Audit integrity | Audit records are append-only for standard users, time-synchronized in UTC, tamper-evident, traceable end to end, and exportable under authorized access. | Books-and-records and reproducibility obligations require durable evidence (`business-brief.md`, Books and Records; Cross-Jurisdiction Control Baseline 12). |
| NFR-04 | Reproducibility | Every material AI output records input/source versions, model/provider/version, prompt or instruction version, parameters, timestamp, and output version sufficient to reproduce or explain it. | Decisions whose rationale cannot be reproduced are explicitly high-risk (`business-brief.md`, High-Risk Uses; Cross-Jurisdiction Control Baseline 5). |
| NFR-05 | Availability | 99.9% monthly availability for core review and orchestration services, excluding planned maintenance; execution controls and emergency halt must remain available under degraded noncritical services. | Time-sensitive exceptions and settlement compression require resilient operations (`business-brief.md`, T+1; DORA). |
| NFR-06 | Performance | P95 application read response under 2 seconds, P95 approval command acknowledgement under 1 second, live execution/health event display within 2 seconds of receipt, and search results under 3 seconds for the defined MVP data volume. | Institutional teams need rapid evidence access and exception response under time pressure (`business-brief.md`, Exception-Driven Operations; T+1). |
| NFR-07 | Reliability and idempotency | Workflow transitions, approvals, order submissions, cancellations, retries, and report generation are idempotent; duplicate requests do not create duplicate approvals, orders, or records. | Execution errors have financial consequences and require deterministic controls (`business-brief.md`, Trade Execution; Cross-Jurisdiction Control Baseline 7). |
| NFR-08 | Data quality | Validate schema, freshness, identifiers, currency, timestamps, completeness, and reconciliation status; quarantine invalid inputs and never silently overwrite authoritative data. | Inconsistent data and identifiers are a core pain point; AI triage must not silently correct (`business-brief.md`, Fragmented Data; Data-Quality Triage). |
| NFR-09 | Privacy and data governance | Support data classification, purpose limitation, entitlement checks, regional handling, configurable retention/deletion, legal hold, and prevention of unauthorized model-provider use. | GDPR, MNPI, licensing, and cross-border obligations gate deployability (`business-brief.md`, Regulatory and Control Considerations; Strategic Conclusion 3). |
| NFR-10 | Model governance | Maintain model inventory, documented use boundaries, predeployment tests, independent validation for consequential use, monitored quality/drift, rollback, and change approval. | Model governance expectations include inventory, validation, limitations, change control, and monitoring (`business-brief.md`, Supervision and Model Governance). |
| NFR-11 | Observability | Centralized metrics, logs, traces, correlation IDs, service and provider health, alerting, and auditable incident actions across all modules. | Operational resilience and rapid exception investigation require connected evidence (`business-brief.md`, DORA; Exception-Driven Operations). |
| NFR-12 | Accessibility | Meet WCAG 2.2 AA for keyboard access, focus, labels, contrast, non-color status cues, tables, dialogs, and screen-reader semantics while preserving the canonical visual design. | Enterprise controls must be usable by authorized professionals; accessibility also reduces operational error. This supports the brief's requirement for meaningful, competent human review (`business-brief.md`, High-Risk Uses). |
| NFR-13 | UI fidelity and responsiveness | Implement the Stitch export exactly as the canonical UI specification. Preserve structure, controls, density, typography, colors, and layouts. Optimize for desktop 1440px+, collapse navigation at laptop widths, and provide responsive stacking only for critical monitoring on smaller screens as specified in `ui/onyx_institutional/DESIGN.md`. | Dense institutional work requires cognitive efficiency; the validated UI operationalizes the business need for reviewable evidence and rapid comparison. |
| NFR-14 | Maintainability | Use modular services and documented provider contracts. Provider replacement or addition must not require changes to core workflow rules. | Institutions remain multi-vendor, and vendor dependencies evolve (`business-brief.md`, Competitive Implications; Legacy Integration and Vendor Dependence). |
| NFR-15 | Business continuity | Document and test backup/restore, degraded-mode behavior, manual approval/execution fallback, provider failover where contracted, and recovery procedures at least quarterly before production scale. | Critical AI-supported functions require continuity, manual fallback, and vendor exit planning (`business-brief.md`, DORA; Cross-Jurisdiction Control Baseline 10-11). |

## User Personas

### Investment Analyst

Researches companies, sectors, macro conditions, and catalysts. Needs fast synthesis, primary-source links, confidence and data-quality warnings, versioned reports, and the ability to challenge generated conclusions. This addresses the brief's manual synthesis burden while preserving analyst verification.

### Portfolio Manager / Human Approver

Owns portfolio decisions within delegated authority. Needs one review context showing thesis, sources, risks, constraints, scenarios, current-versus-proposed impact, and changes. Must be able to approve, reject, or modify with accountable rationale. This implements the brief's requirement for substantive rather than ceremonial oversight.

### Trader / Execution Operator

Executes approved investment intent and manages order exceptions without owning or changing the thesis. Needs cash/validation status, broker health, execution queue, fills, rejects, cancel/halt controls, and audit evidence. This reflects the brief's separation between investment decisions and execution tactics.

### Risk and Compliance Officer

Independently challenges limits, mandate adherence, exceptions, conflicts, and controls. Needs source lineage, deterministic validation results, alert prioritization, approval records, model/version data, and immutable audit exports. This supports independent decision rights and regulatory evidence.

### Investment Operations Analyst

Investigates data, settlement, reconciliation, and reporting exceptions across systems. Needs connected traces, provider health, transaction state, likely-cause evidence, retry/fallback controls, and reconciled reports. This targets the brief's costly, time-sensitive exception work.

### Auditor

Reconstructs who did what, when, with which evidence and authority. Needs read-only search, filters, trace IDs, payloads, chain of custody, retention, and controlled export. This addresses books-and-records and weak decision-memory risks.

### Platform Administrator / SRE

Manages identities, permissions, integrations, secrets, agent versions, health, incidents, and recovery. Needs least-privilege controls, MFA state, connection scopes, key rotation, diagnostics, topology, logs, and safe disablement. This supports cybersecurity, resilience, and vendor governance obligations.

### CIO / Operations Executive

Needs a concise view of pipeline, portfolio performance, active operations, risk, system health, and productivity outcomes without bypassing specialist workflows. The `onyx_executive_dashboard_refined` screen is the canonical summary experience. This responds to cost pressure and the need to govern the full operating chain.

## User Stories

| ID | User story | Related requirements |
|---|---|---|
| US-01 | As an investment analyst, I want a cited market report assembled from authorized current sources so that I can validate evidence instead of manually searching disconnected systems. | FR-MI-01 through FR-MI-05 |
| US-02 | As a portfolio manager, I want a recommendation tied to a specific research version with risk, scenarios, and portfolio impact so that I can make an informed and reproducible decision. | FR-PS-01 through FR-PS-05, FR-HA-01 |
| US-03 | As an approver, I want to approve, reject, or modify a proposal with recorded rationale so that my authority and evidence are explicit. | FR-HA-02 through FR-HA-05 |
| US-04 | As a compliance officer, I want hard-limit breaches blocked independently of AI so that a model cannot override client or regulatory controls. | BR-07, FR-PS-04, NFR-02 |
| US-05 | As a trader, I want to receive only locked approved allocations and see validation and broker status so that I can execute the authorized intent safely. | FR-TE-01 through FR-TE-04 |
| US-06 | As a trader, I want cancel and emergency-halt controls with immediate audit records so that I can contain execution incidents. | FR-TE-05 |
| US-07 | As an operations analyst, I want every execution event correlated across the broker, order, portfolio, and audit record so that I can investigate exceptions quickly. | FR-TE-03, FR-GV-02, FR-GV-03 |
| US-08 | As a portfolio manager, I want live performance, drift, and prioritized risk alerts so that I can identify material changes without clearing duplicate low-value alerts. | FR-PM-01 through FR-PM-03 |
| US-09 | As an approver, I want a rebalance request to return through strategy and approval so that monitoring cannot change investments autonomously. | FR-PM-05, FR-PM-06 |
| US-10 | As an auditor, I want to search and export the full chain from sources through monitored outcome so that I can reproduce a decision. | FR-GV-01 through FR-GV-03 |
| US-11 | As an administrator, I want granular roles, MFA, and separated override permissions so that users have only the authority required by their function. | FR-GV-04, NFR-01, NFR-02 |
| US-12 | As an SRE, I want service, database, agent, and provider health with diagnostics so that I can detect and recover from failures before they disrupt critical operations. | FR-GV-05, FR-GV-07, FR-GV-08 |
| US-13 | As a CIO, I want workflow, performance, risk, and operational KPIs in one executive view so that I can measure control quality and productivity without replacing source systems. | BR-04, BR-10, Success Metrics |

## Acceptance Criteria

### End-to-End Workflow

1. Given authorized data providers are available, when a Market Intelligence job completes, then the system stores a versioned report containing all seven required sections, citations, confidence, source metadata, model/version metadata, workflow ID, and trace ID.
2. Given a completed Market Research Report, when strategy generation starts, then the Portfolio Strategy Agent receives that exact report version and creates a separate versioned recommendation with all nine required contents.
3. Given a recommendation has not been explicitly approved, when any client or service requests order creation or release, then the server rejects the request, creates no order, and writes a blocked audit event.
4. Given an authorized approver selects Approve, then the system records the approver, authority, MFA state, recommendation version, attestation, timestamp, and evidence context before making the locked artifact eligible for execution.
5. Given an approver selects Reject, then a reason is required, the workflow becomes rejected, no execution artifact is issued, and the action is audited.
6. Given an approver selects Modify, then the change and reason create a new recommendation version, validations rerun, prior approval state is invalidated, and fresh approval is required.
7. Given an approved locked portfolio reaches execution, then allocations match the approved version exactly and pre-execution validation covers funds, account eligibility, limits, approval integrity, and broker connectivity.
8. Given orders execute, reject, cancel, or settle, then each state and provider response is stored under the same workflow and trace chain and appears in the canonical execution and audit views.
9. Given executed holdings are available, when monitoring refreshes, then portfolio value, P&L, performance, target drift, sector exposure, risk state, and related activity use reconciled authoritative data and show freshness status.
10. Given a user selects Rebalance from monitoring, then a new strategy workflow is created and no order is generated until it completes human approval.

### Governance and Controls

1. Given a user lacks a required permission or delegated authority, when the user attempts an approval, execution, override, export, integration, or administrative action, then the action is denied server-side and audited.
2. Given a hard constraint fails, then the recommendation cannot be approved for execution until an authorized independent process resolves it; the generative agent cannot close or override the failure.
3. Given a material AI output is displayed, then its source references, confidence/uncertainty, model/version, generated timestamp, and related workflow context are available from the canonical screen.
4. Given a data input is stale, malformed, conflicting, unentitled, or below its configured confidence threshold, then it is flagged or quarantined, not silently corrected or used as verified evidence.
5. Given an auditor searches by trace ID, actor, resource, action, status, or time range, then matching events and their chain of custody are retrievable and export is permission-controlled.
6. Given a generated report or recommendation changes, then the prior version remains retained and its diff, owner/agent, sources, model version, and approval history remain accessible.
7. Given duplicate approval, submission, cancellation, retry, or report requests occur, then exactly one business action is applied while all attempts remain observable.
8. Given an agent or provider fails, then downstream work does not proceed incorrectly; users receive status and failure evidence and an authorized retry, abort, halt, or manual fallback path is available.

### UI Fidelity

1. Every implemented screen matches its corresponding exported `screen.png` and `code.html` structure under `ui/`; no new layout or visual redesign is introduced.
2. Existing navigation, context rails, tables, detail drawers, status treatments, action controls, search/filter surfaces, and density patterns retain their canonical placement and hierarchy.
3. Behavioral requirements such as required rationale or attestation are integrated into the existing interaction surfaces without creating a new page layout.
4. Desktop and laptop behavior follows `ui/onyx_institutional/DESIGN.md`; critical monitoring content stacks responsively at smaller widths without overlap, clipping of essential actions, or loss of keyboard access.
5. Status is conveyed by text or icon in addition to color, all interactive controls have accessible names and focus states, and critical workflows can be completed by keyboard.

## Success Metrics

Initial targets will be baselined during pilot onboarding and measured against the customer's prior workflow.

### Business Outcomes

| Metric | MVP target | Why it matters |
|---|---|---|
| Median analyst time to produce a source-reviewed Market Research Report | At least 40% reduction | Tests the high-value opportunity in search, reading, extraction, and synthesis. |
| Median time from completed research to review-ready recommendation | At least 30% reduction | Measures continuity across fragmented research and portfolio workflows. |
| Median time to assemble evidence for an operational exception | At least 40% reduction | Targets skilled labor spent investigating cross-system residual cases. |
| Manual rekeying steps per workflow | At least 50% reduction | Addresses manual processing and spreadsheet risk. |
| Audit reconstruction time for a sampled investment lifecycle | Under 15 minutes for at least 95% of sampled workflows | Measures decision memory and regulatory evidence quality. |
| Reports delivered on schedule | At least 99% | Measures operational reliability and reporting continuity. |

### Control Outcomes

| Metric | MVP target | Why it matters |
|---|---|---|
| Executions without valid explicit human approval | 0 | Non-negotiable product boundary. |
| Unauthorized or out-of-scope execution attempts successfully completed | 0 | Validates server-side authorization and workflow gates. |
| Material artifacts with complete source/model/version lineage | 100% | Enables substantive review and reproducibility. |
| Material actions linked by workflow and trace ID | 100% | Enables end-to-end auditability. |
| Duplicate orders caused by retry/replay | 0 | Validates idempotency and financial safety. |
| Privileged and approval-role users with MFA | 100% | Supports least privilege and accountable decisions. |
| Critical incidents with tested halt/fallback procedure | 100% | Measures operational resilience. |

### Quality and Adoption

| Metric | MVP target | Why it matters |
|---|---|---|
| Citation validity in sampled generated claims | At least 98% source support; 100% citation presence for material claims | Prevents unsupported generated analysis. |
| Recommendation review completion with source inspection | Baseline and increase through pilot, without reducing review time below governance minimums | Guards against automation bias while measuring usability. |
| Priority-alert precision after human disposition | At least 70% of high-priority alerts judged actionable in pilot | Reduces alert overload without hiding material risk. |
| Monthly active use among licensed pilot users | At least 80% | Indicates workflow value across named professional roles. |
| Core service availability | At least 99.9% monthly | Supports time-sensitive institutional operations. |

## MVP

### In Scope

- Fixed five-stage workflow orchestration with unique workflow and trace IDs
- Market Intelligence Agent with authorized public-market data adapters, sourced synthesis, confidence, and stored Market Research Reports
- Portfolio Strategy Agent with recommendation contents, current-versus-proposed impact, risk/scenario presentation, versioning, and deterministic validation hooks
- Mandatory human approval with approve, reject, modify, rationale, authority, MFA, and immutable decision record
- Trade Execution Agent with one initial broker sandbox/provider adapter, funds and approval validation, order lifecycle, execution logs, cancel and halt controls
- Portfolio Monitoring Agent with holdings, prices, P&L, performance, benchmark, drift, sector allocation, risk alerts, reports, and approved rebalance initiation
- Workflow, executive dashboard, AI agent/job monitoring, Knowledge Center, Audit Trail, Access Control, Integrations, and System Health behavior represented by the canonical Stitch screens
- PostgreSQL persistence, Redis caching/queues as appropriate, FastAPI backend, Next.js/TypeScript/TailwindCSS/shadcn frontend, Docker deployment, and Better Auth or equivalent
- Provider abstractions for market data and brokers
- Role-based access, MFA for privileged/approval roles, encryption, secrets management, audit integrity, observability, backup, and manual fallback
- Desktop-first implementation matching the complete Stitch export

### MVP Constraints

- Public listed equities are the first execution asset class; the data model and provider contracts remain extensible.
- One approved market-data configuration and one broker sandbox integration are sufficient for initial validation; production credentials require separate security and vendor approval.
- Deterministic policy validation may begin with a controlled rule subset agreed with the pilot customer. Ambiguous mandates remain manual and non-executable until resolved.
- Generated client or regulatory communications are out of scope.
- Private assets, autonomous compliance interpretation, autonomous valuation, and autonomous execution are out of scope.

### MVP Exit Criteria

- All end-to-end and governance acceptance criteria pass in a production-like environment.
- Independent security, privacy, model-risk, and control reviews have no unresolved critical findings.
- A broker sandbox test demonstrates approval-gated, idempotent order submission, cancellation, rejection, partial fill, and recovery.
- A sampled workflow can be reconstructed from source evidence through monitoring using exported audit records.
- Backup restore, provider failure, emergency halt, and manual fallback exercises pass.
- Visual and accessibility validation confirms fidelity to the canonical Stitch export at required viewports.

## Future Roadmap

### Phase 2: Institutional Hardening

- Additional market-data, broker, OMS/PMS, custodian, risk, compliance, and accounting adapters
- Entitlement-aware retrieval across customer repositories and licensed research
- Enhanced mandate extraction with compliance approval and deterministic rule testing
- Reconciliation evidence assembly and exception prioritization
- Transaction-cost and broker-quality analysis for best-execution review
- Configurable approval tiers and exception-based escalation within the non-bypassable human-control model
- Expanded model validation, drift monitoring, prompt-injection defenses, and red-team coverage

### Phase 3: Multi-Asset and Operational Depth

- Fixed income, FX, and listed derivatives with asset-specific execution and control models
- Settlement, affirmation, reconciliation, cash, collateral, margin, and corporate-action workflows
- Liquidity and settlement forecasting as decision support, not autonomous control
- Performance, attribution, risk, and exception commentary drafting from reconciled approved data
- Regional calendars, funding cutoffs, and T+1 readiness workflows

### Phase 4: Governed Expansion

- Private-market document extraction, covenant and cash-flow monitoring with committee-controlled valuation workflows
- Cross-portfolio knowledge graph linking theses, decisions, exposures, incidents, and outcomes
- Advanced scenario generation and assumption challenge for portfolio managers
- Federated/private deployment options and jurisdiction-specific retention/residency controls
- Controlled external reporting workflows with compliance review and substantiation

Roadmap prioritization must continue to use reviewability, reversibility, data rights, and consequence as gating criteria (`business-brief.md`, Opportunities for AI Automation).

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Automation bias or ceremonial approval | Reviewers may accept recommendations without meaningful challenge. | Show sources, uncertainty, assumptions, diffs, and risks; require authority and attestation; monitor review behavior and overrides; preserve rejection power and time for review. |
| Hallucinated, stale, or unsupported analysis | Incorrect evidence could influence allocation decisions. | Citation requirements, freshness checks, confidence thresholds, deterministic validation, analyst verification, model testing, and output lineage. |
| Approval bypass or privilege escalation | Unauthorized trades or control overrides could occur. | Server-side workflow gate, least privilege, MFA, separation of duties, immutable events, penetration testing, and zero-tolerance success metric. |
| Licensed data, MNPI, personal data, or confidential data leakage | Legal, regulatory, contractual, and reputational harm. | Entitlement-aware retrieval, classification, approved model endpoints, encryption, information barriers, retention/deletion, DLP, vendor terms, and access auditing. |
| Integration or source-data mismatch | Incorrect positions, prices, allocations, or duplicate records. | Provider contracts, schema/identifier validation, authoritative-source designation, reconciliation state, idempotency, and quarantine rather than silent correction. |
| Broker/API failure or duplicate execution | Financial loss, market impact, or settlement issues. | Connectivity health, idempotency keys, acknowledgement tracking, cancel/halt, retry controls, sandbox certification, and manual fallback. |
| Model or prompt change degrades output | Undetected drift may alter recommendations or evidence quality. | Model inventory, version pinning, independent validation, regression evaluation, canary release, monitoring, and rollback. |
| Alert overload persists or AI suppresses material events | Users may miss consequential risks. | Rank rather than silently suppress; expose reasoning and confidence; tune using dispositions; retain deterministic critical alerts and escalation. |
| Incumbent/vendor lock-in and integration cost | Adoption may stall or economics may deteriorate. | Augmentation positioning, abstract interfaces, phased adapters, exit plans, contractual audit rights, and measurable pilot outcomes. |
| Regulatory variation and changing obligations | A globally uniform control may be insufficient. | Jurisdictional legal review, configurable retention/approval policies, documented use cases, compliance ownership, and release gates. |
| Canonical UI language implies autonomy | Users may misunderstand agent authority. | Enforce bounded behavior in services, training, permissions, audit records, and operating procedures; interpret "autonomous" and "auto-rebalance" only within approved operational boundaries. |
| UI density reduces accessibility or error recognition | Users may overlook evidence or controls. | WCAG 2.2 AA validation, keyboard and screen-reader testing, non-color cues, stable table behavior, responsive critical monitoring, and usability testing with each persona. |
| Business continuity or third-party concentration failure | Critical workflows may become unavailable. | Service/provider health, backups, failover where feasible, tested manual fallback, incident procedures, concentration review, and vendor exit plans. |

## Dependencies

| Dependency | Purpose | Required readiness |
|---|---|---|
| Canonical Stitch export in `ui/` | Defines all layouts, visual hierarchy, controls, states, and interaction surfaces. | Approved and version-controlled; implementation may not redesign it. |
| Market-data and research providers | Supply live market data, fundamentals, news, earnings, ratings, and macro inputs. | Licensing, entitlements, API access, permitted AI use, freshness SLAs, and test environment confirmed. |
| Broker APIs / FIX connectivity | Execute approved orders and return acknowledgements, fills, rejects, and cancellations. | Sandbox certification, credentials, scopes, connectivity, idempotency behavior, and emergency procedures confirmed. |
| Customer OMS/PMS and books of record | Provide approved portfolio context, positions, cash, orders, and authoritative state. | System-of-record ownership, schemas, identifiers, reconciliation rules, and interface contracts agreed. |
| Custodian/accounting/risk/compliance sources | Support monitoring, settlement, reconciliation, risk, and control evidence. | Data ownership, cadence, effective-date rules, and exception handoffs agreed. |
| Identity provider and Better Auth or equivalent | Authentication, MFA, sessions, and enterprise identity integration. | Role mapping, lifecycle provisioning, MFA policy, session controls, and audit integration approved. |
| Approved model provider/runtime | Generate research and recommendation assistance. | Data-use terms, security review, regional deployment, version controls, evaluation results, capacity, and fallback approved. |
| PostgreSQL | Durable workflow, report, approval, transaction, configuration, and audit metadata. | HA, backup, restore, encryption, migration, retention, and capacity plan complete. |
| Redis | Caching, queues, locks, and transient orchestration state where appropriate. | HA/failure behavior, persistence decision, eviction policy, and idempotency design complete. |
| FastAPI services | Modular backend APIs and workflow enforcement. | API contracts, authorization middleware, validation, observability, and deployment standards agreed. |
| Next.js, TypeScript, TailwindCSS, and shadcn/ui | Canonical UI implementation. | Component mapping to Stitch, browser support, accessibility, and visual test strategy agreed. |
| Docker and deployment platform | Repeatable deployment and environment isolation. | CI/CD, image security, secrets, network policy, rollback, monitoring, and recovery approved. |
| Policy, compliance, legal, privacy, security, and model-risk owners | Define decision boundaries, data rights, controls, retention, and release approvals. | Named accountable owners and sign-off criteria established before pilot data or execution access. |
| Pilot customer SMEs | Validate workflows, mandates, role authority, exception handling, and measurable baseline. | Named analyst, PM, trader, operations, risk/compliance, audit, and platform participants available. |

---

This PRD is subordinate to the fixed workflow in `project-context.md` and the canonical interface in `ui/`. Where sample UI copy could imply autonomous investing, the workflow and control requirements in this document govern product behavior without authorizing a visual redesign.
