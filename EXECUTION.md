# Execution Instructions

Step-by-step instructions to set up, run, and test the Campus Event
Management System locally.

---

## Table of Contents

- [Cloning the Repository](#cloning-the-repository)
- [Prerequisites](#prerequisites)
- [Setup Instructions](#setup-instructions)
- [Running the System](#running-the-system)
- [Running Tests](#running-tests)
- [API Documentation](#api-documentation)
- [Environment Variables](#environment-variables)

---

## Cloning the Repository

If you don't already have the project on your machine, clone it from
GitHub first.

**1. Make sure Git is installed:**

```bash
git --version
```

If this returns an error, install Git from
[git-scm.com](https://git-scm.com/downloads) first.

**2. Choose a folder where you want the project to live, then clone it:**

```bash
git clone https://github.com/IamFrank-codes/campus-event-system.git
```

This downloads the full project into a new folder called
`campus-event-system`.

**3. Move into the project folder:**

```bash
cd campus-event-system
```

**4. Confirm you have all five service folders:**

```bash
dir
```

(On Mac/Linux, use `ls` instead of `dir`.) You should see
`user-service`, `event-service`, `booking-service`,
`notification-service`, and `review-service` listed, along with this
`EXECUTION.md` file and the root `README.md`.

You're now ready to continue with the [Prerequisites](#prerequisites)
and [Setup Instructions](#setup-instructions) below.

> **Note:** Cloning only downloads the source code — it does **not**
> download each service's `venv/` folder or `.db` database files, since
> those are intentionally excluded via `.gitignore`. You'll create your
> own virtual environments locally in the next step.

---

## Prerequisites

Before starting, make sure you have installed:

- **Python 3.10 or higher** — check with `python --version`
- **pip** — check with `pip --version`
- **Git** — check with `git --version`

---

## Setup Instructions

Each of the five services must be set up **individually**, since each has
its own isolated virtual environment. Repeat the following for
`user-service`, `event-service`, `booking-service`,
`notification-service`, and `review-service`:

```bash
# 1. Navigate into the service folder
cd <service-name>

# 2. Create a virtual environment
python -m venv venv

# 3. Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt
```

Repeat this for all five service folders before attempting to run the
system.

---

## Running the System

Because each service is independent, running the full system means
starting **all five services at the same time**, each in its own
terminal tab, each on its own port.

Open five separate terminal tabs in VS Code. In each one:

```bash
# Terminal 1 — User / Auth Service
cd user-service
venv\Scripts\activate
uvicorn main:app --reload --port 8001

# Terminal 2 — Event Service
cd event-service
venv\Scripts\activate
uvicorn main:app --reload --port 8002

# Terminal 3 — Booking Service
cd booking-service
venv\Scripts\activate
uvicorn main:app --reload --port 8003

# Terminal 4 — Notification Service
cd notification-service
venv\Scripts\activate
uvicorn main:app --reload --port 8004

# Terminal 5 — Review Service
cd review-service
venv\Scripts\activate
uvicorn main:app --reload --port 8005
```

Once all five are running, each has its own interactive API documentation
page in the browser (see [API Documentation](#api-documentation) below).

### Suggested demo flow

1. Register a user with role `organizer` via the User Service
2. Register a second user with role `student`
3. Log in as the organizer, copy the access token
4. Create an event via the Event Service (this calls the User Service
   behind the scenes to confirm the organizer is valid)
5. Book the student into that event via the Booking Service (this calls
   both the User Service and the Event Service)
6. Send a booking confirmation via the Notification Service
7. Leave a review for the event via the Review Service, then check the
   average rating endpoint

---

## Running Tests

Each service has its own independent test suite. With that service's
virtual environment active:

```bash
cd <service-name>
pytest -v
```

Run this separately in each of the five service folders. Every service
includes tests covering successful operations, validation errors, and
edge cases (e.g. duplicate bookings, full events, invalid tokens).

Services that depend on other services (Event, Booking) use **mocked**
responses during testing, so their test suites run independently without
needing the other services to be live.

---

## API Documentation

Once a service is running, its full interactive API documentation is
available automatically at:

- User / Auth Service: `http://127.0.0.1:8001/docs`
- Event Service: `http://127.0.0.1:8002/docs`
- Booking Service: `http://127.0.0.1:8003/docs`
- Notification Service: `http://127.0.0.1:8004/docs`
- Review Service: `http://127.0.0.1:8005/docs`

These pages allow every endpoint to be tested directly from the browser.

---

## Environment Variables

By default, the User/Auth service uses a development JWT secret key. For
anything beyond local testing, set your own before starting the service:

```bash
export JWT_SECRET_KEY="your-own-random-secret-string"
```

If this is not set, a placeholder development key is used automatically.
