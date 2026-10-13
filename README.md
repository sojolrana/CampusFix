# CampusFix

**A campus issue reporting and resolution platform built with FastAPI.**

CampusFix is a backend application designed to help students and university staff report campus problems, track their progress, and coordinate issue resolution.

The project is being developed incrementally to demonstrate practical backend engineering concepts, including asynchronous APIs, database design, authentication, testing, and deployment.

> **Project status:** Early development. The initial FastAPI application, PostgreSQL connection, user model, database migration, and initial schema tests have been implemented.

## Features

### Implemented
- FastAPI application with interactive API documentation.
- Environment-based application configuration.
- Asynchronous SQLAlchemy database engine.
- PostgreSQL database integration.
- Alembic database migrations.
- Initial user database model and role enumeration.
- Pydantic user creation and response schemas.
- Initial automated tests with pytest.

### Planned
- User registration and secure password hashing.
- JWT-based authentication.
- Role-based access control for students, staff, and administrators.
- Campus issue creation, assignment, and status tracking.
- Comments and issue activity history.
- Search, filtering, and pagination.
- Administrative dashboard and statistics.
- Comprehensive automated tests.
- Docker-based development and deployment.

## Technology Stack

- **Language:** Python
- **API framework:** FastAPI
- **ASGI server:** Uvicorn
- **Validation and settings:** Pydantic, pydantic-settings
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy 2.x (async)
- **PostgreSQL driver:** Psycopg 3
- **Migrations:** Alembic
- **Testing:** pytest, HTTPX
- **Version control:** Git

## Project Structure

```text
campusfix/
├── alembic/
│   └── versions/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/
│   ├── core/
│   │   └── config.py
│   ├── db/
│   │   ├── base.py
│   │   └── session.py
│   ├── enums/
│   │   └── user_role.py
│   ├── models/
│   │   └── user.py
│   ├── repositories/
│   ├── schemas/
│   │   ├── base.py
│   │   └── user.py
│   ├── services/
│   └── main.py
├── tests/
├── .env.example
├── .gitignore
├── alembic.ini
├── requirements.txt
└── README.md
```

The structure will evolve as additional application features are implemented.

## Prerequisites

- Python 3.14 or another compatible Python version.
- PostgreSQL.
- Git.
- A terminal and a code editor.

The commands below assume Ubuntu and a local PostgreSQL installation.

## Local Development Setup

### 1. Clone the repository

```bash
git clone git@github.com:YOUR_GITHUB_USERNAME/campusfix.git
cd campusfix
```

Replace `YOUR_GITHUB_USERNAME` with your GitHub username.

### 2. Create and activate a virtual environment

```bash
python3 -m venv fastapi
source fastapi/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Create your local environment file:

```bash
cp .env.example .env
```

Edit `.env` and configure the application settings and PostgreSQL connection URL.

Example:

```dotenv
APP_NAME=CampusFix
APP_ENV=development
DEBUG=true
API_V1_PREFIX=/api/v1
DATABASE_URL=postgresql+psycopg://campusfix_user:YOUR_PASSWORD@localhost:5432/campusfix_db
```

Replace `YOUR_PASSWORD` with your local PostgreSQL user's password. Never commit `.env` or production credentials.

### 5. Configure PostgreSQL

Create a PostgreSQL database and a dedicated application user, then grant the user ownership of the application database.

Ensure that `DATABASE_URL` in `.env` matches your local configuration.

### 6. Apply database migrations

```bash
alembic upgrade head
```

### 7. Start the development server

```bash
uvicorn app.main:app --reload
```

The API will be available at:

- API root: http://127.0.0.1:8000/
- Health check: http://127.0.0.1:8000/health
- Interactive API documentation: http://127.0.0.1:8000/docs
- Alternative API documentation: http://127.0.0.1:8000/redoc

### 8. Run automated tests

```bash
python -m pytest -v
```

## Architecture

CampusFix follows a layered backend architecture:

- **API endpoints:** Handle HTTP requests and responses.
- **Schemas:** Validate input and define response data.
- **Services:** Implement application and business rules.
- **Repositories:** Encapsulate database queries and persistence.
- **Models:** Represent database tables.
- **Core:** Holds shared configuration and security functionality.

Asynchronous functions are used where asynchronous I/O is required, including database operations.

## Security Notes

- Passwords must be hashed before storage.
- Sensitive configuration must remain outside version control.
- API authorization must be enforced on protected operations.
- Database credentials should use a dedicated application account.
- Debugging and SQL query logging must be configured appropriately for each environment.

## Development Roadmap

- [x] Initial FastAPI application.
- [x] Environment-based configuration.
- [x] PostgreSQL and asynchronous SQLAlchemy setup.
- [x] Initial user model and migration.
- [x] Initial Pydantic schemas and tests.
- [ ] Registration and password hashing.
- [ ] Authentication and authorization.
- [ ] Issue management and assignment.
- [ ] Comments and activity history.
- [ ] Expanded test coverage.
- [ ] Containerization and deployment.

## Contributing

Contributions, suggestions, and bug reports are welcome. Please open an issue to discuss substantial changes before submitting a pull request.

## License

No license has been selected yet. Until a license is added, the source code is not granted an open-source license by default.
