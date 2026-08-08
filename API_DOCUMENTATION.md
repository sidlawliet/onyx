# InvestOps AI — REST API Documentation

Comprehensive REST API reference for the **InvestOps AI Institutional Control Plane**.

---

## 🔐 Authentication & Authorization

All protected endpoints require an HTTP `Authorization` header containing a valid Bearer JWT token:

```http
Authorization: Bearer <access_token>
```

### Institutional Role Profiles
- `ANALYST`: Can initiate workflows, run market research, view reports and strategy recommendations.
- `APPROVER`: Investment authority role. Can record legal attestations and submit `APPROVE` / `REJECT` decisions on locked artifact manifests.
- `TRADER`: Execution authority role. Can submit pre-approved trade execution intents to FIX broker connectors.
- `AUDITOR`: Compliance role. Can query immutable audit logs and export SHA-256 hash-chain verification packages.

---

## 📌 Complete Endpoint Reference

### 1. Authentication Domain

#### `POST /api/v1/auth/login`
Authenticate user credentials and receive JWT access token.
- **Request Body**:
  ```json
  {
    "email": "approver@investops.ai",
    "password": "demo-password"
  }
  ```
- **Response `200 OK`**:
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
    "token_type": "bearer",
    "user_id": "11111111-1111-4111-a111-111111111111",
    "email": "approver@investops.ai",
    "full_name": "Portfolio Approver",
    "roles": ["APPROVER"]
  }
  ```

#### `GET /api/v1/auth/me`
Retrieve authenticated user profile and active tenant scope.
- **Headers**: `Authorization: Bearer <token>`
- **Response `200 OK`**: Returns user profile model.

---

### 2. Multi-Tenant & Portfolio Domain

#### `GET /api/v1/tenants`
List accessible institutional tenant accounts.

#### `GET /api/v1/portfolios`
List managed portfolio funds under current tenant scope (`GROWTH-01`, etc.).

#### `GET /api/v1/portfolios/accounts`
List broker execution accounts associated with managed funds.

---

### 3. Workflow Engine Domain (5-Stage State Machine)

#### `POST /api/v1/workflows`
Initiate a new institutional rebalance workflow pipeline.
- **Request Body**:
  ```json
  {
    "portfolio_id": "88888888-8888-4888-a888-888888888888",
    "title": "Q4 Institutional Tech Rebalance"
  }
  ```
- **Response `201 Created`**:
  ```json
  {
    "id": "99999999-9999-4999-a999-999999999999",
    "stage": "MARKET_INTELLIGENCE",
    "status": "RUNNING",
    "trace_id": "11111111-1111-4111-a111-111111111111"
  }
  ```

#### `GET /api/v1/workflows`
List active and completed workflow pipelines.

#### `GET /api/v1/workflows/{id}`
Retrieve workflow detail including stage transition history, reports, recommendations, approval tasks, and execution intents.

---

### 4. Market Intelligence Domain

#### `POST /api/v1/research-reports/workflows/{workflow_id}/run`
Trigger Market Intelligence Agent execution for a workflow pipeline.
- **Response `200 OK`**: Returns completed research report model with SEC Form 10-K citations, empirical claims, confidence scores, and company/sector analysis ratings.

#### `GET /api/v1/research-reports/workflows/{workflow_id}`
Fetch latest research report for a workflow pipeline.

---

### 5. Portfolio Strategy & Mandate Validation Domain

#### `POST /api/v1/recommendations/workflows/{workflow_id}/generate`
Trigger Portfolio Strategy Agent execution to generate target asset allocations and deterministic SHA-256 artifact content hash (`artifact_hash`).
- **Response `200 OK`**: Returns recommendation version model.

#### `POST /api/v1/recommendations/versions/{version_id}/validate`
Run pre-trade mandate and risk rule compliance checks against recommendation version.
- **Response `200 OK`**:
  ```json
  {
    "status": "PASS",
    "results": [
      {
        "rule_code": "MAX_SINGLE_STOCK_WEIGHT",
        "passed": true,
        "explanation": "Target weight 0.25 <= max allowed 0.30"
      }
    ]
  }
  ```

---

### 6. Human Decision Workspace Domain (Approval Gate)

#### `POST /api/v1/approval-tasks/recommendation-versions/{version_id}/submit`
Lock recommendation version into an `ArtifactManifest` and create pending `ApprovalTask`.
- **Response `200 OK`**: Returns approval task model with `artifact_manifest_id`.

#### `POST /api/v1/approval-tasks/tasks/{task_id}/decision`
Record substantive human investment decision (`APPROVE` or `REJECT`) with legal attestation statement and MFA security verification.
- **Request Body**:
  ```json
  {
    "decision": "APPROVE",
    "attestation": "I attest that I have reviewed the SEC Form 10-K report and approve this allocation.",
    "artifact_hash": "a1b2c3d4...",
    "mfa_verified": true
  }
  ```
- **Response `200 OK`**: Returns recorded approval decision model.

---

### 7. Pre-Approved Trade Execution Safety Gate Domain

#### `POST /api/v1/execution-intents`
Release pre-approved trade execution intent to FIX broker connectors.

> [!CAUTION]
> **Execution Safety Gate Rule**: Requests MUST supply `approved_artifact_id` pointing to an `ArtifactManifest` with an active `APPROVE` decision, and `approved_artifact_hash` MUST match the locked SHA-256 hash exactly. Otherwise, the call is rejected with `409 Conflict` or `422 Unprocessable Entity`.

- **Request Body**:
  ```json
  {
    "approved_artifact_id": "77777777-7777-4777-a777-777777777777",
    "approved_artifact_hash": "a1b2c3d4...",
    "account_id": "33333333-3333-4333-a333-333333333333",
    "integration_id": "44444444-4444-4444-a444-444444444444",
    "idempotency_key": "IDEM-EXEC-20260808-001"
  }
  ```
- **Response `201 Created`**:
  ```json
  {
    "id": "55555555-5555-4555-a555-555555555555",
    "status": "EXECUTED",
    "orders": [
      {
        "client_order_id": "ORD-AAPL-BUY-01",
        "provider_order_id": "FIX-FILL-9921",
        "side": "BUY",
        "status": "FILLED"
      }
    ]
  }
  ```

---

### 8. Portfolio Monitoring & Drift Domain

#### `POST /api/v1/monitoring/portfolios/{id}/capture-snapshots`
Capture real-time holding snapshots and evaluate target allocation drift alerts.

#### `GET /api/v1/monitoring/portfolios/{id}/holdings`
List current position holdings, market values, and weight drift.

#### `GET /api/v1/monitoring/portfolios/{id}/alerts`
List active portfolio drift alerts.

---

### 9. Immutable Audit Domain

#### `GET /api/v1/audit-events/events`
Query audit event log, filterable by `trace_id`.

#### `POST /api/v1/audit-events/export`
Export verified audit chain package with SHA-256 hash-chain validation status (`chain_valid: true`).

---

### 10. System Health & Integrations Domain

#### `GET /api/v1/system-health`
Returns system health status (`HEALTHY`) and database connectivity status.

#### `GET /api/v1/agents/status`
Returns status, queue depth, and success rate for all sandboxed AI agents.

#### `GET /api/v1/integrations`
List external provider connectors (SEC EDGAR, FIX Broker Sandboxes).
