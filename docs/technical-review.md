# InvestOps AI Technical Architecture Review

**Review date:** August 7, 2026  
**Reviewer:** Tech Lead, The Agency  
**Verdict:** Conditional approval for contract/proof-of-control work; not production-ready

## Review Scope

Reviewed `project-context.md`, `business-brief.md`, `docs/PRD.md`, `docs/architecture.md`, and the complete Stitch export under `ui/`.

The architecture is now present and provides a credible baseline: modular FastAPI control plane, isolated market-data/broker/agent/report workers, PostgreSQL authority, Redis Streams transport, versioned object storage, tenant-scoped authorization, immutable approval artifacts, and idempotent broker execution. No implementation code exists to verify runtime behavior.

## Executive Assessment

| Area | Verdict | Assessment |
|---|---|---|
| PRD completeness | PASS WITH CLARIFICATIONS | The PRD covers the five-stage lifecycle, governance, personas, acceptance criteria, UI traceability, MVP, and nonfunctional goals. Tenant deployment, approval delegation, authority matrices, freshness policy, report schemas, workload volumes, and post-trade MVP scope need decisions. |
| Database completeness | PARTIAL PASS | The logical schema is broad and includes workflow, approval, execution, monitoring, audit, integration, and messaging entities. Physical schema rules, effective-dated policy data, provider synchronization, read-model metadata, key metadata, and several operations tables remain underspecified. |
| API coverage | PARTIAL PASS | Core lifecycle APIs and cross-cutting rules are present. Cmd+K search, notification acknowledgment, workflow recovery, detailed admin/configuration, provider callbacks, dashboard export/share, diagnostics status, and some UI actions lack explicit contracts. |
| Service boundaries | PASS WITH CLARIFICATIONS | Domain ownership and dependency direction are strong. The modular monolith plus isolated workers is appropriate for MVP. Policy authority, provider reconciliation, search, projection ownership, and external-system synchronization need explicit owners. |
| Security | PASS WITH HIGH-RISK GAPS | Approval hashing, scoped ABAC, MFA, worker isolation, entitlement propagation, audit chaining, and prompt-injection controls are addressed. KMS/HSM lifecycle, tenant-isolation enforcement, break-glass, provider callback verification, and threat-model evidence remain incomplete. |
| Scalability | PASS WITH SIZING GAPS | Queue separation, worker scaling, projections, partitioning, read replicas, quotas, backpressure, RPO/RTO, and observability are covered. No quantitative workload model, Redis Streams recovery design, search sizing, or load-test evidence exists. |
| UI consistency | PASS WITH BEHAVIORAL GAPS | Refined Stitch screens are mapped and visual rules are preserved. Several visible controls lack explicit API mappings, and refined/non-refined duplicate exports create canonical-source risk. |
| Workflow preservation | PASS IN DESIGN; NOT VERIFIED IN RUNTIME | The state machine and invariants preserve the five stages and forbid autonomous execution. Runtime, race, replay, authorization, and broker-sandbox evidence is absent. |

## Critical Findings

### F-01: Contract artifacts are not present

The architecture names OpenAPI 3.1 and AsyncAPI but provides endpoint outlines and event names rather than request/response schemas, authorization scopes, transition payloads, error codes, compatibility rules, or provider callback schemas.

**Severity:** High. **Action:** Publish versioned OpenAPI and AsyncAPI artifacts before parallel implementation.

### F-02: Tenant and deployment model is undecided

The architecture permits dedicated or controlled multi-tenant production but does not choose an MVP model or define the enforcement boundary across PostgreSQL, Redis, object storage, search, queues, logs, support access, and backups.

**Severity:** High. **Action:** Select dedicated deployment, shared database with enforced RLS, or database-per-tenant and document the testable isolation guarantee.

### F-03: Delegated approval policy is not operationally specified

Authority policies and delegation are named, but thresholds, quorum, exception escalation, precedence, conditions, expiry, and revocation races are not defined.

**Severity:** High. **Action:** Define an effective-dated authority decision table covering portfolio/account, amount, concentration, instrument, exception class, maker-checker, delegation, and emergency controls.

### F-04: Artifact signing and key lifecycle are incomplete

