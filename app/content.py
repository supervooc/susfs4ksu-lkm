"""站点内容层。

重构思路：把原来硬编码在 index.html 里的文案、链接、KMI 矩阵、
FAQ 等全部收敛为 Python 数据结构。模板只负责布局，不再重复文案；
新增/修改内容 = 改这个文件，而不是在 HTML 里找位置。

约定：
- 普通文案可用波浪号标记内联代码，例如 ~/proc/susfs_*~，
  由 render_inline() 转义后渲染为 <code>。
- 可信的展示型 HTML（统计数字、终端片段）单独标注，模板中经 safe 输出。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Final

# --------------------------------------------------------------------------
# 仓库与站点基本信息
# --------------------------------------------------------------------------

REPO_SLUG: Final = "inforcqb/susfs4ksu-for-lkm"
REPO_URL: Final = f"https://github.com/{REPO_SLUG}"
RELEASES_URL: Final = f"{REPO_URL}/releases"
LATEST_RELEASE_URL: Final = f"{RELEASES_URL}/latest"
DOCS_BLOB: Final = f"{REPO_URL}/blob/main"
ISSUES_URL: Final = f"{REPO_URL}/issues"
SITE_URL: Final = "https://inforcqb.github.io/susfs4ksu-for-lkm/"
OG_IMAGE: Final = f"{SITE_URL}assets/og.png"

# GitHub API 不可用时展示的版本号；同时是静态冻结时的快照版本。
FALLBACK_RELEASE_TAG: Final = "v2.3.0-r18.9"

KMI_ASSET_TEMPLATE: Final = "susfs_guard_lkm-{kmi}.ko"
LATEST_DOWNLOAD_TEMPLATE: Final = LATEST_RELEASE_URL + "/download/" + KMI_ASSET_TEMPLATE


@dataclass(frozen=True)
class NavItem:
    href: str
    label: str


@dataclass(frozen=True)
class Chip:
    label: str
    tone: str = ""  # green | blue | violet | ""


@dataclass(frozen=True)
class Action:
    label: str
    href: str
    style: str = "primary"  # primary | secondary
    external: bool = False
    icon: str = "arrow-right"


@dataclass(frozen=True)
class Headline:
    lead: str
    accent: str = ""


@dataclass(frozen=True)
class Segment:
    text: str
    class_name: str = ""  # term-cyan ...
    tag: str = ""  # 覆盖标签，例如 b（原站用 <b> 而不是 span）


@dataclass(frozen=True)
class TerminalLine:
    prefix: str
    line_class: str = ""
    prefix_class: str = ""  # term-prefix；留空为 term-prompt
    segments: tuple[Segment, ...] = ()
    cursor: bool = False


@dataclass(frozen=True)
class FloatCard:
    icon: str
    title: str
    caption: str
    position: str  # float-a | float-b


@dataclass(frozen=True)
class Stat:
    value_html: str  # 可信展示 HTML，例如 5.10<span>–</span>6.18
    label: str


@dataclass(frozen=True)
class Feature:
    icon: str
    title: str
    body: str


@dataclass(frozen=True)
class Step:
    number: str
    title: str
    body: str


@dataclass(frozen=True)
class CodeTab:
    id: str
    tab_id: str
    label: str
    code_label: str
    code: str
    footnote: str


@dataclass(frozen=True)
class KmiRow:
    android: str
    gki: str
    kmi: str


@dataclass(frozen=True)
class DocLink:
    index: str
    title: str
    description: str
    href: str


@dataclass(frozen=True)
class InterfaceCard:
    name: str
    body: str
    href: str = f"{DOCS_BLOB}/PROC_INTERFACES.md"


@dataclass(frozen=True)
class FaqItem:
    question: str
    answer: str


@dataclass(frozen=True)
class FooterColumn:
    title: str
    links: tuple[tuple[str, str], ...]  # (label, href)
    note: str = ""


# --------------------------------------------------------------------------
# <head> 与站点元信息
# --------------------------------------------------------------------------

TITLE: Final = "SUSFS Guard LKM — 无需重编译内核的 SUSFS"
DESCRIPTION: Final = (
    "SUSFS 的可加载内核模块移植版：无需重编译内核，支持 Android 12+、"
    "arm64-v8a、GKI 5.10–6.18，通过 KernelSU 或自带加载器载入。"
)
OG_DESCRIPTION: Final = (
    "把 SUSFS 装进可加载内核模块：保留原厂 GKI，支持 Android 12+ 与 5.10–6.18，"
    "KernelSU / 非 KernelSU 均可加载。"
)
OG_IMAGE_ALT: Final = "SUSFS Guard LKM — 无需重编译内核，直接加载内核模块"
TWITTER_DESCRIPTION: Final = (
    "把 SUSFS 装进可加载内核模块：保留原厂 GKI，支持 Android 12+ 与 5.10–6.18。"
)
THEME_COLOR: Final = "#06090f"

JSON_LD: Final = {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    "name": "SUSFS Guard LKM",
    "alternateName": "susfs4ksu-lkm",
    "applicationCategory": "DeveloperApplication",
    "operatingSystem": "Android 12+",
    "description": "SUSFS 的可加载内核模块移植版，支持 arm64-v8a 与 GKI 5.10–6.18。",
    "url": SITE_URL,
    "downloadUrl": LATEST_RELEASE_URL,
    "codeRepository": REPO_URL,
    "license": "https://www.gnu.org/licenses/old-licenses/gpl-2.0.html",
    "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
}

# --------------------------------------------------------------------------
# 导航 / Hero
# --------------------------------------------------------------------------

NAV: Final[tuple[NavItem, ...]] = (
    NavItem("#features", "特性"),
    NavItem("#install", "安装"),
    NavItem("#kmi", "KMI"),
    NavItem("#docs", "文档"),
    NavItem("#faq", "FAQ"),
)

HERO_EYEBROW: Final = "LOADABLE KERNEL MODULE"
HERO_RELEASE_LABEL: Final = "上游最新"
HERO_HEADLINE: Final = Headline("把 SUSFS", "装进内核模块")
HERO_LEDE: Final = (
    "无需重编译内核，也不用替换 GKI。选择与设备 KMI 匹配的 ~.ko~，"
    "通过 KernelSU 或自带加载器载入，即可暴露完整的 SUSFS ~/proc~ 控制接口。"
)
HERO_ACTIONS: Final = (
    Action("开始安装", "#install", "primary", False, "arrow-right"),
    Action("查看源码", REPO_URL, "secondary", True, "arrow-external"),
)
HERO_CHIPS: Final = (
    Chip("Android 12+", "green"),
    Chip("arm64-v8a", "blue"),
    Chip("GKI 5.10–6.18", "violet"),
    Chip("GPL-2.0-only"),
)

TERMINAL_TITLE: Final = "susfs_guard_lkm · load"
TERMINAL_LABEL: Final = "示意"
TERMINAL_LINES: Final = (
    TerminalLine(
        prefix="$",
        segments=(
            Segment("ksud", "term-cyan"),
            Segment(" insmod /data/adb/loader/susfs_guard_lkm.ko"),
        ),
    ),
    TerminalLine(
        prefix="[ ok ]",
        line_class="term-ok",
        prefix_class="term-prefix",
        segments=(Segment("module "), Segment("susfs_guard_lkm", tag="b"), Segment(" loaded")),
    ),
    TerminalLine(
        prefix="[ ok ]",
        line_class="term-ok",
        prefix_class="term-prefix",
        segments=(Segment("kmi matched "), Segment("android15-6.6", tag="b")),
    ),
    TerminalLine(
        prefix="[ ok ]",
        line_class="term-ok",
        prefix_class="term-prefix",
        segments=(Segment("expose_proc = 1"),),
    ),
    TerminalLine(
        prefix="[ .. ]",
        line_class="term-dim",
        prefix_class="term-prefix",
        segments=(Segment("waiting for susfs rules…"),),
    ),
    TerminalLine(prefix="$", line_class="term-prompt-line", cursor=True),
)
TERMINAL_FOOT: Final = ("GKI 6.6 · arm64-v8a · LKM", "no kernel rebuild")
FLOAT_CARDS: Final = (
    FloatCard("check", "0 次重编译", "keep stock GKI", "float-a"),
    FloatCard("kmi", "KMI 自动匹配", "8 个 GKI 变体", "float-b"),
)

STATS: Final = (
    Stat("8", "KMI 构建变体"),
    Stat("5.10<span>–</span>6.18", "GKI 内核覆盖"),
    Stat("0", "内核重编译次数"),
    Stat("100<span>%</span>", "开源可审计"),
)

# --------------------------------------------------------------------------
# 01 特性
# --------------------------------------------------------------------------

FEATURES_KICKER: Final = "01 / WHY LKM"
FEATURES_HEADLINE: Final = Headline("保留原厂内核，", "只加载需要的能力")
FEATURES_INTRO: Final = (
    "传统 SUSFS 需要把补丁编进内核。LKM 版本把这件事拆开：内核保持原样，"
    "SUSFS 以模块形式按需载入，升级、回滚与审计都更轻。"
)
FEATURES: Final = (
    Feature(
        "kernel",
        "内核零改动",
        "以 ~.ko~ 形式运行，不重编译、不替换 GKI。系统 OTA 与内核分区保持原样，回滚只需卸载模块。",
    ),
    Feature(
        "matrix",
        "按 KMI 精准构建",
        "覆盖 Android 12–17、GKI 5.10–6.18 的 8 个变体。每个产物都对应明确的 Android 版本与内核主版本。",
    ),
    Feature(
        "terminal",
        "KernelSU 原生路径",
        "~ksud insmod~ 直接加载；非 KernelSU 环境可使用 Release 自带的 ~susfs_insmod~，同样无需重新打包内核。",
    ),
    Feature(
        "package",
        "开箱即用的模块包",
        "刷入 KernelSU 模块 ZIP，开机按 ~/proc/sys/kernel/osrelease~ 自动选择 ~.ko~，并带 ~expose_proc=1~。",
    ),
    Feature(
        "sliders",
        "完整控制接口",
        "~expose_proc=1~ 暴露 ~/proc/susfs_*~。路径、挂载、kstat、open redirect 与 mmap 规则统一由用户态下发。",
    ),
    Feature(
        "code",
        "公开、可审计",
        "GPL-2.0-only。源码、KMI 构建矩阵、CFI 调用点检查与完整接口文档全部开放，方便核对每个变体。",
    ),
)

# --------------------------------------------------------------------------
# 02 安装
# --------------------------------------------------------------------------

INSTALL_KICKER: Final = "02 / QUICK START"
INSTALL_HEADLINE: Final = Headline("从下载到加载，", "四步完成")
INSTALL_LEDE: Final = (
    "先确认设备的 Android 版本与内核主版本，再选对应的 ~.ko~。不确定时，优先使用模块 ZIP，"
    "让加载脚本自动匹配。"
)
STEPS: Final = (
    Step(
        "01",
        "确认 KMI",
        "读取 ~ro.build.version.release~ 与 ~/proc/sys/kernel/osrelease~，对照下方矩阵选择产物。",
    ),
    Step(
        "02",
        "载入模块",
        "KernelSU 使用 ~ksud insmod~；其他环境使用 Release 附带的 ~susfs_insmod~。",
    ),
    Step(
        "03",
        "下发规则",
        "模块只负责加载，不设置任何 SUSFS 规则。规则由管理器或你的脚本写入 ~/proc/susfs_*~。",
    ),
    Step(
        "04",
        "需要时卸载",
        "执行 ~rmmod susfs_guard_lkm~ 即可即时卸载；模块包则在管理器中停用或删除后重启。",
    ),
)
INSTALL_CALLOUT_LEAD: Final = "提前加载："
INSTALL_CALLOUT: Final = (
    "如果 SUSFS 规则必须在模块 ~post-fs-data~ 与挂载之前生效，以 root 执行 "
    "~touch /data/adb/modules/susfs_guard_lkm/early_load~ 后重启。"
)

CODE_TABS: Final = (
    CodeTab(
        id="pane-ksu",
        tab_id="tab-ksu",
        label="KernelSU",
        code_label="adb · KernelSU",
        code="""# 1. 推送与设备 KMI 对应的 .ko
