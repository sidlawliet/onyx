# InvestOps AI Architecture

**Status:** Proposed architecture  
**Date:** August 7, 2026  
**Product:** InvestOps AI  
**Source of truth:** `project-context.md`, `business-brief.md`, `docs/PRD.md`, and the Stitch export under `ui/`

## Architecture Principles

- Preserve the fixed workflow: Market Intelligence -> Portfolio Strategy -> Human Approval -> Trade Execution -> Portfolio Monitoring.
- Keep human investment authority explicit and substantive. Agents may prepare, analyze, prioritize, and monitor; they may not approve, release, or autonomously alter investments.
- Treat existing market-data, OMS/PMS, broker, custodian, risk, compliance, and accounting platforms as systems to augment, not replace.
- Keep deterministic controls outside generative agents.
- Make every material input, output, decision, approval, order, execution event, and monitoring result traceable.
- Prefer a modular monolith for the MVP control plane, with isolated workers where security, throughput, or external-session behavior requires independent runtime boundaries.
- Use PostgreSQL for durable business state, Redis only for reconstructible transient concerns, and versioned object storage for large immutable artifacts.
- Make provider interfaces replaceable without changing core workflow rules.
- Preserve the existing Stitch UI structure, hierarchy, density, and visual language. Architecture supplies behavior behind the existing screens; it does not introduce layouts.

## High Level Architecture

```text
                         +----------------------+
                         |  Next.js Web UI      |
                         |  Existing Stitch UI  |
                         +----------+-----------+
                                    |
                         HTTPS / SSE / WebSocket
                                    |
                         +----------v-----------+
                         | API Gateway / Ingress|
                         | auth, rate limits    |
                         +----------+-----------+
                                    |
                    +---------------v----------------+
                    | FastAPI Control Plane           |
                    | modular domain boundaries       |
                    |                                 |
                    | Identity / Authorization         |
                    | Workflow Orchestration           |
                    | Market Intelligence              |
                    | Portfolio Strategy               |
                    | Approval and Artifact Integrity  |
                    | Policy / Pre-Trade Validation    |
                    | Execution Control                |
                    | Portfolio Monitoring             |
                    | Reports / Knowledge              |
                    | Integrations                     |
                    | Audit / Compliance               |
                    +----+------------+-------------+-+
                         |            |               |
                  PostgreSQL       Outbox          Object Storage
                         |            |               |
                         |     +------v-------+
                         |     | Event Bus     |
                         |     | Redis Streams |
                         |     +--+--+--+--+--+
                         |        |  |  |  |
               +---------v--+ +---v--v+ +v--v----------+ +---------------+
               | Scheduler  | | Market | | Agent/Model | | Report /      |
               | and Recon  | | Data   | | Worker      | | Notification  |
               | Worker     | | Worker | | sandbox     | | Worker        |
               +------------+ +-------+ +-------------+ +---------------+
                                      |
                              +-------v--------+
                              | Broker / FIX   |
                              | Worker         |
                              +-------+--------+
                                      |
                    +-----------------+------------------+
                    | External provider boundary        |
                    | market data | broker | custodian  |
                    | OMS/PMS | risk | identity | email  |
                    +------------------------------------+
```

### Runtime Zones

1. **Presentation zone:** Next.js and the existing Stitch screens. No direct database, Redis, model, or broker access.
2. **Control zone:** FastAPI control plane. Owns authentication integration, authorization, workflow transitions, deterministic validation, approval, artifact eligibility, and API contracts.
3. **Data zone:** PostgreSQL, Redis, object storage, and search projections.
4. **Agent zone:** Sandboxed model and agent workers with allowlisted tools, bounded data scopes, and no financial execution credentials.
5. **Execution zone:** Isolated broker/FIX workers with broker credentials, external session handling, sequence tracking, and reconciliation.
6. **Integration zone:** Market-data, OMS/PMS, broker, custodian, risk, identity, and notification provider adapters.

### Recommended Deployment Shape

The MVP uses one FastAPI control-plane deployment with strict internal modules and one PostgreSQL database. The following components run as separately scaled worker deployments from the start:

- Market-data ingestion and normalization workers
- Broker/FIX execution and reconciliation workers
- Agent/model workers
- Scheduler and monitoring workers
- Report, export, and notification workers

This provides modularity and isolation without prematurely creating a large microservice fleet. A module becomes an independently deployed service only when independent ownership, scaling, availability, security, or release cadence justifies the operational cost.

## Domain and Service Boundaries

### Identity and Authorization

Owns users, service principals, sessions, MFA assurance, roles, permissions, tenant scopes, delegated authority, and data entitlements. It is the only module allowed to evaluate access policy.

It does not own workflow decisions, portfolio data, or broker credentials.

### Workflow Orchestration

Owns workflow instances, stage state, transition guards, retries, deadlines, escalation, correlation IDs, and dispatch of stage work.

It coordinates agents and domain modules but does not generate research, recommendations, approvals, orders, or portfolio metrics.

### Market Intelligence

Owns research requests, source registration, evidence, citations, market-data snapshots, freshness state, and Market Research Report versions.

It can publish a completed, stored report to Portfolio Strategy. It cannot create recommendations, approvals, orders, or positions.

### Portfolio Strategy

Owns recommendation drafts, recommendation versions, allocation lines, assumptions, risk/scenario outputs, model lineage, and submission for deterministic validation.

It cannot approve its own output, change permissions, release orders, or directly mutate portfolio holdings.

### Approval and Artifact Integrity

Owns approval tasks, approver eligibility, attestation, reasons, approval conditions, revocation, supersession, and immutable approved artifacts.

Approval applies to one exact artifact hash. The module does not edit the recommendation; a modification creates a new version and invalidates prior approval.

### Policy and Pre-Trade Validation

Owns deterministic mandate, account, cash, risk, restricted-list, data-freshness, and execution-eligibility checks.

Generative agents can consume results and explain them, but cannot override or close a blocking result.

### Execution Control