The architecture requires signed manifests, SHA-256 hashes, customer-managed encryption keys, retention lock, and audit hash chains, but does not define signing algorithm, KMS/HSM ownership, rotation, revocation, verification, or compromise recovery.

**Severity:** High. **Action:** Define key hierarchy, key versions, signing policy, rotation/revocation, dual control, archival verification, and break-glass procedures.

### F-05: Provider callbacks and external synchronization are underspecified

Broker/FIX, drop-copy, fills, positions, cash, settlement, and reconciliation are named without callback authentication, sequence-gap handling, payload schemas, OMS/PMS/custodian synchronization, or source conflict rules.

**Severity:** High. **Action:** Define signed callback/FIX contracts, sequence checkpoints, replay/gap recovery, deduplication, source authority, and reconciliation disposition states.

### F-06: UI action coverage is incomplete

Page-level mapping exists, but explicit contracts are missing for Cmd+K commands, notification acknowledgment, workflow retry/halt/resume, audit deep search/export, executive PDF export/share, Knowledge Center add, integration save/disable/retry, user suspend/provision, role reset/save, and diagnostics status.

**Severity:** Medium-High. **Action:** Create a UI action matrix mapping every control to API, permission, transition, idempotency, audit event, loading state, error state, and stale-data behavior.

### F-07: Search architecture is not defined

The UI contains searches for markets, commands, agents, pipelines, orders, audits, users, resources, systems, companies, reports, and portfolios. An entitlement-aware projection is mentioned but engine, index ownership, freshness, deletion, legal hold, query limits, and command authorization are not specified.

**Severity:** Medium-High. **Action:** Define a tenant/entitlement-aware search service and command gateway.

### F-08: Projection ownership and freshness are unclear

The architecture correctly avoids synchronous dashboard fan-out, but does not assign ownership of workflow, executive, monitoring, audit, and health read models or define rebuild, lag, consistency, and stale-display behavior.

**Severity:** Medium. **Action:** Define projection source events, owner, checkpoint, rebuild/replay, lag metric, freshness SLA, and UI response metadata.

### F-09: Physical PostgreSQL strategy is incomplete

Logical entities and indexes are listed, but RLS deployment, migration ownership, partition lifecycle, transaction isolation, connection budgets, retention/archive jobs, autovacuum, and online migration policy are absent.

**Severity:** Medium-High. **Action:** Add a physical PostgreSQL decision record and production migration/partition plan.

### F-10: Redis Streams recovery is underspecified

At-least-once delivery, outbox/inbox, retries, and DLQ are present, but consumer-group recovery, pending-entry reclamation, stream retention, failover, message sizing, and outbox republish behavior are not defined.

**Severity:** Medium. **Action:** Define stream/group/consumer policies, pending recovery, retention, backpressure, DLQ ownership, and Redis outage behavior.

### F-11: Model governance and cost enforcement need contracts

Model/prompt versions, tool allowlists, budgets, sandboxing, and governance evidence are included, but release states, evaluation thresholds, data-use policy results, cost accounting, fallback models, and output quarantine are not defined.

**Severity:** Medium-High. **Action:** Define model registry lifecycle, release gates, per-tenant budgets, fallback/rollback, and output validation/quarantine.

### F-12: Post-trade coverage is thinner than the institutional workflow

Transactions, settlements, reconciliation, positions, cash, and broker events exist, but allocation/affirmation, standing settlement instructions, accounting/performance handoff, transaction-cost evidence, and corporate actions are not detailed.

**Severity:** Medium. **Action:** Confirm these as MVP scope or explicitly define the external handoff boundary and deferred roadmap.

## Missing Services

These are required capability owners. They may be modules in the MVP modular monolith rather than separately deployed services.

