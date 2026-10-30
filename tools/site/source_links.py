"""Link each lesson to its code on GitHub, from docs/course_map.json.

docs/course_map.json names, for every lesson, its page, the id of its section and
the repository files it uses. This script writes one line at the end of that
section, "Code on GitHub", with a link to each file. The repository address and
branch are in docs/project_links.json. A line that is already on the page keeps
its place and only gets new links. The check also reports a page header, home
page, download README, notice or citation file that names another repository
address.

    python tools/site/source_links.py           write the lines into website
    python tools/site/source_links.py --check   report pages whose lines are out of date
"""
from __future__ import annotations

import argparse
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "website"
# Files that write the repository address by hand.
NAMED = ("website/assets/course-nav.js", "website/index.html", "tools/build_downloads.py",
         "NOTICE", "RIGHTS.md", "CITATION.cff")
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
LINE = re.compile(r'<p class="lesson-code" data-lesson-code="(?P<id>[^"]+)">.*?</p>')


def repository():
    links = json.loads((ROOT / "docs/project_links.json").read_text(encoding="utf-8"))
    url, branch = links["repository_url"], links["branch"]
    if not url or not re.fullmatch(r"https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", url):
        raise SystemExit("docs/project_links.json needs repository_url = https://github.com/OWNER/REPOSITORY")
    if not branch or not re.fullmatch(r"[A-Za-z0-9_./-]+", branch):
        raise SystemExit("docs/project_links.json needs a branch name")
    return url, branch


def line(lesson, base, branch):
    links = []
    for source in lesson["sources"]:
        path = source["path"]
        if not (ROOT / path).is_file():
            raise SystemExit(f"{lesson['id']}: {path} is not a file in the repository")
        # Let long paths break after a slash on a narrow screen.
        shown = "/<wbr>".join(escape(part) for part in path.split("/"))
        links.append(f'<a href="{base}/blob/{branch}/{quote(path)}"><code>{shown}</code> ↗</a>')
    return (f'<p class="lesson-code" data-lesson-code="{lesson["id"]}">'
            f'<span>Code on GitHub</span> {" · ".join(links)}</p>')


class SectionEnd(HTMLParser):
    """Where the element with a given id closes, as (line, column)."""

    def __init__(self, target):
        super().__init__(convert_charrefs=True)
        self.target, self.stack, self.end = target, [], None

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append((tag, dict(attrs).get("id")))

    def handle_endtag(self, tag):
        while self.stack:
            name, ident = self.stack.pop()
            if name == tag:
                if ident == self.target and self.end is None:
                    self.end = self.getpos()
                break


def place(text, lesson, new):
    """The page with the lesson's line replaced, or added before its section closes."""
    found = [m for m in LINE.finditer(text) if m.group("id") == lesson["id"]]
    if len(found) > 1:
        raise SystemExit(f"{lesson['website_path']}: {lesson['id']} has {len(found)} lines")
    if found:
        return text[:found[0].start()] + new + text[found[0].end():]
    parser = SectionEnd(lesson["website_anchor"])
    parser.feed(text)
    if parser.end is None:
        raise SystemExit(f"{lesson['website_path']}: no element with id {lesson['website_anchor']}")
    row, column = parser.end
    offset = sum(len(part) + 1 for part in text.split("\n")[:row - 1]) + column
    return text[:offset] + new + text[offset:]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="report pages whose lines are out of date")
    args = parser.parse_args(argv)
    base, branch = repository()
    elsewhere = [name for name in NAMED if base not in (ROOT / name).read_text(encoding="utf-8")]
    lessons = json.loads((ROOT / "docs/course_map.json").read_text(encoding="utf-8"))["lessons"]
    pages = {}
    for lesson in lessons:
        path = SITE / lesson["website_path"]
        if path not in pages:
            # Keep each page's own line endings.
            with path.open(encoding="utf-8", newline="") as stream:
                pages[path] = stream.read()
        pages[path] = place(pages[path], lesson, line(lesson, base, branch))
    stale = []
    for path, text in pages.items():
        with path.open(encoding="utf-8", newline="") as stream:
            if stream.read() == text:
                continue
        stale.append(path.relative_to(ROOT).as_posix())
        if not args.check:
            with path.open("w", encoding="utf-8", newline="") as stream:
                stream.write(text)
    problems = [f"names another repository address: {name}" for name in elsewhere]
    if args.check:
        problems += [f"out of date: {name}" for name in stale]
        print("\n".join(problems) or "Every lesson links to its code.")
        return 1 if problems else 0
    print(f"Linked {len(lessons)} lessons on {len(pages)} pages to {base} ({branch}); rewrote {len(stale)} pages.")
    if problems:
        print("\n".join(problems))
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
