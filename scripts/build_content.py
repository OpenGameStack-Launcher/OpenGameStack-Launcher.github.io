#!/usr/bin/env python3
"""
Zero-dependency content builder, metadata validator, and static HTML generator for
the Open Game Stack Website (opengamestack.org).

Features:
1. Validates canonical tool metadata in content/tools.json against schema requirements.
2. Verifies exact version and metadata parity against sibling ogs-frozen-stacks/repository.json.
3. Provides modular, reusable HTML rendering helpers for catalog sections and tool detail pages.
4. Provides a UTF-8 file writing utility guaranteeing consistent encoding without BOM.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent

CANONICAL_CATEGORY_NAMES = [
    "Engine",
    "2D",
    "3D",
    "Audio",
    "Level Design",
    "Code",
]

CANONICAL_FROZEN_IDS = [
    "godot",
    "gimp",
    "krita",
    "blender",
    "audacity",
    "git",
    "vscodium",
]

CANONICAL_RADAR_IDS = [
    "pixelorama",
    "libresprite",
    "inkscape",
    "ldtk",
    "tiled",
    "trenchbroom",
    "material-maker",
    "blockbench",
    "armorpaint",
    "lmms",
    "ardour",
    "sfxr",
]

REQUIRED_TOOL_FIELDS = [
    "id",
    "name",
    "tier",
    "category",
    "tagline",
    "summary",
    "replaces",
    "strengths",
    "license",
    "website_url",
    "repo_url",
    "platforms",
    "resources",
]

REQUIRED_CATEGORY_FIELDS = [
    "id",
    "name",
    "description",
    "accent_token",
]

TOOL_ID_PATTERN = re.compile(r"^[a-z0-9-]+$")
SHA256_PATTERN = re.compile(r"^[a-f0-9]{64}$")


def write_file_utf8(path: Path | str, content: str) -> None:
    """Writes text content to path using UTF-8 encoding without BOM and LF line endings."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8", newline="\n") as file_handle:
        file_handle.write(content)


def escape_html(text: Any) -> str:
    """Escapes text for safe HTML embedding."""
    if text is None:
        return ""
    return html.escape(str(text), quote=True)


def load_tools_metadata(path: Path | str | None = None) -> dict[str, Any]:
    """Loads and parses the canonical tools metadata JSON file."""
    metadata_path = Path(path) if path else (REPO_ROOT / "content" / "tools.json")
    if not metadata_path.is_file():
        raise FileNotFoundError(f"Tools metadata file not found at: {metadata_path}")
    content = metadata_path.read_text(encoding="utf-8")
    data = json.loads(content)
    if not isinstance(data, dict):
        raise ValueError("Root of tools metadata must be a JSON object")
    return data


def find_sibling_repository_json() -> Path | None:
    """Finds the sibling ogs-frozen-stacks/repository.json file if present."""
    if REPO_ROOT.parent.name == ".worktrees":
        worktree_candidate = REPO_ROOT.parent.parent.parent / "ogs-frozen-stacks" / "repository.json"
        if worktree_candidate.is_file():
            return worktree_candidate
    candidate = REPO_ROOT.parent / "ogs-frozen-stacks" / "repository.json"
    if candidate.is_file():
        return candidate
    candidate_alt = REPO_ROOT / ".." / "ogs-frozen-stacks" / "repository.json"
    if candidate_alt.resolve().is_file():
        return candidate_alt.resolve()
    return None


