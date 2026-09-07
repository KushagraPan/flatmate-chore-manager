# Backlog Tasks: Flatmate Chore Manager

## 1. Project Initialization & Base Test Suite
Goal: Scaffold the initial Django project structure with a verified passing test.
Description: Initialize the Django project named `chore_manager` alongside an application named `core` configured with SQLite. Create a basic smoke test in `core/tests.py` ensuring the test runner runs smoothly. Verify that running `python manage.py test` executes and passes cleanly.

## 2. Core Data Models (Roommate, Chore, ChoreLog)
Goal: Define and migrate the database schema for roommates, chores, and chore completion history.
Description: Implement the `Roommate` (name, color code, order index, active status), `Chore` (title, description, recurrence interval, next due date, current assignee), and `ChoreLog` (chore reference, completed-by roommate, completion timestamp) models in `core/models.py`. Generate and apply database migrations for SQLite. Write unit tests covering model creation, string representations, default values, and foreign key relationships.

## 3. Database Seed Command
Goal: Provide a reusable management command to populate the database with initial roommates and chores.
Description: Create a custom Django management command `seed_data` that sets up a default household with active flatmates and typical rotating chores across various recurrence intervals. Ensure the command runs idempotently so it can be executed safely multiple times during development or testing. Add automated tests that run the management command and assert that the expected database records are created.

## 4. Roommate Profile Switcher & Session Management
Goal: Enable users to switch their active roommate identity without authentication via a session-backed switcher.
Description: Implement an HTTP endpoint and a Django context processor that stores and retrieves the active `Roommate` ID in the session. Provide template navigation components allowing one-click profile switching from any page in the application. Write tests verifying that session data updates upon selection and defaults gracefully when no profile is selected.

## 5. Main Dashboard View
Goal: Build the primary dashboard displaying chores split into personal tasks and household-wide tasks.
Description: Create a responsive dashboard view rendered with Tailwind CSS that displays two main sections: "My Chores" (chores assigned to the currently selected roommate) and "All Household Chores". Integrate the active roommate context so the view reacts dynamically to the selected profile. Add view tests verifying correct template rendering and chore list segregation.

## 6. Chore CRUD Operations
Goal: Allow flatmates to create, view, edit, and archive chores through web forms.
Description: Build Django forms and views for chore creation, detail editing, and archiving tasks that should no longer rotate. Include inputs for chore title, description, recurrence interval (Daily, Weekly, Bi-weekly, Monthly), initial assignee, and due date. Write unit and integration tests validating form submission, validation error handling, and database persistence.

## 7. Automated Round-Robin Rotation Engine
Goal: Automatically advance chore assignment to the next flatmate and recalculate due dates upon completion.
Description: Implement a "Mark Done" action that records an entry in `ChoreLog`, shifts the chore's `current_assignee` to the next active roommate in `order_index` sequence (wrapping to the beginning when reaching the end), and advances `next_due_date` according to the recurrence interval. Handle edge cases such as single-roommate households and inactive flatmates. Write tests thoroughly verifying the rotation cycle and due date calculation for each recurrence frequency.

## 8. Visual Status Hierarchy & Overdue Nag Banner
Goal: Add visual indicators for chore urgency and a persistent nag banner for overdue chores.
Description: Compute status states for chores (Upcoming if due in >24 hours, Due Today if due within 24 hours, Overdue if past deadline) and render corresponding color-coded badges in the UI. Display a high-visibility warning banner at the top of every page whenever one or more chores in the household are overdue. Write tests verifying status boundary logic and the presence of the alert banner when overdue chores exist.

## 9. Household Activity Feed
Goal: Display a chronological feed of recent chore completions to promote transparency.
Description: Query recent `ChoreLog` entries and render an activity feed on the dashboard showing who completed which chore and when. Include human-readable relative timestamps and friendly empty states when no activity has been logged. Add tests verifying feed ordering, log formatting, and output limits.
