from pathlib import Path

ASSET = Path(__file__).resolve().parents[1] / "app" / "static" / "assets" / "live.js"


def test_live_js_targets_release_pill():
    source = ASSET.read_text(encoding="utf-8")
    assert "data-release-pill" in source
    assert "data-release-tag" in source
    assert "https://api.github.com/repos/inforcqb/susfs4ksu-for-lkm/releases/latest" in source


def test_live_js_has_cache_and_fallback():
    source = ASSET.read_text(encoding="utf-8")
    assert "localStorage" in source
    assert "TTL" in source
    assert ".catch(" in source  # 失败时静默保留服务端快照


def test_live_js_contains_no_secrets():
    source = ASSET.read_text(encoding="utf-8")
    for marker in ("token", "Authorization", "ghp_", "github_pat_"):
        assert marker not in source
