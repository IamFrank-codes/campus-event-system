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

## Getting Started on Windows

The easiest way to run the complete system is to use the supplied
`start-all.bat` launcher. The launcher prepares every service and then starts
all five services on ports 8001–8005.

### Required project layout

Keep `start-all.bat` in the project root, at the same level as the five service folders:

```text
campus-event-system-main/
├── start-all.bat
├── start-all.ps1
├── user-service/
├── event-service/
├── booking-service/
├── notification-service/
└── review-services/
```

The launcher performs these steps for every service in order:

```text
1. Change into the service directory
2. Create the virtual environment with: python -m venv venv
3. Activate it with: venv/Scripts/activate
4. Install dependencies with: pip install -r requirements.txt
5. Start the service with: uvicorn main:app --reload --port <port>
```

### Option 1: Start by double-clicking

Open the project folder in Windows File Explorer and double-click:

```text
start-all.bat
```

The script opens a separate Command Prompt window for each service. Keep these windows open while using the system. If setup fails, the script stops and displays the error in the launcher window.

### Option 2: Start from the VS Code terminal

Open the project root in VS Code. Open a terminal using **Terminal → New Terminal**, then confirm that the terminal is in the project root. You can check the current folder with:

```bat
cd
```

Run the launcher with:

```bat
start-all.bat
```

Alternatively, from PowerShell run:

```powershell
./start-all.ps1
```

The launcher creates or reuses each service's virtual environment, installs its `requirements.txt`, and opens the five services in separate terminal windows. You do not need to activate all five environments manually when using the launcher.

### Service URLs

| Service | Port | API documentation |
|---|---:|---|
| User/Auth Service | 8001 | http://127.0.0.1:8001/docs |
| Event Service | 8002 | http://127.0.0.1:8002/docs |
| Booking Service | 8003 | http://127.0.0.1:8003/docs |
| Notification Service | 8004 | http://127.0.0.1:8004/docs |
| Review Service | 8005 | http://127.0.0.1:8005/docs |

### Manual setup if the launcher is not used

If you prefer to run a service manually, open a separate VS Code terminal for each service and use forward-slash paths:

```bat
cd user-service/
python -m venv venv
venv/Scripts/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

Repeat the same sequence for `event-service/`, `booking-service/`, `notification-service/`, and `review-services/`, changing the port to 8002, 8003, 8004, and 8005 respectively.

For testing instructions and the suggested end-to-end demo flow, see
**[EXECUTION.md](./EXECUTION.md)**.

---



## Production deployment

Copy `.env.example` to `.env`, set a strong `JWT_SECRET_KEY`, set `POSTGRES_PASSWORD`, and review `ALLOWED_HOSTS`. Run the stack with `docker compose up --build`. Production mode rejects the development JWT secret and SQLite.

All state-changing routes require a bearer token. Organizer/admin roles are required for event management, students create bookings and reviews, and users cannot change their own roles. Service URLs and database URLs are configurable through environment variables.

### Notification API

The Notification Service is separate from the Booking Service. Its primary endpoints are `POST /api/notifications/send`, `GET /api/notifications/user/{user_id}`, and `PATCH /api/notifications/{notification_id}/read`. Notifications store a target user, optional event, notification type, message, read state, and creation timestamp.

## Running tests on Windows

Do not run `pytest -v` from the project root. Every service currently contains a file named `test_main.py`, so root-level pytest collection can report an `import file mismatch`. Also, each service has its own dependencies and virtual environment.

Use the supplied test runner from the project root instead:

```bat
run-tests-all.bat
```

This runner does not install or upgrade packages. It only runs pytest with each service's existing interpreter. Install dependencies first with `start-all.bat` or the manual setup commands. The runner uses commands such as:

```bat
user-service/venv/Scripts/python.exe -m pytest -v
```

To run one service manually, first deactivate any currently active environment, then activate the correct service environment:

```powershell
deactivate
cd user-service/
venv/Scripts/activate
python.exe -m pip install --upgrade pip
pip install -r requirements.txt
python.exe -m pytest -v
```

The `email-validator` package is included in `user-service/requirements.txt`. If the User Service reports `ModuleNotFoundError: No module named 'email_validator'`, the wrong virtual environment is active or the User Service requirements have not yet been installed. Run the commands above from `user-service/`.

### Removing the Starlette test-client warning

If pytest still reports `Using httpx with starlette.testclient is deprecated`, the existing virtual environments were created before `httpx2` was added. Run the one-time repair script from the project root:

```bat
fix-test-warnings.bat
```

After it finishes, run the tests without installing anything:

```bat
run-tests-all.bat
```

### Markdown test evidence

Run the test runner from the project root:

```bat
run-tests-all.bat
```

The runner does not install packages. It runs every service with its existing virtual environment and saves all commands and complete pytest output to:

```text
test-results.md
```

At the end of that Markdown file, the runner writes the summary in this format:

```text
User/Auth Service:     9 passed
Event Service:         9 passed
Booking Service:      10 passed
Notification Service:  6 passed
Review Service:       10 passed
--------------------------------
Total:                44 passed
Warnings:              0
```

The actual numbers are calculated from the test run and may change if a test fails or is skipped. Use the generated `test-results.md` as testing evidence in the report.

### Swagger authentication

For the Swagger **Authorize** button, use the OAuth2 password flow. Enter the registered email address in the `username` field, the registration password in the `password` field, and leave `client_id` and `client_secret` blank. The OAuth2 token endpoint is `/api/auth/token`.

The service also retains the JSON login endpoint `/api/auth/login` for clients that send:

```json
{
  "email": "your-email@example.com",
  "password": "your-password"
}
```

After successful authorization, call `GET /api/users/me` without a path parameter. Swagger sends the bearer token automatically and the endpoint returns the profile belonging to that token.

The technical OAuth2 endpoint `/api/auth/token` is hidden from the visible Swagger operation list. It remains available internally for the Swagger Authorize flow so protected endpoints can still be tested securely. The normal client-facing login endpoint remains `/api/auth/login`.

## Postman Testing

The project includes a complete Postman collection and local environment in the `postman/` folder:

```text
postman/Campus-Event-System.postman_collection.json
postman/Campus-Event-System.local.postman_environment.json
```

Import both files into Postman. Select **Campus Event System - Local** as the active environment. Before running the collection, start all five services with `start-all.bat` and confirm that the health checks respond on ports 8001 through 8005.

In the active Postman environment, set these values before running the collection:

```text
organizer_email = a unique organizer email address
organizer_password = OrganizerPass123!
student_email = a unique student email address
student_password = StudentPass123!
```

The collection is organized in this order:

1. Health checks for all five services.
2. User registration and JSON login.
3. Organizer and student profile retrieval.
4. Event creation, listing, filtering, retrieval, and update.
5. Booking creation, duplicate-booking rejection, and booking lookups.
6. Notification creation, listing, and marking as read.
7. Review creation, review listing, and average-rating calculation.
8. Cleanup of the demonstration event, booking, and review.

The collection captures JWTs and generated IDs automatically into environment variables. It uses the normal JSON endpoint `POST /api/auth/login`; the Swagger-only OAuth2 helper is not required for Postman testing. Protected requests automatically use the captured bearer tokens.

Run the requests in order the first time because later requests depend on IDs captured by earlier requests. The collection’s test scripts check expected status codes and save the complete workflow evidence in Postman’s request history. Export screenshots of successful requests and error cases for the assignment report.