def validate_tools_metadata(
    data: dict[str, Any],
    sibling_repo_path: Path | None = None,
) -> list[str]:
    """Validates content/tools.json schema integrity and parity against upstream repository.json.

    Returns a list of error message strings (empty list indicates successful validation).
    """
    errors: list[str] = []

    # Check root fields
    if "categories" not in data or not isinstance(data["categories"], list):
        errors.append("tools.json: Missing or non-array 'categories' field at root")
    if "tools" not in data or not isinstance(data["tools"], list):
        errors.append("tools.json: Missing or non-array 'tools' field at root")

    if errors:
        return errors

    # Validate categories
    category_list = data["categories"]
    discovered_category_names: set[str] = set()
    discovered_category_ids: set[str] = set()

    for idx, cat in enumerate(category_list):
        if not isinstance(cat, dict):
            errors.append(f"tools.json: Category at index {idx} must be an object")
            continue

        for field in REQUIRED_CATEGORY_FIELDS:
            val = cat.get(field)
            if not val or not isinstance(val, str) or not val.strip():
                errors.append(f"tools.json: Category at index {idx} missing non-empty field '{field}'")

        cat_name = cat.get("name", "").strip()
        cat_id = cat.get("id", "").strip()

        if cat_name in discovered_category_names:
            errors.append(f"tools.json: Duplicate category name '{cat_name}'")
        discovered_category_names.add(cat_name)

        if cat_id in discovered_category_ids:
            errors.append(f"tools.json: Duplicate category id '{cat_id}'")
        discovered_category_ids.add(cat_id)

    missing_categories = set(CANONICAL_CATEGORY_NAMES) - discovered_category_names
    if missing_categories:
        errors.append(f"tools.json: Missing required categories: {sorted(missing_categories)}")

    # Validate tools
    tool_list = data["tools"]
    discovered_tool_ids: set[str] = set()
    discovered_frozen_ids: set[str] = set()
    discovered_radar_ids: set[str] = set()

    for idx, tool in enumerate(tool_list):
        if not isinstance(tool, dict):
            errors.append(f"tools.json: Tool at index {idx} must be an object")
            continue

        tid = tool.get("id")
        t_label = f"Tool '{tid or f'index {idx}'}'"

        # Check required fields
        for field in REQUIRED_TOOL_FIELDS:
            val = tool.get(field)
            if val is None:
                errors.append(f"tools.json: {t_label} is missing required field '{field}'")
            elif isinstance(val, str) and not val.strip():
                errors.append(f"tools.json: {t_label} has empty string for field '{field}'")
            elif isinstance(val, list) and len(val) == 0:
                errors.append(f"tools.json: {t_label} has empty list for required field '{field}'")

        if not tid or not isinstance(tid, str) or not tid.strip():
            continue

        if not TOOL_ID_PATTERN.match(tid):
            errors.append(f"tools.json: {t_label} id must contain only lowercase letters, digits, and hyphens")

        if tid in discovered_tool_ids:
            errors.append(f"tools.json: Duplicate tool id '{tid}'")
        discovered_tool_ids.add(tid)

        tier = tool.get("tier")
        if tier not in ("frozen", "radar"):
            errors.append(f"tools.json: {t_label} tier must be 'frozen' or 'radar', found {tier!r}")

        if tier == "frozen":
            discovered_frozen_ids.add(tid)
        elif tier == "radar":
            discovered_radar_ids.add(tid)

        category = tool.get("category")
        if category not in CANONICAL_CATEGORY_NAMES:
            errors.append(
                f"tools.json: {t_label} category '{category}' not in canonical categories: {CANONICAL_CATEGORY_NAMES}"
            )

        # URL validation
        for url_field in ("website_url", "repo_url"):
            url_val = tool.get(url_field)
            if isinstance(url_val, str) and not url_val.startswith("https://"):
                errors.append(
                    f"tools.json: {t_label} {url_field} must start with 'https://' (found {url_val!r})"
                )

        # Resources validation
        resources = tool.get("resources")
        if isinstance(resources, list):
            for r_idx, resource in enumerate(resources):
                if not isinstance(resource, dict):
                    errors.append(f"tools.json: {t_label} resource at index {r_idx} must be an object")
                    continue
                r_title = resource.get("title")
                r_url = resource.get("url")
                r_type = resource.get("type")
                if not r_title or not isinstance(r_title, str) or not r_title.strip():
                    errors.append(f"tools.json: {t_label} resource at index {r_idx} missing 'title'")
                if not r_type or not isinstance(r_type, str) or not r_type.strip():
                    errors.append(f"tools.json: {t_label} resource at index {r_idx} missing 'type'")
                if not r_url or not isinstance(r_url, str) or not r_url.startswith("https://"):
                    errors.append(
                        f"tools.json: {t_label} resource at index {r_idx} url must start with 'https://' (found {r_url!r})"
                    )

        # Image asset validation
        img = tool.get("image")
        if img is not None:
            if not isinstance(img, str) or not img.strip():
                errors.append(f"tools.json: {t_label} image must be a non-empty string or null")
            else:
                img_path = REPO_ROOT / img
                if not img_path.is_file():
                    errors.append(f"tools.json: {t_label} image path '{img}' does not exist on disk")

        # Versions validation
        versions = tool.get("versions")
        if not isinstance(versions, list):
            errors.append(f"tools.json: {t_label} versions must be an array")
        elif tier == "frozen":
            if len(versions) == 0:
                errors.append(f"tools.json: {t_label} is frozen but has no versions listed")
            for v_idx, ver in enumerate(versions):
                if not isinstance(ver, dict):
                    errors.append(f"tools.json: {t_label} version at index {v_idx} must be an object")
                    continue
                for ver_field in (
                    "version",
                    "category",
                    "info_url",
                    "archive_url",
                    "sha256",
                    "size_bytes",
                    "executable_path",
                ):
                    v_val = ver.get(ver_field)
                    if v_val is None:
                        errors.append(f"tools.json: {t_label} version {v_idx} missing '{ver_field}'")
                    elif isinstance(v_val, str) and not v_val.strip():
                        errors.append(f"tools.json: {t_label} version {v_idx} empty '{ver_field}'")
                v_sha = ver.get("sha256", "")
                if isinstance(v_sha, str) and not SHA256_PATTERN.match(v_sha):
                    errors.append(f"tools.json: {t_label} version {v_idx} invalid sha256 checksum format")
                v_size = ver.get("size_bytes")
                if not isinstance(v_size, int) or v_size <= 0:
                    errors.append(f"tools.json: {t_label} version {v_idx} size_bytes must be a positive integer")
                for u_field in ("info_url", "archive_url"):
                    u_val = ver.get(u_field)
                    if isinstance(u_val, str) and not u_val.startswith("https://"):
                        errors.append(f"tools.json: {t_label} version {v_idx} {u_field} must start with 'https://'")

    # Verify all canonical frozen and radar IDs exist
    missing_frozen = set(CANONICAL_FROZEN_IDS) - discovered_frozen_ids
    if missing_frozen:
        errors.append(f"tools.json: Missing canonical frozen tools: {sorted(missing_frozen)}")

    missing_radar = set(CANONICAL_RADAR_IDS) - discovered_radar_ids
    if missing_radar:
        errors.append(f"tools.json: Missing canonical radar tools: {sorted(missing_radar)}")

    # Verify parity against sibling repository.json if present
    repo_file = sibling_repo_path or find_sibling_repository_json()
    if repo_file and repo_file.is_file():
        try:
            repo_data = json.loads(repo_file.read_text(encoding="utf-8"))
            repo_tools = repo_data.get("tools", [])
            tools_by_id = {t["id"]: t for t in tool_list if isinstance(t, dict) and "id" in t}

            # Map repository.json entries by tool id
            upstream_by_id: dict[str, list[dict[str, Any]]] = {}
            for item in repo_tools:
                tid = item.get("id")
                if tid:
                    upstream_by_id.setdefault(tid, []).append(item)

            for upstream_id, upstream_versions in upstream_by_id.items():
                if upstream_id not in tools_by_id:
                    errors.append(
                        f"tools.json: Upstream frozen tool '{upstream_id}' not found in tools.json"
                    )
                    continue

                local_tool = tools_by_id[upstream_id]
                local_versions = local_tool.get("versions", [])
                local_ver_map = {v.get("version"): v for v in local_versions if isinstance(v, dict)}

                for u_ver in upstream_versions:
                    ver_string = u_ver.get("version")
                    if ver_string not in local_ver_map:
                        errors.append(
                            f"tools.json: Tool '{upstream_id}' missing upstream version '{ver_string}'"
                        )
                        continue

                    l_ver = local_ver_map[ver_string]
                    for check_key in (
                        "category",
                        "info_url",
                        "archive_url",
                        "sha256",
                        "size_bytes",
                        "executable_path",
                    ):
                        if l_ver.get(check_key) != u_ver.get(check_key):
                            errors.append(
                                f"tools.json: Tool '{upstream_id}' version '{ver_string}' {check_key} mismatch. "
                                f"Expected {u_ver.get(check_key)!r}, got {l_ver.get(check_key)!r}"
                            )

                if len(local_versions) != len(upstream_versions):
                    errors.append(
                        f"tools.json: Tool '{upstream_id}' version count mismatch. "
                        f"Upstream has {len(upstream_versions)}, local tools.json has {len(local_versions)}"
                    )

        except Exception as exc:
            errors.append(f"tools.json: Failed to inspect sibling repository.json: {exc}")

    return errors


