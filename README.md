# CarMaintenanceApp
# Car Maintenance Tracker: Refined MVP Blueprint

A mobile-friendly web application using Next.js, FastAPI, and PostgreSQL, with an AI maintenance assistant, email/SMS reminders, manual mileage tracking, and a dashboard with one-click light/dark mode switching.

The application will initially support one vehicle and one account, but its architecture will support multiple vehicles and users without a major redesign.

## 1. Finalized MVP scope

PROJECT DEFINITION

# Garage Maintenance Tracker

Working project name

MVP scope

Platform

Responsive web

Vehicles at launch

1

Notifications

Email + SMS

AI

Suggestions + logging

Mileage

Manual entry

Appearance

Light + dark

### Core requirements

| Module               | MVP requirements                                                            |
| -------------------- | --------------------------------------------------------------------------- |
| Dashboard            | Current vehicle, mileage, overdue tasks, upcoming services, recent activity |
| Vehicle profile      | Year, make, model, trim, engine, optional VIN, mileage                      |
| Maintenance tracking | Add, edit, complete, delete, and view maintenance tasks                     |
| Service history      | Date, mileage, service type, cost, notes, optional parts                    |
| Recurrence           | Calendar intervals, mileage intervals, or whichever occurs first            |
| Reminders            | Email and SMS, customizable lead times                                      |
| AI assistant         | Suggest services and interpret natural-language maintenance entries         |
| Theme                | Light/dark toggle, saved preference, system default                         |
| Authentication       | One authenticated user, extensible to multiple accounts                     |

Defering receipt scanning, OBD-II integration, advanced cost analytics, mobile apps, and multi-user collaboration until after the MVP.

## 2. Application architecture

Next.js + TypeScript

Dashboard • Forms • Theme • AI chat

Authenticated HTTPS API

FastAPI Backend

Maintenance logic • AI orchestration • Notifications

PostgreSQL

Vehicles, tasks, records

OpenAI API

Suggestions, structured logging

Resend

Email delivery

Twilio

SMS delivery

Scheduled background worker

Checks due tasks, queues messages, records delivery outcomes

### Recommended infrastructure

- Frontend: Next.js App Router, TypeScript, Tailwind CSS, shadcn/ui.
- Backend: Python 3.12+, FastAPI, SQLAlchemy, Alembic, Pydantic.
- Database and authentication: Supabase PostgreSQL and Supabase Auth.
- AI: OpenAI API using structured outputs for maintenance entries and recommendations.
- Email and SMS: Resend and Twilio.
- Deployment: Vercel for the frontend and a Python-compatible hosting service for the backend and scheduled worker.
- Testing: Pytest for backend logic and Playwright for end-to-end workflows.

Use Supabase Auth tokens for API authentication, with FastAPI verifying each request and enforcing vehicle ownership. Store API keys exclusively on the server.

## 3. Dashboard and theme behavior

The dashboard should prioritize tasks requiring action instead of showing large amounts of vehicle information.

## Contributing

Contributions are welcome! Whether you're fixing a bug, improving existing functionality, adding a feature, or updating documentation, your help is appreciated.

Please follow the guidelines below to keep the development process organized and maintain code quality.

### 1. Report Bugs and Suggest Improvements

- If you discover a bug, identify something that could be improved, or have an idea for a new feature, **open a GitHub Issue**.
- Before creating an issue, check existing issues to avoid duplicates.
- Provide a clear description of the problem or suggestion, including relevant details, screenshots, or steps to reproduce when applicable.
- For major features or architectural changes, open an issue to discuss the proposed approach before beginning development.

### 2. Making Contributions

If you would like to work on an existing issue or implement a proposed improvement:

1. **Choose an issue:** Find an existing issue you want to address, or create a new one describing your proposed change.
2. **Clone the repository:** Clone the project to your local development environment.
3. **Create a branch:** Create a new feature or bugfix branch based on the latest `dev` branch.
4. **Make your changes:** Implement your solution while following the project's existing coding conventions.
5. **Test your changes:** Verify that your changes work as intended and do not break existing functionality.
6. **Push your branch:** Push your changes to GitHub.
7. **Open a Pull Request:** Submit a pull request targeting the **`dev` branch** for review. Reference the issue your changes resolve.

When submitting a pull request, include a brief summary of your changes, any relevant testing information, and the associated issue number.

### 3. Branching Guidelines

To maintain a stable codebase, please follow these conventions:

- **`main`**: Stable, production-ready code.
- **`dev`**: Active development and integration branch. All contributions should target this branch for review.

**Do not push directly to `main`.** All changes should go through a pull request and be reviewed before merging.

### 4. Code Quality and Best Practices

- Keep changes focused on the issue or feature being addressed.
- Follow the existing project structure, naming conventions, and formatting standards.
- Write readable, maintainable code with comments where additional explanation is necessary.
- Avoid introducing unnecessary dependencies.
- Remove debugging statements, unused code, and temporary files before submitting a pull request.
- Update relevant documentation when adding or modifying functionality.
- Never commit API keys, passwords, credentials, or other sensitive information.
- Use descriptive commit messages that clearly explain the changes made.

### 5. Pull Request Review Process

- All pull requests should target the `dev` branch.
- Pull requests will be reviewed for correctness, maintainability, code quality, and compatibility with existing functionality.
- Additional changes may be requested before approval.
- Keep your pull request updated if changes are requested during review.
- Once approved, contributions will be merged into `dev`.
- Changes will be integrated into `main` when they are tested and ready for release.

### 6. General Guidelines

- Be respectful and constructive when discussing issues, proposing changes, or reviewing contributions.
- Avoid unrelated changes within the same pull request.
- Prefer improvements that maintain simplicity, performance, security, and long-term maintainability.
- If you're unsure whether a change fits the project's goals, open an issue and discuss it before implementing.

Thank you for helping improve this project!
