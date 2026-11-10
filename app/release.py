"""GitHub Release 信息：站点的动态数据源。

原站点把 "上游最新 v2.3.0-r18.9" 写死在 HTML 里，版本一变就得手工改。
Python 版在渲染时查询 GitHub API，带 TTL 缓存与离线回退：
- 拿到数据 -> 页面展示真实 tag，/api/release 返回完整资产列表；
- 拿不到 -> 回退到 content.FALLBACK_RELEASE_TAG，页面照常可用。
"""

from __future__ import annotations

import json
import os
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field

from . import content

API_URL = "https://api.github.com/repos/{}/releases/latest".format(content.REPO_SLUG)
USER_AGENT = "susfs-guard-lkm-site/1.0 (+{})".format(content.REPO_URL)

DEFAULT_TTL = 600.0
FAILURE_TTL = 60.0
DEFAULT_TIMEOUT = 4.0


@dataclass(frozen=True)
class Asset:
    name: str
    size: int
    download_url: str


@dataclass(frozen=True)
class ReleaseInfo:
    tag: str
    html_url: str
    published_at: str | None
    source: str
    assets: tuple[Asset, ...] = ()

    @property
    def is_live(self) -> bool:
        return self.source == "live"

    def asset(self, name: str) -> Asset | None:
        for item in self.assets:
            if item.name == name:
                return item
        return None


FALLBACK = ReleaseInfo(
    tag=content.FALLBACK_RELEASE_TAG,
    html_url=content.RELEASES_URL,
    published_at=None,
    source="fallback",
)


def _parse(payload: dict) -> ReleaseInfo:
    assets = tuple(
        Asset(
            name=item.get("name", ""),
            size=int(item.get("size") or 0),
            download_url=item.get("browser_download_url", ""),
        )
        for item in payload.get("assets") or []
        if item.get("name")
    )
    return ReleaseInfo(
        tag=payload.get("tag_name") or FALLBACK.tag,
        html_url=payload.get("html_url") or FALLBACK.html_url,
        published_at=payload.get("published_at"),
        source="live",
        assets=assets,
    )


class ReleaseCache:
    """进程内 TTL 缓存；失败时短期缓存回退值，避免每次请求都走网络。"""

    def __init__(
        self,
        ttl: float = DEFAULT_TTL,
        timeout: float = DEFAULT_TIMEOUT,
        offline: bool | None = None,
    ) -> None:
        self.ttl = ttl
        self.timeout = timeout
        if offline is None:
            offline = os.environ.get("SITE_OFFLINE", "").lower() in {"1", "true", "yes"}
        self.offline = offline
        self._lock = threading.Lock()
        self._value: ReleaseInfo | None = None
        self._expires_at = 0.0

    # -- 读取 ---------------------------------------------------------
    def peek(self) -> ReleaseInfo:
        """只读缓存，不触发网络请求。"""
        with self._lock:
            if self._value is not None and time.monotonic() < self._expires_at:
                return self._value
            return FALLBACK

    def get(self) -> ReleaseInfo:
        with self._lock:
            if self._value is not None and time.monotonic() < self._expires_at:
                return self._value
        if self.offline:
            return FALLBACK
        return self.refresh()

    def refresh(self) -> ReleaseInfo:
        try:
            info = self._fetch()
            ttl = self.ttl
        except Exception:  # 网络/解析失败一律回退，页面不应因此 500
            info = FALLBACK
            ttl = FAILURE_TTL
        with self._lock:
            self._value = info
            self._expires_at = time.monotonic() + ttl
        return info

    # -- 网络 ---------------------------------------------------------
    def _fetch(self) -> ReleaseInfo:
        request = urllib.request.Request(
            API_URL,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "application/vnd.github+json",
            },
        )
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("unexpected GitHub release payload")
        return _parse(payload)


__all__ = ["Asset", "ReleaseInfo", "ReleaseCache", "FALLBACK"]
