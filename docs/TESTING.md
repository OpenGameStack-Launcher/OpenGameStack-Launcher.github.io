# Automated Testing & Site Validation Guide

This document describes the automated validation architecture for the **Open Game Stack Website** (`OpenGameStack-Launcher.github.io`).

---

## 1. Philosophy: Zero-Dependency Validation

Consistent with the Open Game Stack principle of **"Sovereignty Over Subscription,"** the website's automated test suite (`tests/validate_site.py`) uses **only the Python 3 standard library** (`html.parser`, `pathlib`, `re`, `sys`, `urllib.parse`, `json`). No external packages, Node.js toolchains, or browser drivers are required to run the validation suite locally or in CI.

---

## 2. Running the Validation Suite

From the repository root (`C:\Projects\OpenGameStack-Launcher.github.io`) or inside an isolated worktree (`.worktrees/issue-<number>`), run:

```powershell
python tests/validate_site.py
```

### Expected Output
```text
OGS Website Validation Summary: 2746 checks run | tests passed: 2746 | tests failed: 0
All static website validation checks passed.
```

The script exits with code `0` when all checks pass and `1` if any check fails.

### Running the Tool Metadata and Content Builder Check

To validate canonical tool metadata in `content/tools.json` and verify schema integrity and parity against sibling `ogs-frozen-stacks/repository.json`:

```powershell
python scripts/build_content.py --check
```

### Expected Output
```text
[PASS] Tools metadata validation succeeded: 6 categories, 19 tools (7 frozen, 12 radar).
```

### Generating Tool Profile Pages

To build or regenerate static deep-dive HTML profile pages for all Tier-1 Launcher tools:

```powershell
python scripts/build_content.py --build
```

---

## 3. Validation Coverage (`tests/validate_site.py`)

`tests/validate_site.py` enforces the following categories of checks across all HTML, CSS, JSON, and script files in the repository:

1. **Required Repository Files, Assets & Custom Domain (`CNAME`):**
   - Verifies that `CNAME`, `index.html`, `launcher/index.html`, `mission/index.html`, `tools/index.html`, `examples/index.html`, `content/tools.json`, `scripts/build_content.py`, `assets/css/site.css`, `assets/fonts/fonts-local.css`, `favicon.png`, and `logo.png` exist.
   - Verifies that all 7 Tier-1 dedicated tool profile pages (`tools/godot/index.html`, `tools/blender/index.html`, `tools/krita/index.html`, `tools/gimp/index.html`, `tools/audacity/index.html`, `tools/git/index.html`, `tools/vscodium/index.html`) exist in `REQUIRED_FILES`.
   - Verifies that all 19 tool logos and icons (`assets/images/Godot.png`, `Blender.png`, `Krita.png`, `GIMP.png`, `Audacity.png`, `Git.png`, `VSCodium.png`, `pixelorama.png`, `libresprite.png`, `inkscape.svg`, `ldtk.svg`, `tiled.png`, `trenchbroom.png`, `material-maker.png`, `blockbench.png`, `armorpaint.png`, `lmms.png`, `ardour.png`, `sfxr.png`) exist in `REQUIRED_FILES` with exact case-sensitivity verified on disk.
   - Confirms that legacy `pages/` and `manifesto/` directories do not exist.
   - Confirms `CNAME` equals `opengamestack.org`.
2. **HTML5 Document Structure & Landmarks:**
   - Every `.html` file declares `<!DOCTYPE html>` and `<html lang="en">`.
   - Every `.html` file includes `<meta charset="UTF-8">`, a responsive `<meta name="viewport">`, a non-empty `<meta name="description">`, and a non-empty `<title>`.
   - Every `.html` file contains `<header class="site-header">`, `<main id="main">`, and `<footer class="site-footer">`.
   - Every `.html` file contains a skip-to-content accessibility landmark link (`<a class="skip-link" href="#main">`).
3. **Internal Link & Asset Resolution with Case-Exact Disk Verification:**
   - Every local `<a href="...">`, `<link href="...">`, `<script src="...">`, and `<img src="...">` resolves to an existing file in the repository. Directory targets containing `index.html` (such as `launcher/`, `tools/`, `mission/`, `./`) resolve cleanly to the underlying `index.html` file.
   - Enforces case-exact local file and directory path resolution by verifying directory entries on disk for every path segment, preventing subtle broken links on case-sensitive operating systems like Linux in GitHub Pages.
   - Confirms that no active HTML files contain links or references to legacy `manifesto.html`, `manifesto/`, or `/manifesto/`.
   - Primary navigation (`site-logo`, `site-nav-link`), footer links (`site-footer-link`), and internal CTA buttons (`btn`, `btn-outline`) are strictly prohibited from exposing `index.html`, legacy `pages/`, or `.html` file extensions, enforcing clean directory URLs.
   - Same-page `#fragment` links resolve to a matching `id` attribute in that document.
   - Every local `url(...)` reference in `assets/css/site.css` and `assets/fonts/fonts-local.css` resolves to an existing file on disk.
