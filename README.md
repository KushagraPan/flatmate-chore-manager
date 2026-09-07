# Flatmate Chore Manager

A lightweight, frictionless web application designed for shared apartments and roommates to manage household chores fairly and transparently.

---

## Overview

Dividing chores among flatmates often leads to misunderstandings, forgotten tasks, and awkward reminders. The **Flatmate Chore Manager** automates chore rotation using a cyclic round-robin mechanism, keeps everyone accountable via visual overdue alerts and an activity feed, and eliminates login friction with a quick profile switcher.

---

## Features

- **Automated Round-Robin Rotation**: When a chore is marked done, it automatically re-assigns to the next flatmate in sequence and advances the due date.
- **Low-Friction Profile Switcher**: Switch between roommate profiles with a single click in the top bar (stored in session; no passwords or sign-up needed).
- **Honor System Completion**: Simple "Mark as Done" action without complicated photo uploads or verification gates.
- **Visual Overdue Nags**: 
  - 🟢 **Upcoming**: Due in more than 24 hours.
  - 🟡 **Due Today**: Due within 24 hours.
  - 🔴 **Overdue**: Highlighted with warning badges and top-of-page nag banners.
- **Activity Feed**: Real-time log displaying recent chore completions across the household.

---

## Tech Stack

- **Backend**: Python 3, Django
- **Database**: SQLite
- **Frontend**: Django Templates + Tailwind CSS (via CDN)
- **Session**: Django Session Framework

---

## Project Structure

```text
flatmate-chore-manager/
├── manage.py
├── pyproject.toml
├── uv.lock
├── core/                   # Main chore tracking app
│   ├── models.py           # Roommate, Chore, ChoreLog models
│   ├── views.py            # Dashboard, mark_done, profile switcher
│   ├── urls.py
│   └── templates/          # Server-rendered HTML templates
├── chore_manager/          # Django project configuration
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── .gitignore
└── README.md
```

---

## Getting Started

### Prerequisites
- Python 3.10+
- [uv](https://docs.astral.sh/uv/)

### Installation & Setup

1. **Navigate to the project directory**:
   ```bash
   cd flatmate-chore-manager
   ```

2. **Sync dependencies**:
   ```bash
   uv sync
   ```

3. **Apply database migrations**:
   ```bash
   uv run python manage.py migrate
   ```

4. **Run the development server**:
   ```bash
   uv run python manage.py runserver
   ```

5. **Run test suite**:
   ```bash
   uv run python manage.py test
   ```

6. **Open in browser**:
   Visit [http://127.0.0.1:8000](http://127.0.0.1:8000) to view the application.

---

## Specification & Roadmap

For full functional specifications, data models, and the implementation roadmap, refer to [_docs/plan.md](_docs/plan.md).
