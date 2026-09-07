# Development Process & Workflow

This document outlines the AI-native development workflow for the **Flatmate Chore Manager** project, adhering to the AI Dev Tools Zoomcamp context-engineering principles.

---

## Core Principles

1. **GitHub Issues as Single Source of Truth**: All tasks originate from GitHub issues defined in `_docs/backlog.md`.
2. **One Issue at a Time**: Work is strictly scoped to one issue per session. Never bundle multiple tasks or begin subsequent issues before the current one is completed, verified, and committed.
3. **Strict Scope Discipline**: Implement only what the issue asks for. Do not introduce premature refactors, speculative utilities, or out-of-scope capabilities.
4. **Environment Uniformity via `uv`**: All execution, dependency management, and testing must use `uv` rather than global Python or `pip`.

---

## Step-by-Step Task Lifecycle

### 1. Issue Selection & Context Loading
- Pick the next open issue in sequential order from the repository backlog.
- Read the issue title, goal, and full description carefully.
- Cross-reference relevant specifications in `_docs/plan.md` and data models in `_docs/architecture.md` to confirm requirements and interfaces before writing code.

### 2. Implementation within Requested Scope
- Implement the requested models, views, templates, or commands.
- Adhere strictly to the project architecture:
  - Session-based identity (no passwords or standard Django auth).
  - Clean Django idioms with server-rendered templates styled via Tailwind CSS CDN.
- Keep changes minimal, targeted, and cohesive.

### 3. Automated & Manual Testing
- Write automated tests in `core/tests.py` covering all new behavior, edge cases, and constraints.
- Run the test suite:
  ```bash
  uv run python manage.py test
  ```
- Run Django system checks:
  ```bash
  uv run python manage.py check
  ```
- All tests must pass with zero errors and zero warnings before proceeding.

### 4. Verification Against Acceptance Criteria
- Verify that every item mentioned in the issue's goal and description is satisfied.
- If UI or endpoints are involved, run the development server:
  ```bash
  uv run python manage.py runserver
  ```
  Verify rendering, response status codes, and browser interaction as expected.

### 5. Commit and Push
- Stage only the files relevant to the completed task:
  ```bash
  git add <modified_files>
  ```
- Write a clear, imperative commit message referencing the issue number to close it:
  ```bash
  git commit -m "<Short summary of changes> (Closes #<issue_number>)"
  ```
- Push to origin:
  ```bash
  git push origin main
  ```
- Verify on GitHub that the issue automatically transitioned to `CLOSED`.