def render_catalog_filters_html(categories: list[dict[str, Any]] | None = None) -> str:
    """Generates accessible filter controls for the two-tier tools catalog."""
    cat_buttons = [
        '                <button type="button" class="filter-btn is-active" data-filter-cat="all" aria-pressed="true">All Categories</button>'
    ]
    if categories:
        for cat in categories:
            cname = escape_html(cat.get("name", ""))
            cat_buttons.append(
                f'                <button type="button" class="filter-btn" data-filter-cat="{cname}" aria-pressed="false">{cname}</button>'
            )
    else:
        for cname in CANONICAL_CATEGORY_NAMES:
            cat_buttons.append(
                f'                <button type="button" class="filter-btn" data-filter-cat="{cname}" aria-pressed="false">{cname}</button>'
            )
    cats_markup = "\n".join(cat_buttons)

    return (
        f'        <section class="catalog-filters" aria-label="Catalog Filters">\n'
        f'            <div class="filter-group" role="group" aria-label="Filter by Tier">\n'
        f'                <span class="filter-group-label">Tier:</span>\n'
        f'                <button type="button" class="filter-btn is-active" data-filter-tier="all" aria-pressed="true">All Tools</button>\n'
        f'                <button type="button" class="filter-btn" data-filter-tier="frozen" aria-pressed="false">Frozen in Launcher</button>\n'
        f'                <button type="button" class="filter-btn" data-filter-tier="radar" aria-pressed="false">Ecosystem Radar</button>\n'
        f'            </div>\n'
        f'            <div class="filter-group" role="group" aria-label="Filter by Category">\n'
        f'                <span class="filter-group-label">Category:</span>\n'
        f'{cats_markup}\n'
        f'            </div>\n'
        f'        </section>'
    )


