# Documentation Index

This index consolidates the essential docs for quick review by contributors and AI code assistants.

Core
- Overview: README.md (features, architecture, quick start)
- Critical rule: CRITICAL_NO_PORTS_RULE.md (always use `http://localhost/scraper`)
- Setup: SETUP.md (env, DB, OAuth, IIS)
- Structure: blueprints (admin, assets, search, jobs, sources, user, ai) + config.py

Run & Test
- Start: `python start.py` or `python app.py` (access via `/scraper`)
- Quick checks: `python simple_test.py`, `python comprehensive_test.py`
- UI/API: `python test_scraper_app.py` (Playwright)
- Makefile: `make run`, `make check-ports`, `make clean-artifacts`, `make hooks`
- Route map: `python scripts/print_routes.py`

Security & Auth
- OAuth flow and callback: auth.py (uses `/scraper/auth/google/callback`)
- Google OAuth update steps: GOOGLE_OAUTH_UPDATE.md

Deployment
- Windows/IIS: web.config (reverse proxy to backend), docs/WINDOWS_DEPLOYMENT_GUIDE.md
- General: docs/DEPLOYMENT_GUIDE.md, docs/DEPLOYMENT_CHECKLIST.md

Troubleshooting
- HOW TO ACCESS: docs/HOW_TO_ACCESS.md (URLs and common fixes)
- Logs: `logs/` (app and oauth logs)

Contributing
- Guidelines: AGENTS.md (project structure, style, tests, PR checklist)

Notes
- Internal backend ports may appear in config examples; never expose ports in browser-facing URLs or app code.