Owns execution intents, order plans, parent/child orders, idempotency, cancellation, emergency halt, broker state normalization, and reconciliation state.

It accepts references to approved artifacts only. It never receives a free-form portfolio payload from the UI or an agent.

### Portfolio Monitoring

Owns holdings and valuation projections, drift, P&L, performance, risk alerts, monitoring cycles, reconciliations, and monitoring reports.

It can initiate a new rebalance workflow. It cannot create execution orders directly or modify historical execution state.

### Agent and Model Runtime

Owns agent definitions, model versions, prompt/policy versions, job scheduling, tool allowlists, run inputs/outputs, evaluations, quotas, and model governance evidence.

Agents are untrusted computation workers from the control plane's perspective. They have no database credentials, approval capability, broker credentials, or unrestricted network access.

### Reports and Knowledge

Owns report metadata, report versions, document metadata, tags, effective dates, retention classification, search projections, and authorized object retrieval.

Large files remain in object storage. PostgreSQL stores identity, lineage, access, hash, and retention metadata.

### Integrations and Credentials

Owns provider configuration, environment, capability, credential references, scopes, rotation, health, circuit state, and normalized integration errors.

Credentials are held in a secrets manager and are never returned through ordinary API responses.

### Audit and Compliance

Owns append-only audit events, event integrity, retention/legal hold, audit search projections, and signed export packages.

Business modules remain owners of their transactional aggregates. Audit is the durable evidence layer, not the source of truth for orders or approvals.

## Folder Structure

The structure below is an architectural boundary, not implementation code. It maps the existing UI pages to frontend routes and separates backend domain modules, workers, contracts, and infrastructure.

```text
apps/
  web/
    app/
      workflow/
      intelligence/
      strategy/
      approvals/
      execution/
      monitoring/
      dashboard/
      agents/
      knowledge/
      audit/
      access-control/
      integrations/
      system-health/
    components/
    api-client/
    lib/
  api/
    app/
      api/
      modules/
        identity_access/
        workflow/
        market_intelligence/
        portfolio_strategy/
        approval/
        policy_validation/
        execution/
        portfolio_monitoring/
        agents_models/
        reporting_knowledge/
        integrations/
        audit_compliance/
        notifications/
        system_health/
      events/
      policies/
      security/
      observability/
      db/
  workers/
    market_data/
    broker_fix/
    agent_model/
    scheduler_reconciliation/
    report_notification/
packages/
  contracts/
    openapi/
    asyncapi/
    schemas/
  canonicalization/
  domain_types/
  integration_interfaces/
  observability/
  test_fixtures/
infrastructure/
  docker/
  migrations/
  deployment/
  monitoring/
```

### Dependency Direction

- UI depends on versioned API contracts only.
- API modules depend on domain contracts and repositories, not on UI code.
- Workflow depends on domain command interfaces, not worker implementations.
- Workers depend on event contracts and provider interfaces, not presentation modules.
- Broker adapters depend on execution commands and integration credentials, not strategy generation.
- Agent workers depend on bounded tool interfaces, not direct database or broker access.
- Read models depend on published domain events and snapshots, not transactional cross-module joins at request time.

## Database Design

**Primary database:** PostgreSQL 16 or later.

### Database Principles

- Use UUID or ULID identifiers and UTC `timestamptz` values.
- Every tenant-scoped record carries `tenant_id`, enforced consistently across foreign keys and row-level policies.
- Use `numeric` with explicit precision/scale or integer minor units for money, quantity, price, weights, returns, and risk values. Never use binary floating point for financial records.
- Use JSONB only for provider payloads, model metadata, extensible configuration, and versioned external data. Core query fields remain typed columns.
- Durable state is stored in PostgreSQL. Redis never becomes authoritative for approvals, orders, positions, audit, or workflow state.
- Immutable records are append-only. Corrections create a new version or compensating record.
- Mutable administrative records use optimistic concurrency through a version column or equivalent ETag.
- Financial transitions use database transactions, row locks, and durable outbox records.
- High-volume histories are partitioned by time and, where required, tenant.

### Authority Matrix

| Domain | InvestOps AI responsibility | External authoritative source |
|---|---|---|
| Research evidence | Store source references, retained permitted excerpts, citations, and generated report lineage. | Market-data/research providers and customer repositories. |
| Recommendation | Own generated recommendation version and approval context. | InvestOps AI decision artifact until superseded or rejected. |
| Approval | Own approval decision and artifact lock. | InvestOps AI approval record, subject to customer governance. |
| Orders and fills | Own normalized execution record and trace. | Broker/OMS execution acknowledgements and fills for provider facts. |
| Positions and cash | Reconcile and project for monitoring. | Customer OMS/PMS/custodian source designated per portfolio/account. |
| Market prices | Normalize and retain permitted snapshots. | Provider designated by instrument/data policy. |
| Risk and mandate rules | Store effective policy versions and validation results. | Customer-approved policy and independent risk/compliance systems where integrated. |
| Audit | Preserve complete platform evidence. | InvestOps AI audit record plus customer retention/archive policy. |

### Core Logical Entities

#### Identity and Tenancy

- `tenants`, `tenant_settings`
- `users`, `user_identities`, `service_principals`, `sessions`, `mfa_assurance_events`
- `roles`, `permissions`, `role_permissions`, `user_role_assignments`
- `scopes`, `user_scope_grants`, `data_entitlements`
- `authority_policies`, `authority_policy_versions`, `delegations`

#### Portfolio and Reference Data

- `firms`, `funds`, `portfolios`, `accounts`, `strategies`
- `mandates`, `mandate_versions`, `benchmarks`, `portfolio_benchmarks`
- `instruments`, `instrument_identifiers`, `instrument_classifications`, `provider_instrument_mappings`
- `currencies`, `trading_calendars`, `source_systems`, `source_authority_rules`
- `position_snapshots`, `cash_snapshots`, `price_observations`, `fx_rates`, `portfolio_metric_snapshots`

#### Workflow and Agent Jobs

