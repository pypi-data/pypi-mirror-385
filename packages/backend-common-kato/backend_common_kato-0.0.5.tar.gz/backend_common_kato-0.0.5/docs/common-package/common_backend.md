Backend Structure Requirements:
- config/ – Application settings and environment configuration (settings.py).
- core/ – Core modules such as:
  - auth/ – Authentication and authorization logic. For internal application, use simple token-based auth.
  - exceptions/ – Custom exception handlers, include exceptions.py and handlers.py.
  - utils/ - Core utility functions such as loggings.py
- models/ – Database models and ORM schemas.
- db/ – Database connection and session management.
- services/ – Business logic and integrations:
    - base/ – Base service classes.
    - service_name/ - Specific service implementations.
- utils/ – Helper functions and utilities.
- migrations/ – Database migration files (e.g., Alembic). (Just placeholder, we will use command line to generate migrations)
- api/ – API endpoints and routing (organized by feature).
- tests/ – Unit and integration tests.
- main.py – Application entry point.
- requirements.txt – Python dependencies.

Output Requirements:
- Present as a clear directory tree structure, best practices, scalable.
- Output is BACKEND.md file.
- Use short descriptions for each folder or file.
- Do not include code examples.