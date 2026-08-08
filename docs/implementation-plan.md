# Onyx Implementation Plan

**Project:** Onyx  
**Planning basis:** `project-context.md`, `docs/PRD.md`, `docs/architecture.md`, `docs/technical-review.md`, and the canonical Stitch export in `ui/`  
**Timebox:** 6 hours total  
**Delivery objective:** A demo-safe vertical slice of the complete five-stage workflow

## Hackathon Objective

Deliver one coherent, clickable demonstration that visibly moves through:

```text
Market Intelligence
  -> Portfolio Strategy
  -> Human Approval
  -> Trade Execution
  -> Portfolio Monitoring
```

The demo must prove three product truths:

1. AI produces reviewable, source-linked research and strategy artifacts.
2. No execution occurs until a human explicitly approves the exact recommendation.
3. The complete decision-to-outcome chain is visible through workflow status and audit evidence.

The six-hour build uses one single-tenant demo environment, deterministic fixtures, mock market-data responses, a broker sandbox/mock, seeded users, and the existing UI. It does not claim production security, live trading, multi-tenancy, or autonomous investing.

## Scope Rules

### Must Ship

- Existing Stitch layout and navigation remain unchanged.
- One seeded investment workflow with realistic fixture data.
- Market Research Report with sources, confidence, and model metadata.
- Portfolio Recommendation Report with allocations, risk, expected return, volatility, scenario, and reasoning fields.
- Human `Approve`, `Reject`, and `Modify` behavior.
- Server-side execution rejection before approval.
- Approved-artifact identity/hash check in the demo path.
- Mock execution queue with validation, submitted, partial fill, executed, and audit events.
- Portfolio monitoring view with holdings, P&L, drift, alert, and completed execution activity.
- Visible audit chain using workflow ID and trace ID.
- One repeatable demo script and seeded reset state.

### Explicitly Deferred

- Live broker or market-data credentials.
- Real FIX sessions, production webhooks, and external OMS/PMS synchronization.
- Multi-tenant deployment and production RLS.
- Full KMS/HSM lifecycle and production signing infrastructure.
- Complete notification provider integrations.
- Full search index and command gateway.
- Corporate actions, affirmation, accounting, tax, derivatives, private assets, and full settlement operations.
- Production-grade model evaluation, load testing, disaster recovery, and regulatory certification.
- New screens, redesigns, or broad component refactors.

## Team Model

| Role | Primary ownership | Backup |
|---|---|---|
| Tech Lead / PM | Scope, architecture decisions, integration, demo, acceptance gate | All lanes |
| Frontend A | Workflow, Market Intelligence, Strategy/Approval screens | Frontend B |
| Frontend B | Execution, Monitoring, Audit screen wiring | Frontend A |
| Backend A | Workflow, recommendation, approval, artifact gate | Backend B |
| Backend B | Mock broker, execution lifecycle, monitoring, audit events | Backend A |
| AI/Data + DevOps/QA | Fixtures, report payloads, provider mocks, seeded environment, smoke tests | Tech Lead |

If fewer people are available, preserve the critical path in this order: backend workflow/approval gate, frontend decision screen, execution/audit, then monitoring polish.

## Epics

| Epic | Outcome | Priority |
|---|---|---|
| E1. Demo Foundation | Application starts with seeded tenant/user/portfolio and a stable fixture reset. | P0 |
| E2. Workflow Orchestration | One workflow moves through the five required stages with traceable state. | P0 |
| E3. Intelligence and Strategy | Reviewable research and recommendation artifacts populate existing screens. | P0 |
| E4. Human Approval Gate | Approval, rejection, modification, and server-side execution blocking work. | P0 |
| E5. Mock Execution and Monitoring | Approved plan produces simulated order lifecycle and monitoring outcome. | P0 |
| E6. Audit and Demo Readiness | Audit chain, visible status, seeded reset, smoke tests, and demo script are reliable. | P0 |
| E7. Deferred Production Hardening | Technical-review P0/P1 gaps not required for a six-hour demo. | P1, post-hackathon |

## Features

### E1. Demo Foundation

- F1.1 Single-tenant demo mode
- F1.2 Seeded user roles: analyst, portfolio manager/approver, trader, auditor
- F1.3 Seeded portfolio, holdings, cash, market snapshots, sources, and broker responses
- F1.4 Deterministic reset to `DRAFT`
- F1.5 Runtime configuration identifying all external data and execution as mock/sandbox