- `workflows`, `workflow_stages`, `workflow_transitions`, `workflow_stage_attempts`, `workflow_failures`
- `agent_definitions`, `agent_versions`, `agent_jobs`, `agent_job_attempts`, `agent_job_logs`
- `model_providers`, `model_versions`, `prompt_templates`, `prompt_versions`, `model_evaluations`

#### Evidence and Intelligence

- `source_documents`, `source_document_versions`, `source_entitlements`, `source_excerpts`
- `intelligence_requests`, `intelligence_runs`, `research_reports`, `research_report_versions`
- `research_claims`, `claim_citations`, `analyst_verifications`, `data_quality_issues`, `data_quality_dispositions`

#### Strategy, Rules, and Approval

- `recommendations`, `recommendation_versions`, `recommendation_allocations`
- `recommendation_risks`, `recommendation_scenarios`, `recommendation_reasoning_items`
- `policy_rules`, `policy_rule_versions`, `validation_runs`, `validation_results`
- `approval_tasks`, `approval_decisions`, `approval_attestations`, `approval_conditions`, `approval_revocations`
- `artifact_manifests`, `artifact_components`, `artifact_signatures`, `artifact_supersessions`

#### Execution and Post-Trade

- `execution_intents`, `execution_intent_items`, `pretrade_check_runs`
- `order_plans`, `order_plan_items`, `broker_accounts`, `broker_orders`
- `broker_order_events`, `fills`, `cancellations`, `trade_corrections`
- `transactions`, `settlements`, `settlement_status_history`, `execution_reconciliations`
- `execution_control_states`, `emergency_halts`, `broker_sequence_checkpoints`

#### Monitoring and Reporting

- `monitoring_cycles`, `holding_snapshots`, `performance_series`, `risk_metric_snapshots`, `drift_measurements`
- `alerts`, `alert_evidence`, `alert_dispositions`, `alert_escalations`
- `report_definitions`, `report_schedules`, `report_runs`, `report_artifacts`
- `knowledge_documents`, `knowledge_document_versions`, `document_tags`, `document_tag_assignments`
- `retention_policies`, `legal_holds`, `data_deletion_requests`

#### Integrations, Notifications, and Operations

- `integrations`, `integration_environments`, `integration_scopes`, `credential_references`, `credential_rotations`
- `integration_health_samples`, `integration_events`, `rate_limit_states`
- `notification_templates`, `notification_deliveries`, `notification_attempts`, `notification_acknowledgements`, `escalation_policies`
- `service_catalog`, `service_health_samples`, `incidents`, `incident_events`, `diagnostic_runs`

#### Audit and Messaging

- `audit_events`, `audit_event_integrity`, `audit_exports`
- `outbox_events`, `inbox_messages`, `dead_letter_messages`, `idempotency_records`
- `api_request_logs`, `access_events`

### Required Constraints and Indexes

- Foreign keys enforce tenant consistency; cross-tenant references are invalid.
- Approved artifacts are immutable and orders must reference both `approved_artifact_id` and `approved_artifact_hash`.
- An execution request must reference a current approval, valid artifact, passing validations, and an eligible account.
- Unique `(tenant_id, idempotency_key)` prevents duplicate state-changing commands.
- Unique provider message IDs, broker order IDs, and deterministic client order IDs prevent duplicate broker processing.
- Order state transitions are monotonic; terminal financial states cannot revert.
- Audit, market observation, broker event, health sample, log, and monitoring tables use time-based partitions when volume requires it.
- Index `(tenant_id, occurred_at DESC)` for audit; `(workflow_id, created_at)` for lifecycle retrieval; `(portfolio_id, observed_at DESC)` for monitoring; status/assignee/portfolio indexes for UI queues.
- Partial indexes target active approvals, open orders, unresolved alerts, pending outbox events, and unresolved reconciliation breaks.

## PostgreSQL Schema

The following is the logical schema contract. It intentionally avoids implementation SQL. Physical migrations must preserve these ownership and integrity rules.

### `workflows`

| Field | Requirement |
|---|---|
| `id` | Primary workflow identifier. |
| `tenant_id` | Required tenant scope. |
| `portfolio_id` | Target portfolio. |
| `mandate_version_id` | Effective mandate used by the workflow. |
| `stage` | Controlled fixed workflow stage. |
| `status` | Controlled state such as running, awaiting approval, rejected, halted, or completed. |
| `trace_id` | End-to-end correlation identifier. |
| `version` | Optimistic concurrency version. |
| `created_by` / `created_at` | Initiator and time. |
| `updated_at` | Last durable state change. |

### `workflow_transitions`

Append-only history of stage/state changes. Each record includes workflow ID, previous state, new state, actor, command ID, causation ID, reason, validation summary, timestamp, and event hash.

Allowed stage order is strictly:

```text
MARKET_INTELLIGENCE
  -> PORTFOLIO_STRATEGY
  -> HUMAN_APPROVAL
  -> TRADE_EXECUTION
  -> PORTFOLIO_MONITORING
```

### `research_report_versions`

Stores the report version, workflow ID, source snapshot references, claim/citation references, model and prompt versions, confidence summary, report artifact reference, artifact hash, freshness state, analyst verification state, and schema version.

Required report sections are Market Summary, Top Opportunities, Top Risks, Company Analysis, Sector Analysis, Confidence Scores, and Source References.

### `recommendation_versions`

Stores the recommendation version, exact research report version, portfolio/mandate context, allocation artifact, expected return, volatility, diversification analysis, investment horizon, confidence, reasoning, model lineage, risk/scenario references, validation status, and immutable artifact hash.

### `validation_runs` and `validation_results`

Stores rule-set version, input snapshot IDs, calculated time, validator identity, each rule result, severity, blocking state, explanation, freshness, and disposition. Generative output cannot modify a result.

### `approval_tasks` and `approval_decisions`

Stores assigned human approver, required authority, MFA assurance, recommendation version, artifact hash, decision, reason, attestation, conditions, timestamps, expiry, supersession, and revocation information.

Approval is valid only when:

