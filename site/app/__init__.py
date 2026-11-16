"""SUSFS Guard LKM 站点（Python 版）。

应用工厂：Flask + Jinja2，内容来自 app.content，图标来自 app.icons，
动态数据（最新 Release）来自 app.release。模板与静态资源与静态站完全
兼容，因此同一套代码既能作为服务端应用运行，也能冻结成 GitHub Pages
可托管的静态文件（见 freeze.py）。

启动：
    flask --app wsgi run --debug
"""

from __future__ import annotations

import os
from datetime import datetime, timezone

from flask import Flask, current_app, request, url_for
from markupsafe import Markup

from . import content, icons
from .release import ReleaseCache
from .text import highlight_shell, render_inline

_ICON_MAP = {
    "brand": icons.BRAND_MARK,
    "github": icons.GITHUB,
    "arrow-right": icons.ARROW_RIGHT_16,
    "arrow-download": icons.ARROW_DOWNLOAD_16,
    "arrow-external": icons.ARROW_EXTERNAL_16,
    "arrow-external-12": icons.ARROW_EXTERNAL_12,
    "download-14": icons.ARROW_DOWNLOAD_14,
    "float-check": icons.FLOAT_CHECK,
    "float-kmi": icons.FLOAT_KMI,
    "callout-info": icons.CALLOUT_INFO,
}


def icon(name: str) -> Markup:
    """按名称返回内联 SVG；feature:<key> 取特性图标。"""
    if name.startswith("feature:"):
        return Markup(icons.FEATURE_ICONS[name.split(":", 1)[1]])
    try:
        return Markup(_ICON_MAP[name])
    except KeyError:  # pragma: no cover - 模板拼错时快速失败
        raise KeyError("unknown icon: {}".format(name)) from None


def asset(filename: str) -> str:
    """静态资源地址；静态导出时使用相对路径，便于部署在子目录。"""
    app = current_app
    if app.config.get("STATIC_EXPORT"):
        return "assets/" + filename
    return url_for("site.assets", filename=filename)


def download_url(kmi: str) -> str:
    """下载入口：动态站点走 /download/<kmi>（可统计/换源），静态导出用 GitHub 直链。"""
    app = current_app
    if app.config.get("STATIC_EXPORT"):
        return content.LATEST_DOWNLOAD_TEMPLATE.format(kmi=kmi)
    return url_for("site.download", kmi=kmi)


def create_app(overrides: dict | None = None) -> Flask:
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config.update(
        SITE_URL=content.SITE_URL,
        RELEASE_TTL=600.0,
        RELEASE_TIMEOUT=4.0,
        OFFLINE=False,
        STATIC_EXPORT=False,
        JSON_AS_ASCII=False,
    )
    if overrides:
        app.config.update(overrides)
    if hasattr(app, "json"):  # Flask >= 2.2：让 JSON 中的中文保持可读
        app.json.ensure_ascii = False

    app.extensions["release_cache"] = ReleaseCache(
        ttl=float(app.config["RELEASE_TTL"]),
        timeout=float(app.config["RELEASE_TIMEOUT"]),
        offline=bool(app.config["OFFLINE"]) or None,
    )

    app.jinja_env.globals.update(
        c=content,
        icons=icons,
        icon=icon,
        asset=asset,
        download_url=download_url,
        inline=lambda text: Markup(render_inline(text)),
        highlight=lambda source: Markup(highlight_shell(source)),
        site_url=content.SITE_URL,
    )

    @app.context_processor
    def _inject_globals() -> dict:
        static_export = bool(app.config["STATIC_EXPORT"])
        home_url = content.SITE_URL if static_export else url_for("site.index")
        return {
            "static_export": static_export,
            "home_url": home_url,
            "year": datetime.now(timezone.utc).year,
            "request_path": request.path if request else "/",
        }

    from .routes import bp as site_bp

    app.register_blueprint(site_bp)
    return app


__all__ = ["create_app", "icon", "asset", "download_url"]