### E2. Workflow Orchestration

- F2.1 Workflow ID and trace ID generation
- F2.2 Fixed stage/status state machine
- F2.3 Stage transition history
- F2.4 Existing workflow UI status and timeline wiring
- F2.5 Event/audit emission for each transition

### E3. Intelligence and Strategy

- F3.1 Market Intelligence fixture/job completion
- F3.2 Stored Market Research Report with citations and confidence
- F3.3 Automatic handoff to Portfolio Strategy
- F3.4 Portfolio Recommendation Report with exact required fields
- F3.5 Versioned recommendation artifact and deterministic content hash

### E4. Human Approval Gate

- F4.1 Approval task assigned to seeded approver
- F4.2 Review context populated in existing Decision Workspace
- F4.3 Approve with attestation
- F4.4 Reject with reason
- F4.5 Modify with reason, new version, and invalidated prior approval
- F4.6 Execution endpoint rejects missing, stale, revoked, or mismatched approval

### E5. Mock Execution and Monitoring

- F5.1 Approved-artifact-only execution intent
- F5.2 Deterministic funds and allocation validation
- F5.3 Simulated order queue and lifecycle events
- F5.4 Partial fill, executed, rejected, and cancel state fixtures
- F5.5 Portfolio holdings/P&L/drift update from simulated execution
- F5.6 Monitoring alert and approved rebalance workflow entry point

### E6. Audit and Demo Readiness

- F6.1 Audit events for report, recommendation, approval, execution, fill, and monitoring
- F6.2 Search/filter by workflow ID and trace ID within the demo data set
- F6.3 Existing Audit Trail detail view wiring
- F6.4 Smoke test for approval bypass and happy path
- F6.5 Demo reset and rehearsal script
- F6.6 Honest mock/sandbox labeling in existing context/status surfaces where available

## Stories

Stories are intentionally small enough for a six-hour build. A story is complete only when its acceptance criteria pass in the demo environment.

### Foundation and Workflow

| ID | Story | Acceptance criteria | Depends on |
|---|---|---|---|
| S-01 | As a demo operator, I can reset one seeded workflow to a known initial state. | Reset returns the workflow to `DRAFT`; all prior fixture events and artifacts are cleared/reseeded; reset is auditable. | None |
| S-02 | As the system, I create a workflow ID and trace ID once and preserve them across all five stages. | Same IDs appear in workflow, recommendation, approval, execution, monitoring, and audit views. | S-01 |
| S-03 | As the system, I enforce the fixed stage order. | Illegal direct transitions, especially Strategy -> Execution and Monitoring -> Order, are rejected. | S-02 |
| S-04 | As an operator, I can see stage and status transitions in the existing Workflow screen. | Active workflow, stage, status, timestamps, and failure state render without layout changes. | S-02 |

### Intelligence and Strategy

| ID | Story | Acceptance criteria | Depends on |
|---|---|---|---|
| S-05 | As an analyst, I can run Market Intelligence on seeded authorized data. | Job completes using fixture market data and produces a stored report artifact. | S-02 |
| S-06 | As an analyst, I can review a cited Market Research Report. | Report includes Market Summary, opportunities, risks, company/sector analysis, confidence, and source references. | S-05 |
| S-07 | As the system, I automatically pass the exact research version to Strategy. | Strategy records the research artifact ID/hash and cannot use an unstored or altered report. | S-06 |
| S-08 | As a portfolio manager, I can review a Portfolio Recommendation Report. | Recommendation includes companies, allocation percentages, risk, expected return, volatility, diversification, horizon, confidence, and reasoning. | S-07 |
| S-09 | As the system, I create an immutable recommendation artifact identity. | Artifact has a deterministic content hash; changing an allocation creates a new version. | S-08 |

### Human Approval and Safety Gate

| ID | Story | Acceptance criteria | Depends on |
|---|---|---|---|
| S-10 | As an approver, I can inspect thesis, evidence, recommendation, risk, scenario, impact, confidence, and version data in the existing Decision Workspace. | All review-critical data is visible through the existing hierarchy. | S-08 |
| S-11 | As an approver, I can approve an exact recommendation. | Approve requires seeded approver role and attestation; records artifact hash, actor, time, and trace. | S-09, S-10 |
| S-12 | As an approver, I can reject a recommendation. | Reject requires a reason, leaves no executable approval, and creates an audit event. | S-10 |
| S-13 | As an approver, I can modify allocations. | Modify requires a reason, creates a new recommendation/artifact version, and invalidates prior approval. | S-09, S-10 |
| S-14 | As a safety tester, I can prove execution is blocked before approval. | Execution request before approval returns a visible failure; no order is created; blocked attempt is audited. | S-09 |
| S-15 | As a safety tester, I can prove execution rejects a mismatched artifact. | Changing the artifact hash or version causes rejection and no order creation. | S-11 |

