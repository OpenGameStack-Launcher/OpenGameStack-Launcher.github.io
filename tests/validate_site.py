#!/usr/bin/env python3
"""
Automated static site validator for OpenGameStack-Launcher.github.io (opengamestack.org).

Checks:
1. Required site files and CNAME configuration.
2. HTML5 document structure, metadata, landmarks, and navigation consistency.
3. Internal relative link and asset path resolution across HTML and CSS files.
4. Accessibility (image alt attributes) and external link security (rel="noopener noreferrer").
5. Zero external dependencies, self-hosted fonts, no trackers/CDNs, and safe DOM rendering.
"""

from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


REPO_ROOT = Path(__file__).resolve().parent.parent

REQUIRED_FILES = [
    "CNAME",
    "index.html",
    "pages/manifesto.html",
    "pages/tools.html",
    "examples/index.html",
    "assets/css/site.css",
    "assets/fonts/fonts-local.css",
    "favicon.png",
    "logo.png",
]

FORBIDDEN_EXTERNAL_PATTERNS = [
    "fonts.googleapis.com",
    "fonts.gstatic.com",
    "google-analytics.com",
    "googletagmanager.com",
    "connect.facebook.net",
    "doubleclick.net",
    "hotjar.com",
    "plausible.io",
    "unpkg.com",
    "cdn.jsdelivr.net",
    "cdnjs.cloudflare.com",
]


