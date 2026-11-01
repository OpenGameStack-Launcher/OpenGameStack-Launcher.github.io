# AI Agent Guidelines for Open Game Stack Website (`OpenGameStack-Launcher.github.io`)

Welcome to the **Open Game Stack Website** repository (`C:\Projects\OpenGameStack-Launcher.github.io`), which powers [opengamestack.org](https://opengamestack.org). This file is the primary entry point for AI coding agents working in this workspace.

## 1. Project Mission & Core Architecture

**Vision:** "Sovereignty Over Subscription." This repository hosts the official public web presence for the Open Game Stack initiative, serving as the public front door for the OGS Launcher (`C:\Projects\ogs-launcher`) and the Frozen Tool Stack (`C:\Projects\ogs-frozen-stacks`).

All code changes must strictly preserve these four architectural pillars:
1. **Zero Dependencies & No Build Step:** The website is built exclusively with semantic **HTML5**, modern **CSS3** (`assets/css/site.css`), and progressive-enhancement **vanilla JavaScript**. Never introduce frontend frameworks (React, Vue, Tailwind, etc.), bundlers, or external runtime libraries.
2. **Privacy-First & Self-Hosted Assets:** Respect user privacy by design. Never add third-party analytics, telemetry scripts, tracking pixels, or external font/CSS CDNs (such as Google Fonts or jsDelivr). All fonts (`assets/fonts/*.woff2`, `assets/fonts/fonts-local.css`) and icons/images (`assets/images/`) must be self-hosted inside the repository.
3. **Offline-Resilient Progressive Enhancement:** Every page must render complete, readable content even when JavaScript is disabled or remote network requests fail. Specifically, `tools/index.html` must maintain a complete static HTML tool catalog inside `[data-catalog]` as a fallback alongside its dynamic fetch of `ogs-frozen-stacks/repository.json`.
4. **Defensive DOM & Link Security:** Treat fetched JSON data (`repository.json`) as untrusted input. Always construct DOM nodes with `document.createElement()` and assign text via `.textContent` (never `.innerHTML`). All external links (`target="_blank"`) must include `rel="noopener noreferrer"`.

---

## 2. Cross-Repository Synchronization Rules

This website sits alongside two sibling repositories in the workspace and must stay synchronized with them:
- **OGS Launcher (`C:\Projects\ogs-launcher`):**
  - Landing page download links and release notes in `index.html` must reference the current published release tag and asset name from `OpenGameStack-Launcher/ogs-launcher` (for example, `v0.2.0` and the current Godot engine target `Godot 4.7.2`).
  - References to OGS project manifest files in documentation or landing copy must use the canonical filenames (`ogs_stack.json` and `ogs_config.json`).
- **OGS Frozen Stacks (`C:\Projects\ogs-frozen-stacks`):**
  - The tool catalog page (`tools/index.html`) dynamically fetches `https://raw.githubusercontent.com/OpenGameStack-Launcher/ogs-frozen-stacks/main/repository.json`.
  - Whenever tools, categories (such as `Engine`, `2D`, `3D`, `Audio`, `Code`), or versions are added or updated in `C:\Projects\ogs-frozen-stacks\repository.json`, `tools/index.html` must be synchronized across:
    1. The static HTML fallback cards inside `<section class="catalog" ... data-catalog>`.
    2. The inline JS `categoryOrder`, `categoryDescriptions`, and `toolDetails` maps.
    3. Tool icon assets in `assets/images/` (or verified `.tool-mark` monogram fallback).

---

## 3. Environment & Shell Rules

- **Operating System:** Windows 11 with **PowerShell**.
- **PowerShell Syntax:** Never use Linux shell commands (`grep`, `ls`, `cat`, `sed`, `awk`) or bash command chaining (`&&` in Windows PowerShell 5.1). Use `;` or separate tool calls, and prefer built-in agent file/search tools over shell commands.
- **UTF-8 File Encoding:** Never generate `.html`, `.css`, `.py`, or `.md` files using PowerShell redirection (`>` or `Set-Content` without UTF-8 encoding), as UTF-16 LE or unexpected BOMs can corrupt web assets. Always use your native file-writing tools (`write_file`, `edit_file`).
- **Writing Style:** Never use em-dashes or en-dashes as parenthetical dashes in website copy, documentation, comments, or commit messages. Use commas, colons, parentheses, or separate sentences.
- **GitHub CLI (`gh`) Token Scope Guardrail:** Never run bare `gh issue view <id>` or `gh pr view <id>` commands, as they can fail with `read:project` token scope errors. Always pass explicit `--json` fields:
  - `gh issue view <id> --json number,title,body,state,labels,assignees`
  - `gh pr view <id> --json number,title,body,state,baseRefName,headRefName,commits,files`

---

## 4. Tech Stack, Validation & Visual QA Conventions

- **HTML5 & Accessibility (`index.html`, `mission/index.html`, `tools/index.html`, `examples/index.html`):**
  - Every page must include `<!DOCTYPE html>`, `<html lang="en">`, `<meta charset="UTF-8">`, `<meta name="viewport" content="width=device-width, initial-scale=1.0">`, a descriptive `<meta name="description">`, and a `<title>`.
  - Maintain consistent `<header class="site-header">`, `<main class="container" id="main">`, and `<footer class="site-footer">` landmarks across all pages.
  - Every `<img>` must have a non-empty `alt` attribute.
  - Preserve keyboard focus visibility (`:focus-visible`) and reduced-motion support (`@media (prefers-reduced-motion: reduce)`).
- **Shared Stylesheet (`assets/css/site.css`):**
  - Keep shared layout, Neon Tech design tokens (`:root` CSS custom properties), glassmorphism cards, and responsive breakpoints (`850px`, `768px`) in `assets/css/site.css`. Avoid inline `style=""` attributes in HTML files.
- **Automated Site Validation Suite (`tests/validate_site.py`):**
  - All structural, link, asset, accessibility, and privacy/security checks live in `tests/validate_site.py` (zero-dependency Python 3 script).
  - Run the automated test suite from the repository or worktree root:
    ```powershell
    python tests/validate_site.py
    ```
  - All checks must pass (`tests failed: 0`, exit code `0`) before opening or merging any Pull Request.
- **Local Preview & Visual QA:**
  - To inspect layout, responsive behavior, or dynamic catalog rendering locally, serve the repository or worktree over HTTP:
    ```powershell
    python -m http.server 8000 --bind 127.0.0.1
    ```
  - Always stop any background local HTTP server process once visual inspection is complete so ports and worktree directories are released cleanly.

---

## 5. Workflows, Skills & Canonical Documentation

This repository uses the same structured multi-agent workflow as `ogs-launcher` for issue creation, resolution, and PR review:

### Agent Skills (`.agents/skills/`)
- **Issue Orchestration (`.agents/skills/issue-orchestration/SKILL.md`):** Defines how the primary orchestrator spawns and manages single-task `issue_creator`, `issue_resolver`, and `pr_reviewer` subagents sequentially with 10-minute liveness timers and strict user authorization gates.
- **Code Review (`.agents/skills/code-review/SKILL.md`):** Structured checklist for reviewing HTML5, CSS3, vanilla JS, asset, and documentation diffs against Open Game Stack web standards.

### Agent Rules (`.agents/rules/`)
- **Git Worktree Workflow (`.agents/rules/git_workflow.md`):** Enforces isolated worktrees under `.worktrees/` and complete branch/worktree cleanup.
- **Issue Resolution Workflow (`.agents/rules/issue_resolution_workflow.md`):** Step-by-step instructions for triaging, implementing, testing, and submitting PRs.
- **PR Review Workflow (`.agents/rules/pr_review_workflow.md`):** Step-by-step instructions for reviewing PRs, running `python tests/validate_site.py`, synchronizing docs, dispatching `ci.yml`, and merging.
- **Security & Privacy Rules (`.agents/rules/security_privacy.md`):** Zero-tracker, self-hosted asset, and safe DOM rendering guardrails.

### Canonical Workflow Guides (`docs/`)
- **Creating Issues:** [docs/CREATING_ISSUES.md](docs/CREATING_ISSUES.md)
- **Resolving Issues:** [docs/RESOLVING_ISSUES.md](docs/RESOLVING_ISSUES.md)
- **Reviewing & Merging PRs:** [docs/REVIEWING_AND_MERGING_PRS.md](docs/REVIEWING_AND_MERGING_PRS.md)
- **Automated Testing Guide:** [docs/TESTING.md](docs/TESTING.md)
- **Manual Testing Guide:** [docs/MANUAL_TESTING.md](docs/MANUAL_TESTING.md)