### Execution, Monitoring, and Audit

| ID | Story | Acceptance criteria | Depends on |
|---|---|---|---|
| S-16 | As a trader, I can submit only an approved artifact to the mock broker. | Approved execution creates one execution intent and order plan; free-form allocation is not accepted. | S-11, S-15 |
| S-17 | As a trader, I can see simulated order lifecycle state. | Existing Execution screen shows validation, queued/submitted, partial fill or executed, and audit events. | S-16 |
| S-18 | As an operations user, I can see simulated portfolio outcome. | Existing Monitoring screen shows updated holding, P&L, drift, performance, alert/activity state, and source trace. | S-17 |
| S-19 | As an auditor, I can reconstruct the demo workflow. | Audit view filters by trace ID and shows research -> recommendation -> approval -> order -> fill -> monitoring chain. | S-02, S-06, S-11, S-17, S-18 |
| S-20 | As a user, I can start a rebalance workflow without direct execution. | Rebalance creates a new Strategy-stage workflow and no order is created. | S-18 |
| S-21 | As a demo operator, I can run the complete happy-path demo repeatedly. | Reset plus scripted clicks completes within five minutes with no manual database edits. | S-01 through S-19 |

## Development Order

### Critical Path

```text
S-01
  -> S-02
  -> S-03
  -> S-05 -> S-06 -> S-07 -> S-08 -> S-09
  -> S-10 -> S-11 -> S-14/S-15
  -> S-16 -> S-17 -> S-18 -> S-19 -> S-21
```

### Build Rules

1. Establish the seeded vertical slice before polishing any secondary screen.
2. Implement the approval bypass test before declaring execution complete.
3. Use the existing refined Stitch screens as integration targets; do not rebuild layout.
4. Prefer fixture-driven behavior over live-provider integration.
5. Keep every event and artifact tied to workflow ID and trace ID from the first backend story.
6. Stop adding features at the three-hour mark if the end-to-end path is not working.

## Parallel Tasks

Parallelism starts only after the 30-minute kickoff and shared contract decision.

### Lane A: Control Plane and Workflow

Owner: Backend A + Tech Lead

- S-01 seeded reset
- S-02 IDs and workflow state
- S-03 transition guard
- S-04 workflow query/timeline
- S-07 intelligence-to-strategy handoff
- S-09 artifact hash

### Lane B: Approval and Safety

Owner: Backend B

- S-10 approval context contract
- S-11 approve
- S-12 reject
- S-13 modify/version invalidation
- S-14 pre-approval rejection
- S-15 artifact mismatch rejection

Lane B can use placeholder report/recommendation fixtures while Lane A builds the workflow.

### Lane C: Existing UI Wiring

Owner: Frontend A

- Wire Workflow screen and stage states.
- Wire Market Intelligence report/evidence state.
- Wire Decision Workspace review and action states.
- Preserve exact navigation, hierarchy, density, controls, and layout.

### Lane D: Execution, Monitoring, and Audit UI

Owner: Frontend B + Backend B pairing after S-11

- Wire Execution queue/progress/logs.
- Wire Monitoring holdings/P&L/drift/alerts/activity.
- Wire Audit Trail trace search/detail.
- Keep mock/sandbox state visibly honest without redesigning screens.

### Lane E: Fixtures, Mocks, and Verification

Owner: AI/Data + DevOps/QA

- Seed report sources, research claims, recommendation, holdings, cash, order/fill events.
- Provide market-data and broker mock responses.
- Prepare Docker/local environment and reset command.
- Run smoke checks and capture screenshots/demo evidence.

### Integration Rule

All lanes use one minimal shared contract:

- `workflow_id`
- `trace_id`
- `artifact_id`
- `artifact_hash`
- `stage`
- `status`
- `actor_id`
- `event_id`

Avoid new shared abstractions until the vertical slice works.

## Milestones

