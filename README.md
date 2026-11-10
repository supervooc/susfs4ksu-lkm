# SUSFS Guard LKM 站点（Python 版）

原 `gh-pages` 分支是一个纯静态单页站：一个 679 行的 `index.html`、一份 `styles.css`、一个 `main.js`。
本次重构把它变成以 Python 为核心的站点：**Flask + Jinja2 服务端渲染**，内容、图标、代码高亮、
Release 信息、KMI 解析、下载入口全部由 Python 负责，同时保留「一键冻结成静态站」的能力，
因此仍可继续托管在 GitHub Pages。

页面视觉与原站一致：CSS/JS 原样复用，DOM 结构有测试逐元素对拍（`tests/test_structure.py`）。

## 结论先说

- **能重构，且已完成**。原站没有任何框架依赖，改造成本低；风险集中在部署方式（见「取舍」）。
- 纯静态托管 + Python 核心并不矛盾：运行时用 Flask，发布时 `python freeze.py` 导出静态文件。
- 如果目标只是「换个静态生成器」，Pelican / MkDocs 更轻；选 Flask 是为了顺带拿到动态能力
  （最新版本号、下载重定向、KMI 解析接口、可扩展的 JSON API）。

## 架构

```
浏览器
  └─ Flask (wsgi.py)
       ├─ app/content.py     内容层：文案、链接、KMI 矩阵、FAQ、页脚（唯一事实来源）
       ├─ app/icons.py       内联 SVG 图标
       ├─ app/text.py        ~code~ 内联标记、Shell 注释高亮、HTML 转义
       ├─ app/kmi.py         osrelease / android+kernel -> KMI 变体
       ├─ app/release.py     GitHub Release 抓取 + TTL 缓存 + 离线回退
       ├─ app/routes.py      页面路由、下载重定向、JSON API、robots/sitemap/manifest
       ├─ app/templates/     base.html / index.html / partials / 404
       └─ app/static/assets/ styles.css、main.js、favicon、og 图片（原样复用）
```

目录：

```
site-python/
├─ app/
│  ├─ __init__.py        应用工厂、Jinja 全局函数（icon/asset/download_url/inline/highlight）
│  ├─ content.py         全部站点内容（中文文案集中在此）
│  ├─ icons.py           SVG 图标常量
│  ├─ kmi.py             KMI 解析规则
│  ├─ release.py         Release 数据源（缓存 + 回退）
│  ├─ routes.py          路由与 API
│  ├─ text.py            渲染小工具
│  ├─ templates/         Jinja2 模板
│  └─ static/assets/     复用的静态资源
├─ tests/                内容 / 文本 / KMI / Release / 路由 / 冻结 / 结构对拍
├─ freeze.py             导出静态站（GitHub Pages 可用）
├─ wsgi.py               WSGI 入口
├─ requirements.txt      运行依赖（Flask、gunicorn）
├─ requirements-dev.txt  开发依赖（pytest）
└─ Dockerfile            容器化部署
```

## 原站 → Python 版的映射

| 原站部分 | Python 版位置 |
| --- | --- |
| `index.html` 的文案 | `app/content.py` 数据类实例 |
| 内联 SVG | `app/icons.py` |
| 手写的 `<code>` 标签 | `app/text.py` 的 `render_inline()`（~code~ 标记） |
| 代码块里的 `<span class="c">` | `app/text.py` 的 `highlight_shell()` |
| 写死的版本号 v2.3.0-r18.9 | `app/release.py` 实时查询，失败回退到 `FALLBACK_RELEASE_TAG` |
| 直接指向 GitHub 的下载链接 | `/download/<kmi>` -> 302 上游资产（静态导出时还原为直链） |
| 静态 `robots.txt` / `sitemap.xml` / `manifest.webmanifest` | 由 `app/routes.py` 生成 |
| `index.html` 页面骨架 | `app/templates/index.html` + `partials/*.html` |
| `404.html` | `app/templates/error404.html`（同样由 Flask 兜底） |

## 用 Python 换来哪些能力

1. **版本号不再手改**：渲染时读 GitHub Releases API，10 分钟缓存；断网时回退，页面不报错。
2. **下载可路由**：`/download/android15-6.6` 校验 KMI 后 302 到上游资产，未来可加统计或镜像切换。
3. **KMI 解析接口**：`/api/kmi/resolve?osrelease=6.6.30-android15-8-gabc` -> `android15-6.6`，
   与模块 ZIP 的自动匹配规则同源，并有单元测试。
4. **矩阵可复用**：`/api/kmi` 返回 8 个变体，方便脚本或其他前端消费。
5. **内容单一来源**：改 FAQ、加特性、调 KMI 只动 `app/content.py`，不用在 HTML 里找匹配的闭合标签。
6. **SEO 元数据由模板渲染**：canonical / OG / JSON-LD 从同一份数据生成，不会漂移。

## 本地运行

```bash
cd site-python
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
# source .venv/bin/activate

pip install -r requirements-dev.txt
flask --app wsgi run --debug
```