def render_tool_card_static(tool: dict[str, Any], base_url: str = "..") -> str:
    """Generates the static HTML markup for a single tool card."""
    tid = escape_html(tool.get("id", ""))
    tname = escape_html(tool.get("name", tid))
    tier = escape_html(tool.get("tier", "frozen"))
    category = escape_html(tool.get("category", ""))
    license_name = escape_html(tool.get("license", ""))
    image_path = tool.get("image")
    tagline = escape_html(tool.get("tagline", ""))
    summary = escape_html(tool.get("summary", ""))
    description = summary or tagline
    replaces = tool.get("replaces", [])
    versions = tool.get("versions", [])
    tier_label = "Frozen in Launcher" if tier == "frozen" else "Ecosystem Radar"

    if image_path:
        full_img_src = f"{base_url}/{image_path.lstrip('/')}"
        visual_html = f'<img class="tool-icon" src="{full_img_src}" alt="{tname} logo">'
    else:
        initial = (tid[:1] if tid else "T").upper()
        visual_html = f'<span class="tool-mark" aria-label="{tid}">{initial}</span>'

    # Replaces metadata
    if replaces:
        chips = "".join(
            f'                                <span class="replaces-chip">{escape_html(r)}</span>\n'
            for r in replaces
        )
        replaces_markup = (
            f'                            <div class="tool-replaces">\n'
            f'                                <span class="replaces-label">Replaces:</span>\n'
            f'{chips}'
            f'                            </div>\n'
        )
    else:
        replaces_markup = ""

    version_items: list[str] = []
    if tier == "frozen" and versions:
        for ver in versions:
            v_num = escape_html(ver.get("version", ""))
            v_info = escape_html(ver.get("info_url", ""))
            v_arch = escape_html(ver.get("archive_url", ""))
            version_items.append(
                f'                        <li class="version-item">\n'
                f'                            <span class="version-tag">{v_num}</span>\n'
                f'                            <a class="release-link" href="{v_info}" target="_blank" rel="noopener noreferrer">Official release page</a>\n'
                f'                            <a class="archive-link" href="{v_arch}" target="_blank" rel="noopener noreferrer">Frozen archive</a>\n'
                f'                        </li>'
            )
        version_label = "Version"
    else:
        web_url = escape_html(tool.get("website_url", ""))
        repo_url = escape_html(tool.get("repo_url", ""))
        version_items.append(
            f'                        <li class="version-item">\n'
            f'                            <a class="release-link" href="{web_url}" target="_blank" rel="noopener noreferrer">Project homepage</a>\n'
            f'                            <a class="archive-link" href="{repo_url}" target="_blank" rel="noopener noreferrer">Source repository</a>\n'
            f'                        </li>'
        )
        version_label = "Links"

    versions_markup = "\n".join(version_items)

    return (
        f'                    <div class="tool-card" data-tool-id="{tid}" data-tier="{tier}" data-category="{category}">\n'
        f'                        <div class="tool-visual">\n'
        f'                            {visual_html}\n'
        f'                        </div>\n'
        f'                        <div class="tool-content">\n'
        f'                            <div class="tool-id-row">\n'
        f'                                <h3 class="tool-id">{tid}</h3>\n'
        f'                                <span class="badge-tier-{tier}">{tier_label}</span>\n'
        f'                                <span class="badge-license">{license_name}</span>\n'
        f'                            </div>\n'
        f'                            <p class="tool-description">{description}</p>\n'
        f'{replaces_markup}'
        f'                            <p class="version-label">{version_label}</p>\n'
        f'                            <ul class="version-list">\n'
        f'{versions_markup}\n'
        f'                            </ul>\n'
        f'                        </div>\n'
        f'                    </div>'
    )


