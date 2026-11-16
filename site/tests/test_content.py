"""内容层自检：确保 Python 数据与页面约定一致。"""

from app import content


def test_kmi_registry_matches_rows():
    assert content.KMI_VARIANTS == tuple(row.kmi for row in content.KMI_ROWS)
    assert len(content.KMI_VARIANTS) == 8
    assert len(set(content.KMI_VARIANTS)) == len(content.KMI_VARIANTS)


def test_kmi_rows_cover_android_and_gki():
    expected = {
        ("Android 12", "5.10"),
        ("Android 13", "5.10"),
        ("Android 13", "5.15"),
        ("Android 14", "5.15"),
        ("Android 14", "6.1"),
        ("Android 15", "6.6"),
        ("Android 16", "6.12"),
        ("Android 17", "6.18"),
    }
    assert {(row.android, row.gki) for row in content.KMI_ROWS} == expected


def test_asset_template_builds_release_names():
    name = content.KMI_ASSET_TEMPLATE.format(kmi="android15-6.6")
    assert name == "susfs_guard_lkm-android15-6.6.ko"
    assert content.LATEST_DOWNLOAD_TEMPLATE.format(kmi="android15-6.6").endswith(
        "/download/" + name
    )


def test_navigation_anchors_exist_in_content():
    anchors = {item.href for item in content.NAV}
    assert anchors == {"#features", "#install", "#kmi", "#docs", "#faq"}


def test_fallback_release_tag_looks_like_a_release():
    assert content.FALLBACK_RELEASE_TAG.startswith("v")
    assert "-" in content.FALLBACK_RELEASE_TAG


def test_faq_and_features_have_expected_counts():
    assert len(content.FEATURES) == 6
    assert len(content.FAQ) == 6
    assert len(content.STEPS) == 4
    assert len(content.CODE_TABS) == 3
    assert len(content.INTERFACES) == 6


def test_inline_markup_pairs_are_balanced():
    texts = [content.HERO_LEDE, content.INSTALL_LEDE, content.DOCS_INTRO]
    texts += [feature.body for feature in content.FEATURES]
    texts += [step.body for step in content.STEPS]
    texts += [item.answer for item in content.FAQ]
    texts += [card.body for card in content.INTERFACES]
    for text in texts:
        assert text.count("~") % 2 == 0, text
