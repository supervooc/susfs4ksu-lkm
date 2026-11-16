"""站点内联 SVG 图标库。

原本散落在 HTML 里的图标集中到 Python 模块，模板通过 icon 名称引用；
替换图标只需改这一处。

所有字符串均为可信常量，模板里使用 safe 过滤器输出。
"""

from __future__ import annotations

BRAND_MARK = """<svg viewBox="0 0 32 32" fill="none">
            <rect x="7.5" y="7.5" width="17" height="17" rx="4.5" stroke="currentColor" stroke-width="1.7"/>
            <rect x="12.5" y="12.5" width="7" height="7" rx="1.8" fill="currentColor"/>
            <path d="M12 3.5v4M16 3.5v4M20 3.5v4M12 24.5v4M16 24.5v4M20 24.5v4M3.5 12h4M3.5 16h4M3.5 20h4M24.5 12h4M24.5 16h4M24.5 20h4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
          </svg>"""

GITHUB = """<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2.5a9.5 9.5 0 0 0-3 18.52c.48.09.65-.2.65-.46v-1.8c-2.66.58-3.22-1.13-3.22-1.13-.44-1.1-1.06-1.4-1.06-1.4-.86-.59.07-.58.07-.58.96.07 1.46.98 1.46.98.85 1.45 2.22 1.03 2.76.79.09-.62.33-1.03.6-1.27-2.12-.24-4.35-1.06-4.35-4.72 0-1.04.37-1.9.98-2.57-.1-.24-.43-1.21.09-2.53 0 0 .8-.26 2.62.98a9.1 9.1 0 0 1 4.77 0c1.82-1.24 2.62-.98 2.62-.98.52 1.32.19 2.29.09 2.53.61.67.98 1.53.98 2.57 0 3.67-2.23 4.48-4.36 4.71.34.3.65.88.65 1.78v2.64c0 .26.17.55.66.46A9.5 9.5 0 0 0 12 2.5Z" fill="currentColor"/></svg>"""

ARROW_RIGHT_16 = """<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3 8h10m0 0-4-4m4 4-4 4" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>"""

ARROW_DOWNLOAD_16 = """<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M8 2v8m0 0 3-3m-3 3L5 7M3 13h10" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>"""

ARROW_DOWNLOAD_14 = """<svg viewBox="0 0 14 14" aria-hidden="true"><path d="M7 2v7m0 0 2.5-2.5M7 9 4.5 6.5M2.5 12h9" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/></svg>"""

ARROW_EXTERNAL_12 = """<svg viewBox="0 0 12 12" aria-hidden="true"><path d="M3 9 9 3M4 3h5v5" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/></svg>"""

ARROW_EXTERNAL_16 = """<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M5 11 11 5M6 5h5v5" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>"""

FEATURE_ICONS = {
    "kernel": """<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="6.5" y="6.5" width="11" height="11" rx="2.5" stroke="currentColor" stroke-width="1.5"/><rect x="10" y="10" width="4" height="4" rx="1" fill="currentColor"/><path d="M9 3v3M12 3v3M15 3v3M9 18v3M12 18v3M15 18v3M3 9h3M3 12h3M3 15h3M18 9h3M18 12h3M18 15h3" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/></svg>""",
    "matrix": """<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m12 3 8 4.5v9L12 21l-8-4.5v-9L12 3Z" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/><path d="m4.5 7.8 7.5 4.3 7.5-4.3M12 12v8.3" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/></svg>""",
    "terminal": """<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="4" width="18" height="16" rx="3" stroke="currentColor" stroke-width="1.5"/><path d="m7 9 3 3-3 3M12.5 15H17" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>""",
    "package": """<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3 4.5 6.5v5c0 4.6 3.1 7.9 7.5 9.5 4.4-1.6 7.5-4.9 7.5-9.5v-5L12 3Z" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/><path d="m8.5 12 2.2 2.2 4.8-4.8" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>""",
    "sliders": """<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h10M18 7h2M4 17h2M10 17h10" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/><circle cx="16" cy="7" r="2.2" stroke="currentColor" stroke-width="1.5"/><circle cx="8" cy="17" r="2.2" stroke="currentColor" stroke-width="1.5"/></svg>""",
    "code": """<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m8 8-4 4 4 4M16 8l4 4-4 4M13.5 5l-3 14" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>""",
}

FLOAT_CHECK = """<svg viewBox="0 0 20 20" aria-hidden="true"><path d="M4 10.5 8 14l8-8" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg>"""

FLOAT_KMI = """<svg viewBox="0 0 20 20" aria-hidden="true"><path d="M10 3v14M3 10h14M5.5 5.5l9 9M14.5 5.5l-9 9" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/></svg>"""

CALLOUT_INFO = """<svg viewBox="0 0 20 20" aria-hidden="true"><circle cx="10" cy="10" r="7.2" stroke="currentColor" stroke-width="1.4"/><path d="M10 9v4.5M10 6.4v.2" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>"""

__all__ = [
    "BRAND_MARK",
    "GITHUB",
    "ARROW_RIGHT_16",
    "ARROW_DOWNLOAD_16",
    "ARROW_DOWNLOAD_14",
    "ARROW_EXTERNAL_12",
    "ARROW_EXTERNAL_16",
    "FEATURE_ICONS",
    "FLOAT_CHECK",
    "FLOAT_KMI",
    "CALLOUT_INFO",
]
