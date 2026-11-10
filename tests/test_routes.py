"""路由行为测试：页面、下载入口、JSON API、静态导出。"""

from app import content

DEFAULT_TAG = content.FALLBACK_RELEASE_TAG


def test_index_renders_full_page(client):
    response = client.get("/")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "<title>SUSFS Guard LKM — 无需重编译内核的 SUSFS</title>" in html
    assert "把 SUSFS" in html
    assert html.count('class="feature-card reveal"') == 6
    assert html.count('class="stat"') == 4
    assert html.count("<details>") == 6
    assert html.count('class="tab"') == 3
    assert html.count('class="doc-link"') == 4
    assert html.count('class="interface-card"') == 6
    assert html.count('href="/download/') == 8
    assert DEFAULT_TAG in html  # 离线时回退版本号仍然渲染
    assert 'aria-selected="true"' in html


def test_index_contains_only_one_h1(client):
    html = client.get("/").get_data(as_text=True)
    assert html.count("<h1") == 1


def test_inline_code_is_rendered_not_escaped(client):
    html = client.get("/").get_data(as_text=True)
    assert "<code>.ko</code>" in html
    assert "~.ko~" not in html


def test_assets_are_served(client):
    for name in ("styles.css", "main.js", "favicon.svg", "og.png", "og.svg"):
        response = client.get("/assets/" + name)
        assert response.status_code == 200, name


def test_download_redirects_to_release_asset(client):
    for variant in content.KMI_VARIANTS:
        response = client.get("/download/" + variant)
        assert response.status_code == 302
        location = response.headers["Location"]
        assert location == (
            "https://github.com/inforcqb/susfs4ksu-for-lkm/releases/latest/download/"
            "susfs_guard_lkm-{}.ko".format(variant)
        )


def test_download_unknown_kmi_is_404(client):
    response = client.get("/download/android99-9.9")
    assert response.status_code == 404
    assert "这个页面没有加载成功。" in response.get_data(as_text=True)


def test_404_page(client):
    response = client.get("/no-such-page")
    assert response.status_code == 404
    assert "返回首页" in response.get_data(as_text=True)


def test_robots_txt(client):
    response = client.get("/robots.txt")
    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Sitemap: https://inforcqb.github.io/susfs4ksu-for-lkm/sitemap.xml" in body


def test_sitemap(client):
    response = client.get("/sitemap.xml")
    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "<loc>https://inforcqb.github.io/susfs4ksu-for-lkm/</loc>" in body


def test_manifest(client):
    response = client.get("/manifest.webmanifest")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["short_name"] == "SUSFS LKM"
    assert payload["icons"][0]["src"] == "assets/favicon.svg"


def test_api_health(client):
    payload = client.get("/api/health").get_json()
    assert payload["status"] == "ok"
    assert payload["release"]["source"] == "fallback"


def test_api_release(client):
    payload = client.get("/api/release").get_json()
    assert payload["tag"] == DEFAULT_TAG
    assert payload["source"] == "fallback"
    assert payload["assets"] == []


def test_api_kmi(client):
    payload = client.get("/api/kmi").get_json()
    assert payload["variants"] == list(content.KMI_VARIANTS)
    assert len(payload["rows"]) == 8
    assert payload["asset_template"] == "susfs_guard_lkm-{kmi}.ko"


def test_api_kmi_resolve_osrelease(client):
    payload = client.get("/api/kmi/resolve?osrelease=6.6.30-android15-8-gabc").get_json()
    assert payload["kmi"] == "android15-6.6"
    assert payload["asset"] == "susfs_guard_lkm-android15-6.6.ko"
    assert payload["download_url"].endswith("/susfs_guard_lkm-android15-6.6.ko")


def test_api_kmi_resolve_android_kernel(client):
    payload = client.get("/api/kmi/resolve?android=13&kernel=5.10.209").get_json()
    assert payload["kmi"] == "android13-5.10"


def test_api_kmi_resolve_requires_parameters(client):
    assert client.get("/api/kmi/resolve").status_code == 400
    assert client.get("/api/kmi/resolve?osrelease=6.6.30").status_code == 404


def test_static_export_uses_relative_assets():
    from app import create_app

    app = create_app({"TESTING": True, "OFFLINE": True, "STATIC_EXPORT": True})
    with app.test_client() as client:
        html = client.get("/").get_data(as_text=True)
    assert 'href="assets/styles.css"' in html
    assert 'src="assets/main.js"' in html
    assert 'href="manifest.webmanifest"' in html
    # 静态导出没有 /download 路由，直接指向 GitHub Release
    assert 'href="https://github.com/inforcqb/susfs4ksu-for-lkm/releases/latest/download/susfs_guard_lkm-android15-6.6.ko"' in html
