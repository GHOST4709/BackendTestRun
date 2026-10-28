# TaskForge Backend

**TaskForge** is a fictional team workspace and task-management service built as a substantial learning backend for FastAPI and pytest. It is separate from DriveLegal and is designed for local development, API exploration, and practicing backend tests.

## Features

- FastAPI application factory and versioned `/api/v1` routes
- Registration, login, JWT bearer authentication, password hashing, and profile management
- Basic role-based access control (`user` and `admin`)
- Project CRUD, unique URL-friendly slugs, project membership management, and private-project access control
- Task CRUD with status/priority validation, project-member assignment, filters, pagination, and due dates
- Task comments with author/owner deletion rules
- Activity stream and user dashboard aggregates
- Health and database-readiness endpoints
- SQLAlchemy 2 ORM with SQLite by default; `DATABASE_URL` can point to another SQLAlchemy-supported database
- A local seed script with two users, an example project, sample tasks, comments, and activity
- Isolated pytest suite using an in-memory SQLite database so tests don't alter the normal `taskforge.db`
- Dockerfile, Makefile, environment template, and test/coverage commands

> **Learning project notice:** This is demo code, not a security-audited production service. Use a strong private `SECRET_KEY`, HTTPS, proper secrets management, database migrations, rate limiting, and a production-grade security review before deploying it publicly. The seed credentials are for local use only.

## Directory layout

```text
taskforge-backend/
├── app/
│   ├── api/routes/       # HTTP route modules
│   ├── core/             # Settings, auth dependencies, password/JWT helpers
│   ├── db/               # SQLAlchemy base, engine, and sessions
│   ├── models/           # ORM models: users, projects, tasks, comments, activity
│   ├── schemas/          # Request and response validation schemas
│   ├── services/         # Activity logging and project permissions
│   └── main.py           # FastAPI app factory and app entry point
├── scripts/seed_demo.py  # Populate a local demo database
├── tests/                # Feature tests grouped by API area
├── postman/              # Importable Postman collection
├── .github/workflows/    # Run pytest in GitHub Actions
├── test.py               # Root pytest smoke tests
├── pytest.ini
├── requirements.txt
├── .env.example
├── Dockerfile
├── Makefile
└── README.md
```

## 1. Create your environment

Python 3.10 or newer is recommended. From the project root:

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cp .env.example .env
```

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

The example environment uses SQLite and is suitable for local experiments. `python-dotenv` loads a `.env` file when the app is imported. Set a unique `SECRET_KEY` before anything beyond local testing.

## 2. Start the API

```bash
python -m uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

- Interactive Swagger docs: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- Liveness: `http://127.0.0.1:8000/health`
- Database readiness: `http://127.0.0.1:8000/health/ready`

The SQLite database file (`taskforge.db`) is created in the current working directory on application startup. Tests use an isolated in-memory database instead.

## 3. Seed sample data (optional)

Stop the server or keep it running, then in a second terminal from the project root run:

```bash
python -m scripts.seed_demo
```

Default local demo credentials:

| Role | Email | Password |
|---|---|---|
| Admin | `admin@taskforge.local` | `AdminPass123!` |
| User | `demo@taskforge.local` | `DemoPass123!` |

The seed command is idempotent for the sample project. Credentials can be overridden with `DEMO_ADMIN_EMAIL`, `DEMO_ADMIN_PASSWORD`, `DEMO_USER_EMAIL`, and `DEMO_USER_PASSWORD`. **Do not use these defaults for a public deployment.**

## 4. Run pytest

From the project root, with your virtual environment active:

```bash
python -m pytest -v
```

The root `test.py` contains smoke tests; feature tests are under `tests/`. Pytest collects both (74 tests at the time this demo was prepared). No running web server is needed. Each test gets a new app instance and an in-memory SQLite database, so the regular `taskforge.db` is not changed.

Run a single feature group:

```bash
python -m pytest -v tests/test_auth.py
python -m pytest -v tests/test_projects.py
python -m pytest -v tests/test_tasks.py
python -m pytest -v tests/test_comments_dashboard.py
```

Run coverage:

```bash
python -m coverage run -m pytest
python -m coverage report -m
```

If you use `make`, these shortcuts are available:

```bash
make install
make run
make test
make coverage
make seed
```

## API route catalogue

All business endpoints are prefixed with `/api/v1`.

| Method | Route | Auth | Purpose |
|---|---|---|---|
| GET | `/health` | No | Liveness probe |
| GET | `/health/ready` | No | Database readiness probe |
| POST | `/auth/register` | No | Create a user |
| POST | `/auth/login` | No | Login and receive a JWT |
| GET | `/auth/me` | Yes | Current user from JWT |
| GET | `/users/me` | Yes | View profile |
| PATCH | `/users/me` | Yes | Update display name |
| GET | `/users/` | Admin | List users |
| GET / POST | `/projects/` | Yes | List visible projects / create one |
| GET / PATCH / DELETE | `/projects/{project_id}` | Yes | Read/update/delete project (owner/admin for writes) |
| POST | `/projects/{project_id}/members` | Owner/admin | Add a member |
| DELETE | `/projects/{project_id}/members/{member_id}` | Owner/admin | Remove a member |
| GET / POST | `/tasks/` | Yes | List/create tasks |
| GET / PATCH / DELETE | `/tasks/{task_id}` | Yes | Read/update/delete a task (owner/admin for deletion) |
| GET / POST | `/tasks/{task_id}/comments` | Yes | List/create task comments |
| DELETE | `/comments/{comment_id}` | Yes | Delete own comment, or as owner/admin |
| GET | `/dashboard/summary` | Yes | Task/project aggregates |
| GET | `/dashboard/projects` | Yes | Per-project task counts |
| GET | `/dashboard/activity` | Yes | Recent activity feed |

Task list query parameters include `project_id`, `status`, `priority`, `assignee_id`, `limit` (1–100), and `offset` (0 or more). Valid statuses are `todo`, `in_progress`, `blocked`, and `done`; valid priorities are `low`, `medium`, `high`, and `urgent`.

## 5. Explore the API with Postman

Import `postman/TaskForge.postman_collection.json` into Postman. Start the API, then run the **Login (save token)** request. It stores the returned JWT in the collection `token` variable and subsequent requests include it as a bearer token. If you seeded the database, the default collection credentials match the local demo admin. The collection includes health checks, auth/profile, projects, membership, tasks, comments, and dashboard routes. You can change the collection variables for `baseUrl`, `email`, and `password`.

## 6. GitHub Actions

The workflow at `.github/workflows/tests.yml` installs `requirements.txt` and runs `python -m pytest -v` on pushes and pull requests. The local command is the same as the CI command, which makes failures easier to reproduce.

## Example: register, login, and create a project

Register:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"you@example.com","display_name":"Your Name","password":"SecurePass123!"}'
```

Login (copy `access_token` from the response):

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"you@example.com","password":"SecurePass123!"}'
```

Create a project using the token:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/projects/ \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN' \
  -d '{"title":"My First Project","description":"Trying TaskForge"}'
```

## Notes for learning

- `app/main.py` exposes `create_app()` so tests can create isolated instances with a test database.
- `app/db/session.py` wires request-scoped SQLAlchemy sessions through FastAPI dependencies.
- `app/core/security.py` contains an explicit PBKDF2 password hash and JWT helpers so you can follow the mechanics. For production, prefer a mature password-hashing library and secret rotation process.
- `app/services/permissions.py` centralizes private-project visibility and ownership rules.
- `app/services/activity.py` centralizes activity recording so routes don't duplicate the persistence details.
- Pydantic schemas validate request payloads and omit password hashes from user API responses.