- Actor is a human identity, not an agent or service principal.
- Actor has approval permission for the portfolio/account and action.
- Separation-of-duties policy passes.
- Required validation results are passing.
- Approval references the exact immutable artifact hash.
- Approval has not expired, been revoked, or been superseded.

### `execution_intents`, `order_plans`, and `broker_orders`

`execution_intents` references the approved artifact, approval decision, portfolio/account, broker integration, validation run, and idempotency key. `order_plans` stores the exact approved order quantities and limits. `broker_orders` stores normalized provider state, client order ID, provider order ID, and current state.

No execution record may be created from mutable UI allocation fields. The execution API accepts an approved-artifact reference and derives order quantities from the immutable order plan.

### `audit_events`

Append-only events include tenant, actor, subject, action, resource, workflow/trace IDs, authorization outcome, source/model versions, timestamp, request correlation, before/after hashes where applicable, payload classification, previous event hash, and current event hash.

## API Contracts

**Style:** OpenAPI 3.1 REST for UI and administrative operations; AsyncAPI for events; SSE or WebSocket for live status surfaces.

**Base path:** `/api/v1`.

### Cross-Cutting Contract Rules

- `Authorization` is required on every protected request.
- `X-Correlation-ID` is accepted and propagated through database, event, worker, and provider calls.
- `Idempotency-Key` is required for approvals, workflow commands, execution commands, cancellation, retries, report generation, provisioning, credential rotation, and other state-changing operations.
- `If-Match` or an explicit version is required for mutable drafts and administrative configuration.
- Responses use stable machine-readable error codes with correlation ID, retryability, and field-level validation details.
- Lists use cursor pagination and allowlisted filters/sorts.
- Asynchronous operations return `202 Accepted` with job/resource status URLs.
- `403` covers authorization or entitlement denial; `409` covers stale versions, invalid transitions, artifact mismatch, or duplicate command conflicts; `422` covers deterministic validation failure; `503` covers safe queuing/dependency unavailability.
- Secrets, raw credentials, unentitled source content, and unrestricted model payloads are never returned by normal API responses.

### Workflow and Intelligence

```text
GET  /api/v1/workflows
POST /api/v1/workflows
GET  /api/v1/workflows/{workflow_id}
GET  /api/v1/workflows/{workflow_id}/timeline
POST /api/v1/workflows/{workflow_id}/intelligence-runs
GET  /api/v1/research-reports/{report_id}
GET  /api/v1/research-reports/{report_id}/versions
GET  /api/v1/research-reports/{report_id}/claims
POST /api/v1/research-reports/{report_id}/verify
POST /api/v1/research-reports/{report_id}/deep-dive
GET  /api/v1/evidence/{evidence_id}
```

### Strategy and Approval

```text
POST /api/v1/workflows/{workflow_id}/recommendations
GET  /api/v1/recommendations/{recommendation_id}
GET  /api/v1/recommendations/{recommendation_id}/versions
GET  /api/v1/recommendations/{recommendation_id}/diff
POST /api/v1/recommendations/{recommendation_id}/revisions
POST /api/v1/recommendations/{recommendation_id}/validate
GET  /api/v1/recommendations/{recommendation_id}/validations
POST /api/v1/recommendations/{recommendation_id}/submit-for-approval
GET  /api/v1/approval-tasks
GET  /api/v1/approval-tasks/{task_id}
POST /api/v1/approval-tasks/{task_id}/approve
POST /api/v1/approval-tasks/{task_id}/reject
POST /api/v1/approval-tasks/{task_id}/modify
POST /api/v1/approvals/{approval_id}/revoke
```

Approval request bodies contain the expected recommendation version, artifact hash, reason where required, attestation, and client idempotency key. The server ignores client-supplied allocation contents for approval eligibility and reloads the canonical artifact.

### Execution

```text
POST /api/v1/execution-intents
GET  /api/v1/execution-intents/{execution_intent_id}
GET  /api/v1/execution-intents/{execution_intent_id}/orders
GET  /api/v1/orders
GET  /api/v1/orders/{order_id}
POST /api/v1/orders/{order_id}/cancel
POST /api/v1/execution-control/cancel-all
POST /api/v1/execution-control/emergency-halt
POST /api/v1/execution-control/resume
GET  /api/v1/execution-intents/{execution_intent_id}/events
```

The execution endpoint accepts only `approved_artifact_id`, `approved_artifact_hash`, and account/broker scope. It rejects free-form allocations. Before enqueueing, the control plane verifies approval status, artifact hash, validation results, authority, expiry, freshness, and emergency-halt state.

### Monitoring, Reports, Governance, and Operations

```text
GET  /api/v1/portfolios/{portfolio_id}/summary
GET  /api/v1/portfolios/{portfolio_id}/performance
GET  /api/v1/portfolios/{portfolio_id}/holdings
GET  /api/v1/portfolios/{portfolio_id}/alerts
POST /api/v1/alerts/{alert_id}/dispositions
POST /api/v1/portfolios/{portfolio_id}/rebalance-workflows
POST /api/v1/reports
GET  /api/v1/reports/{report_id}
GET  /api/v1/reports/{report_id}/download
GET  /api/v1/audit-events
GET  /api/v1/audit-events/{event_id}
POST /api/v1/audit-exports
GET  /api/v1/agents
POST /api/v1/agent-runs
GET  /api/v1/agent-runs/{run_id}
POST /api/v1/agent-runs/{run_id}/abort
GET  /api/v1/users
POST /api/v1/users
GET  /api/v1/roles/{role_id}/effective-permissions
PATCH /api/v1/roles/{role_id}
GET  /api/v1/integrations
POST /api/v1/integrations
POST /api/v1/integrations/{integration_id}/test
POST /api/v1/integrations/{integration_id}/rotate-credentials
GET  /api/v1/system-health
POST /api/v1/system-health/diagnostics
```

### Live Updates

Use SSE or WebSocket channels for the existing live execution, agent-console, workflow, notification, and system-health surfaces. Channels must enforce authorization at connection and subscription time, carry event IDs, support reconnect cursors, preserve per-resource ordering, and expose stale/disconnected state.