def render_catalog_category_section(
    category: dict[str, Any],
    tools: list[dict[str, Any]],
    base_url: str = "..",
) -> str:
    """Generates an HTML <article class="category ..."> section for a category and its tools."""
    cat_id = escape_html(category.get("id", ""))
    cat_name = escape_html(category.get("name", ""))
    cat_desc = escape_html(category.get("description", ""))

    cards_html = "\n".join(render_tool_card_static(tool, base_url=base_url) for tool in tools)

    return (
        f'            <article class="category cat-{cat_id}" data-category="{cat_name}">\n'
        f'                <div class="category-head">\n'
        f'                    <h2 class="category-title">{cat_name}</h2>\n'
        f'                    <p class="category-description">{cat_desc}</p>\n'
        f'                </div>\n'
        f'                <div class="tool-list">\n'
        f'{cards_html}\n'
        f'                </div>\n'
        f'            </article>'
    )


def render_catalog_static_html(tools_data: dict[str, Any], base_url: str = "..") -> str:
    """Generates complete static HTML category sections for insertion into data-catalog."""
    categories = tools_data.get("categories", [])
    tools = tools_data.get("tools", [])

    tools_by_cat: dict[str, list[dict[str, Any]]] = {}
    for tool in tools:
        cat_name = tool.get("category", "")
        tools_by_cat.setdefault(cat_name, []).append(tool)

    category_sections: list[str] = []
    for cat in categories:
        cat_name = cat.get("name", "")
        cat_tools = tools_by_cat.get(cat_name, [])
        if cat_tools:
            # Sort tools: frozen first, then alphabetically by ID
            sorted_tools = sorted(
                cat_tools,
                key=lambda t: (0 if t.get("tier") == "frozen" else 1, t.get("id", "")),
            )
            category_sections.append(
                render_catalog_category_section(cat, sorted_tools, base_url=base_url)
            )

    return "\n\n".join(category_sections)


