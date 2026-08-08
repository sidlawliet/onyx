# Contributing to InvestOps AI

Thank you for contributing to **InvestOps AI**! This guide outlines the development standards, repository structure, conventional commit formats, and pull request testing requirements.

---

## 🌲 Branching & Commit Strategy

### Branch Naming Conventions
- `feature/<short-description>` — New platform capability or API endpoint
- `fix/<issue-description>` — Bug fix or safety gate remediation
- `docs/<doc-name>` — Technical documentation updates
- `test/<test-scope>` — Unit, integration, or Playwright E2E test additions

### Conventional Commit Format
All commits MUST follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```text
<type>(<scope>): <short summary>

[optional body]
```

#### Allowed Types
- `feat`: New feature or endpoint implementation
- `fix`: Bug fix in backend, frontend, or database layer
- `test`: Unit, integration, or Playwright test additions
- `docs`: Documentation updates
- `refactor`: Code refactoring without behavioral changes
- `ci`: Infrastructure or GitHub Actions CI/CD pipeline changes

---

## 🛠️ Code & Architectural Standards

### 1. Python Backend Standards (`apps/api`)
- Enforce strict type hints using Python 3.11+ syntax (`str | None`, `list[UUID]`).
- Use Pydantic v2 `BaseModel` schemas for API request/response validation.
- Use SQLAlchemy 2.0 ORM patterns (`select(Model)`, `db.execute()`).
- All numeric financial values (prices, market values, quantities, weights) MUST use `Decimal` for precision.

### 2. Frontend Standards (`apps/web`)
- Enforce TypeScript strict mode (`tsconfig.json`).
- Preserve Stitch visual design language, HSL/hex dark theme palettes, and spacing tokens.
- Use centralized `apiClient` in `apps/web/lib/api-client.ts` for all backend HTTP calls.
- Include loading indicators (`LoadingState.tsx`) and error banners (`ErrorBanner.tsx`).

---

## 🧪 Testing Guidelines (All PRs Must Pass)

Before submitting a Pull Request, verify that all three test suites pass cleanly locally:

### 1. Run Python Unit & Integration Tests
```bash
python -m pytest -v
```

### 2. Run Next.js Production Build
```bash
cd apps/web
npm run build
```

### 3. Run Playwright E2E Tests
```bash
cd apps/web
npx playwright test
```

---

## 🚀 Pull Request Checklist

Before requesting review:
- [ ] Code follows Python Pydantic/SQLAlchemy and TypeScript strict standards.
- [ ] All 5 workflow stage invariants and execution safety gate rules remain intact.
- [ ] Pytest integration suite passes cleanly with zero failures.
- [ ] Next.js build compiles cleanly with zero TypeScript errors.
- [ ] Documentation is updated if API endpoints or environment variables were modified.
