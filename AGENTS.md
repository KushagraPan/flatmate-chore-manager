# AGENTS.md

## Project Overview
The **Flatmate Chore Manager** is a lightweight, web-based household chore tracking application built with **Django**, **SQLite**, and **Tailwind CSS** (via CDN). Its core purpose is to eliminate roommate friction by providing:
- **Automated Round-Robin Rotation**: Chores automatically reassign to the next active flatmate upon completion and advance the next due date.
- **Session-Based Profile Switcher**: Fast, one-click identity switcher in the navigation bar stored in Django sessions (no passwords, accounts, or auth screens).
- **Visual Status Hierarchy & Nag Banner**: Color-coded urgency indicators (🟢 Upcoming >24h, 🟡 Due Today <=24h, 🔴 Overdue) and a persistent top-of-page nag banner for overdue tasks.
- **Household Activity Feed**: Chronological completion history log.

### Explicitly Out of Scope
- No user authentication, passwords, or JWT tokens.
- No photo upload proofs or verification approval gates.
- No external notifications (no email, SMS, or webhooks).
- No financial or expense-tracking systems.

---

## Tech Stack & Environment
- **Language**: Python 3.10+ (running on Python 3.12 via `uv`)
- **Framework**: Django 5.x
- **Database**: SQLite (`db.sqlite3`)
- **Frontend**: Server-rendered Django Templates + Tailwind CSS (CDN)
- **Package & Environment Manager**: `uv` (do not use raw `pip` or standard `python -m venv`)

---

## Essential Commands
Always use `uv run` to execute commands within the project environment:

| Action | Command |
| :--- | :--- |
| **Run Test Suite** | `uv run python manage.py test` |
| **Django System Check** | `uv run python manage.py check` |
| **Start Dev Server** | `uv run python manage.py runserver` |
| **Make Migrations** | `uv run python manage.py makemigrations` |
| **Apply Migrations** | `uv run python manage.py migrate` |
| **Django Shell** | `uv run python manage.py shell` |
| **Add Dependency** | `uv add <package>` |

---

## Development Guidelines for Agents
1. **Single-Task Focus**: Work on one task/issue at a time as outlined in `_docs/process.md`.
2. **Strict Scope Control**: Do not add unrequested features or over-engineer abstractions. Keep models and views aligned with `_docs/architecture.md`.
3. **No Auth Inventions**: Keep roommate identity purely session-driven. Never introduce authentication models, login redirects, or password fields.
4. **Test-First Verification**: Every change must maintain or increase test coverage. Run `uv run python manage.py test` before and after modifications.
5. **Dependency Integrity**: Use `uv` exclusively. Never commit unmanaged dependencies or bypass `uv.lock`.

---

## Documentation Index
- `_docs/plan.md`: Comprehensive product specification, functional requirements, and roadmap.
- `_docs/architecture.md`: Data models, ER diagrams, and technical architecture.
- `_docs/backlog.md`: Detailed backlog tasks corresponding to GitHub issues.
- `_docs/process.md`: Step-by-step developer workflow from issue pick-up to commit/push.
- `README.md`: High-level project summary, directory structure, and setup notes.