def render_tool_profile_page(
    tool: dict[str, Any],
    category: dict[str, Any],
    base_url: str = "../..",
) -> str:
    """Generates a complete standalone HTML5 profile page for /tools/<id>/index.html."""
    tid = escape_html(tool.get("id", ""))
    tname = escape_html(tool.get("name", tid))
    tagline = escape_html(tool.get("tagline", ""))
    summary = escape_html(tool.get("summary", ""))
    license_name = escape_html(tool.get("license", ""))
    tier = escape_html(tool.get("tier", "frozen"))
    website_url = escape_html(tool.get("website_url", ""))
    repo_url = escape_html(tool.get("repo_url", ""))
    cat_name = escape_html(category.get("name", tool.get("category", "")))
    cat_id = escape_html(category.get("id", "general"))
    tier_label = "Frozen in Launcher" if tier == "frozen" else "Ecosystem Radar"
    meta_desc = escape_html(f"{tname} profile in the Open Game Stack tool directory. {tagline}")

    # Visual header
    image_path = tool.get("image")
    if image_path:
        full_img_src = f"{base_url}/{image_path.lstrip('/')}"
        icon_html = f'<img class="tool-icon" src="{full_img_src}" alt="{tname} logo">'
    else:
        initial = (tid[:1] if tid else "T").upper()
        icon_html = f'<span class="tool-mark" aria-label="{tname}">{initial}</span>'

    # Replaces chips
    replaces_chips = "".join(
        f'<span class="badge">{escape_html(r)}</span>' for r in tool.get("replaces", [])
    )

    # Platforms chips
    platforms_chips = "".join(
        f'<span class="badge">{escape_html(p)}</span>' for p in tool.get("platforms", [])
    )

    # Strengths list
    strengths_items = "".join(
        f'<li>{escape_html(s)}</li>' for s in tool.get("strengths", [])
    )

    # Versions table (if frozen)
    versions = tool.get("versions", [])
    if tier == "frozen" and versions:
        version_rows = []
        for ver in versions:
            v_str = escape_html(ver.get("version", ""))
            v_size = f"{ver.get('size_bytes', 0) / (1024 * 1024):.1f} MB"
            v_sha = escape_html(ver.get("sha256", "")[:16] + "...")
            v_info = escape_html(ver.get("info_url", ""))
            v_arch = escape_html(ver.get("archive_url", ""))
            version_rows.append(
                f'                        <tr>\n'
                f'                            <td><code>{v_str}</code></td>\n'
                f'                            <td>{v_size}</td>\n'
                f'                            <td><code title="{escape_html(ver.get("sha256", ""))}">{v_sha}</code></td>\n'
                f'                            <td><a href="{v_info}" target="_blank" rel="noopener noreferrer">Release Notes</a></td>\n'
                f'                            <td><a href="{v_arch}" target="_blank" rel="noopener noreferrer">Download ZIP</a></td>\n'
                f'                        </tr>'
            )
        version_rows_str = "\n".join(version_rows)
        versions_section = (
            f'            <section class="prose">\n'
            f'                <h2>Frozen Releases</h2>\n'
            f'                <p>These versioned builds are frozen and guaranteed to install reproducibly through the Open Game Stack Launcher.</p>\n'
            f'                <table class="version-table">\n'
            f'                    <thead>\n'
            f'                        <tr><th>Version</th><th>Size</th><th>SHA-256</th><th>Notes</th><th>Archive</th></tr>\n'
            f'                    </thead>\n'
            f'                    <tbody>\n'
            f'{version_rows_str}\n'
            f'                    </tbody>\n'
            f'                </table>\n'
            f'            </section>\n'
        )
    else:
        versions_section = (
            f'            <section class="callout">\n'
            f'                <h3>Ecosystem Radar Status</h3>\n'
            f'                <p>This tool is actively tracked on our Ecosystem Radar as a recommended open-source asset creation or level authoring companion for game developers.</p>\n'
            f'            </section>\n'
        )

    # Resources list
    resources = tool.get("resources", [])
    resource_items = []
    for r in resources:
        r_title = escape_html(r.get("title", ""))
        r_url = escape_html(r.get("url", ""))
        r_type = escape_html(r.get("type", "Resource"))
        resource_items.append(
            f'                    <li><strong>[{r_type}]</strong> <a href="{r_url}" target="_blank" rel="noopener noreferrer">{r_title}</a></li>'
        )
    resources_html = "\n".join(resource_items)

    return f"""<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{meta_desc}">
    <title>{tname} | Open Game Stack</title>
    <link rel="stylesheet" href="{base_url}/assets/css/site.css">
    <link rel="icon" type="image/png" href="{base_url}/favicon.png">
</head>

<body>
    <a class="skip-link" href="#main">Skip to main content</a>

    <header class="site-header">
        <a class="site-logo" href="{base_url}/">
            <img class="site-logo-icon" src="{base_url}/logo.png" alt="Open Game Stack logo">
            <span class="site-logo-text">Open Game Stack</span>
        </a>
        <nav class="site-nav" aria-label="Main Navigation">
            <a class="site-nav-link" href="{base_url}/launcher/">Launcher</a>
            <a class="site-nav-link active" href="{base_url}/tools/">Tools</a>
            <a class="site-nav-link" href="{base_url}/mission/">Mission</a>
            <a class="site-nav-link" href="{base_url}/examples/">Examples</a>
        </nav>
    </header>

    <main class="container" id="main">
        <nav class="breadcrumb" aria-label="Breadcrumb">
            <a href="{base_url}/tools/">Tools</a> &gt; <span>{tname}</span>
        </nav>

        <article class="article-body">
            <header class="tool-profile-header">
                <div class="tool-profile-visual">
                    {icon_html}
                </div>
                <div class="tool-profile-info">
                    <div class="tool-id-row">
                        <h1 class="tool-profile-title">{tname}</h1>
                        <span class="badge badge-tier-{tier}">{tier_label}</span>
                        <span class="badge badge-cat-{cat_id}">{cat_name}</span>
                    </div>
                    <p class="tool-profile-tagline">{tagline}</p>
                    <div class="tool-profile-links">
                        <a class="btn btn-outline" href="{website_url}" target="_blank" rel="noopener noreferrer">Official Website</a>
                        <a class="btn btn-outline" href="{repo_url}" target="_blank" rel="noopener noreferrer">Source Repository</a>
                    </div>
                </div>
            </header>

            <section class="prose">
                <h2>Overview</h2>
                <p>{summary}</p>
            </section>

            <section class="prose">
                <h2>Key Capabilities</h2>
                <ul>
                    {strengths_items}
                </ul>
            </section>

            <section class="spec-table-container">
                <table class="spec-table">
                    <tbody>
                        <tr><th>Category</th><td>{cat_name}</td></tr>
                        <tr><th>License</th><td><code>{license_name}</code></td></tr>
                        <tr><th>Supported Platforms</th><td>{platforms_chips}</td></tr>
                        <tr><th>Replaces</th><td>{replaces_chips}</td></tr>
                    </tbody>
                </table>
            </section>

{versions_section}
            <section class="prose">
                <h2>Curated Learning Resources</h2>
                <ul>
{resources_html}
                </ul>
            </section>
        </article>
    </main>

    <footer class="site-footer">
        <div class="site-footer-content">
            <p class="site-footer-tagline">Open-source tools and reproducible workflows for game creators.</p>
            <nav class="site-footer-links" aria-label="Footer Navigation">
                <a class="site-footer-link" href="{base_url}/launcher/">Launcher</a>
                <a class="site-footer-link" href="{base_url}/tools/">Tools</a>
                <a class="site-footer-link" href="{base_url}/mission/">Mission</a>
                <a class="site-footer-link" href="{base_url}/examples/">Examples</a>
                <a class="site-footer-link" href="https://opengamestack.substack.com/" target="_blank" rel="noopener noreferrer">Newsletter</a>
                <a class="site-footer-link" href="https://github.com/OpenGameStack-Launcher" target="_blank" rel="noopener noreferrer">GitHub</a>
            </nav>
            <p class="site-footer-copy">&copy; 2026 Open Game Stack contributors. Sovereign and independent.</p>
        </div>
    </footer>
</body>

</html>
"""


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for content builder and metadata validator."""
    parser = argparse.ArgumentParser(
        description="Open Game Stack Content Builder and Tool Metadata Validator"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate content/tools.json schema integrity and repository parity without building",
    )
    parser.add_argument(
        "--tools-file",
        type=Path,
        default=REPO_ROOT / "content" / "tools.json",
        help="Path to tools.json metadata file (defaults to content/tools.json)",
    )
    parser.add_argument(
        "--sibling-repo",
        type=Path,
        default=None,
        help="Path to sibling ogs-frozen-stacks/repository.json for parity checks",
    )

    args = parser.parse_args(argv)

    try:
        data = load_tools_metadata(args.tools_file)
    except Exception as exc:
        print(f"[FAIL] Unable to load tools metadata from {args.tools_file}: {exc}", file=sys.stderr)
        return 1

    errors = validate_tools_metadata(data, sibling_repo_path=args.sibling_repo)

    if errors:
        print(f"[FAIL] Tool metadata validation encountered {len(errors)} error(s):", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    tool_count = len(data.get("tools", []))
    category_count = len(data.get("categories", []))
    frozen_count = sum(1 for t in data.get("tools", []) if t.get("tier") == "frozen")
    radar_count = sum(1 for t in data.get("tools", []) if t.get("tier") == "radar")

    print(
        f"[PASS] Tools metadata validation succeeded: "
        f"{category_count} categories, {tool_count} tools ({frozen_count} frozen, {radar_count} radar)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
