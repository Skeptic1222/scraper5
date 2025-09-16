#!/usr/bin/env python3
"""
Utility: Print all registered Flask routes for quick inspection.
Sets a safe default DATABASE_URL if not configured to avoid import errors.
"""

import os
import sys

os.environ.setdefault("DATABASE_URL", "sqlite:///instance/scraper.db")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app import app  # noqa: E402

for rule in sorted(app.url_map.iter_rules(), key=lambda r: r.rule):
    methods = ",".join(sorted(m for m in rule.methods if m not in {"HEAD", "OPTIONS"}))
    print(f"{rule.rule:40s}  [{methods}]  -> {rule.endpoint}")
