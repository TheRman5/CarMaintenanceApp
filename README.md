# CarMaintenanceApp
# Car Maintenance Tracker: Refined MVP Blueprint

Based on your decisions, I recommend building a mobile-friendly web application using Next.js, FastAPI, and PostgreSQL, with an AI maintenance assistant, email/SMS reminders, manual mileage tracking, and a dashboard with one-click light/dark mode switching.

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

I would defer receipt scanning, OBD-II integration, advanced cost analytics, mobile apps, and multi-user collaboration until after the MVP.

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

## My Garage

Maintenance overview
