from app.kmi import match_kmi, resolve_kmi


def test_resolve_from_osrelease():
    assert resolve_kmi("6.6.30-android15-8-g1234abc") == "android15-6.6"
    assert resolve_kmi("5.10.209-android12-9-00001-gdeadbeef") == "android12-5.10"
    assert resolve_kmi("6.1.25-android14-11-gabc") == "android14-6.1"


def test_resolve_rejects_unknown_variant():
    assert resolve_kmi("6.6.30-android15-8") == "android15-6.6"
    assert resolve_kmi("4.19.0-android9-8") is None
    assert resolve_kmi("6.6.30") is None
    assert resolve_kmi("") is None


def test_match_accepts_short_android_version():
    assert match_kmi("15", "6.6.30") == "android15-6.6"
    assert match_kmi("15.0", "6.6.30") == "android15-6.6"
    assert match_kmi("13", "5.10.209") == "android13-5.10"
    assert match_kmi("13", "5.14.0") is None
    assert match_kmi("abc", "6.6") is None
