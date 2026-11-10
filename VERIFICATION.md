# 验证记录

仓库：`supervooc/susfs4ksu-lkm`（fork 自 `inforcqb/susfs4ksu-for-lkm`），分支 `site-python` / `gh-pages`。
验证时间：2026-11-10（UTC）。环境：Windows 11 + Python 3.12.10 + Flask 3.1.3 + pytest 9.2.0。

## 1. 仓库自包含（从 GitHub 拉取快照验证）

```bash
curl -L https://codeload.github.com/supervooc/susfs4ksu-lkm/tar.gz/refs/heads/site-python -o site.tar.gz
tar -xzf site.tar.gz && cd susfs4ksu-lkm-site-python
python -m venv .venv
.venv/Scripts/pip install -r requirements-dev.txt
python -m pytest                # 37 passed, 1 skipped
python freeze.py --out public   # 导出 6 个文件
```

`1 skipped` 是与原静态站（`site-gh-pages/index.html`）的 DOM 对拍用例；该文件不在本仓库内，
所以在独立克隆里自动跳过，属于预期行为。

用生产级 WSGI 服务器起 `wsgi:app` 后实测：

| 请求 | 结果 |
| --- | --- |
| `GET /` | 200，标题 `SUSFS Guard LKM — 无需重编译内核的 SUSFS` |
| `GET /api/health` | `{"status":"ok","release":{"tag":"v2.3.0-r18.9-1","source":"live"}}` |
| `GET /api/kmi/resolve?osrelease=6.12.30-android16-8-gabc` | `android16-6.12` |
| `GET /download/android16-6.12` | 302 → 上游 Release 资产 |
| `GET /nope` | 404（自定义 404 页） |

## 2. GitHub Actions

运行 [#42856151014](https://github.com/supervooc/susfs4ksu-lkm/actions/runs/42856151014)：

| Job | 结论 | 内容 |
| --- | --- | --- |
| `test` | success | 安装依赖 -> `python -m pytest` -> `freeze.py` |
| `smoke` | success | ubuntu + gunicorn 起生产进程，实探页面 / API / 下载 302 |
| `deploy` | success | 冻结产物强推 `gh-pages`（commit `cab0ddb`） |

触发方式：push 到 `site-python`、每周一 03:00 UTC 定时、手动 `workflow_dispatch`。

## 3. GitHub Pages

https://supervooc.github.io/susfs4ksu-lkm/

- 首页 200，`<title>` 正确；
- `assets/styles.css`、`assets/main.js`、`favicon.svg`、`og.png`、`manifest.webmanifest`、
  `robots.txt`、`sitemap.xml` 全部 200；
- 版本号显示实时快照 `v2.3.0-r18.9-1`；
- 不存在的路径返回 404，命中自定义 404 页。

## 已知限制

- fork 仓库默认禁用 Actions，需在 Actions 页面手动启用一次；
- GitHub Pages 只能托管静态产物：`/download/<kmi>` 302、`/api/release` 实时数据、
  `/api/kmi/*` 只在动态部署（Docker / Render / Fly）时可用，静态版走 GitHub 直链与快照版本号。
