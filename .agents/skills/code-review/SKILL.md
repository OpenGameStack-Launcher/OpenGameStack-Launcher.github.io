---
name: code-review
description: >-
  Use when reviewing pull requests or diffs that touch HTML (.html), CSS (.css), JavaScript, assets, or validation scripts in the Open Game Stack Website repository (OpenGameStack-Launcher.github.io). Performs a structured code review against OGS web standards, zero-dependency/privacy rules, cross-repo synchronization, accessibility, and automated validation requirements.
---

# Web Code Review (Open Game Stack Website)

Structured review procedure for changes to HTML, CSS, inline JavaScript, assets, and tests in `OpenGameStack-Launcher.github.io`. Apply this on pull requests, diffs, or any request to review website changes.

## Review Checklist

Walk the diff against each section below. Focus comments on lines that are part of the diff (changed or added), unless a change clearly breaks surrounding code.

### 1. Zero Dependencies, Privacy & Sovereign Web Architecture
- Reject any external runtime framework, library, or CDN link (`fonts.googleapis.com`, `fonts.gstatic.com`, `unpkg.com`, `jsdelivr.net`, `cdnjs.cloudflare.com`).
- Reject any analytics, telemetry, or tracking script (`google-analytics`, `googletagmanager`, tracking pixels, third-party beacons).
- Confirm all fonts (`assets/fonts/*.woff2`) and images (`assets/images/*.png`) are self-hosted within the repository.
- Confirm `CNAME` (`opengamestack.org`) is intact at the repository root.

### 2. Semantic HTML5, Accessibility & Navigation Consistency
- Every `.html` page must include `<!DOCTYPE html>`, `<html lang="en">`, `<meta charset="UTF-8">`, `<meta name="viewport" content="width=device-width, initial-scale=1.0">`, a non-empty `<meta name="description">`, and a `<title>`.
- Confirm `<header class="site-header">`, `<main class="container" id="main">`, and `<footer class="site-footer">` landmarks are consistent across `index.html`, `pages/*.html`, and `examples/*.html`.
- Every `<img>` tag must include a descriptive, non-empty `alt` attribute.
- Keyboard focus states (`:focus-visible`) and `@media (prefers-reduced-motion: reduce)` rules in `assets/css/site.css` must be preserved.

### 3. Defensive Security & Safe DOM Construction
- Every external link (`http://` or `https://`) with `target="_blank"` must include `rel="noopener noreferrer"`.
- In any inline JavaScript (such as `pages/tools.html`), confirm untrusted data (`repository.json`) is validated before rendering and rendered exclusively via `document.createElement()` and `.textContent`. Flag any use of `.innerHTML`, `outerHTML`, or `insertAdjacentHTML`.

### 4. Offline Fallback & Cross-Repo Synchronization
- **Offline Progressive Enhancement:** Confirm `pages/tools.html` retains a complete static HTML tool catalog inside `<section class="catalog" ... data-catalog>` so the page works without JavaScript or network connectivity.
- **OGS Frozen Stacks Sync:** When updating tool catalog entries in `pages/tools.html`, verify that the static HTML cards, `categoryOrder`, `categoryDescriptions`, and `toolDetails` match `C:\Projects\ogs-frozen-stacks\repository.json`.
- **OGS Launcher Sync:** When updating release links or engine target notes in `index.html`, verify they match the published release in `OpenGameStack-Launcher/ogs-launcher` and use canonical manifest filenames (`ogs_stack.json` and `ogs_config.json`).

### 5. Styling & Writing Standards
- Shared styling belongs in `assets/css/site.css` using `:root` CSS custom properties (`--primary`, `--bg-dark`, `--card-bg`, etc.) and existing responsive breakpoints (`850px`, `768px`). Flag unnecessary inline `style=""` attributes.
- Confirm no em-dashes or en-dashes (as parenthetical dashes) appear in page copy, comments, or documentation.

### 6. Automated Validation (`tests/validate_site.py`)
- Confirm `python tests/validate_site.py` passes with 0 failures (`tests failed: 0`, exit code `0`).
- Confirm new pages or structural invariants have corresponding checks in `tests/validate_site.py`, and that `docs/TESTING.md` / `docs/MANUAL_TESTING.md` are updated when needed.

## Output Format

Report findings grouped by severity:

- **Blocking:** Broken links or missing assets, external CDN/tracker additions, `.innerHTML` usage, missing `rel="noopener noreferrer"`, missing image `alt` text, broken offline fallback in `pages/tools.html`, or failing `tests/validate_site.py`.
- **Should Fix:** Out-of-sync catalog/release metadata, inline styles instead of `site.css` classes, missing documentation updates.
- **Nit:** Copy polish, class naming, or minor readability suggestions.

For each finding, reference the file and line, explain the issue, and suggest the concrete fix. If the diff is clean, state that explicitly.
