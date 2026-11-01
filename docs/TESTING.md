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
OGS Website Validation Summary: <N> checks run | tests passed: <N> | tests failed: 0
All static website validation checks passed.
```

The script exits with code `0` when all checks pass and `1` if any check fails.

---

## 3. Validation Coverage (`tests/validate_site.py`)

`tests/validate_site.py` enforces the following categories of checks across all HTML and CSS files in the repository:

1. **Required Repository Files & Custom Domain (`CNAME`):**
   - Verifies that `CNAME`, `index.html`, `manifesto/index.html`, `tools/index.html`, `examples/index.html`, `assets/css/site.css`, `assets/fonts/fonts-local.css`, `favicon.png`, and `logo.png` exist.
   - Confirms that the legacy `pages/` directory does not exist.
   - Confirms `CNAME` equals `opengamestack.org`.
2. **HTML5 Document Structure & Landmarks:**
   - Every `.html` file declares `<!DOCTYPE html>` and `<html lang="en">`.
   - Every `.html` file includes `<meta charset="UTF-8">`, a responsive `<meta name="viewport">`, a non-empty `<meta name="description">`, and a non-empty `<title>`.
   - Every `.html` file contains `<header class="site-header">`, `<main id="main">`, and `<footer class="site-footer">`.
   - Every `.html` file contains a skip-to-content accessibility landmark link (`<a class="skip-link" href="#main">`).
3. **Internal Link & Asset Resolution:**
   - Every local `<a href="...">`, `<link href="...">`, `<script src="...">`, and `<img src="...">` resolves to an existing file in the repository. Directory targets containing `index.html` (such as `manifesto/`, `../tools/`, `./`) resolve cleanly to the underlying `index.html` file.
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
6. **Landing Page Release & Manifest Verifications (`index.html`):**
   - Asserts at least 2 download links pointing to the current published release package (`OGS-Launcher-win64-0.2.0.zip` under `v0.2.0`).
   - Asserts canonical manifest and config naming (`ogs_stack.json` and `ogs_config.json`).
   - Asserts Godot engine target reference (`Godot 4.7.2`).
   - Prohibits obsolete `v0.1.5` release links and legacy un-prefixed `stack.json` naming.
7. **Tool Catalog Static Fallback Parity (`tools/index.html`):**
   - Confirms `tools/index.html` includes the `[data-catalog]` container.
   - Confirms exactly 7 static fallback tool cards inside `[data-catalog]`.
   - Verifies static tool catalog IDs (`godot`, `gimp`, `krita`, `blender`, `audacity`, `git`, `vscodium`) and version sets against sibling `ogs-frozen-stacks/repository.json` (or baseline fallback).
   - Verifies `.tool-mark` monograms for icon-less tools (`git` and `vscodium`).

---

## 4. Continuous Integration (`.github/workflows/ci.yml`)

The repository includes a GitHub Actions workflow (`.github/workflows/ci.yml`) supporting both `workflow_dispatch` (manual pre-merge gate used by the PR Reviewer agent) and pushes to `main`. It runs `python tests/validate_site.py` on an Ubuntu runner and fails the build if any validation check fails.