## Event Bus

Use a transactional PostgreSQL outbox as the publication boundary and Redis Streams for MVP worker transport. The event contract remains transport-neutral so the bus can move to Kafka or a managed equivalent if volume requires it.

### Event Envelope

```text
event_id
event_type
event_version
schema_version
occurred_at
tenant_id
aggregate_type
aggregate_id
workflow_id
trace_id
correlation_id
causation_id
actor_type
actor_id
payload_hash
payload
```

### Topics

```text
workflow.stage-transitioned.v1
intelligence.report-completed.v1
intelligence.source-entitlement-denied.v1
strategy.recommendation-published.v1
artifact.created.v1
approval.requested.v1
approval.approved.v1
approval.rejected.v1
approval.invalidated.v1
execution.intent-created.v1
execution.pretrade-failed.v1
order.submission-requested.v1
order.accepted.v1
order.rejected.v1
order.fill-received.v1
order.reconciliation-required.v1
portfolio.monitoring-completed.v1
portfolio.breach-detected.v1
report.generated.v1
notification.delivery-failed.v1
integration.health-changed.v1
audit.event-recorded.v1
```

### Delivery Semantics

- At-least-once delivery; all consumers are idempotent.
- Ordering is guaranteed per aggregate key for workflows, approvals, executions, orders, and portfolios. There is no global ordering requirement.
- Events are published only after the owning PostgreSQL transaction commits.
- Consumers record `event_id` in `inbox_messages` before applying a business effect.
- Retry with exponential backoff and jitter; dead-letter after a bounded number of attempts.
- Replays may rebuild read models and audit projections but may not re-submit broker commands.
- Poison events are quarantined with operator-visible reason and full lineage.

## Agent Communication

Agents communicate through control-plane commands and versioned events. They do not call each other directly, access PostgreSQL directly, or call external market/broker providers directly.

### Agent Run Contract

Each job records:

- Agent ID and immutable agent version
- Model provider and model version
- Prompt/template/policy version
- Requesting human or service principal
- Tenant, workflow, portfolio, and data scope
- Input artifact IDs and hashes
- Entitlements and permitted tools
- Token, time, cost, and concurrency budget
- Output schema and risk classification
- Human-review requirement
- Output artifact and provenance references

### Agent Permissions

- Read-only by default.
- Tool access is allowlisted and mediated by a tool gateway.
- Market Intelligence may retrieve authorized sources and write research artifacts.
- Portfolio Strategy may read a completed research report and write recommendation drafts.
- Trade Execution may read an approved artifact through a narrow execution command, but cannot research, generate recommendations, change allocations, or approve.
- Portfolio Monitoring may read reconciled portfolio data and write alerts/reports; rebalance creates a new strategy workflow only.
- No agent can approve, release an order, override a hard limit, close a compliance breach, alter audit records, or access broker credentials.
- Retrieved documents are untrusted input; prompt injection, arbitrary tool invocation, and data exfiltration controls apply.

## Redis

Redis is transient infrastructure, not a system of record.

### Allowed Uses

- Short-lived cache for read-heavy, non-authoritative data.
- Rate-limit counters and provider throttling state.
- Redis Streams for worker wake-up and queue transport.
- Short-lived distributed locks with lease expiry and fencing tokens.
- Session/cache support when required by Better Auth configuration.
- Short-lived idempotency response cache, backed by durable PostgreSQL idempotency records.
- UI hint pub/sub where missing a message is safe.

### Prohibited Uses

- Approval, order, fill, position, cash, risk-limit, audit, or workflow authority.
- Durable report, source, or artifact storage.
- Permanent event history.
- Authorization decisions without database-backed policy evaluation.
- Sole storage of broker commands.

If Redis is unavailable, financial correctness remains intact. Queued work may pause or fall back to a durable recovery path; approvals and execution fail closed rather than using stale cache state.

## Authentication and Authorization

### Authentication

- OIDC-compatible enterprise identity provider integrated through Better Auth or equivalent.
- Secure HTTP-only, same-site sessions or short-lived access tokens with rotation and revocation.
- MFA required for approval, execution control, access administration, integration administration, and emergency halt/resume.
- Service-to-service mTLS or workload identity.
- Separate human and service principal identities; services cannot impersonate approvers.
- Session assurance level is recorded with approval and execution commands.

### Authorization

Use RBAC plus scoped ABAC. Scope dimensions are tenant, firm/desk, portfolio, account, instrument class, data provider, environment, and action.

Separate permissions include:

```text
strategy:create
strategy:publish
approval:decide
execution:prepare
execution:release
execution:cancel
execution:emergency-halt
limits:manage
audit:read
audit:export
access-control:manage
integrations:manage
```

Maker-checker policy prevents a proposal author from approving their own proposal unless an explicit customer policy permits it. Agents and service principals can never approve. Resource-level authorization is evaluated for every read, write, export, model invocation, and provider request.

### Tenant and Entitlement Propagation

Tenant and entitlement context must propagate through PostgreSQL, Redis keys, queues, object storage, search indexes, logs, traces, model requests, and provider adapters. Authorization is checked at ingestion, retrieval, model input construction, report access, export, deletion, and execution.

## Report Storage

Use S3-compatible object storage with versioning, encryption, retention lock, lifecycle policies, and customer-managed encryption keys where required.

### Stored Artifact Classes

- Raw permitted market-data payloads
- Source documents and document versions
- Market Research Reports
- Portfolio Recommendation Reports
- Immutable approved artifacts and signatures
- Execution evidence and broker responses
- Portfolio monitoring and periodic reports
- Audit exports

PostgreSQL stores metadata, ownership, classification, source lineage, artifact hash, object version ID, retention class, and access policy. Objects are never overwritten. Downloads use short-lived signed URLs after authorization and entitlement checks.

Every generated report records report ID, schema version, workflow/stage, input artifact IDs, source and snapshot references, model/agent provenance, calculation version, generated timestamp, artifact hash, classification, and retention policy.

