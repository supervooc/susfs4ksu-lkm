"""KMI 解析：把内核 release 字符串映射到构建变体。

模块 ZIP 的自动匹配逻辑在站点里复刻了一遍，既能在 /api/kmi/resolve
里演示，也有单元测试兜底，避免两处规则各说各话。
"""

from __future__ import annotations

import re

from . import content

_KERNEL_VERSION = re.compile(r"^(\d+)\.(\d+)")
_ANDROID_TAG = re.compile(r"android(\d{1,2})", re.IGNORECASE)
_ANDROID_VERSION = re.compile(r"^(\d{1,2})(?:\.\d+)?$")


def match_kmi(android: str, kernel: str) -> str | None:
    """由 Android 版本与内核主/次版本得到 KMI 变体，未收录则返回 None。"""
    kernel_match = _KERNEL_VERSION.match(kernel.strip())
    android_match = _ANDROID_VERSION.match(android.strip())
    if not kernel_match or not android_match:
        return None
    candidate = "android{}-{}.{}".format(
        android_match.group(1), kernel_match.group(1), kernel_match.group(2)
    )
    return candidate if candidate in content.KMI_VARIANTS else None


def resolve_kmi(osrelease: str) -> str | None:
    """从完整的 osrelease 字符串解析 KMI，例如 6.6.30-android15-... -> android15-6.6。"""
    text = osrelease.strip()
    if not text:
        return None
    kernel_match = _KERNEL_VERSION.match(text)
    android_match = _ANDROID_TAG.search(text)
    if not kernel_match or not android_match:
        return None
    candidate = "android{}-{}.{}".format(
        android_match.group(1), kernel_match.group(1), kernel_match.group(2)
    )
    return candidate if candidate in content.KMI_VARIANTS else None


__all__ = ["match_kmi", "resolve_kmi"]