| Priority | Missing or underdefined service | Responsibility |
|---|---|---|
| P0 | Policy and Authority Decision | Effective-dated mandate/risk rules, approval thresholds, quorum, delegation, waivers, separation of duties, and deterministic decisions. |
| P0 | Provider Callback and Reconciliation | Authenticate, sequence, deduplicate, normalize, reconcile, and disposition broker/OMS/PMS/custodian messages. |
| P0 | Key and Artifact Integrity | Canonical serialization, signing, KMS/HSM references, rotation/revocation, verification, and artifact-lock health. |
| P0 | External System Synchronization | Source authority and synchronization for positions, cash, orders, risk, settlement, accounting, and performance. |
| P1 | Entitlement-Aware Search | Search index, Cmd+K commands, resource links, tenant/entitlement filtering, freshness, deletion, and query budgets. |
| P1 | Read Model and Projection | Executive, workflow, monitoring, health, audit, and activity projections with checkpoints, lag, rebuild, and freshness. |
| P1 | Model Governance and Cost | Model release state, evaluation gates, data-use policy, token/cost budgets, fallback, rollback, and output quarantine. |
| P1 | Notification and Escalation Policy | Recipients, acknowledgments, escalation timers, deduplication, delivery state, and on-call ownership. |
| P1 | Export and Evidence Packaging | Async PDF/CSV/JSON/audit packages, manifests, signed downloads, retention, and export authorization. |
| P1 | Incident and Diagnostics | Incident state, runbook ownership, diagnostic lifecycle, operator actions, and audit. |
| P2 | Corporate Actions | Event ingestion, position/cash impact, review, and reconciliation if included in post-trade scope. |

## Missing APIs

### Workflow, Task, and Notification

```text
POST /api/v1/workflows/{workflow_id}/retry
POST /api/v1/workflows/{workflow_id}/halt
POST /api/v1/workflows/{workflow_id}/resume
GET  /api/v1/workflows/{workflow_id}/tasks
POST /api/v1/tasks/{task_id}/acknowledge
GET  /api/v1/notifications
POST /api/v1/notifications/{notification_id}/acknowledge
GET  /api/v1/notification-preferences
```

### Search and Commands

```text
GET  /api/v1/search?q=&scope=&cursor=
GET  /api/v1/commands?q=&scope=
POST /api/v1/commands/{command_id}/execute
GET  /api/v1/search/index-status
```

Command execution must re-evaluate permissions, tenant scope, resource scope, and confirmation requirements.

### Administration and Integrations

```text
GET    /api/v1/users/{user_id}
POST   /api/v1/users/{user_id}/suspend
POST   /api/v1/users/{user_id}/reinstate
GET    /api/v1/users/{user_id}/effective-permissions
POST   /api/v1/roles/{role_id}/reset
GET    /api/v1/integrations/{integration_id}
PATCH  /api/v1/integrations/{integration_id}
POST   /api/v1/integrations/{integration_id}/disable
GET    /api/v1/integrations/{integration_id}/events
GET    /api/v1/integrations/{integration_id}/health
GET    /api/v1/integrations/{integration_id}/scopes
```

### Health and Exports

```text
GET  /api/v1/system-health/services
GET  /api/v1/system-health/alerts
GET  /api/v1/system-health/diagnostics/{diagnostic_id}
POST /api/v1/system-health/reports
POST /api/v1/dashboard/exports
POST /api/v1/dashboard/share
POST /api/v1/audit-exports
GET  /api/v1/audit-exports/{export_id}
GET  /api/v1/audit-exports/{export_id}/download
```

### Provider Callback Contracts

Define authenticated, replay-safe contracts for broker/FIX session events, fills, rejects, cancels, corrections, drop copy, settlement, OMS/PMS/custodian positions and cash, market-data sequence gaps and entitlement changes, identity lifecycle/MFA events, and notification delivery receipts.

### Contract Requirements

- Publish OpenAPI 3.1 and AsyncAPI schemas with compatibility rules.
- Define request/response fields, error codes, retryability, pagination, authorization scopes, and state transitions.
- Require `Idempotency-Key` for financial, approval, workflow, retry, export, credential, and admin commands.
- Require `If-Match` or a version for mutable roles, integrations, policies, drafts, and configurations.
- Define SSE/WebSocket authorization, reconnect cursor, ordering, replay, and stale-state payloads.

## Missing Tables

### Policy and Authority

- `approval_policy_versions`
- `policy_rule_effective_windows`
- `policy_waivers`, `policy_waiver_approvals`
- `separation_of_duties_exceptions`
- `authority_evaluation_records`

### Reference and System of Record

- `portfolio_hierarchy_nodes`
- `source_system_entities`, `source_system_sync_cursors`
- `instrument_corporate_actions`, `instrument_lifecycle_events`, `instrument_restrictions`
- `standing_settlement_instructions`, `account_trading_calendars`, `account_capabilities`
- `benchmark_observations`, `factor_exposures`, `risk_calculation_runs`, `performance_attribution_snapshots`

