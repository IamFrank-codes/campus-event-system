# Campus Event Management System

A service-oriented backend for managing campus events, built as five
independent REST API microservices. Students can register, browse events,
book a spot, receive notifications, and leave reviews after attending.

Built for **NADV 744 — Advanced Development Systems**

---

## Architecture Overview

The system consists of five independent microservices, each with its own
database, communicating over REST APIs:

| Service | Port | Responsibility |
|---|---|---|
| **User / Auth Service** | 8001 | Registration, login, JWT authentication, user profiles |
| **Event Service** | 8002 | Create, list, update, and delete campus events |
| **Booking Service** | 8003 | Book a spot at an event, enforce capacity limits, cancellations |
| **Notification Service** | 8004 | Create, list, and mark simulated booking/event notifications as read |
| **Review Service** | 8005 | Post-event ratings and comments |

Two services genuinely depend on others to do their job, demonstrating
real service-oriented communication:

- **Booking Service** calls the **User Service** (to verify the student
  exists) and the **Event Service** (to verify the event exists and has
  capacity) before confirming a booking.
- **Event Service** calls the **User Service** to verify that whoever
  creating an event is a registered organizer or admin.
- **Notification Service** verifies the target user and optional event before
  storing a notification, then exposes user-specific notification retrieval
  and mark-as-read operations.

Each service can be started, stopped, and tested completely independently
of the others.

---

## Tech Stack

- **Language:** Python 3.13
- **Framework:** FastAPI
- **Database:** SQLite (one independent database file per service)
- **Authentication:** JWT (JSON Web Tokens), passwords hashed with bcrypt
- **Inter-service communication:** REST over HTTP, via `httpx`
- **Testing:** pytest, FastAPI's `TestClient`
- **Version control:** Git / GitHub

---

## Project Structure

```
campus-event-system/
├── README.md                  <- you are here
├── EXECUTION.md                <- full setup & run instructions
├── .gitignore
├── user-service/
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── database.py
│   ├── auth.py
│   ├── test_main.py
│   ├── requirements.txt
│   └── README.md
├── event-service/
│   └── (same pattern)
├── booking-service/
│   └── (same pattern)
├── notification-service/
│   └── (same pattern)
└── review-service/
    └── (same pattern)
```

Each service folder is self-contained: its own virtual environment, its
own dependencies, its own database file, and its own test suite.

---

## Getting Started

For full step-by-step setup, run, and test instructions, see
**[EXECUTION.md](./EXECUTION.md)**.

Quick summary:

1. Set up each service's virtual environment and install its dependencies
2. Start all five services at once, each in its own terminal, each on its
   own port (8001–8005)
3. Use each service's `/docs` page to interact with it, or follow the
   suggested demo flow in EXECUTION.md

---



## Production deployment

Copy `.env.example` to `.env`, set a strong `JWT_SECRET_KEY`, set `POSTGRES_PASSWORD`, and review `ALLOWED_HOSTS`. Run the stack with `docker compose up --build`. Production mode rejects the development JWT secret and SQLite.

All state-changing routes require a bearer token. Organizer/admin roles are required for event management, students create bookings and reviews, and users cannot change their own roles. Service URLs and database URLs are configurable through environment variables.

### Notification API

The Notification Service is separate from the Booking Service. Its primary endpoints are `POST /api/notifications/send`, `GET /api/notifications/user/{user_id}`, and `PATCH /api/notifications/{notification_id}/read`. Notifications store a target user, optional event, notification type, message, read state, and creation timestamp.
