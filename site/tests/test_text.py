from app.text import highlight_shell, render_inline, strip_inline_markup


def test_render_inline_converts_code_markers():
    assert render_inline("选择 ~.ko~ 产物") == "选择 <code>.ko</code> 产物"


def test_render_inline_escapes_html():
    assert render_inline("<script>x</script>") == "&lt;script&gt;x&lt;/script&gt;"
    assert render_inline("~<tag>~") == "<code>&lt;tag&gt;</code>"


def test_strip_inline_markup_removes_markers():
    assert strip_inline_markup("~a~ 和 ~b~") == "a 和 b"


def test_highlight_shell_marks_comment_lines():
    out = highlight_shell("# 注释\nadb push a b\n")
    assert out == '<span class="c"># 注释</span>\nadb push a b'


def test_highlight_shell_escapes_special_chars():
    out = highlight_shell("echo a > b && echo <c>")
    assert out == "echo a &gt; b &amp;&amp; echo &lt;c&gt;"