## Market Data Layer

### Adapter Responsibilities

- Provider authentication and credential isolation.
- Live and historical market data, fundamentals, news, earnings, ratings, and macro indicators.
- Vendor-to-internal instrument mapping.
- Entitlement checks and purpose restrictions.
- Normalization of identifiers, units, currencies, timestamps, and time zones.
- Payload hashing and permitted retention.
- Freshness and quality checks for missing, stale, duplicate, conflicting, and outlier data.
- Provider health, rate limits, circuit breakers, and fallback.

### Data States

```text
FRESH | STALE | DEGRADED | CONFLICTING | UNAVAILABLE | UNENTITLED
```

Research may display degraded or conflicting data with explicit flags. Strategy and execution controls reject data that is stale or unentitled under the effective policy. Conflicting provider values are preserved and surfaced; they are not silently averaged for execution-critical decisions.

The market-data worker cannot create orders, approvals, or portfolio positions.

## Broker Layer

### Adapter Responsibilities

- Broker account and instrument capability discovery.
- Order submission, cancel, replace, status query, fills, positions, cash, and settlement updates.
- FIX session lifecycle and sequence state where applicable.
- Provider-specific request/response normalization.
- Client-order-ID support detection.
- Rate limits, throttling, timeouts, circuit breakers, and reconnect behavior.
- Drop-copy and reconciliation processing.

### Execution Safety

The broker worker receives only a signed execution command containing the immutable approved artifact hash and exact order-plan references. It cannot invent quantities or alter portfolio intent.

Unknown or ambiguous broker state becomes `RECONCILIATION_REQUIRED`. The worker queries provider state by deterministic client order ID before retrying. A timeout never authorizes blind duplicate submission.

### Idempotency

Each state-changing API request requires an `Idempotency-Key`. Each order has a deterministic client order ID derived from tenant, broker account, approved artifact hash, order-plan item, and order version. PostgreSQL uniqueness constraints, durable inbox records, and broker-side status reconciliation prevent duplicate orders.

Cancel/replace creates a new authorized command and order version; it does not mutate the original order plan.

## Notification Layer

The notification worker supports in-app notifications, email, approved messaging providers, and scoped webhooks.

- Templates are versioned.
- Recipient resolution uses scoped escalation policies.
- Sensitive content is minimized; links require authentication.
- Delivery is asynchronous, retryable, rate-limited, and deduplicated.
- Critical review tasks, failures, alerts, and incidents support acknowledgment and escalation timers.
- Notification failure never changes workflow, approval, or execution state.
- Delivery attempts and final outcomes are audited.

## Audit Layer

Audit is mandatory for authentication, authorization, data access, source retrieval, entitlement decisions, agent runs, tool calls, model/prompt versions, strategy creation, approval actions, artifact creation/signing/invalidation, validation, broker requests/responses, fills, cancellations, monitoring breaches, configuration changes, exports, failures, and emergency controls.

### Audit Event Fields

```text
event_id
tenant_id
actor_type / actor_id
subject_type / subject_id
action
resource_type / resource_id
workflow_id / trace_id
correlation_id / causation_id
authorization_outcome
occurred_at / received_at
model_version / policy_version where applicable
before_hash / after_hash where applicable
classification
previous_event_hash / event_hash
payload_reference
```

Events are append-only, time-synchronized in UTC, hash chained per tenant/partition, and exported to immutable object storage. Application administrators cannot update or delete audit events. Retention, legal hold, archive, deletion, and export policies are configurable by record class and jurisdiction.

## Immutable Approval and Workflow Enforcement

### Approved Artifact

The canonical approved artifact is a deterministic, signed manifest containing:

- Tenant, workflow, portfolio, and account IDs.
- Exact recommendation version and allocation lines.
- Exact order plan and quantities.
- Mandate, policy, rule-set, and risk-check versions.
- Market-data snapshot IDs and freshness state.
- Model, agent, prompt, and calculation versions.
- Schema version, creation time, expiry time, and SHA-256 content hash.

### Enforcement Sequence

1. Portfolio Strategy creates a recommendation version.
2. Deterministic validation evaluates the candidate against effective policy and data freshness.
3. Canonicalization produces immutable artifact bytes and a hash.
4. Artifact manifest and components are stored in PostgreSQL and versioned object storage.
5. A qualified human approves the exact artifact hash with MFA/session assurance, reason/attestation, and authority scope.
6. Any change to allocations, order plan, sources, model, prompt, policy, constraints, or required freshness invalidates the prior approval and creates a new artifact.
7. Execution accepts only `approved_artifact_id` and `approved_artifact_hash`.
8. Control plane reloads and rehashes the artifact, verifies approval, expiry, revocation, tenant, authority, and validation state.
9. Broker worker revalidates the signed command before submission.
10. Mismatch, stale state, unknown state, or failed hard check blocks execution and creates an audit event.

The execution API must never accept free-form allocations from the UI, strategy agent, monitoring agent, or broker worker.

## Event Bus and Agent Handoff

### Event Envelope

```text
event_id
event_type
event_version
schema_version
occurred_at
tenant_id
aggregate_type / aggregate_id
workflow_id / trace_id
correlation_id / causation_id
actor_type / actor_id
payload_hash
payload
```

### Core Events

```text
workflow.stage-transitioned.v1
intelligence.report-completed.v1
intelligence.source-entitlement-denied.v1
strategy.recommendation-published.v1
artifact.created.v1
approval.requested.v1
approval.approved.v1
approval.rejected.v1
approval.invalidated.v1
execution.intent-created.v1
execution.pretrade-failed.v1
order.submission-requested.v1
order.accepted.v1
order.rejected.v1
order.fill-received.v1
order.reconciliation-required.v1
portfolio.monitoring-completed.v1
portfolio.breach-detected.v1
report.generated.v1
notification.delivery-failed.v1
integration.health-changed.v1
audit.event-recorded.v1
```

### Delivery Semantics

