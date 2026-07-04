# AIvora Backend

SaaS AI Document Intelligence Platform — Backend API

## Architecture

Clean Architecture + Domain-Driven Design (DDD) + SOLID + Twelve-Factor App.

```
Domain → Application → Infrastructure → API
```

| Layer | Path | Responsibility |
|-------|------|----------------|
| Domain | `app/domain/` | Entities, value objects, domain events, repo interfaces |
| Application | `app/application/` | Use-case command/query handlers |
| Infrastructure | `app/infrastructure/` | ORM, DB, Redis, ES, AI, Storage, Celery |
| API | `app/api/` | FastAPI routers, Pydantic schemas, DI |
| Services | `app/services/` | Thin coordinators between API and use-cases |

## Tech Stack

| Technology | Version | Purpose |
|-----------|---------|---------|
| Python | 3.13+ | Runtime |
| FastAPI | 0.115+ | Web framework |
| Pydantic v2 | 2.10+ | Validation |
| SQLAlchemy 2.0 | 2.0+ | ORM (async) |
| Alembic | 1.14+ | DB migrations |
| PostgreSQL | 16 | Primary database |
| Redis | 7 | Cache + Celery broker |
| Elasticsearch | 8 | Document search + vector storage |
| Celery | 5.4+ | Async task queue |
| JWT | via python-jose | Authentication |
| OpenTelemetry | 1.29+ | Observability |
| Docker | 24+ | Containerization |

## Project Structure

```
AIvora_Backend/
├── app/
│   ├── api/v1/          # Versioned HTTP routers (auth, users, docs, chat…)
│   ├── application/     # Use-case handlers (commands/queries)
│   ├── config/          # Environment-based settings (Pydantic BaseSettings)
│   ├── core/            # App factory, lifespan, logging, telemetry
│   ├── dependencies/    # FastAPI DI: db session, auth, RBAC, pagination
│   ├── domain/          # Pure domain: entities, value objects, events, interfaces
│   ├── exceptions/      # Custom exceptions + global handlers
│   ├── infrastructure/  # DB, Redis, ES, AI, Storage, Celery adapters
│   ├── middleware/       # CORS, rate limit, security headers, request ID
│   ├── repositories/    # Concrete SQLAlchemy repo implementations
│   ├── schemas/         # Pydantic v2 request/response models
│   ├── security/        # JWT, password hashing, token models
│   ├── services/        # Service layer (coordinates use-cases)
│   ├── tasks/           # Celery task definitions
│   ├── utils/           # Pure helpers: pagination, datetime, responses
│   ├── workers/         # Celery worker bootstrap
│   └── main.py          # Application entrypoint
├── alembic/             # DB migrations
├── tests/               # Pytest test suite
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── Makefile
└── .env.example
```

## Quick Start (Local)

### Prerequisites
- Python 3.13+
- Docker & Docker Compose

### 1. Clone and setup

```bash
git clone <repo>
cd AIvora_Backend
cp .env.example .env
make install-dev
```

### 2. Start infrastructure services

```bash
make docker-up
```

### 3. Run migrations

```bash
make migrate
```

### 4. Start development server

```bash
make dev
```

### 5. Open docs

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health: http://localhost:8000/api/v1/health

## Available Commands

```bash
make dev            # Start dev server
make worker         # Start Celery worker
make test           # Run tests
make lint           # Run ruff linter
make format         # Run ruff formatter
make type-check     # Run mypy
make migrate        # Apply DB migrations
make docker-up      # Start all Docker services
make docker-down    # Stop all Docker services
make help           # Show all commands
```

## Environment Variables

See [`.env.example`](.env.example) for a full list with descriptions.

## API Versioning

All endpoints are under `/api/v1/`. Future versions will add `/api/v2/` without breaking existing clients.

## Contributing

1. Install pre-commit: `pre-commit install`
2. All commits are automatically linted and type-checked.
3. Write tests for all new feature code.
