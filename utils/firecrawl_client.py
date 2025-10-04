"""
Optional Firecrawl client for fetching rendered HTML snapshots.
Requires FIRECRAWL_API_KEY in environment. If not set, this module is a noop.
"""
from __future__ import annotations

import os
from typing import Optional

import requests


class FirecrawlClient:
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or os.getenv("FIRECRAWL_API_KEY")
        self.base_url = base_url or os.getenv("FIRECRAWL_BASE_URL", "https://api.firecrawl.dev/v1/scrape")
        self.session = requests.Session()

    def available(self) -> bool:
        return bool(self.api_key)

    def fetch_html(self, url: str, timeout: int = 25) -> Optional[str]:
        """Fetch rendered HTML for a URL via Firecrawl API.

        Returns the HTML string or None on error.
        """
        if not self.available():
            return None
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "MediaScraper/1.0",
            }
            payload = {"url": url}
            resp = self.session.post(self.base_url, json=payload, headers=headers, timeout=timeout)
            if resp.status_code == 200:
                data = resp.json()
                # Support common payload shapes: { html: "..." } or { data: { html: "..." } }
                if isinstance(data, dict):
                    html = (
                        data.get("html")
                        or (data.get("data") or {}).get("html")
                        or (data.get("result") or {}).get("html")
                    )
                    if isinstance(html, str) and html.strip():
                        return html
            return None
        except Exception:
            return None


firecrawl_client = FirecrawlClient()