### Reconciliation and Provider Messages

- `provider_message_receipts`, `provider_sequence_gaps`, `provider_replay_requests`, `provider_callback_failures`
- `reconciliation_break_items`, `reconciliation_evidence`, `reconciliation_approvals`, `reconciliation_actions`
- `account_allocations`, `affirmations`, `settlement_instructions`, `settlement_exceptions`

### Search, Read Models, and Operations

- `read_model_checkpoints`, `read_model_rebuilds`, `projection_lag_samples`
- `search_index_documents`, `search_index_versions`, `search_deletion_queue` if self-managed
- `command_catalog`, `command_authorization_policies`, `command_execution_records`
- `diagnostic_results`, `incident_runbooks`, `incident_owners`
- `export_requests`, `export_manifests`, `export_downloads`, `export_failures`
- `tenant_quotas`, `usage_counters`, `model_cost_records`, `provider_cost_records`

### Security and Key Metadata

- `key_references`, `key_versions`, `key_rotation_events`, `key_revocations`
- `artifact_verification_runs`, `audit_integrity_checks`
- `privileged_access_sessions`, `break_glass_events`, `admin_approval_records`
- `provider_webhook_keys`, `callback_verification_events`

### Physical Database Requirements

- Choose MVP tenancy enforcement, including RLS or equivalent and automated tenant-consistency tests.
- Define transaction isolation and locking for approval, execution-intent, cancel/halt, and reconciliation commands.
- Define partition keys and archive jobs for audit, market observations, broker events, health samples, logs, and monitoring metrics.
- Define online migration, backward-compatible event/API versions, rollback, autovacuum, index maintenance, and connection budgets.
- Define retention/archive/legal-hold precedence before deletion jobs.
- Use fixed precision for money/risk fields and preserve source timestamp, receipt timestamp, and provider sequence.

## Security Risks

| Severity | Risk | Required mitigation |
|---|---|---|
| Critical | Approval bypass through stale artifact, internal API, queue replay, or tampered execution payload. | Single execution ingress, exact hash revalidation, signed command, authority/MFA/expiry/revocation checks, constraints, and negative tests. |
| Critical | Cross-tenant or cross-entitlement exposure in databases, queues, caches, storage, search, logs, traces, or model prompts. | Enforced tenant isolation, RLS/equivalent tests, scoped keys/paths/topics, entitlement checks at every boundary, and redaction tests. |
| Critical | Broker credential theft or unauthorized order scope. | External vault/HSM, workload identity, broker-worker-only access, scoped credentials, network controls, rotation, no readback, and auditing. |
| Critical | Audit or artifact signature tampering. | KMS/HSM-backed keys, immutable archive, separate audit roles, signed manifests, rotation/revocation, integrity verification, and privileged monitoring. |
| High | Forged or replayed broker/OMS/PMS callbacks. | mTLS/signature verification, provider key rotation, sequence/checkpoint validation, message IDs, payload hashes, replay windows, and reconciliation on ambiguity. |
| High | Prompt injection in filings, news, research, or documents. | Untrusted-content handling, deny-by-default tools/network, data/instruction separation, scanning, schema validation, and adversarial tests. |
| High | Restricted, licensed, personal, or MNPI data sent to an unauthorized model. | Classification/egress policy, approved model registry, entitlement retrieval, minimization/redaction, private endpoints, and blocked-use audits. |
| High | Approval account takeover or privilege escalation. | Phishing-resistant MFA, step-up auth, short sessions, revocation, dual control, effective-permission review, and anomaly detection. |
| High | Unsafe emergency halt/resume, cancel-all, role change, credential rotation, or broad export. | Scoped, idempotent, step-up/dual-controlled actions with confirmation, independent availability, short-lived export links, and audit evidence. |
| Medium | Sensitive data in logs/traces/model telemetry. | Classified logging schema, secret/PII/financial redaction, trace sampling policy, and secret scanning. |
| Medium | Dependency, image, or model supply-chain compromise. | Pinned/scanned dependencies, SBOM, signed images, build provenance, model allowlist, evaluations, and rollback. |
| Medium | Break-glass access becomes permanent or unaudited. | Time-bound access, separate approval, reason, session recording, auto-revocation, and independent review. |

