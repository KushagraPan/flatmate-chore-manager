# Technical Architecture & Data Models: Flatmate Chore Manager

## 1. Technical Architecture & Stack

| Component | Technology | Rationale |
| :--- | :--- | :--- |
| **Backend** | Python 3 + Django | Built-in ORM, admin panel, robust routing, and form validation. |
| **Database** | SQLite | Zero-config, file-based, perfect for homework grading and demos. |
| **Frontend** | Django Templates + Tailwind/Bootstrap CSS | Server-rendered, no complex frontend build step required. |
| **State / Session** | Django Sessions | Remembers active roommate profile across pages. |

---

## 2. Data Models

```mermaid
erDiagram
    Roommate ||--o{ Chore : "currently assigned to"
    Roommate ||--o{ ChoreLog : "completed by"
    Chore ||--o{ ChoreLog : "has completion history"

    Roommate {
        int id PK
        string name
        string color_code
        int order_index
        boolean is_active
    }

    Chore {
        int id PK
        string title
        string description
        string recurrence_type
        date next_due_date
        int current_assignee_id FK
    }

    ChoreLog {
        int id PK
        int chore_id FK
        int completed_by_id FK
        datetime completed_at
    }
```
