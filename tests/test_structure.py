"""结构对拍：Python 渲染结果与原静态 index.html 的 DOM 结构一致。

比较每个元素的 (tag, id, class 集合)；文本内容由内容层单独测试。
静态站已不在仓库内时自动跳过。
"""

from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

import pytest

STATIC_INDEX = Path(__file__).resolve().parents[2] / "site-gh-pages" / "index.html"


class StructureProbe(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.elements: Counter = Counter()

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        classes = tuple(sorted((attributes.get("class") or "").split()))
        self.elements[(tag, attributes.get("id"), classes)] += 1

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)


def probe(html: str) -> Counter:
    parser = StructureProbe()
    parser.feed(html)
    parser.close()
    return parser.elements


@pytest.mark.skipif(not STATIC_INDEX.exists(), reason="原静态站不在工作区")
def test_dom_structure_matches_static_site(client):
    original = probe(STATIC_INDEX.read_text(encoding="utf-8"))
    rendered = probe(client.get("/").get_data(as_text=True))

    missing = original - rendered
    extra = rendered - original
    assert not missing, "Python 模板缺少元素: {}".format(missing.most_common(10))
    assert not extra, "Python 模板多出元素: {}".format(extra.most_common(10))