## Performance Risks

| Severity | Risk | Mitigation |
|---|---|---|
| High | Market observations and broker events use general PostgreSQL paths without measured partitioning. | Define retention/snapshot policy, partition high-volume histories, batch ingestion, and load test peak bursts. |
| High | Dashboard, monitoring, workflow, and audit pages fan out synchronously. | Assign projection ownership, materialize read models, expose freshness/lag, and avoid request-time cross-domain joins. |
| High | Broker, model, market-data, and report work share capacity. | Separate queues/worker pools, priority classes, tenant quotas, circuit breakers, and concurrency budgets. |
| High | Broker timeout retries occur before reconciliation. | Query provider state by client order ID, use inbox/sequence state, block unknown state, and test network partitions. |
| Medium | Redis Streams retention and pending-entry recovery are unspecified. | Define consumer recovery, pending reclamation, retention, DLQ, backpressure, failover, and outbox republish. |
| Medium | Search scans transactions or indexes unentitled data. | Dedicated entitlement-aware projection, bounded queries, index-lag tracking, deletion propagation, and query budgets. |
| Medium | Reports/documents/logs are database blobs. | Encrypted object storage for binaries; PostgreSQL metadata, hashes, versions, and retention only. |
| Medium | Agent/model calls hold HTTP/database resources. | Async jobs, deadlines, cancellation, bounded retries, quotas, and status/event APIs. |
| Medium | Metrics calculate fully on demand. | Versioned snapshots, incremental aggregates, calculation IDs, and rebuildable projections. |
| Medium | Provider rate limits cascade into control-plane failure. | Provider-specific throttling, circuit breakers, bulkheads, stale states, fallbacks, and bounded retries. |
| Medium | No quantitative workload model exists. | Define MVP/three-year volumes and run load, failover, replay, restore, and broker-sandbox tests. |

## UI Consistency Review

### Confirmed

The architecture maps the refined Stitch screens for workflows, intelligence, decision approval, execution, monitoring, executive dashboard, agents, knowledge, audit, access control, integrations, and system health. It preserves the canonical 240px navigation, 8px grid, dense/standard row modes, right drawers, tonal surfaces, semantic status pips, blue interaction state, Inter/Geist typography, and desktop-first responsive behavior.

### Gaps

- Refined and non-refined AI Agent and Knowledge Center exports coexist. Declare refined exports canonical for implementation.
- Existing `Approve Allocation`, `Modify`, `Reject`, `Emergency Halt`, `Cancel All`, `Cancel Order`, credential rotation, role save/reset, user provisioning, integration save/disable/retry, export, and diagnostics controls need explicit API/action contracts.
- Execution `Modify` must return through Strategy and Approval; it cannot mutate the approved plan.
- Monitoring `Rebalance` must create a new workflow, not an order.
- Repeated Cmd+K/search surfaces need one entitlement-aware command/search contract.
- Live execution, agent-console, workflow, notification, and health surfaces need reconnect cursors, ordering, stale state, and authorization at subscription time.
- "Autonomous agents" and "Auto-Rebalance Executed" are UI copy only; runtime permissions and prior approved traces govern behavior.
- Executive PDF/share, audit deep search/export, Knowledge Center add, and integration retry are not fully represented in the architecture API list.

No redesign is recommended. These are behavioral and contract gaps behind existing screens.

## Workflow Preservation Review

### Required Sequence

```text
Market Intelligence
  -> Portfolio Strategy
  -> Human Approval
  -> Trade Execution
  -> Portfolio Monitoring
```

The architecture preserves this sequence through the state machine, outbox events, artifact hash, deterministic validation, and execution precondition:

1. Intelligence publishes an exact stored research report version and hash.
2. Strategy consumes that version and publishes a recommendation version.
3. Deterministic validation precedes approval.
4. A qualified human approves one immutable artifact hash.
5. Execution revalidates approval, authority, freshness, expiry, and hash.
6. Orders derive from the approved order plan, not UI allocation fields.
7. Monitoring reconciles outcomes and creates a new strategy workflow for rebalance.

### Runtime Evidence Still Required

