from pathlib import Path

from freeze import freeze


def test_freeze_writes_complete_static_site(tmp_path):
    out = tmp_path / "public"
    written = freeze(out, offline=True)

    names = {path.name for path in out.iterdir()}
    assert {"index.html", "404.html", "robots.txt", "sitemap.xml", "manifest.webmanifest"} <= names
    assert (out / ".nojekyll").exists()
    assert (out / "assets" / "styles.css").exists()
    assert (out / "assets" / "og.png").exists()
    assert (out / "assets" / "live.js").exists()
    assert len(written) == 6

    index = (out / "index.html").read_text(encoding="utf-8")
    assert "把 SUSFS" in index
    assert index.count('href="assets/styles.css"') == 1
    assert index.count("releases/latest/download/susfs_guard_lkm-") == 8


def test_freeze_is_idempotent(tmp_path):
    out = tmp_path / "public"
    freeze(out, offline=True)
    first = (out / "index.html").read_bytes()
    freeze(out, offline=True)
    assert (out / "index.html").read_bytes() == first
