"""文本渲染工具：内联代码标记、Shell 代码高亮、内联标记校验。

原站点把 <code> 与高亮 span 直接写在 HTML 里。Python 版把它们
交给函数处理：内容层保持纯文本，渲染层负责转义与标记，安全性更好，
也让代码片段可以单独测试。
"""

from __future__ import annotations

import html
import re

# 内容层用波浪号包裹内联代码：~ro.build.version.release~
_INLINE_CODE = re.compile(r"~([^~\n]+)~")


def render_inline(text: str) -> str:
    """把纯文本渲染为 HTML：先整体转义，再把 ~code~ 变成 <code>。"""
    escaped = html.escape(text, quote=False)
    return _INLINE_CODE.sub(r"<code>\1</code>", escaped)


def strip_inline_markup(text: str) -> str:
    """去掉内联代码标记，返回纯文本（用于 meta / JSON 输出）。"""
    return text.replace("~", "")


def highlight_shell(source: str) -> str:
    """最简 Shell 高亮：整行 # 注释包一层 span.c，其余转义。

    与原站点手工书写的 <span class="c"> 结构保持一致，所以样式无需改动。
    """
    lines = source.rstrip("\n").split("\n")
    rendered: list[str] = []
    for line in lines:
        if line.lstrip().startswith("#"):
            rendered.append(f'<span class="c">{html.escape(line, quote=False)}</span>')
        else:
            rendered.append(html.escape(line, quote=False))
    return "\n".join(rendered)


__all__ = ["render_inline", "strip_inline_markup", "highlight_shell"]