4. **Accessibility & External Link Hardening:**
   - Every `<img>` element has a non-empty `alt` attribute.
   - Every external link (`http://` or `https://`) with `target="_blank"` includes `rel="noopener noreferrer"`.
   - `javascript:` pseudo-links are prohibited.
5. **Zero External Dependencies, Privacy & Safe DOM Rendering:**
   - Rejects external `<script src="...">` and external `<link rel="stylesheet">` tags.
   - Rejects references to third-party font/asset CDNs and analytics trackers (`fonts.googleapis.com`, `fonts.gstatic.com`, `google-analytics.com`, `googletagmanager.com`, `unpkg.com`, `jsdelivr.net`, `cdnjs.cloudflare.com`, etc.).
   - Rejects `.innerHTML` usage in inline scripts to enforce safe DOM construction (`document.createElement` + `.textContent`).
6. **Hub Landing Page Verifications (`index.html`):**
   - Asserts hub navigation and callout links to `launcher/`, `tools/`, `mission/`, `examples/`, and Substack (`https://opengamestack.substack.com/`).
   - Asserts download links pointing to the current published release package (`OGS-Launcher-win64-0.2.0.zip` under `v0.2.0`).
   - Asserts canonical manifest and config naming (`ogs_stack.json` and `ogs_config.json`).
   - Asserts Godot engine target reference (`Godot 4.7.2`).
   - Prohibits obsolete `v0.1.5` release links and legacy un-prefixed `stack.json` naming.
7. **Tool Catalog Static Fallback Parity & Consistency (`tools/index.html`):**
   - Confirms `tools/index.html` includes the `[data-catalog]` container.
   - Confirms all 19 static fallback tool cards inside `[data-catalog]` (7 Tier-1 Frozen in Launcher tools and 12 Tier-2 Ecosystem Radar tools across 6 categories).
   - Verifies that all 7 Tier-1 tool cards link directly to their dedicated profile pages (`./<id>/`) via both tool title links (`.tool-title-link`) and action buttons (`.tool-profile-link`).
   - Verifies that Tier-2 radar tools have no subpage profile links.
   - Verifies static tool catalog IDs and Tier-1 version sets against sibling `ogs-frozen-stacks/repository.json` (or baseline fallback).
   - Verifies that all 19 catalog tools have self-hosted image assets in `assets/images/` verified in `REQUIRED_FILES` with exact case matching.
   - Verifies zero generic `.tool-mark` monogram elements across both static fallback cards and inline `toolDetails`, requiring official tool images for every entry.
   - Verifies accessible filter controls in `.catalog-filters`, including `role="group"` ARIA attributes, semantic filter buttons (`.filter-btn`), and `aria-pressed` states for tier and category selection.
   - Verifies that inline `toolDetails` in the hydration script specifies valid local image paths for all 19 catalog tools.
8. **Dedicated Tool Deep-Dive Profile Page Verifications (`tools/<id>/index.html`):**
   - Verifies that all 7 Tier-1 tools have standalone HTML profile pages (`tools/godot/index.html`, `tools/blender/index.html`, `tools/krita/index.html`, `tools/gimp/index.html`, `tools/audacity/index.html`, `tools/git/index.html`, `tools/vscodium/index.html`).
   - Verifies page title format (`<Tool Name> - Open Game Stack Profile | Open Game Stack`).
   - Verifies breadcrumb back-link navigation (`<a href="../" class="back-link">&larr; Back to Tool Catalog</a>`).
   - Verifies required section anchors: `#role`, `#launcher-integration`, `#vital-signs`, `#resources`.
   - Verifies frozen release specification table listing exact version, download size, 64-character SHA-256 checksum, and executable path matching `content/tools.json` and sibling `repository.json`.
   - Verifies `ogs_stack.json` manifest code block with JSON syntax.
   - Verifies vital signs table containing license, platform badges, category badge, and links.
   - Verifies curated learning resource links with `target="_blank"` and `rel="noopener noreferrer"`.
   - Asserts that Tier-2 radar tools do not have profile subpages.
9. **Mission Page Verifications (`mission/index.html`):**
   - Verifies that `mission/index.html` title text equals `Mission | Open Game Stack`.
   - Verifies that `mission/index.html` preserves required section anchor IDs (`#sovereignty`, `#environment`, `#dual-use`, `#stability`).
   - Verifies that `mission/index.html` includes matching `.section-index` links for all four section anchors.
   - Verifies that mission prose reframes creator sovereignty around indie game developers and studios.
   - Verifies that `index.html` includes the secondary CTA button with text `The Mission` pointing to `mission/`.