- At-least-once delivery.
- Idempotent consumers required for every topic.
- Ordering guaranteed per aggregate key, not globally.
- PostgreSQL outbox publishes only after the owning transaction commits.
- Consumer inbox records prevent duplicate business effects.
- Exponential backoff with jitter and bounded retries.
- Dead-letter queues for poison messages.
- Replay may rebuild projections but may never re-submit a broker command.

### Required Handoffs

- `intelligence.report-completed.v1` contains the exact stored Market Research Report version and artifact hash. Portfolio Strategy consumes that immutable reference.
- `strategy.recommendation-published.v1` creates a validation/approval task; it does not create an execution intent.
- `approval.approved.v1` contains the exact approved artifact reference and hash. Execution can consume it only after server-side revalidation.
- `portfolio.breach-detected.v1` creates an alert/disposition task. Corrective allocations create a new strategy workflow.

## Authentication and Authorization

### Authentication

- OIDC-compatible enterprise identity provider through Better Auth or equivalent.
- Secure HTTP-only, same-site sessions or short-lived access tokens with rotation and revocation.
- MFA required for approval, execution control, access administration, integration administration, and emergency halt/resume.
- Service-to-service mTLS or workload identity.
- Human and service identities are distinct; service principals cannot impersonate approvers.
- Approval and execution commands record session assurance level.

### Authorization Model

RBAC plus scoped ABAC. Scopes cover tenant, firm/desk, portfolio, account, instrument class, data provider, environment, and action.

Separate permissions include:

```text
strategy:create
strategy:publish
approval:decide
execution:prepare
execution:release
execution:cancel
execution:emergency-halt
limits:manage
audit:read
audit:export
access-control:manage
integrations:manage
```

Maker-checker policy prevents a proposal author from approving their own proposal unless explicitly allowed by customer policy. Agents and service principals can never approve. Resource authorization is evaluated for every read, write, export, model invocation, and provider request.

## Deployment

### Environments

- Local: Docker Compose with provider mocks and synthetic market/broker data.
- Test: isolated PostgreSQL, Redis, object storage, model sandbox, provider simulators, and deterministic fixtures.
- Staging: production-like topology with broker sandbox and non-production credentials.
- Production: isolated tenant/customer deployment or controlled multi-tenant deployment according to the approved tenancy model.

### Production Components

- Next.js web application behind an ingress/CDN.
- FastAPI control-plane replicas behind an API gateway.
- Market-data worker deployment.
- Broker/FIX worker deployment on a restricted network segment.
- Agent/model worker deployment in a sandboxed network segment.
- Scheduler/reconciliation worker deployment.
- Report/notification/export worker deployment.
- Highly available PostgreSQL with point-in-time recovery, encrypted backups, and read replicas where required.
- Redis replication/failover for queues and transient state.
- Versioned encrypted object storage with retention lock.
- Centralized logs, metrics, traces, alerting, and secrets manager.

### Recovery Targets

- Initial target RPO: 5 minutes for transactional data.
- Initial target RTO: 30 minutes for the control plane.
- Broker submission resumes only after provider reconciliation and execution-control review following recovery.
- No execution proceeds on uncertain approval, broker, market-data, or database state.

## Security

- TLS 1.2+ externally and mTLS/workload identity internally.
- Encryption at rest for PostgreSQL, Redis, object storage, and backups.
- Secrets in a managed vault; no secrets in source, images, environment manifests, logs, or normal API responses.
- Broker credentials accessible only to broker workers; model credentials only to agent workers.
- Network policies deny UI-to-database, UI-to-broker, and agent-to-broker access.
- Deny-by-default model tools and outbound network destinations.
- Validate inputs, encode outputs, protect against SSRF, limit request/file sizes, and scan uploaded/retrieved documents.
- Treat external documents as untrusted prompt-injection content.
- Apply entitlement checks before source retrieval, model input construction, report access, and export.
- Redact credentials, tokens, personal data, and sensitive financial payloads from logs and traces.
- Enforce row-level or equivalent tenant isolation in every persistence and search layer.
- Require step-up MFA and dual control for approval, emergency halt/resume, permission changes, credential rotation, and broad exports.
- Audit denied sensitive requests as well as successful material actions.
- Pin and scan dependencies/images, generate SBOMs, sign deployment artifacts, and validate build provenance.
- Maintain a model inventory, model/prompt versions, evaluation evidence, rollback path, drift monitoring, and documented prohibited uses.

## Scalability and Reliability

### Workload Model Required Before Production Sizing

Define MVP and three-year estimates for tenants, users, concurrent sessions, portfolios, accounts, holdings, instruments, market observations, research documents, model jobs/tokens, recommendations, approvals, orders, fills, audit events, reports, and retention duration.

### Scaling Strategy

- Stateless API replicas.
- Independent worker autoscaling by queue depth and workload class.
- Separate queues for market data, model jobs, broker execution, monitoring, and reports.
- Priority and concurrency limits that protect broker and approval controls.
- PostgreSQL connection pooling, read replicas, projections, and time/tenant partitioning for high-volume histories.
- Object storage for large documents, reports, broker responses, and exports.
- Entitlement-aware search index/read projection rather than unbounded transactional scans.
- Batch market-data ingestion and incremental monitoring calculations.
- Provider-specific throttling, timeouts, circuit breakers, and bulkheads.
- Per-tenant quotas for model usage, exports, data-provider calls, and worker concurrency.

### Failure Behavior

- Workflow and approval state remain durable during queue or worker restarts.
- Approval, policy validation, and execution fail closed when required dependencies are unavailable or stale.
- Portfolio screens may become read-only with freshness status during upstream outages.
- Broker ambiguity becomes reconciliation-required, never blind retry.
- Dead-letter queues and replay tools are operator-controlled and audited.
- Redis failure pauses or reroutes transient work but cannot corrupt financial correctness.
- PostgreSQL restore requires event/outbox reconciliation before financial commands resume.

### Observability

OpenTelemetry traces propagate through:

```text
UI -> API -> PostgreSQL/outbox -> event bus -> worker -> provider/broker -> audit
```

