import json

from app import release


class FakeResponse:
    def __init__(self, payload: dict):
        self._body = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        return False

    def read(self) -> bytes:
        return self._body


def test_live_release_is_parsed(monkeypatch):
    payload = {
        "tag_name": "v9.9.9",
        "html_url": "https://example.test/releases/v9.9.9",
        "published_at": "2026-01-01T00:00:00Z",
        "assets": [
            {
                "name": "susfs_guard_lkm-android15-6.6.ko",
                "size": 1234,
                "browser_download_url": "https://example.test/a.ko",
            }
        ],
    }
    monkeypatch.setattr(
        release.urllib.request, "urlopen", lambda request, timeout: FakeResponse(payload)
    )
    cache = release.ReleaseCache(offline=False)
    info = cache.get()
    assert info.is_live
    assert info.tag == "v9.9.9"
    assert info.asset("susfs_guard_lkm-android15-6.6.ko").size == 1234
    assert cache.peek().tag == "v9.9.9"


def test_network_failure_falls_back(monkeypatch):
    def boom(request, timeout):
        raise OSError("offline")

    monkeypatch.setattr(release.urllib.request, "urlopen", boom)
    cache = release.ReleaseCache(offline=False)
    info = cache.get()
    assert not info.is_live
    assert info.tag == release.FALLBACK.tag


def test_offline_cache_never_calls_network(monkeypatch):
    def boom(request, timeout):  # pragma: no cover - 不应被触发
        raise AssertionError("network should not be used")

    monkeypatch.setattr(release.urllib.request, "urlopen", boom)
    cache = release.ReleaseCache(offline=True)
    assert cache.get().source == "fallback"