打开 http://127.0.0.1:5000/ 。

离线（不访问 GitHub API）：

```bash
# Windows PowerShell
$env:SITE_OFFLINE = "1"
flask --app wsgi run --debug
```

## 测试

```bash
pytest
```

覆盖：内容一致性、文本渲染/转义、KMI 解析、Release 缓存与回退、全部路由与 API、
静态冻结、以及与原 `index.html` 的 DOM 结构对拍。

## 导出静态站（继续用 GitHub Pages）

```bash
python freeze.py --out public          # 联网取最新 Release
python freeze.py --out public --offline  # 使用回退版本
```

`public/` 里是完整静态站（含 `404.html`、`robots.txt`、`sitemap.xml`、`manifest.webmanifest`、`.nojekyll`）。
把这个目录推到 `gh-pages` 分支即可。注意静态版的差异：

- 版本号是构建时快照，不会自动更新（需要定时重建）；
- 下载链接直接指向 GitHub Release，不经过 `/download/<kmi>`。

## 部署

**动态（推荐，Python 为核心）**：

```bash
docker build -t susfs-site .
docker run -p 8000:8000 susfs-site
# 或
gunicorn -b 0.0.0.0:8000 --workers 2 wsgi:app
```

也可以直接部署到 Render / Fly.io / Railway / 任意 VPS（WSGI 应用，无状态）。

**静态**：`python freeze.py` 后托管到 GitHub Pages / Cloudflare Pages / Nginx。

## 取舍与风险

1. **GitHub Pages 不能运行 Python**。当前 `gh-pages` 分支靠静态文件工作；改成 Flask 后必须
   二选一：部署 Python 服务，或用 `freeze.py` 继续静态托管。两者都保留，切换成本低。
2. **动态能力需要运行时**：进程、依赖、监控、证书。单页文档站属于过度设计，只有在需要
   「实时版本号 / 下载统计 / 内容管理」时才值得。
3. **GitHub API 匿名限流**：60 次/小时/IP；站点 10 分钟缓存 + 失败回退，正常访问远低于上限。
   生产环境建议配置 token 或改为构建时注入。
4. **依赖增加**：Flask 及其依赖需要维护；静态站则零依赖。若想更轻，可换 FastAPI 或纯标准库，
   但 Jinja2 + Flask 的模板生态更省事。
5. **样式与脚本未重写**：`styles.css` / `main.js` 原样复用，减少视觉回归；代价是前端仍是
   原生 JS，不是 Python 能覆盖的部分。

## 后续可做

- 用 Markdown + front-matter 管理 `/proc` 接口文档，Flask 端渲染成子页面；
- 加一个只读管理后台维护 FAQ / KMI 矩阵（当前改 `content.py` 即可，无需后台）；
- 全量 Releases 列表与各变体下载量统计；
- 中英双语路由（`/` 与 `/en/`），内容层已按数据组织，加语言字段即可；
- 构建时抓取 Release 并生成 `release.json`，让静态站也能更新版本号。

## 验证记录

环境：Windows 11 / Python 3.12.10 / Flask 3.1.3 / Jinja2 3.1.6 / pytest 9.2.0，无头 Edge 截图。

1. **单元与集成测试**：`pytest` 38 项全部通过，覆盖内容一致性、文本渲染与转义、KMI 解析、
   Release 缓存与回退、全部页面 / API / 404 / 下载重定向、静态冻结。
2. **DOM 结构对拍**：`tests/test_structure.py` 把 Flask 渲染结果与原 `index.html` 逐元素比较
   （tag + id + class 集合），缺失与多余元素均为 0。
3. **可见文本对拍**：去掉标签后原站 5071 字符、Python 版 5073 字符，唯一差异是实时版本号
   `v2.3.0-r18.9` -> `v2.3.0-r18.9-1`（多 2 个字符），其余文案 100% 相同。
4. **像素级视觉回归**（1440px 宽、2x 缩放的整页截图）：
   - Flask 动态渲染 vs `freeze.py` 静态导出：**0 个差异像素**；
   - Python 版 vs 原静态站（同一 http 协议下）：**179 个差异像素**，边界框
     `(121, 81) - (255, 266)`，正是 hero 里 release 版本号所在区域；
   - 作为对照，原静态站自身在 `file://` 与 `http://` 下渲染就相差 4.6 万像素（字体平滑差异），
     说明剩余差异与重构无关。
5. **行为验证**：`/download/android15-6.6` 返回 302 且 Location 指向
   `releases/latest/download/susfs_guard_lkm-android15-6.6.ko`；未知 KMI 返回 404；
   `/api/release` 实际返回上游 8 个资产（含大小），断网时回退到 `v2.3.0-r18.9`。

截图与对比脚本放在工作区 `shots/`（`compare_png.py` 为不依赖 Pillow 的 PNG 解码对比）。

---

原站与本文档均指向 [inforcqb/susfs4ksu-for-lkm](https://github.com/inforcqb/susfs4ksu-for-lkm)。
站点内容与内核模块操作风险说明保持原文不变。
