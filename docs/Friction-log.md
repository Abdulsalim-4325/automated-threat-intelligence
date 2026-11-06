# Developer Friction Log & Notes

FR-01 — Refactoring Pydantic V1 schemas to V2 syntax
Task attempted: Setting up the initial Pydantic data validation schemas (`IndicatorBase`) for the threat intelligence API.
Steps taken:
1. Defined Pydantic models using legacy `class Config` configurations.
2. Utilized the standard `.json()` method for model serialization in the test block.
3. Executed the schema validation script to verify output.
Expected vs. actual: The expected result was clean schema validation and a JSON output. The actual result was a flood of deprecation warnings (`PydanticDeprecatedSince20`) and a fatal `TypeError` regarding `dumps_kwargs`, caused by FastAPI's migration to Pydantic V2 strictness.
Severity: Medium.
Workaround: Refactored the code to use the modern V2 syntax. Swapped `class Config` for `model_config = ConfigDict(from_attributes=True)` and replaced the deprecated `.json()` method with `.model_dump_json()`.
Actionable suggestion: Enforce Pydantic V2 linting rules in the project's CI/CD pipeline (using Ruff or similar) to flag legacy V1 code during PR reviews.
Status: Resolved.

FR-02 — Resolving Alembic and PostgreSQL Docker boot race condition
Task attempted: Running initial database migrations on a fresh Docker compose environment.
Steps taken:
1. Spun up the local infrastructure using `docker compose up -d`.
2. Immediately attempted to run `alembic upgrade head` in the terminal.
Expected vs. actual: Expected Alembic to connect to the database and generate the initial tables. Actually hit a `ConnectionResetError: [Errno 104]` because Postgres was still internally initializing its `/var/lib/postgresql/data` directory and actively refusing connections.
Severity: High.
Workaround: Nuked the partial Docker volume with `docker compose down -v`, brought the containers back up, tailed the PostgreSQL logs until it confirmed it was ready to accept connections, and then successfully ran the Alembic migration.
Actionable suggestion: Add a `wait-for-it.sh` or `pg_isready` health-check script inside the Docker `entrypoint.sh` to block the API and migration execution until the database is fully initialized.
Status: Partially resolved. Manual workaround works, but CI/CD automation will need the script.

FR-03 — Synchronizing FastAPI database dependency injection imports
Task attempted: Scaffolding the `/health` and `/lookup` API endpoints and attaching the database session.
Steps taken:
1. Scaffolded the API routers in the `endpoints` directory.
2. Imported the database session dependency into the router files.
3. Booted the Uvicorn local development server.
Expected vs. actual: Expected Uvicorn to start serving the API; actual result was an immediate `ImportError` fatal crash because the dependency was named `get_db` in the core module, but the endpoints were trying to import it as `get_db_session`.
Severity: High.
Workaround: Used terminal `sed` commands (`sed -i 's/get_db_session/get_db/g'`) to rapidly bulk-replace the incorrect imports across the entire `api/v1/endpoints` directory.
Actionable suggestion: Standardize all core dependency imports within a single `app/api/dependencies.py` facade file to create a single source of truth, rather than importing directly from database core files.
Status: Resolved.

FR-04 — Restoring WSL 2 Docker daemon connectivity after system sleep
Task attempted: Resuming backend development in the terminal after leaving the machine idle.
Steps taken:
1. Left the local development environment idle while stepping away.
2. Attempted to execute standard `docker compose ps` commands in the WSL 2 terminal upon returning.
Expected vs. actual: Expected the Docker CLI to respond normally; actually received "The command 'docker' could not be found in this WSL 2 distro" because Windows Docker Desktop aggressively suspended itself to save memory, severing the WSL integration pipe.
Severity: Low.
Workaround: Manually launched the Docker Desktop GUI in Windows, waited for the engine status indicator to turn green, and then re-ran the commands in the WSL terminal.
Actionable suggestion: Document this specific WSL 2/Docker Desktop memory-management behavior in the `README.md` troubleshooting section so future maintainers on Windows environments aren't confused by sudden CLI failures.
Status: Resolved.

FR-05 — Freeing bound development server ports in the background
Task attempted: Restarting the FastAPI Uvicorn server to apply new environment configuration changes.
Steps taken:
1. Sent the Uvicorn server process to run in the background using the `&` operator.
2. Modified the `config.py` environment variables.
3. Attempted to start a new Uvicorn instance.
Expected vs. actual: Expected the server to restart with the new configuration; actually crashed with `[Errno 98] address already in use` because the invisible background process was still holding port 8000 hostage.
Severity: Medium.
Workaround: Executed `pkill -f uvicorn` to forcibly terminate all hanging Python web server background processes before booting the fresh instance.
Actionable suggestion: Implement a local `Makefile` command (e.g., `make dev-restart`) that systematically checks for and kills any processes holding port 8000 before spinning up the new Uvicorn instance.
Status: Resolved.

FR-06 — Mitigating PostgreSQL asyncpg timezone strictness exceptions
Task attempted: Testing the atomic upsert via the POST `/api/v1/indicators/import` endpoint.
Steps taken:
1. Defined the database schema column as `TIMESTAMP WITHOUT TIME ZONE`.
2. Generated a timezone-aware UTC datetime object in the Python ingestion logic.
3. Attempted to execute the batch upsert.
Expected vs. actual: Expected successful batch data ingestion; actually received a 500 Internal Server Error triggered by `asyncpg.exceptions.DataError (can't subtract offset-naive and offset-aware datetimes)`. The asyncpg driver is highly strict and refused to automatically cast the Python timezone.
Severity: High.
Workaround: Stripped the timezone information in Python using `.replace(tzinfo=None)` right after generating the UTC timestamp, safely converting it to a "naive" object before passing it to the SQLAlchemy session.
Actionable suggestion: Standardize a project-wide utility function for datetime generation (e.g., `get_utc_now_naive()`) in `app.core.utils` to prevent developer mismatches across different endpoints and services.
Status: Resolved.

FR-07 — Realigning Git path contexts in multi-project terminal sessions
Task attempted: Committing the Day 10 progress and endpoint files to the repository.
Steps taken:
1. Opened a fresh WSL terminal tab to execute version control.
2. Attempted to run `git add` and `git commit` commands for the modified files.
Expected vs. actual: Expected files to stage for commit; actually received fatal pathspec errors (`pathspec 'main' did not match any file(s)`) because the new terminal tab defaulted to the parent backup directory (`~/GITHUB-BACKUP-2026-08-26/`) rather than the project root, causing Git to search the wrong context.
Severity: Low.
Workaround: Changed directories back into the actual `Automated-threat-intelligence` folder and successfully re-ran the staging and commit commands.
Actionable suggestion: Add a prompt hook or modify the `.bashrc` to include a visual indicator that clearly displays the active Git repository name and branch on the command line to prevent blind context execution.
Status: Resolved.