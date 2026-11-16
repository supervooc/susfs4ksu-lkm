"""把 Flask 站点冻结成静态文件，继续托管在 GitHub Pages。

服务端渲染是运行时能力；GitHub Pages 只能托管静态文件。两条路都保留：
- 动态部署（Render / Fly / 自有服务器）：python 为核心，Release 信息实时更新；
- 静态部署：python freeze.py 导出 public/，内容与模板仍由 Python 生成。

用法：
    python freeze.py                      # 输出 public/，联网取最新 Release
    python freeze.py --out dist --offline # 离线，使用 content 中的回退版本
"""

from __future__ import annotations

import argparse
import os
import shutil
import stat
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import create_app  # noqa: E402

# (URL, 输出文件名)；顺序即导出顺序
PAGES = (
    ("/", "index.html"),
    ("/robots.txt", "robots.txt"),
    ("/sitemap.xml", "sitemap.xml"),
    ("/manifest.webmanifest", "manifest.webmanifest"),
)

NOT_FOUND_PROBE = "/__freeze_404_probe__"


def _force_rmtree(path: Path) -> None:
    """删除输出目录；兼容 Windows 上 git 对象的只读属性。"""

    def _retry(func, target, exc):
        try:
            os.chmod(target, stat.S_IWRITE)
        except OSError:
            pass
        func(target)

    if sys.version_info >= (3, 12):
        shutil.rmtree(path, onexc=_retry)
    else:  # pragma: no cover - 兼容 Python 3.11 及更早
        shutil.rmtree(
            path,
            onerror=lambda func, target, exc_info: _retry(func, target, exc_info[1]),
        )


def freeze(out: Path, offline: bool = False) -> list[Path]:
    app = create_app({"STATIC_EXPORT": True, "OFFLINE": offline})
    out = Path(out)
    if out.exists():
        _force_rmtree(out)
    shutil.copytree(ROOT / "app" / "static" / "assets", out / "assets")

    written: list[Path] = []
    with app.test_client() as client:
        for url, name in PAGES:
            response = client.get(url)
            if response.status_code != 200:
                raise RuntimeError("{} returned {}".format(url, response.status_code))
            target = out / name
            target.write_bytes(response.data)
            written.append(target)

        response = client.get(NOT_FOUND_PROBE)
        if response.status_code != 404:
            raise RuntimeError("404 page returned {}".format(response.status_code))
        target = out / "404.html"
        target.write_bytes(response.data)
        written.append(target)

    (out / ".nojekyll").write_text("", encoding="utf-8")
    written.append(out / ".nojekyll")
    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="导出静态站")
    parser.add_argument("--out", default="public", help="输出目录（默认 public/）")
    parser.add_argument("--offline", action="store_true", help="不访问 GitHub API")
    args = parser.parse_args(argv)

    out = Path(args.out)
    if not out.is_absolute():
        out = ROOT / out
    written = freeze(out, offline=args.offline)
    print("已导出 {} 个文件到 {}".format(len(written), out))
    for path in written:
        print("  -", path.relative_to(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