adb push susfs_guard_lkm-android15-6.6.ko /data/adb/loader/susfs_guard_lkm.ko

# 2. 通过 KernelSU 载入
adb shell su -c "ksud insmod /data/adb/loader/susfs_guard_lkm.ko"

# 3. 确认模块已载入
adb shell su -c "lsmod | grep susfs_guard_lkm"
""",
        footnote="设备上的目标路径可自定义；示例以 Android 15 / GKI 6.6 为例。",
    ),
    CodeTab(
        id="pane-loader",
        tab_id="tab-loader",
        label="非 KernelSU",
        code_label="adb · susfs_insmod",
        code="""# 1. 推送模块与 Release 自带的加载器
adb push susfs_guard_lkm-android14-6.1.ko /data/adb/loader/susfs_guard_lkm.ko
adb push susfs_insmod /data/adb/loader/susfs_insmod

# 2. 赋予执行权限并载入
adb shell su -c "chmod 755 /data/adb/loader/susfs_insmod"
adb shell su -c "/data/adb/loader/susfs_insmod /data/adb/loader/susfs_guard_lkm.ko"

# 3. 卸载
adb shell su -c "rmmod susfs_guard_lkm"
""",
        footnote="非 KernelSU 环境依靠 ~susfs_insmod~ 在用户态完成符号解析与载入。",
    ),
    CodeTab(
        id="pane-zip",
        tab_id="tab-zip",
        label="模块 ZIP",
        code_label="KernelSU Manager",
        code="""# 在 KernelSU 管理器中：