10. **Dedicated Launcher Page Verifications (`launcher/index.html`):**
    - Verifies that `launcher/index.html` title text equals `Launcher | Open Game Stack`.
    - Asserts at least 2 download links pointing to the current published release package (`OGS-Launcher-win64-0.2.0.zip` under `v0.2.0`).
    - Asserts desktop application runtime reference (`Godot 4.7.2`).
    - Asserts canonical manifest references (`ogs_stack.json` and `ogs_config.json`).
11. **Reference Examples Showcase Verifications (`examples/index.html`):**
    - Verifies that `examples/index.html` title text equals `Examples | Open Game Stack`.
    - Confirms structured layout using `.grid` and `.project-card` containers.
    - Confirms showcase cards for both reference projects (`Sudoku` and `Letter Logic`).
    - Verifies frozen tool stack badges (`Godot`, `Git`, `Krita`) across project cards.
    - Verifies required outbound repository and playable web demo links (`https://github.com/OpenGameStack/sudoku`, `https://audrain.games/sudoku`, `https://github.com/OpenGameStack/letter-logic`, `https://audrain.games/letter-logic`) with `target="_blank"` and `rel="noopener noreferrer"`.
12. **Sitewide Navigation, Footer Consistency & Tagline Enforcement:**
    - Verifies that primary navigation (`.site-nav`) across all pages includes the appropriate relative link to the Launcher page (`launcher/`, `./`, `../launcher/`, or `../../launcher/` for nested subpages).
    - Verifies depth-aware navigation resolution for subpages at depth 2 (`tools/<id>/index.html`).
    - Verifies that footer link lists (`.site-footer-links`) across all pages include the official Substack link (`https://opengamestack.substack.com/`) with `rel="noopener noreferrer"`.
    - Enforces the sitewide footer copyright tagline: `Open-source tools and reproducible workflows for game creators.`.
    - Prohibits obsolete footer copyright copy (`Dual-use technology for open simulation.`) on all pages.
13. **Game Studio Dark CSS Tokens & Component Selectors (`assets/css/site.css`):**
    - Verifies required surface tokens (`--bg-dark`, `--bg-surface`, `--card-bg`, `--card-border`).
    - Verifies required semantic category accent properties (`--cat-engine`, `--cat-2d`, `--cat-3d`, `--cat-audio`, `--cat-level`, `--cat-code`).
    - Verifies required category accent alias variables (`--accent-engine`, `--accent-2d`, `--accent-3d`, `--accent-audio`, `--accent-level`, `--accent-code`).
    - Verifies required editorial typography, catalog filter, table, and callout classes (`.prose`, `.article-body`, `.catalog-filters`, `.filter-btn`, `.badge-tier-frozen`, `.badge-tier-radar`, `.spec-table`, `.version-table`, `.code-block`, `.code-header`, `.callout`).
    - Verifies project card and button utility classes (`.btn-sm`, `.project-card`, `.card-badges`, `.card-actions`).
    - Verifies tool profile header, breadcrumb, and resource list styling classes (`.breadcrumb`, `.back-link`, `.tool-profile-header`, `.tool-profile-visual`, `.tool-profile-info`, `.tool-profile-title`, `.tool-profile-tagline`, `.tool-profile-links`, `.tool-title-link`, `.tool-profile-link`, `.resource-list`).
14. **Canonical Tool Metadata Schema Integrity & Zero-Dependency Builder Parity (`content/tools.json` & `scripts/build_content.py`):**
    - Verifies JSON structure and schema validity of `content/tools.json`.
    - Confirms existence and completeness of 6 canonical tool categories (`Engine`, `2D`, `3D`, `Audio`, `Level Design`, `Code`).
    - Validates 7 Tier-1 Launcher frozen tools with exact version, archive, sha256 checksum, size, and executable path parity against upstream `ogs-frozen-stacks/repository.json`.
    - Validates 12 Tier-2 Ecosystem Radar tools (`pixelorama`, `libresprite`, `inkscape`, `ldtk`, `tiled`, `trenchbroom`, `material-maker`, `blockbench`, `armorpaint`, `lmms`, `ardour`, `sfxr`).
    - Confirms all required metadata fields (`id`, `name`, `tier`, `category`, `tagline`, `summary`, `replaces`, `strengths`, `license`, `website_url`, `repo_url`, `platforms`, `resources`) are non-empty across all 19 tools.
    - Validates secure `https://` schemes across all website, repository, archive, info, and learning resource URLs.
    - Integrates schema integrity verification via `scripts/build_content.py validate_tools_metadata()`.

---

## 4. Continuous Integration (`.github/workflows/ci.yml`)

The repository includes a GitHub Actions workflow (`.github/workflows/ci.yml`) supporting both `workflow_dispatch` (manual pre-merge gate used by the PR Reviewer agent) and pushes to `main`. It runs `python tests/validate_site.py` on an Ubuntu runner and fails the build if any validation check fails.
