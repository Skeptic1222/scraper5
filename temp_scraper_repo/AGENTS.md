# Repository Guidelines

## Project Structure & Module Organization
- Core app in `app.py`, auth in `auth.py`, models in `models.py`.
- New blueprints live in `blueprints/` (admin, assets, search, jobs, sources, user, ai). Prefer adding routes via blueprints.
- Scrapers and services live under `src/` (`src/scrapers/`, `src/services/`, `src/api/`).
- Frontend assets in `static/` and views in `templates/`.
- Config in `.env` and `web.config`; DB files under `instance/`; logs in `logs/`.
- Tests exist both in root (`test_*.py`) and grouped folders under `tests/`.

## Build, Test, and Development Commands
```bash
pip install -r requirements.txt           # Install runtime deps
cp .env.example .env                      # Configure environment
python start.py                           # Run app (init + server)
# Alternate: python app.py

# Or via Makefile shortcuts
make run                                   # Start app
make check-ports                           # Scan for forbidden URLs
make clean-artifacts                        # Remove test artifacts
make hooks                                  # Set up git hooks
make install-dev                            # Install ruff/black (dev only)
make lint                                   # Run ruff + black --check
make format                                 # Auto-fix with ruff and black

# Quick checks
python simple_test.py                     # Fast health check
python comprehensive_test.py              # Broader functional sweep
python test_scraper_app.py                # UI/API checks (Playwright)

# UI tests (first time): pip install playwright && python -m playwright install
```
Important: Access via `http://localhost/scraper` (IIS proxy). Do not add ports to URLs. See `CRITICAL_NO_PORTS_RULE.md`.

For a quick overview of all docs, see `DOCS_INDEX.md`.

## Coding Style & Naming Conventions
- Python 3.x, PEP 8, 4‑space indentation, 88‑char soft wrap.
- Names: `snake_case` for functions/vars, `PascalCase` for classes, `UPPER_SNAKE` for constants.
- Module patterns match current code: `*_manager.py`, `*_utils.py`, `*_api.py`.
- Prefer type hints and docstrings (`"""Summary..."""`).
- Configuration: centralized in `config.py` (`APP_BASE`, session, DB defaults). Injected via `init_app_config()`.
- Shared helpers: `utils/responses.py` (JSON helpers). Reuse in new endpoints.

## Testing Guidelines
- Smoke and functional tests are Python scripts; some UI flows use Playwright.
- Run targeted scripts above; capture artifacts in repo root (e.g., `test_results.json`).
- Keep tests deterministic and avoid network calls outside the app.
- Name new tests `test_<area>.py`; place quick checks at root, suites under `tests/<type>/`.
- Useful scripts:
  - `python test_compat_endpoints.py` (legacy endpoint compatibility)
  - `python test_endpoints_smoke.py` (basic availability of key JSON endpoints)

## Commit & Pull Request Guidelines
- Conventional Commits: `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`, `perf:`, `security:`.
- PRs must include: concise summary, linked issues, steps to validate, and screenshots for UI changes.
- Checklist: no hardcoded ports, `.env` not committed, logs/secrets excluded, tests updated.

## Security & Configuration Tips
- Never expose backend ports; all routes must work under `/scraper`.
- Keep secrets in `.env`; prefer `DATABASE_URL` and OAuth vars from env.
- Validate inputs at route handlers; follow RBAC patterns in `auth.py`.
