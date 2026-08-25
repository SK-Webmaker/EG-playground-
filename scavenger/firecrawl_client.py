"""Thin Firecrawl v2 wrapper with retry/backoff and on-disk response caching.

Caching matters: a re-run should never pay twice for the same page, and it keeps
you inside the concurrency limit that the live API enforces.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path

import requests

API_ROOT = "https://api.firecrawl.dev/v2"
CACHE_DIR = Path(os.getenv("SCAVENGER_CACHE", "data/raw/cache"))


class FirecrawlError(RuntimeError):
    pass


class Firecrawl:
    def __init__(self, api_key: str | None = None, cache: bool = True, qps: float = 0.6):
        self.api_key = api_key or os.getenv("FIRECRAWL_API_KEY")
        if not self.api_key:
            raise FirecrawlError(
                "FIRECRAWL_API_KEY is not set. Copy .env.example to .env and fill it in."
            )
        self.cache = cache
        self.qps = qps
        self._last_call = 0.0
        CACHE_DIR.mkdir(parents=True, exist_ok=True)

    # -- internals ----------------------------------------------------------
    def _cache_path(self, endpoint: str, payload: dict) -> Path:
        digest = hashlib.sha1(
            (endpoint + json.dumps(payload, sort_keys=True)).encode()
        ).hexdigest()
        return CACHE_DIR / f"{endpoint.strip('/')}-{digest}.json"

    def _throttle(self) -> None:
        gap = time.monotonic() - self._last_call
        if gap < 1 / self.qps:
            time.sleep(1 / self.qps - gap)
        self._last_call = time.monotonic()

    def _post(self, endpoint: str, payload: dict, attempts: int = 4) -> dict:
        cache_file = self._cache_path(endpoint, payload)
        if self.cache and cache_file.exists():
            return json.loads(cache_file.read_text())

        last_err: Exception | None = None
        for attempt in range(attempts):
            self._throttle()
            try:
                resp = requests.post(
                    f"{API_ROOT}{endpoint}",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json=payload,
                    timeout=120,
                )
                # 429 = concurrency limit; back off rather than hammering.
                if resp.status_code == 429:
                    time.sleep(2 ** attempt * 3)
                    continue
                resp.raise_for_status()
                data = resp.json()
                if self.cache:
                    cache_file.write_text(json.dumps(data))
                return data
            except Exception as exc:  # noqa: BLE001 - retried below
                last_err = exc
                time.sleep(2 ** attempt)
        raise FirecrawlError(f"{endpoint} failed after {attempts} attempts: {last_err}")

    # -- public -------------------------------------------------------------
    def scrape(self, url: str, formats: list | None = None, **kwargs) -> dict:
        payload = {"url": url, "formats": formats or ["markdown"], **kwargs}
        return self._post("/scrape", payload).get("data", {})

    def scrape_json(self, url: str, prompt: str, schema: dict, **kwargs) -> dict:
        data = self.scrape(
            url,
            formats=[{"type": "json", "prompt": prompt, "schema": schema}],
            **kwargs,
        )
        return data.get("json", {}) or {}

    def search(self, query: str, limit: int = 10, **kwargs) -> list[dict]:
        payload = {"query": query, "limit": limit, **kwargs}
        data = self._post("/search", payload).get("data", {})
        if isinstance(data, dict):
            return data.get("web", []) or []
        return data or []