class PageInspector(HTMLParser):
    """Collects structural elements, links, images, scripts, and IDs from an HTML file."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.has_doctype: bool = False
        self.html_lang: str | None = None
        self.has_charset_utf8: bool = False
        self.has_viewport: bool = False
        self.meta_description: str | None = None
        self.in_title: bool = False
        self.title_parts: list[str] = []
        self.has_header: bool = False
        self.has_main_id: bool = False
        self.has_footer: bool = False
        self.ids: set[str] = set()
        self.links: list[tuple[int, str, str | None, str | None]] = []
        self.stylesheets: list[tuple[int, str]] = []
        self.images: list[tuple[int, str | None, str | None]] = []
        self.scripts: list[tuple[int, str | None]] = []
        self.in_script: bool = False
        self.inline_scripts: list[str] = []
        self._current_script: list[str] = []
        self.has_catalog_container: bool = False
        self.catalog_tool_cards: int = 0

    def handle_decl(self, decl: str) -> None:
        if decl.strip().lower() == "doctype html":
            self.has_doctype = True

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {k.lower(): v for k, v in attrs}
        line, _ = self.getpos()

        if "id" in attr_map and attr_map["id"]:
            self.ids.add(attr_map["id"])

        if tag == "html":
            self.html_lang = attr_map.get("lang")
        elif tag == "meta":
            charset = attr_map.get("charset", "")
            if charset and charset.lower() == "utf-8":
                self.has_charset_utf8 = True
            name = (attr_map.get("name") or "").lower()
            content = (attr_map.get("content") or "").strip()
            if name == "viewport" and content:
                self.has_viewport = True
            elif name == "description" and content:
                self.meta_description = content
        elif tag == "title":
            self.in_title = True
        elif tag == "header":
            classes = (attr_map.get("class") or "").split()
            if "site-header" in classes:
                self.has_header = True
        elif tag == "main":
            if attr_map.get("id") == "main":
                self.has_main_id = True
        elif tag == "footer":
            classes = (attr_map.get("class") or "").split()
            if "site-footer" in classes:
                self.has_footer = True
        elif tag == "a":
            href = attr_map.get("href") or ""
            target = attr_map.get("target")
            rel = attr_map.get("rel")
            self.links.append((line, href, target, rel))
        elif tag == "link":
            rel_tokens = (attr_map.get("rel") or "").lower().split()
            href = attr_map.get("href") or ""
            if "stylesheet" in rel_tokens or "icon" in rel_tokens:
                self.stylesheets.append((line, href))
        elif tag == "img":
            self.images.append((line, attr_map.get("src"), attr_map.get("alt")))
        elif tag == "script":
            self.scripts.append((line, attr_map.get("src")))
            self.in_script = True
            self._current_script = []
        elif tag == "section":
            if "data-catalog" in attr_map:
                self.has_catalog_container = True
        elif tag == "div":
            classes = (attr_map.get("class") or "").split()
            if "tool-card" in classes:
                self.catalog_tool_cards += 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False
        elif tag == "script" and self.in_script:
            self.in_script = False
            self.inline_scripts.append("".join(self._current_script))
            self._current_script = []

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)
        if self.in_script:
            self._current_script.append(data)

    @property
    def title_text(self) -> str:
        return "".join(self.title_parts).strip()


class TestResults:
    """Tracks passed/failed checks and failure messages."""

    def __init__(self) -> None:
        self.passed: int = 0
        self.failed: int = 0
        self.failures: list[str] = []

    def expect(self, condition: bool, message: str) -> None:
        if condition:
            self.passed += 1
        else:
            self.failed += 1
            self.failures.append(message)


def discover_html_files(root: Path) -> list[Path]:
    html_files: list[Path] = []
    for path in sorted(root.rglob("*.html")):
        rel_parts = path.relative_to(root).parts
        if any(part.startswith(".") for part in rel_parts):
            continue
        html_files.append(path)
    return html_files


def discover_css_files(root: Path) -> list[Path]:
    css_files: list[Path] = []
    for path in sorted(root.rglob("*.css")):
        rel_parts = path.relative_to(root).parts
        if any(part.startswith(".") for part in rel_parts):
            continue
        css_files.append(path)
    return css_files


def validate_required_files(results: TestResults) -> None:
    for rel_path in REQUIRED_FILES:
        full_path = REPO_ROOT / rel_path
        results.expect(
            full_path.is_file(),
            f"Missing required repository file: {rel_path}",
        )

    cname_path = REPO_ROOT / "CNAME"
    if cname_path.is_file():
        cname_value = cname_path.read_text(encoding="utf-8").strip()
        results.expect(
            cname_value == "opengamestack.org",
            f"CNAME must be 'opengamestack.org', found '{cname_value}'",
        )


def resolve_local_reference(source_file: Path, raw_ref: str) -> tuple[Path | None, str]:
    parsed = urlsplit(raw_ref)
    path_part = unquote(parsed.path)
    fragment = unquote(parsed.fragment)
    if not path_part:
        return source_file, fragment
    if path_part.startswith("/"):
        target = (REPO_ROOT / path_part.lstrip("/")).resolve()
    else:
        target = (source_file.parent / path_part).resolve()
    return target, fragment


def validate_html_file(html_path: Path, results: TestResults) -> None:
    rel_name = html_path.relative_to(REPO_ROOT).as_posix()
    content = html_path.read_text(encoding="utf-8")

    inspector = PageInspector()
    inspector.feed(content)

    # 1. Core HTML5 & semantic structure checks
    results.expect(inspector.has_doctype, f"{rel_name}: Missing <!DOCTYPE html>")
    results.expect(
        inspector.html_lang == "en",
        f"{rel_name}: <html> must specify lang='en' (found {inspector.html_lang!r})",
    )
    results.expect(inspector.has_charset_utf8, f"{rel_name}: Missing <meta charset='UTF-8'>")
    results.expect(inspector.has_viewport, f"{rel_name}: Missing responsive <meta name='viewport'>")
    results.expect(
        bool(inspector.meta_description),
        f"{rel_name}: Missing or empty <meta name='description'>",
    )
    results.expect(bool(inspector.title_text), f"{rel_name}: Missing or empty <title>")
    results.expect(inspector.has_header, f"{rel_name}: Missing <header class='site-header'>")
    results.expect(inspector.has_main_id, f"{rel_name}: Missing <main id='main'> landmark")
    results.expect(inspector.has_footer, f"{rel_name}: Missing <footer class='site-footer'>")

    # 2. Zero-tracker / no third-party CDN check
    lower_content = content.lower()
    for pattern in FORBIDDEN_EXTERNAL_PATTERNS:
        results.expect(
            pattern not in lower_content,
            f"{rel_name}: Forbidden external dependency or tracker reference '{pattern}'",
        )

    # 3. External scripts check & safe DOM rendering
    for line, src in inspector.scripts:
        results.expect(
            src is None or not src.lower().startswith(("http://", "https://", "//")),
            f"{rel_name}:{line}: External <script src='{src}'> is prohibited",
        )
        if src:
            target, _ = resolve_local_reference(html_path, src)
            results.expect(
                target is not None and target.is_file(),
                f"{rel_name}:{line}: Script src '{src}' does not exist",
            )

    for script_body in inspector.inline_scripts:
        results.expect(
            ".innerHTML" not in script_body,
            f"{rel_name}: Inline script must not use .innerHTML (use safe DOM creation + textContent)",
        )

    # 4. Stylesheet & icon links
    for line, href in inspector.stylesheets:
        results.expect(
            not href.lower().startswith(("http://", "https://", "//")),
            f"{rel_name}:{line}: External stylesheet/icon '{href}' is prohibited",
        )
        target, _ = resolve_local_reference(html_path, href)
        results.expect(
            target is not None and target.is_file(),
            f"{rel_name}:{line}: Linked resource '{href}' does not exist",
        )

    # 5. Images: local file existence and non-empty alt text
    for line, src, alt in inspector.images:
        results.expect(bool(src), f"{rel_name}:{line}: <img> missing src attribute")
        results.expect(
            alt is not None and len(alt.strip()) > 0,
            f"{rel_name}:{line}: <img> missing non-empty alt attribute (src={src!r})",
        )
        if src and not src.lower().startswith(("http://", "https://", "data:")):
            target, _ = resolve_local_reference(html_path, src)
            results.expect(
                target is not None and target.is_file(),
                f"{rel_name}:{line}: Image src '{src}' does not exist",
            )

    # 6. Anchor links: internal path resolution and external rel="noopener noreferrer"
    for line, href, target_attr, rel_attr in inspector.links:
        results.expect(bool(href), f"{rel_name}:{line}: <a> tag has empty href")
        if not href:
            continue

        if href.startswith(("mailto:", "tel:", "javascript:")):
            results.expect(
                not href.lower().startswith("javascript:"),
                f"{rel_name}:{line}: javascript: pseudo-links are prohibited",
            )
            continue

        if href.startswith(("http://", "https://", "//")):
            if target_attr == "_blank":
                rel_tokens = set((rel_attr or "").lower().split())
                results.expect(
                    {"noopener", "noreferrer"}.issubset(rel_tokens),
                    f"{rel_name}:{line}: External target='_blank' link '{href}' must include rel='noopener noreferrer'",
                )
            continue

        target_file, fragment = resolve_local_reference(html_path, href)
        results.expect(
            target_file is not None and target_file.is_file(),
            f"{rel_name}:{line}: Internal link '{href}' does not resolve to an existing file",
        )
        if target_file == html_path and fragment:
            results.expect(
                fragment in inspector.ids,
                f"{rel_name}:{line}: Internal anchor '#{fragment}' does not match any element id in {rel_name}",
            )

    # 7. Special check for pages/tools.html static fallback
    if rel_name == "pages/tools.html":
        results.expect(
            inspector.has_catalog_container,
            "pages/tools.html: Missing [data-catalog] section container",
        )
        results.expect(
            inspector.catalog_tool_cards >= 4,
            f"pages/tools.html: Expected static fallback tool cards inside [data-catalog], found {inspector.catalog_tool_cards}",
        )


def validate_css_file(css_path: Path, results: TestResults) -> None:
    rel_name = css_path.relative_to(REPO_ROOT).as_posix()
    content = css_path.read_text(encoding="utf-8")

    lower_content = content.lower()
    for pattern in FORBIDDEN_EXTERNAL_PATTERNS:
        results.expect(
            pattern not in lower_content,
            f"{rel_name}: Forbidden external dependency reference '{pattern}'",
        )

    url_pattern = re.compile(r"url\(\s*(['\"]?)(.*?)\1\s*\)")
    for match in url_pattern.finditer(content):
        raw_url = match.group(2).strip()
        if not raw_url or raw_url.startswith("data:"):
            continue
        results.expect(
            not raw_url.lower().startswith(("http://", "https://", "//")),
            f"{rel_name}: External CSS url('{raw_url}') is prohibited",
        )
        target, _ = resolve_local_reference(css_path, raw_url)
        results.expect(
            target is not None and target.is_file(),
            f"{rel_name}: CSS url('{raw_url}') does not resolve to an existing file",
        )


def main() -> int:
    results = TestResults()

    validate_required_files(results)

    html_files = discover_html_files(REPO_ROOT)
    results.expect(len(html_files) >= 4, f"Expected at least 4 HTML files, found {len(html_files)}")
    for html_file in html_files:
        validate_html_file(html_file, results)

    css_files = discover_css_files(REPO_ROOT)
    results.expect(len(css_files) >= 2, f"Expected at least 2 CSS files, found {len(css_files)}")
    for css_file in css_files:
        validate_css_file(css_file, results)

    total = results.passed + results.failed
    print(f"OGS Website Validation Summary: {total} checks run | tests passed: {results.passed} | tests failed: {results.failed}")
    if results.failures:
        print("\nFailures:")
        for failure in results.failures:
            print(f"  - [FAIL] {failure}")
        return 1

    print("All static website validation checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