| Milestone | Time | Exit criteria |
|---|---:|---|
| M0. Kickoff and scope lock | 0:00-0:30 | Team roles assigned; single-tenant mock scope accepted; refined UI declared canonical; shared IDs/statuses agreed. |
| M1. Foundation green | 0:30-1:15 | App starts, seed/reset works, workflow/trace IDs exist, basic state endpoint and UI route load. |
| M2. Research-to-approval ready | 1:15-2:30 | Research and recommendation artifacts render in existing UI; exact artifact hash exists; approval task is visible. |
| M3. Safety gate proven | 2:30-3:15 | Pre-approval and mismatched-artifact execution attempts fail and are audited; approve/reject/modify behavior works. |
| M4. Executed outcome | 3:15-4:30 | Approved artifact creates one simulated order lifecycle; monitoring reflects resulting holding/P&L/drift. |
| M5. Audit and demo hardening | 4:30-5:30 | Full trace visible, reset works, primary smoke tests pass, UI loading/error states are acceptable. |
| M6. Demo freeze | 5:30-6:00 | No new features; demo rehearsed twice; screenshots/recording and fallback path ready. |

## Six-Hour Sprint Plan

This is one sprint with six timeboxed phases. The timebox is fixed; tasks are cut when their phase ends.

### Phase 1: Kickoff and Contract Lock, 0:00-0:30

**Activities:**

- Confirm single-tenant demo mode and mock/sandbox providers.
- Declare refined UI exports canonical.
- Agree stage/status names and shared identifiers.
- Confirm no live trading, autonomous investing, or UI redesign.
- Create GitHub issues from P0 stories.

**Deliverable:** One-page team contract and seeded demo scenario.

### Phase 2: Foundation, 0:30-1:15

**Backend:** S-01, S-02, S-03.  
**Frontend:** S-04 route/state wiring.  
**Data/DevOps:** fixtures, reset, provider mocks.

**Deliverable:** Workflow can be reset and displays the initial stage with stable IDs.

### Phase 3: Research to Approval, 1:15-2:30

**Backend:** S-05 through S-09.  
**Frontend:** research and Decision Workspace data wiring.  
**Data/AI:** realistic cited report and recommendation fixture.

**Deliverable:** A recommendation with sources, risk, allocation, confidence, model metadata, and artifact hash is ready for human review.

### Phase 4: Safety Gate, 2:30-3:15

**Backend:** S-10 through S-15.  
**Frontend:** approve/reject/modify action states and failure display.  
**QA:** execute bypass and hash mismatch tests.

**Deliverable:** The demo proves that no order exists before explicit human approval.

### Phase 5: Execution to Monitoring, 3:15-4:30

**Backend:** S-16 through S-18.  
**Frontend:** Execution, Monitoring, and live/status wiring.  
**QA:** duplicate/replay check and happy-path smoke test.

**Deliverable:** One approved recommendation produces a simulated fill and visible portfolio outcome.

### Phase 6: Audit, Polish, and Demo Freeze, 4:30-6:00

**Backend:** S-19/S-20 trace and rebalance guard.  
**Frontend:** Audit detail, workflow polish, honest mock labels where available.  
**QA/PM:** S-21, screenshots, rehearsal, fallback recording.

**Deliverable:** Repeatable five-minute demo with visible audit chain and no known approval bypass.

## GitHub Milestones

### GitHub Milestone 1: `Hackathon / Foundation`

**Due:** End of hour 1  
**Issues:** S-01, S-02, S-03, S-04  
**Exit:** Seed/reset, IDs, fixed state machine, initial workflow screen.

### GitHub Milestone 2: `Hackathon / Intelligence-to-Approval`

**Due:** End of hour 2.5  
**Issues:** S-05, S-06, S-07, S-08, S-09, S-10  
**Exit:** Stored research and recommendation artifacts rendered in the existing review flow.

### GitHub Milestone 3: `Hackathon / Approval Gate`

**Due:** End of hour 3.25  
**Issues:** S-11, S-12, S-13, S-14, S-15  
**Exit:** Approval, rejection, modification, pre-approval block, mismatch block, and audit events.

### GitHub Milestone 4: `Hackathon / Execution-to-Monitoring`

**Due:** End of hour 4.5  
**Issues:** S-16, S-17, S-18  
**Exit:** Mock order lifecycle and monitoring outcome.

### GitHub Milestone 5: `Hackathon / Demo Freeze`

**Due:** End of hour 6  
**Issues:** S-19, S-20, S-21  
**Exit:** Full trace, reset, smoke tests, demo script, screenshots/recording, and no new scope.

