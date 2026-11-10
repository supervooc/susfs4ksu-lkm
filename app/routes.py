"""HTTP 路由：页面、下载入口与 JSON API。

页面本身是服务端渲染的 Jinja2 模板；JSON 接口是 Python 化的增量能力，
让 KMI 矩阵、Release 信息可以被脚本或其他前端复用。
"""

from __future__ import annotations

import json
import os

from flask import (
    Blueprint,
    Response,
    abort,
    current_app,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)

from . import content, kmi as kmi_module

bp = Blueprint("site", __name__)


def _release_cache():
    return current_app.extensions["release_cache"]


# --------------------------------------------------------------------------
# 页面
# --------------------------------------------------------------------------

@bp.get("/")
def index():
    release = _release_cache().get()
    return render_template("index.html", release=release, page="home")


@bp.get("/assets/<path:filename>")
def assets(filename: str):
    return send_from_directory(
        os.path.join(current_app.static_folder, "assets"),
        filename,
        max_age=3600,
    )


@bp.get("/download/<kmi>")
def download(kmi: str):
    """把站内下载地址重定向到上游 Release 中的同名产物。"""
    if kmi not in content.KMI_VARIANTS:
        abort(404)
    asset_name = content.KMI_ASSET_TEMPLATE.format(kmi=kmi)
    return redirect("{}/download/{}".format(content.LATEST_RELEASE_URL, asset_name)), 302


@bp.get("/robots.txt")
def robots():
    body = (
        "User-agent: *\n"
        "Allow: /\n"
        "\n"
        "Sitemap: {}sitemap.xml\n".format(content.SITE_URL)
    )
    return Response(body, mimetype="text/plain")


@bp.get("/sitemap.xml")
def sitemap():
    body = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        "  <url>\n"
        "    <loc>{}</loc>\n"
        "    <changefreq>weekly</changefreq>\n"
        "    <priority>1.0</priority>\n"
        "  </url>\n"
        "</urlset>\n"
    ).format(content.SITE_URL)
    return Response(body, mimetype="application/xml")


@bp.get("/manifest.webmanifest")
def manifest():
    payload = {
        "name": "SUSFS Guard LKM",
        "short_name": "SUSFS LKM",
        "description": "SUSFS 的可加载内核模块移植版，适用于 Android GKI / KernelSU。",
        "start_url": "./",
        "scope": "./",
        "display": "standalone",
        "background_color": content.THEME_COLOR,
        "theme_color": content.THEME_COLOR,
        "icons": [
            {
                "src": "assets/favicon.svg",
                "sizes": "any",
                "type": "image/svg+xml",
                "purpose": "any",
            }
        ],
    }
    return Response(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        mimetype="application/manifest+json",
    )


# --------------------------------------------------------------------------
# JSON API
# --------------------------------------------------------------------------

@bp.get("/api/health")
def api_health():
    release = _release_cache().peek()
    return jsonify(
        {
            "status": "ok",
            "release": {"tag": release.tag, "source": release.source},
        }
    )


@bp.get("/api/release")
def api_release():
    release = _release_cache().get()
    return jsonify(
        {
            "tag": release.tag,
            "html_url": release.html_url,
            "published_at": release.published_at,
            "source": release.source,
            "assets": [
                {"name": item.name, "size": item.size, "download_url": item.download_url}
                for item in release.assets
            ],
        }
    )


@bp.get("/api/kmi")
def api_kmi():
    return jsonify(
        {
            "variants": list(content.KMI_VARIANTS),
            "rows": [
                {"android": row.android, "gki": row.gki, "kmi": row.kmi}
                for row in content.KMI_ROWS
            ],
            "asset_template": content.KMI_ASSET_TEMPLATE,
            "download_base": "{}/download/".format(content.LATEST_RELEASE_URL),
        }
    )


@bp.get("/api/kmi/resolve")
def api_kmi_resolve():
    """由 osrelease 或 android+kernel 解析 KMI，对应模块 ZIP 的匹配逻辑。"""
    osrelease = request.args.get("osrelease", "").strip()
    android = request.args.get("android", "").strip()
    kernel = request.args.get("kernel", "").strip()

    if osrelease:
        resolved = kmi_module.resolve_kmi(osrelease)
        source = {"osrelease": osrelease}
    elif android and kernel:
        resolved = kmi_module.match_kmi(android, kernel)
        source = {"android": android, "kernel": kernel}
    else:
        return jsonify({"error": "缺少参数：提供 osrelease，或 android + kernel"}), 400

    if not resolved:
        return jsonify({"error": "未匹配到已收录的 KMI 变体", "input": source}), 404

    asset_name = content.KMI_ASSET_TEMPLATE.format(kmi=resolved)
    return jsonify(
        {
            "kmi": resolved,
            "asset": asset_name,
            "download_url": "{}/download/{}".format(content.LATEST_RELEASE_URL, asset_name),
            "input": source,
        }
    )


# --------------------------------------------------------------------------
# 错误页
# --------------------------------------------------------------------------

@bp.app_errorhandler(404)
def not_found(error):
    return render_template("error404.html"), 404


__all__ = ["bp"]
