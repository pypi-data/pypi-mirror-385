# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PyArchInit-Mini is a lightweight archaeological data management system focused on core functionality without GIS dependencies. It provides multiple interfaces (REST API, Web UI, Desktop GUI, CLI) for managing archaeological sites, stratigraphic units (US), and material inventories.

## Architecture

### Layered Architecture
The codebase follows a clean, service-oriented architecture:

```
pyarchinit_mini/
├── models/          # SQLAlchemy ORM models (Site, US, InventarioMateriali, etc.)
├── database/        # Connection management, migrations, DatabaseManager
├── services/        # Business logic layer (SiteService, USService, etc.)
├── dto/             # Data Transfer Objects for clean API boundaries
├── api/             # FastAPI REST endpoints with Pydantic schemas
├── utils/           # Validators, exceptions, utilities
├── harris_matrix/   # Harris Matrix generation and visualization
├── pdf_export/      # PDF report generation
└── media_manager/   # Media file handling
```

### Key Design Patterns

**Session Management**: All database operations use context managers via `DatabaseConnection.get_session()`. The session automatically commits on success and rolls back on errors. Never manually create sessions outside this pattern.

**Service Layer**: Business logic lives in services (e.g., `SiteService`, `USService`). Services use `DatabaseManager` for CRUD operations and contain validation logic. API endpoints should be thin wrappers around service calls.

**DTO Pattern**: Models are converted to DTOs before leaving the service layer to avoid SQLAlchemy lazy loading issues outside sessions. Use `SiteDTO.from_model(site)` while still in session context.

**Multi-Database Support**: Code supports both PostgreSQL and SQLite. Database-specific logic is isolated in `DatabaseConnection`. Test with both databases when making schema changes.

## Common Development Commands

### Running the Application

```bash
# Start REST API server (FastAPI)
python main.py
# Access API docs at http://localhost:8000/docs

# Start Web Interface (Flask)
python web_interface/app.py
# Access at http://localhost:5000

# Start Desktop GUI (Tkinter)
python desktop_gui/gui_app.py
# OR
python run_gui.py

# Start CLI Interface
python cli_interface/cli_app.py
```

### Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_site_service.py

# Run with coverage
pytest --cov=pyarchinit_mini

# Run with verbose output
pytest -v
```

### Database Operations

```bash
# Run migrations (creates/updates schema)
python -c "from pyarchinit_mini.database import DatabaseConnection, DatabaseManager; \
           db = DatabaseConnection('sqlite:///./pyarchinit_mini.db'); \
           DatabaseManager(db).run_migrations()"

# Migrate existing database
python migrate_database.py

# Load sample data for testing
python launch_with_sample_data.py
python scripts/populate_sample_data.py
```

### Code Quality

```bash
# Format code with Black
black pyarchinit_mini/

# Sort imports
isort pyarchinit_mini/

# Lint with flake8
flake8 pyarchinit_mini/

# Type checking
mypy pyarchinit_mini/
```

## Critical Implementation Details

### Database Sessions

**ALWAYS** use the session context manager pattern:

```python
# CORRECT
with self.db_manager.connection.get_session() as session:
    site = session.query(Site).filter(Site.id_sito == site_id).first()
    dto = SiteDTO.from_model(site)  # Convert to DTO while in session
    return dto

# WRONG - Never do this
session = self.db_manager.connection.SessionLocal()
site = session.query(Site).get(site_id)
# Missing rollback/commit handling, resource leak
```

### Service Methods

Services have two patterns for CRUD operations:

1. **Model-returning methods** (legacy): Return SQLAlchemy models
2. **DTO-returning methods** (preferred): Return DTOs, suffix with `_dto`

When adding new endpoints, prefer DTO-returning service methods to avoid detached instance errors.

### Foreign Key Relationships

SQLite requires explicit foreign key enforcement. This is configured in `DatabaseConnection`:

```python
@event.listens_for(self.engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor.execute("PRAGMA foreign_keys=ON")
```

When defining relationships in models, ensure proper cascade settings for deletions.

### Harris Matrix Generation

The Harris Matrix system uses NetworkX for graph operations:

```python
from pyarchinit_mini.harris_matrix import HarrisMatrixGenerator, MatrixVisualizer

generator = HarrisMatrixGenerator(db_manager)
graph = generator.generate_matrix(site_name)  # Returns NetworkX DiGraph
levels = generator.get_matrix_levels(graph)   # Topological ordering
```

US relationships are defined via `rapporti_stratigrafici` field (e.g., "Covers 1002, 1003").

## Environment Configuration

### Database Configuration

```bash
# SQLite (default)
export DATABASE_URL="sqlite:///./pyarchinit_mini.db"

# PostgreSQL
export DATABASE_URL="postgresql://user:password@localhost:5432/pyarchinit"
```

### FastAPI Server Configuration

```bash
# Server settings
export HOST="0.0.0.0"
export PORT="8000"
export RELOAD="true"  # Auto-reload on code changes
```

## Important Files

- `main.py`: FastAPI application entry point
- `pyarchinit_mini/__init__.py`: Package exports (DatabaseManager, services)
- `pyarchinit_mini/database/manager.py`: Generic CRUD operations, query builder
- `pyarchinit_mini/database/connection.py`: Session management, DB connection
- `pyarchinit_mini/api/dependencies.py`: FastAPI dependency injection for DB
- `requirements.txt`: Python dependencies
- `pyproject.toml`: Project metadata, tool configuration (black, mypy, pytest)

## Common Gotchas

1. **Detached Instance Errors**: Always convert models to DTOs within session context before returning from services
2. **Foreign Key Constraints**: Remember SQLite needs PRAGMA foreign_keys=ON (already configured)
3. **Session Lifecycle**: Never store SQLAlchemy model instances beyond session scope
4. **Relationship Loading**: Use eager loading (joinedload) for relationships accessed outside sessions
5. **Database URL Format**: PostgreSQL uses `postgresql://` not `postgres://`

## Adding New Features

### Adding a New Model

1. Create model in `pyarchinit_mini/models/your_model.py` extending `BaseModel`
2. Add DTO in `pyarchinit_mini/dto/your_dto.py`
3. Create service in `pyarchinit_mini/services/your_service.py`
4. Add API router in `pyarchinit_mini/api/your_router.py`
5. Register router in `pyarchinit_mini/api/__init__.py` `create_app()`
6. Run migrations to create table
7. Add tests in `tests/unit/test_your_service.py`

### Adding a New API Endpoint

1. Use dependency injection for database access:
   ```python
   from .dependencies import get_db_manager

   @router.get("/")
   async def list_items(db_manager: DatabaseManager = Depends(get_db_manager)):
       service = YourService(db_manager)
       return service.get_all_items_dto()
   ```

2. Use Pydantic schemas for request/response validation
3. Follow REST conventions (GET for read, POST for create, PUT for update, DELETE for delete)
4. Return DTOs, not raw SQLAlchemy models

## Testing Guidelines

- Use pytest fixtures from `tests/conftest.py` for database setup
- Each test should use a fresh database session
- Test both SQLite and PostgreSQL code paths for schema changes
- Mock external dependencies (file system, network) in unit tests
- Integration tests should test full service layer operations