- Illegal state-transition contract tests.
- API proof that no order is created without current approval and matching artifact hash.
- Race tests for approval revoke/expiry, duplicate approval, duplicate submit, cancel-all versus fill, and halt versus queued order.
- Event replay tests proving replay cannot resubmit broker commands.
- Worker permission tests proving agents cannot approve, release, alter limits, or access broker credentials.
- Broker sandbox tests for ack, fill, partial fill, reject, cancel, timeout, reconnect, sequence gap, duplicate callback, correction, and reconciliation.
- Rebalance tests proving monitoring cannot create direct orders.
- Full workflow export from source evidence through monitoring outcome.

The workflow is preserved in architecture, but not yet verified in runtime.

## Recommended Improvements

### P0 - Before Parallel Implementation

1. Decide MVP tenancy and deployment isolation, then document enforcement and tests.
2. Publish OpenAPI 3.1 and AsyncAPI schemas for all endpoints, events, live updates, and provider callbacks.
3. Create a complete UI action matrix mapping every control to API, permission, transition, idempotency, audit event, and failure state.
4. Define effective-dated authority policy: thresholds, quorum, delegation, expiry, revocation, escalation, waivers, and separation of duties.
5. Define KMS/HSM key hierarchy, artifact signing, rotation, revocation, archival verification, and break-glass.
6. Define callback authentication, sequence/gap recovery, deduplication, and external-system source authority.
7. Define read-model ownership, freshness/lag thresholds, rebuild/replay, and UI consistency metadata.
8. Define physical PostgreSQL RLS, migrations, partitions, connection budgets, isolation, retention/archive, and restore.
9. Define Redis Streams consumer recovery, retention, DLQ, backpressure, failover, and outbox republish.

### P1 - Before MVP Production Pilot

1. Add a threat model covering approval, broker, callbacks, model/tools, ingestion, search, export, administration, and tenant boundaries.
2. Define model release gates, evaluation thresholds, cost budgets, data-use policy, fallback, output quarantine, and rollback.
3. Define allocation, affirmation, settlement, reconciliation, accounting/performance, and corporate-action scope or explicit external handoffs.
4. Add policy, provider receipt/sequence, reconciliation, projection, export, quota, key, break-glass, and callback-verification tables.
5. Define notification acknowledgment/escalation and incident/diagnostic ownership.
6. Define search index security, freshness, deletion/legal-hold propagation, command authorization, and query budgets.
7. Establish contract, state-machine, authorization, idempotency, replay, load, failover, restore, visual, and accessibility tests.
8. Define API/schema compatibility, event versioning, migration ownership, and provider adapter certification.

### P2 - Scale Readiness

1. Establish quantitative MVP/three-year workload and cost models.
2. Load test market-data bursts, audit writes, approval queues, dashboard reads, exports, model jobs, and broker bursts.
3. Run chaos/failover exercises for PostgreSQL, Redis, object storage, identity, model, market, broker, notification, and event replay.
4. Add regional residency/deployment patterns only after customer and jurisdiction requirements are explicit.
5. Add corporate-actions, transaction-cost, best-execution analytics, and multi-asset extensions behind stable provider interfaces.

## Approval Gate

Move from conditional approval to implementation approval when:

- Tenancy and authority decisions are signed off.
- Contract artifacts exist and every UI action maps to an API, permission, event, and failure state.
- PostgreSQL physical strategy and missing tables are resolved.
- Provider callback and post-trade synchronization contracts are approved.
- Key-management and artifact/audit integrity design is independently reviewed.
- Threat model has no unresolved critical findings.
- Workload model supports performance, availability, RPO, and RTO targets.
- State-machine, approval-bypass, idempotency, replay, and broker-sandbox tests pass.
- Canonical refined UI routes remain unchanged and behavior is implemented behind them.

## Final Recommendation

**Conditionally approve the architecture for contract and proof-of-control work only. Do not approve production execution or broad parallel feature development yet.**

The architecture is directionally correct. Its strongest decisions are the modular monolith control plane, isolated broker/model/market workers, PostgreSQL authority, outbox/inbox delivery, immutable approved artifacts, and fail-closed execution behavior. The next milestone is producing the missing contract artifacts and proving approval gating, tenant/entitlement isolation, provider reconciliation, idempotent execution, and audit lineage in a broker-sandbox environment.