Track API latency, workflow stage duration, approval queue age, artifact mismatches, pre-trade rejection, broker acknowledgment latency, unknown broker states, reconciliation lag, market-data freshness, agent success/cost, queue lag, DLQ volume, notification delivery, database health, backup status, and audit integrity.

Initial objectives:

- Control-plane availability: 99.9%.
- Read API P95: under 200 ms excluding report generation.
- Command acceptance P95: under 500 ms when dependencies are healthy.
- Audit durable-write success: 99.99%.
- Zero duplicate broker orders caused by platform retries.
- 100% detection of approved-artifact mismatch.

## Report and UI Mapping

The architecture backs the existing UI without redesign:

| Existing UI export | Architectural backing |
|---|---|
| `onyx_workflow_engine_refined` | Workflow queries, stage transitions, task assignment, retries, and timeline read model. |
| `onyx_market_intelligence_refined` | Market-data snapshots, intelligence jobs, reports, citations, confidence, freshness, and evidence APIs. |
| `onyx_decision_workspace_refined` | Recommendation versions, artifact manifests, validation results, approval task/context, compare, approve, modify, and reject commands. |
| `onyx_trade_execution_refined` | Execution intents, pre-trade checks, queue, broker health, order/fill state, cancel/halt controls, and live execution events. |
| `onyx_portfolio_monitoring_refined` | Portfolio read models, holdings/drift, performance, alerts, activity, reports, and rebalance workflow creation. |
| `onyx_executive_dashboard_refined` | Read-only executive projections for pipeline, performance, active operations, risk, and recent activity. |
| `onyx_ai_agents_workspace_refined` | Agent registry, job queue, sandbox logs, model/prompt provenance, export, and abort commands. |
| `onyx_knowledge_center_refined` | Document/report metadata, collections, versioning, search, entitlements, and object-storage retrieval. |
| `onyx_audit_trail_refined` | Audit search, event detail, chain of custody, integrity status, and export jobs. |
| `onyx_access_control_refined` | User directory, roles, MFA state, scoped permissions, delegation, and effective-policy views. |
| `onyx_integrations_refined` | Provider configuration, health, credential references, scopes, rotation, tests, and event stream. |
| `onyx_system_health_refined` | Service/provider health, topology, alerts, diagnostics, incidents, and operational report export. |

Behavioral constraints behind existing controls:

- `Approve Allocation`, `Modify`, and `Reject` require authority, version checks, rationale/attestation where required, and audit events.
- Execution `Modify` cannot mutate approved allocation; it must return through strategy validation and human approval.
- Monitoring `Rebalance` creates a new recommendation workflow and never an order.
- `Emergency Halt` and `Cancel All` are scoped, authorized, idempotent, and audited.
- "Autonomous agents" is status copy only; agent permissions remain bounded.
- "Auto-Rebalance Executed" is valid only when linked to a prior approved trace and execution record.

The navigation, fixed 240px desktop navigation, 8px grid, dense tables, 32px/40px row modes, right-side drawers, tonal surfaces, blue primary interaction state, and semantic status pips are defined by `ui/onyx_institutional/DESIGN.md` and remain unchanged.

## Workflow State Machine

```text
DRAFT
  -> INTELLIGENCE_RUNNING
  -> INTELLIGENCE_COMPLETE
  -> STRATEGY_RUNNING
  -> STRATEGY_READY
  -> PENDING_HUMAN_APPROVAL
  -> APPROVED
  -> EXECUTION_PRECHECK
  -> EXECUTION_SUBMITTED
  -> PARTIALLY_EXECUTED
  -> EXECUTED
  -> MONITORING
  -> COMPLETED
```

Failure/terminal branches:

```text
INTELLIGENCE_RUNNING -> RECONCILIATION_REQUIRED
STRATEGY_RUNNING -> RECONCILIATION_REQUIRED
PENDING_HUMAN_APPROVAL -> REJECTED | EXPIRED
APPROVED -> EXPIRED | CANCELLED
EXECUTION_PRECHECK -> RECONCILIATION_REQUIRED
EXECUTION_SUBMITTED -> RECONCILIATION_REQUIRED
PARTIALLY_EXECUTED -> RECONCILIATION_REQUIRED
MONITORING -> RECONCILIATION_REQUIRED
```

### Non-Negotiable Invariants

1. No execution without current explicit human approval.
2. Approval binds to one immutable artifact hash.
3. Any material artifact change invalidates approval.
4. Agents and service principals cannot approve or release trades.
5. Execution cannot proceed with stale, unentitled, or conflicting required data.
6. Every order maps to an approved order-plan item.
7. Broker submissions are idempotent or reconciled before retry.
8. Terminal financial states are append-only and immutable.
9. Audit records cannot be updated or deleted through application APIs.
10. Monitoring cannot modify historical executions or approved artifacts.
11. Notification failure cannot trigger or duplicate financial action.
12. Every cross-module command carries tenant, actor, workflow, trace, correlation, and causation context.

## Architecture Decision Summary

- **Pattern:** Modular monolith control plane plus isolated workers.
- **Backend:** FastAPI with explicit domain modules and versioned contracts.
- **Frontend:** Existing Next.js/TypeScript/TailwindCSS/shadcn Stitch implementation; no redesign.
- **Durable state:** PostgreSQL.
- **Transient queues/cache:** Redis Streams and Redis cache with PostgreSQL authority.
- **Artifacts:** Versioned encrypted object storage with PostgreSQL metadata.
- **Events:** Transactional outbox, at-least-once delivery, idempotent consumers.
- **Auth:** Better Auth or OIDC-compatible provider, MFA, RBAC plus scoped ABAC.
- **Market data:** Isolated provider adapters with entitlement and freshness enforcement.
- **Broker:** Isolated broker/FIX worker with signed approved-artifact commands, deterministic client IDs, and reconciliation before ambiguous retry.
- **Audit:** Append-only, hash-chained, retained, exportable evidence layer.
- **Workflow:** Server-side state machine; approval is a hard execution precondition.