# 模块 → 从本地安装 → 选择 ZIP → 重启

# 产物名称
susfs_guard_lkm-module-<tag>-arm64.zip

# 默认行为
# - 自动匹配设备 KMI
# - 以 expose_proc=1 载入
# - 不设置任何 SUSFS 规则

# 可选：手动指定 KMI
echo android15-6.6 > /data/adb/modules/susfs_guard_lkm/kmi_override
""",
        footnote="仅 arm64 与 KernelSU 系管理器；模块包会跳过已存在的 SUSFS 接口。",
    ),
)

# --------------------------------------------------------------------------
# 03 KMI 兼容矩阵
# --------------------------------------------------------------------------

KMI_KICKER: Final = "03 / COMPATIBILITY"
KMI_HEADLINE: Final = Headline("选对 KMI，", "再载入模块")
KMI_INTRO: Final = (
    "Android 版本与内核主版本共同决定产物。下载链接始终指向上游最新 Release 中的同名文件；"
    "若使用模块 ZIP，则无需手动选择。"
)
KMI_ROWS: Final = (
    KmiRow("Android 12", "5.10", "android12-5.10"),
    KmiRow("Android 13", "5.10", "android13-5.10"),
    KmiRow("Android 13", "5.15", "android13-5.15"),
    KmiRow("Android 14", "5.15", "android14-5.15"),
    KmiRow("Android 14", "6.1", "android14-6.1"),
    KmiRow("Android 15", "6.6", "android15-6.6"),
    KmiRow("Android 16", "6.12", "android16-6.12"),
    KmiRow("Android 17", "6.18", "android17-6.18"),
)
KMI_CHECK_KICKER: Final = "HOW TO CHECK"
KMI_CHECK_TITLE: Final = "设备 KMI 怎么确认？"
KMI_CHECK_BODY: Final = (
    "内核 release 字符串通常同时包含内核版本与 Android 标签，例如 ~6.6.30-android15-…~。"
)
KMI_CHECK_COMMANDS: Final = (
    "getprop ro.build.version.release",
    "cat /proc/sys/kernel/osrelease",
)
KMI_CHECK_NOTE: Final = "仅支持 arm64-v8a。x64 设备请使用单独的社区移植。"
KMI_ASIDE_LINK: Final = (
    "获取模块 ZIP",
    "推荐给不想手动选 .ko 的用户",
    LATEST_RELEASE_URL,
)

# --------------------------------------------------------------------------
# 04 文档与接口
# --------------------------------------------------------------------------

DOCS_KICKER: Final = "04 / DOCUMENTATION"
DOCS_HEADLINE: Final = Headline("规则怎么下发，", "接口里都有答案")
DOCS_INTRO: Final = (
    "加载只是第一步。真正的 SUSFS 行为由用户态通过 ~/proc/susfs_*~ 控制；"
    "所有写入成功返回长度，失败返回负 errno。"
)
DOC_LINKS: Final = (
    DocLink("01", "中文 README", "加载、模块包与 early_load 说明", f"{DOCS_BLOB}/README.md"),
    DocLink("02", "/proc 接口手册", "全部控制节点、写命令与状态输出", f"{DOCS_BLOB}/PROC_INTERFACES.md"),
    DocLink("03", "English README", "Installation and module package guide", f"{DOCS_BLOB}/README.en.md"),
    DocLink("04", "构建矩阵与 CI", "8 个 GKI 变体、符号与 CFI 检查", f"{DOCS_BLOB}/.github/workflows/build-ddk.yml"),
)
INTERFACES: Final = (
    InterfaceCard("/proc/susfs_kstat", "伪装 ~stat()~ / ~statx()~ / maps 中的 inode 与时间戳。"),
    InterfaceCard("/proc/susfs_open_redirect", "把指定 ~open()~ 重定向到另一个文件，并覆盖反向面。"),
    InterfaceCard("/proc/susfs_path", "sus_path 规则表。直接 ~cat~ 即可查看当前隐藏清单。"),
    InterfaceCard("/proc/susfs_map", "按 inode 隐藏 mmap 的真实文件，覆盖 maps / pagemap 等视图。"),
    InterfaceCard("/proc/susfs_hide_mounts", "定义哪些挂载属于“我们的”，决定最终隐藏的挂载集合。"),
    InterfaceCard("/proc/susfs_hide_modules", "按名字把其他内核模块从 ~/proc/modules~ 中移除。"),
)

# --------------------------------------------------------------------------
# 05 FAQ
# --------------------------------------------------------------------------

FAQ_KICKER: Final = "05 / FAQ"
FAQ_HEADLINE: Final = Headline("开始之前，", "先看这几个问题")
FAQ_INTRO: Final = (
    "还有未覆盖的情况？直接在模块仓库提交 Issue，附上设备、Android 版本、内核 release 与加载日志。"
)
FAQ_LINK: Final = ("前往 Issues", ISSUES_URL)
FAQ: Final = (
    FaqItem(
        "需要重新编译内核吗？",
        "不需要。LKM 版本以 ~.ko~ 形式运行，不修改内核源码，也不替换 GKI。你只需要选择与设备 KMI 匹配的产物，然后载入。",
    ),
    FaqItem(
        "如何确认设备应该用哪个 KMI？",
        "运行 ~getprop ro.build.version.release~ 与 ~cat /proc/sys/kernel/osrelease~。"
        "例如 release 为 ~6.6.30-android15-…~，对应 ~android15-6.6~。模块 ZIP 会自动完成同样的匹配。",
    ),
    FaqItem(
        "非 KernelSU 设备可以用吗？",
        "可以。Release 附带独立的 ~susfs_insmod~ 加载器，在 root 环境中直接载入 ~.ko~。"
        "注意它仍然要求设备满足 Android 12+、arm64-v8a 与对应 GKI 版本。",
    ),
    FaqItem(
        "刷入模块后没有 ~/proc/susfs_*~ 怎么办？",
        "先确认模块确实以 ~expose_proc=1~ 载入，并检查 ~lsmod | grep susfs~。"
        "如果系统已有内置 SUSFS，模块会跳过加载；此时应由现有接口负责。模块本身不会创建规则。",
    ),
    FaqItem(
        "模块会修改系统分区吗？",
        "不会写入内核分区。手动方式只在运行时载入 LKM；模块 ZIP 也只增加 KernelSU 模块目录下的加载脚本与产物，"
        "停用或删除后重启即可恢复。",
    ),
    FaqItem(
        "为什么下载链接指向 GitHub Release？",
        "本站不单独发布二进制，实际构建产物由 ~inforcqb/susfs4ksu-for-lkm~ 的 Release 提供。"
        "站点不镜像、不重打包这些文件，下载后请自行校验来源。",
    ),
)

# --------------------------------------------------------------------------
# CTA / 页脚
# --------------------------------------------------------------------------

CTA_KICKER: Final = "READY WHEN YOU ARE"
CTA_TITLE: Final = "把 SUSFS 装进你的内核。"
CTA_BODY: Final = (
    "保留原厂 GKI，选择正确的 KMI，然后开始。遇到问题，源码、构建日志与接口文档都在手边。"
)
CTA_ACTIONS: Final = (
    Action("下载最新版本", LATEST_RELEASE_URL, "primary", True, "arrow-download"),
    Action("GitHub 仓库", REPO_URL, "secondary", True, "arrow-external"),
)

FOOTER_TAGLINE: Final = "把 SUSFS 变成可加载内核模块。"
FOOTER_TAGLINE_2: Final = "保留原厂 GKI，按需载入。"
FOOTER_BADGES: Final = ("Android 12+", "arm64-v8a", "GPL-2.0-only")
FOOTER_STATIC_NOTE: Final = "仅供技术研究"
FOOTER_COLUMNS: Final = (
    FooterColumn(
        "资源",
        (
            ("安装指南", "#install"),
            ("KMI 兼容矩阵", "#kmi"),
            ("/proc 接口文档", f"{DOCS_BLOB}/PROC_INTERFACES.md"),
            ("README", f"{DOCS_BLOB}/README.md"),
        ),
    ),
    FooterColumn(
        "项目",
        (
            ("项目主仓库", REPO_URL),
            ("Releases", RELEASES_URL),
            ("x64 移植", "https://github.com/ymuuuu/susfs4ksu-lkm-x64"),
        ),
    ),
    FooterColumn(
        "说明",
        (
            ("GPL-2.0-only", f"{DOCS_BLOB}/LICENSE"),
            ("问题反馈", ISSUES_URL),
            ("站点源码", f"{REPO_URL}/tree/gh-pages"),
        ),
        note=FOOTER_STATIC_NOTE,
    ),
)
FOOTER_COPYRIGHT: Final = "SUSFS Guard LKM · Android GKI / KernelSU 项目文档。"
FOOTER_DISCLAIMER: Final = (
    "内核模块操作有风险。请先备份，并在理解加载机制后自行承担使用后果。"
)

# 供路由与测试使用的 KMI 注册表
KMI_VARIANTS: Final = tuple(row.kmi for row in KMI_ROWS)

__all__ = [
    "REPO_SLUG", "REPO_URL", "RELEASES_URL", "LATEST_RELEASE_URL", "DOCS_BLOB",
    "ISSUES_URL", "SITE_URL", "OG_IMAGE", "FALLBACK_RELEASE_TAG", "KMI_ASSET_TEMPLATE",
    "LATEST_DOWNLOAD_TEMPLATE", "NavItem", "Chip", "Action", "Headline", "Segment",
    "TerminalLine", "FloatCard", "Stat", "Feature", "Step", "CodeTab", "KmiRow",
    "DocLink", "InterfaceCard", "FaqItem", "FooterColumn", "TITLE", "DESCRIPTION",
    "OG_DESCRIPTION", "OG_IMAGE_ALT", "TWITTER_DESCRIPTION", "THEME_COLOR", "JSON_LD",
    "NAV", "HERO_EYEBROW", "HERO_RELEASE_LABEL", "HERO_HEADLINE", "HERO_LEDE",
    "HERO_ACTIONS", "HERO_CHIPS", "TERMINAL_TITLE", "TERMINAL_LABEL", "TERMINAL_LINES",
    "TERMINAL_FOOT", "FLOAT_CARDS", "STATS", "FEATURES_KICKER", "FEATURES_HEADLINE",
    "FEATURES_INTRO", "FEATURES", "INSTALL_KICKER", "INSTALL_HEADLINE", "INSTALL_LEDE",
    "STEPS", "INSTALL_CALLOUT_LEAD", "INSTALL_CALLOUT", "CODE_TABS", "KMI_KICKER",
    "KMI_HEADLINE", "KMI_INTRO", "KMI_ROWS", "KMI_CHECK_KICKER", "KMI_CHECK_TITLE",
    "KMI_CHECK_BODY", "KMI_CHECK_COMMANDS", "KMI_CHECK_NOTE", "KMI_ASIDE_LINK",
    "DOCS_KICKER", "DOCS_HEADLINE", "DOCS_INTRO", "DOC_LINKS", "INTERFACES",
    "FAQ_KICKER", "FAQ_HEADLINE", "FAQ_INTRO", "FAQ_LINK", "FAQ", "CTA_KICKER",
    "CTA_TITLE", "CTA_BODY", "CTA_ACTIONS", "FOOTER_TAGLINE", "FOOTER_TAGLINE_2",
    "FOOTER_BADGES", "FOOTER_COLUMNS", "FOOTER_STATIC_NOTE", "FOOTER_COPYRIGHT",
    "FOOTER_DISCLAIMER", "KMI_VARIANTS",
]
