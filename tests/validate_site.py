#!/usr/bin/env python3
"""
Automated static site validator for OpenGameStack-Launcher.github.io (opengamestack.org).

Checks:
1. Required site files and CNAME configuration.
2. HTML5 document structure, metadata, landmarks, skip links, and navigation consistency.
3. Internal relative link and asset path resolution across HTML and CSS files.
4. Accessibility (image alt attributes) and external link security (rel="noopener noreferrer").
5. Zero external dependencies, self-hosted fonts, no trackers/CDNs, and safe DOM rendering.
6. Landing page v0.2.0 release links, engine notes, and canonical manifest naming.
7. Tool catalog static fallback parity against repository.json (or canonical 7-tool baseline).
8. Game studio dark CSS tokens (category accents, surface tokens) and editorial/catalog classes in site.css.
9. Dedicated /launcher/ page checks and hub navigation consistency.
10. Sitewide Launcher navigation, Substack footer links, and reframed Mission/Examples pages.
"""

from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


REPO_ROOT = Path(__file__).resolve().parent.parent

REQUIRED_FILES = [
    "CNAME",
    "index.html",
    "launcher/index.html",
    "mission/index.html",
    "tools/index.html",
    "examples/index.html",
    "assets/css/site.css",
    "assets/fonts/fonts-local.css",
    "favicon.png",
    "logo.png",
    "assets/images/Godot.png",
    "assets/images/Blender.png",
    "assets/images/Krita.png",
    "assets/images/GIMP.png",
    "assets/images/Audacity.png",
    "assets/images/Git.png",
    "assets/images/VSCodium.png",
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
        self.has_skip_link: bool = False
        self.has_header: bool = False
        self.has_main_id: bool = False
        self.has_footer: bool = False
        self.ids: set[str] = set()
        self.links: list[tuple[int, str, str | None, str | None, list[str]]] = []
        self.stylesheets: list[tuple[int, str]] = []
        self.images: list[tuple[int, str | None, str | None]] = []
        self.scripts: list[tuple[int, str | None]] = []
        self.in_script: bool = False
        self.inline_scripts: list[str] = []
        self._current_script: list[str] = []
        self.has_catalog_container: bool = False
        self.catalog_tool_cards: int = 0
        self.catalog_tools: dict[str, list[str]] = {}
        self.catalog_tool_marks: list[str] = []
        self.catalog_tool_images: dict[str, tuple[int, str, str]] = {}
        self._current_card_icon: tuple[int, str, str] | None = None
        self._current_tool_id: str | None = None
        self._in_tool_id: bool = False
        self._in_version_tag: bool = False
        self._tag_text_parts: list[str] = []

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
            classes = (attr_map.get("class") or "").split()
            if "skip-link" in classes and href == "#main":
                self.has_skip_link = True
            self.links.append((line, href, target, rel, classes))
        elif tag == "link":
            rel_tokens = (attr_map.get("rel") or "").lower().split()
            href = attr_map.get("href") or ""
            if "stylesheet" in rel_tokens or "icon" in rel_tokens:
                self.stylesheets.append((line, href))
        elif tag == "img":
            self.images.append((line, attr_map.get("src"), attr_map.get("alt")))
            classes = (attr_map.get("class") or "").split()
            if "tool-icon" in classes:
                self._current_card_icon = (line, attr_map.get("src") or "", attr_map.get("alt") or "")
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
                self._current_card_icon = None
        elif tag == "h3":
            classes = (attr_map.get("class") or "").split()
            if "tool-id" in classes:
                self._in_tool_id = True
                self._tag_text_parts = []
        elif tag == "span":
            classes = (attr_map.get("class") or "").split()
            if "version-tag" in classes:
                self._in_version_tag = True
                self._tag_text_parts = []
            if "tool-mark" in classes:
                mark_label = attr_map.get("aria-label") or ""
                if mark_label:
                    self.catalog_tool_marks.append(mark_label)

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False
        elif tag == "script" and self.in_script:
            self.in_script = False
            self.inline_scripts.append("".join(self._current_script))
            self._current_script = []
        elif tag == "h3" and self._in_tool_id:
            self._in_tool_id = False
            tid = "".join(self._tag_text_parts).strip().lower()
            self._current_tool_id = tid
            if tid and tid not in self.catalog_tools:
                self.catalog_tools[tid] = []
            if tid and self._current_card_icon:
                self.catalog_tool_images[tid] = self._current_card_icon
            self._tag_text_parts = []
        elif tag == "span" and self._in_version_tag:
            self._in_version_tag = False
            ver = "".join(self._tag_text_parts).strip()
            if ver and self._current_tool_id:
                self.catalog_tools[self._current_tool_id].append(ver)
            self._tag_text_parts = []

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)
        if self.in_script:
            self._current_script.append(data)
        if self._in_tool_id or self._in_version_tag:
            self._tag_text_parts.append(data)

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

    legacy_pages_dir = REPO_ROOT / "pages"
    results.expect(
        not legacy_pages_dir.exists(),
        "Legacy 'pages/' directory must be removed from repository",
    )

    legacy_manifesto_dir = REPO_ROOT / "manifesto"
    results.expect(
        not legacy_manifesto_dir.exists(),
        "Legacy 'manifesto/' directory must be removed from repository",
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
    if target.is_dir() and (target / "index.html").is_file():
        target = (target / "index.html").resolve()
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
    results.expect(
        inspector.has_skip_link,
        f"{rel_name}: Missing <a class='skip-link' href='#main'> accessibility landmark",
    )
    results.expect(inspector.has_header, f"{rel_name}: Missing <header class='site-header'>")
    results.expect(inspector.has_main_id, f"{rel_name}: Missing <main id='main'> landmark")
    results.expect(inspector.has_footer, f"{rel_name}: Missing <footer class='site-footer'>")

    # 2. Zero-tracker / no third-party CDN check
    results.expect(
        "manifesto.html" not in content.lower() and "manifesto/" not in content.lower(),
        f"{rel_name}: Obsolete 'manifesto' route or file reference found in HTML content",
    )
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
    for line, href, target_attr, rel_attr, classes in inspector.links:
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

        is_nav_or_cta = bool(
            set(classes).intersection(
                {"site-logo", "site-nav-link", "site-footer-link", "btn", "btn-outline"}
            )
        )
        if is_nav_or_cta:
            clean_href = href.split("?")[0].split("#")[0]
            results.expect(
                "index.html" not in href and not clean_href.endswith(".html"),
                f"{rel_name}:{line}: Clean URL violation in navigation/CTA link '{href}'. Clean directory URLs required (no .html or index.html).",
            )

        results.expect(
            "pages/" not in href,
            f"{rel_name}:{line}: Legacy 'pages/' reference in link '{href}'",
        )
        results.expect(
            "manifesto" not in href.lower(),
            f"{rel_name}:{line}: Legacy 'manifesto' reference in link '{href}'",
        )

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

    # 7. Sitewide navigation and footer consistency checks
    expected_launcher_nav = (
        "launcher/"
        if rel_name == "index.html"
        else ("./" if rel_name == "launcher/index.html" else "../launcher/")
    )
    nav_launcher_links = [
        href
        for _, href, _, _, classes in inspector.links
        if "site-nav-link" in classes and href == expected_launcher_nav
    ]
    results.expect(
        len(nav_launcher_links) >= 1,
        f"{rel_name}: Missing expected .site-nav link to '{expected_launcher_nav}'",
    )

    substack_url = "https://opengamestack.substack.com/"
    footer_substack_links = [
        (line, rel)
        for line, href, target, rel, classes in inspector.links
        if "site-footer-link" in classes and href == substack_url
    ]
    results.expect(
        len(footer_substack_links) >= 1,
        f"{rel_name}: Missing expected .site-footer-links link to '{substack_url}'",
    )
    for line, rel in footer_substack_links:
        rel_tokens = set((rel or "").lower().split())
        results.expect(
            {"noopener", "noreferrer"}.issubset(rel_tokens),
            f"{rel_name}:{line}: Substack footer link must include rel='noopener noreferrer'",
        )

    results.expect(
        "Dual-use technology for open simulation." not in content,
        f"{rel_name}: Obsolete footer tagline 'Dual-use technology for open simulation.' found",
    )
    results.expect(
        "Open-source tools and reproducible workflows for game creators." in content,
        f"{rel_name}: Missing updated footer tagline 'Open-source tools and reproducible workflows for game creators.'",
    )

    # 8. Landing page checks (v0.2.0 links, manifest naming, Godot version)
    if rel_name == "index.html":
        expected_v020_download = (
            "https://github.com/OpenGameStack-Launcher/ogs-launcher/releases/download/v0.2.0/OGS-Launcher-win64-0.2.0.zip"
        )
        v020_download_links = [
            href for _, href, _, _, _ in inspector.links if href == expected_v020_download
        ]
        results.expect(
            len(v020_download_links) >= 2,
            f"index.html: Expected at least 2 links to '{expected_v020_download}', found {len(v020_download_links)}",
        )
        results.expect(
            "ogs_stack.json" in content,
            "index.html: Missing canonical 'ogs_stack.json' manifest reference",
        )
        results.expect(
            "ogs_config.json" in content,
            "index.html: Missing canonical 'ogs_config.json' config reference",
        )
        results.expect(
            "Godot 4.7.2" in content,
            "index.html: Missing 'Godot 4.7.2' reference in launcher target description",
        )
        results.expect(
            "v0.1.5" not in content,
            "index.html: Obsolete v0.1.5 release reference found",
        )
        results.expect(
            "<code>stack.json</code>" not in content,
            "index.html: Obsolete 'stack.json' manifest naming found",
        )
        cta_mission_links = [
            href for _, href, _, _, _ in inspector.links if href == "mission/"
        ]
        results.expect(
            len(cta_mission_links) >= 1,
            "index.html: Missing hero/nav link to 'mission/'",
        )
        results.expect(
            "The Mission" in content,
            "index.html: Missing 'The Mission' CTA button text",
        )
        for required_link in [
            "launcher/",
            "tools/",
            "mission/",
            "examples/",
            "https://opengamestack.substack.com/",
        ]:
            has_link = any(href == required_link for _, href, _, _, _ in inspector.links)
            results.expect(
                has_link,
                f"index.html: Missing expected hub link to '{required_link}'",
            )

    if rel_name == "launcher/index.html":
        results.expect(
            inspector.title_text == "Launcher | Open Game Stack",
            f"launcher/index.html: Expected title 'Launcher | Open Game Stack', found '{inspector.title_text}'",
        )
        expected_v020_download = (
            "https://github.com/OpenGameStack-Launcher/ogs-launcher/releases/download/v0.2.0/OGS-Launcher-win64-0.2.0.zip"
        )
        v020_download_links = [
            href for _, href, _, _, _ in inspector.links if href == expected_v020_download
        ]
        results.expect(
            len(v020_download_links) >= 2,
            f"launcher/index.html: Expected at least 2 links to '{expected_v020_download}', found {len(v020_download_links)}",
        )
        results.expect(
            "Godot 4.7.2" in content,
            "launcher/index.html: Missing 'Godot 4.7.2' reference in desktop runtime description",
        )
        results.expect(
            "ogs_stack.json" in content,
            "launcher/index.html: Missing canonical 'ogs_stack.json' manifest reference",
        )
        results.expect(
            "ogs_config.json" in content,
            "launcher/index.html: Missing canonical 'ogs_config.json' config reference",
        )

    if rel_name == "mission/index.html":
        results.expect(
            inspector.title_text == "Mission | Open Game Stack",
            f"mission/index.html: Expected title 'Mission | Open Game Stack', found '{inspector.title_text}'",
        )
        for anchor_id in ["sovereignty", "environment", "dual-use", "stability"]:
            results.expect(
                anchor_id in inspector.ids,
                f"mission/index.html: Missing expected section anchor id '{anchor_id}'",
            )

            has_index_link = any(
                href == f"#{anchor_id}" for _, href, _, _, _ in inspector.links
            )
            results.expect(
                has_index_link,
                f"mission/index.html: Missing .section-index link to '#{anchor_id}'",
            )
        results.expect(
            "indie" in content.lower() or "studios" in content.lower(),
            "mission/index.html: Missing indie/studio reframing in mission prose",
        )

    if rel_name == "examples/index.html":
        results.expect(
            inspector.title_text == "Examples | Open Game Stack",
            f"examples/index.html: Expected title 'Examples | Open Game Stack', found '{inspector.title_text}'",
        )
        results.expect(
            "class=\"grid\"" in content or "class='grid'" in content,
            "examples/index.html: Missing structured .grid container for project examples",
        )
        results.expect(
            "Sudoku" in content,
            "examples/index.html: Missing 'Sudoku' reference project card",
        )
        results.expect(
            "Letter Logic" in content,
            "examples/index.html: Missing 'Letter Logic' reference project card",
        )
        for tool_name in ["Godot", "Git", "Krita"]:
            results.expect(
                tool_name in content,
                f"examples/index.html: Missing tool stack badge reference '{tool_name}'",
            )
        for required_example_link in [
            "https://github.com/OpenGameStack/sudoku",
            "https://audrain.games/sudoku",
            "https://github.com/OpenGameStack/letter-logic",
            "https://audrain.games/letter-logic",
        ]:
            has_link = any(
                href == required_example_link for _, href, _, _, _ in inspector.links
            )
            results.expect(
                has_link,
                f"examples/index.html: Missing expected reference project link '{required_example_link}'",
            )

    # 9. Tool catalog static fallback parity and structure
    if rel_name == "tools/index.html":
        results.expect(
            inspector.has_catalog_container,
            "tools/index.html: Missing [data-catalog] section container",
        )
        results.expect(
            inspector.catalog_tool_cards == 7,
            f"tools/index.html: Expected 7 static fallback tool cards inside [data-catalog], found {inspector.catalog_tool_cards}",
        )

        expected_catalog_tools: dict[str, set[str]] = {
            "godot": {"4.7.2", "4.3"},
            "gimp": {"3.2.4"},
            "krita": {"5.3.3", "5.2.15"},
            "blender": {"5.2", "4.5.7"},
            "audacity": {"3.7.8", "3.7.7"},
            "git": {"2.56.0.4"},
            "vscodium": {"1.143.17232"},
        }

        # Verify against sibling repository.json if present
        sibling_repo = REPO_ROOT.parent / "ogs-frozen-stacks" / "repository.json"
        if sibling_repo.is_file():
            try:
                repo_data = json.loads(sibling_repo.read_text(encoding="utf-8"))
                discovered_tools: dict[str, set[str]] = {}
                for tool in repo_data.get("tools", []):
                    tid = tool.get("id")
                    ver = tool.get("version")
                    if tid and ver:
                        discovered_tools.setdefault(tid, set()).add(ver)
                if discovered_tools:
                    expected_catalog_tools = discovered_tools
            except Exception:
                pass

        results.expect(
            set(inspector.catalog_tools.keys()) == set(expected_catalog_tools.keys()),
            f"tools/index.html: Static catalog tool IDs mismatch. Expected {sorted(expected_catalog_tools.keys())}, found {sorted(inspector.catalog_tools.keys())}",
        )

        for tool_id, expected_versions in expected_catalog_tools.items():
            actual_versions = set(inspector.catalog_tools.get(tool_id, []))
            results.expect(
                actual_versions == expected_versions,
                f"tools/index.html: Tool '{tool_id}' version mismatch. Expected {sorted(expected_versions)}, found {sorted(actual_versions)}",
            )

        results.expect(
            len(inspector.catalog_tool_marks) == 0,
            f"tools/index.html: Unexpected .tool-mark monograms found: {inspector.catalog_tool_marks}",
        )

        for tool_id in expected_catalog_tools:
            results.expect(
                tool_id in inspector.catalog_tool_images,
                f"tools/index.html: Static catalog tool '{tool_id}' is missing a .tool-icon <img> element",
            )
            if tool_id in inspector.catalog_tool_images:
                icon_line, icon_src, icon_alt = inspector.catalog_tool_images[tool_id]
                results.expect(
                    bool(icon_src),
                    f"tools/index.html:{icon_line}: Tool '{tool_id}' icon missing src attribute",
                )
                results.expect(
                    bool(icon_alt and icon_alt.strip()),
                    f"tools/index.html:{icon_line}: Tool '{tool_id}' icon missing non-empty alt attribute",
                )
                target_img, _ = resolve_local_reference(html_path, icon_src)
                results.expect(
                    target_img is not None and target_img.is_file(),
                    f"tools/index.html:{icon_line}: Tool '{tool_id}' icon src '{icon_src}' does not exist",
                )

        combined_scripts = "\n".join(inspector.inline_scripts)
        for tool_id in expected_catalog_tools:
            tool_pattern = re.compile(
                rf"{tool_id}\s*:\s*\{{[^}}]*image\s*:\s*['\"]([^'\"]+)['\"]",
                re.DOTALL,
            )
            match = tool_pattern.search(combined_scripts)
            results.expect(
                match is not None,
                f"tools/index.html: Inline toolDetails missing image property for '{tool_id}'",
            )
            if match:
                raw_img_path = match.group(1)
                target_img, _ = resolve_local_reference(html_path, raw_img_path)
                results.expect(
                    target_img is not None and target_img.is_file(),
                    f"tools/index.html: Inline toolDetails image '{raw_img_path}' for '{tool_id}' does not resolve to an existing file",
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


    if rel_name == "assets/css/site.css":
        required_surface_tokens = [
            "--bg-dark",
            "--bg-surface",
            "--card-bg",
            "--card-border",
        ]
        for token in required_surface_tokens:
            results.expect(
                token in content,
                f"{rel_name}: Missing required surface token '{token}'",
            )

        required_category_properties = [
            "--cat-engine",
            "--cat-2d",
            "--cat-3d",
            "--cat-audio",
            "--cat-level",
            "--cat-code",
        ]
        for prop in required_category_properties:
            results.expect(
                prop in content,
                f"{rel_name}: Missing required category custom property '{prop}'",
            )

        required_css_classes = [
            ".prose",
            ".article-body",
            ".catalog-filters",
            ".filter-btn",
            ".badge-tier-frozen",
            ".badge-tier-radar",
            ".spec-table",
            ".version-table",
            ".code-block",
            ".code-header",
            ".callout",
        ]
        for cls in required_css_classes:
            results.expect(
                cls in content,
                f"{rel_name}: Missing required CSS class selector '{cls}'",
            )


def main() -> int:
    results = TestResults()

    validate_required_files(results)

    html_files = discover_html_files(REPO_ROOT)
    results.expect(len(html_files) >= 5, f"Expected at least 5 HTML files, found {len(html_files)}")
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