### Post-Hackathon GitHub Milestone: `Production Readiness Gates`

Carry forward all items from `docs/technical-review.md` P0/P1:

- OpenAPI/AsyncAPI schemas
- Tenancy and RLS decision
- Authority policy and key lifecycle
- Provider callbacks and reconciliation
- Physical PostgreSQL strategy
- Redis Streams recovery
- Search and projection contracts
- Threat model and security testing
- Workload/load/failover testing
- Post-trade scope expansion

## Demo Script

1. Open Workflow screen and show a seeded workflow ID/trace ID at Market Intelligence.
2. Open Intelligence and show market summary, top opportunities/risks, confidence, and cited sources.
3. Show automatic handoff to Portfolio Strategy and open the recommendation.
4. Attempt execution before approval. Show rejection and the audit event.
5. Return to Decision Workspace. Review evidence, risk, scenario, current/proposed allocation, and model metadata.
6. Click `Approve Allocation` and provide the seeded attestation.
7. Open Execution. Show approved -> validation -> queued/submitted -> partial fill/executed lifecycle.
8. Open Monitoring. Show updated holding, P&L, drift, alert/activity, and the link to the same trace.
9. Open Audit. Filter by trace ID and show the full chain from research to monitoring.
10. Optionally click `Rebalance` and show creation of a new strategy workflow with no direct order.
11. Reset and repeat the first critical safety check if time permits.

## Scope Cuts and Decision Rules

Cut in this order if time slips:

1. Notifications and nonessential live updates.
2. Search beyond workflow/trace ID.
3. Multiple order states beyond one partial-fill happy path.
4. Executive dashboard data refresh beyond seeded read model.
5. Modify UI polish, while retaining backend version invalidation.
6. Additional user/admin screens beyond seeded role checks.

Never cut:

- Human approval.
- Server-side rejection before approval.
- Exact artifact identity/hash check.
- Workflow ID and trace ID.
- Audit events for approval and execution.
- Fixed stage ordering.
- Mock/sandbox labeling and no-live-trading boundary.
- Existing UI structure.

## Milestone Definition of Done

### Feature Done

- Story acceptance criteria pass against the seeded environment.
- State changes are tied to workflow ID, trace ID, actor, and event ID.
- Existing UI hierarchy and layout are unchanged.
- Failure behavior is visible enough for the demo.
- No story introduces autonomous approval, allocation, or trading.

### Hackathon Done

- App starts from the documented demo environment.
- Reset produces the same known state.
- Five-stage happy path completes in under five minutes.
- Pre-approval execution attempt creates no order.
- Artifact mismatch creates no order.
- Approved artifact creates exactly one simulated execution intent.
- Monitoring reflects the simulated outcome.
- Audit view reconstructs the complete chain.
- No critical console/runtime error blocks the demo.
- Demo is rehearsed twice and fallback screenshots/recording exist.

## Risks and Mitigations

| Risk | Mitigation during six hours |
|---|---|
| Architecture P0 decisions consume the timebox | Use single-tenant, one portfolio, seeded roles, deterministic rules, and mock providers; document deferred production decisions. |
| UI wiring takes longer than backend | Use existing HTML structure as the contract; populate the primary decision/execution/audit path first. |
| Agent/model output is unreliable | Use deterministic fixture outputs with visible model/source metadata; keep the agent boundary represented but bounded. |
| Demo accidentally implies live trading | Label provider as mock/sandbox in existing context/status data; never use real credentials or live endpoints. |
| Approval bypass remains hidden | Test the bypass before happy-path execution and keep the negative check in the demo script. |
| Integration conflicts across lanes | Lock shared identifiers and state names in Phase 1; integrate at M2 and M4 only. |
| Six hours consumed by production hardening | Defer KMS/HSM, multi-tenancy, full search, external callbacks, load tests, and advanced post-trade work. |
| Demo environment drift | Provide one reset path, seeded fixture version, and a final demo freeze at 5:30. |

## Post-Hackathon Order

After the demo, implement in this order:

1. Contract artifacts and UI action matrix.
2. Tenancy and authority policy decisions.
3. KMS/HSM artifact/audit integrity.
4. Provider callback, OMS/PMS synchronization, and reconciliation.
5. Physical PostgreSQL and Redis production strategy.
6. Threat model and security tests.
7. Search/read-model contracts and workload tests.
8. Production broker certification and post-trade expansion.
