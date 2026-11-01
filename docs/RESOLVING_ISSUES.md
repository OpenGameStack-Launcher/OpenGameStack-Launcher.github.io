# Issue Resolution Workflow & Standards

This document establishes the official standards, Git worktree workflow, and coding guidelines for anyone resolving issues in the **Open Game Stack Website** repository (`OpenGameStack-Launcher.github.io`), whether human contributor or autonomous agent.

---

## 0. Operational Rules
* **PowerShell Chaining:** When executing shell commands on Windows, NEVER use `&&` to chain commands together (it fails in Windows PowerShell 5.1). Instead, use `;` or execute commands sequentially in separate tool calls.
* **File Generation Encoding:** Generating text files via PowerShell pipes (e.g., `>` or `Set-Content` without explicit UTF-8 encoding) often creates UTF-16 LE encoding errors or unexpected BOMs. ALWAYS use your native agent file-writing and editing tools (`write_file` / `edit_file`) to generate or edit HTML, CSS, Python, or Markdown files.
* **Writing Style:** Never use em-dashes or en-dashes as parenthetical dashes in website copy, comments, or documentation.
* **Documentation Redundancy:** Before requesting the PR Reviewer to document a feature or testing steps, always verify whether the documentation already exists in `docs/TESTING.md`, `docs/MANUAL_TESTING.md`, or `README.md`.

---

## 1. Role Overview & Core Boundaries

The **Issue Resolver** is responsible for taking an open issue from conception to an unmerged, thoroughly validated, and well-documented Pull Request.

### Primary Responsibilities
1. **Triage & Select:** Identify the next unblocked issue based on dependencies, priority, and issue number.
2. **Worktree Isolation:** Create and work within an isolated Git worktree under `.worktrees/`.
3. **Implement:** Write clean, semantic HTML5, modular CSS3 in `assets/css/site.css`, and defensive vanilla JavaScript meeting all acceptance criteria.
4. **Validate:** Run the automated site validation suite (`python tests/validate_site.py`), add new checks in `tests/validate_site.py` when appropriate, and verify visual/responsive layout.
5. **Detailed Pull Request:** Push the branch and submit a detailed PR against `main`.

### Explicit Boundaries (What the Issue Resolver Does NOT Do)
* **DO NOT merge into `main`:** The Issue Resolver must never merge the PR or push directly to `main`.
* **DO NOT update project documentation:** Updating `docs/TESTING.md`, `docs/MANUAL_TESTING.md`, or `README.md` is handled by the **PR Reviewer & Documentation Agent** (unless the issue itself is specifically a documentation-only issue). The resolver provides the necessary handoff details in the PR body so the reviewing agent can update documentation accurately on the branch prior to merge.

---

## 2. Issue Discovery & Triage Protocol

When tasked with resolving an issue, follow this triage procedure:

### 1. Inspect Open Issues
List open issues via the GitHub CLI:
```powershell
Set-Location "C:\Projects\OpenGameStack-Launcher.github.io"
gh issue list --state open --limit 50 --json number,title,labels,body
```

> [!WARNING]
> **NEVER run a bare `gh issue view <id>` command.** Repository token configurations can trigger a `read:project` scope error for bare view commands. You must ALWAYS pass the `--json` flag:

```powershell
gh issue view <issue_number> --json number,title,body,state,labels,assignees
```

### 2. Dependency Checking (`Depends on #X`)
* Read the issue description carefully.
* If the issue header or body contains **`Depends on #<number>`**, check the status of the dependency:
  ```powershell
  gh issue view <dependency_number> --json state
  ```
* If the dependency issue is still `OPEN`, **do not begin work on this issue**. Move to the next unblocked issue or report the blocker.
* Only begin work if all dependencies are `CLOSED` and their pull requests are merged into `main`.

### 3. Issue Selection Strategy
Unless instructed to work on a specific issue:
1. Prioritize unblocked issues by severity (`severity: critical`, `severity: high`) and foundational scope (`type: catalog-sync`, `type: security-privacy`, shared `assets/css/site.css`, `tests/validate_site.py`) before localized copy tweaks.
2. Within the same priority tier, select the lowest-numbered open issue.

---

## 3. Git Worktree & Branching Workflow

All work must occur inside an isolated worktree under `.worktrees/` to keep the primary working tree clean.

### 1. Fetch Latest Remote Changes
```powershell
Set-Location "C:\Projects\OpenGameStack-Launcher.github.io"
git fetch origin
```

### 2. Create the Worktree
Create a new branch based on `origin/main` inside `.worktrees/issue-<number>`:
```powershell
git worktree add .worktrees/issue-<number> -b fix/issue-<number>-<short-description> origin/main
```
*(Use `feature/issue-<number>-<short-description>` for new features or enhancements).*

Run all validation commands and commits inside `.worktrees/issue-<number>`.

### 3. Commit Guidelines & Clean Working Tree Check
* Use clear commit messages referencing the issue or [Conventional Commits](https://www.conventionalcommits.org/):
  * `fix: <description> (Fixes #<number>)`
  * `feat: <description> (Resolves #<number>)`
  * `test: <description>`
  * `docs: <description>`
* **CRITICAL:** After committing and BEFORE pushing or opening a PR, run `git status` inside the worktree. Ensure there are **no modified files** and **no untracked files** (such as temporary `pr_body.md` files).

---

## 4. Coding & Architecture Standards

### 1. OGS Website Core Architectural Rules
* **Zero External Dependencies:** Pure HTML5, CSS3, and vanilla JavaScript. No frontend frameworks, build tools, or external runtime libraries.
* **Privacy-First & Self-Hosted Assets:** No external font CDNs (`fonts.googleapis.com`), CSS CDNs, analytics, or telemetry scripts. All fonts (`assets/fonts/*.woff2`) and images (`assets/images/*.png`) must live inside the repository.
* **Offline Fallback Resilience:** `tools/index.html` must always contain a complete static HTML tool catalog inside `<section class="catalog" ... data-catalog>` so users viewing the site offline or without JavaScript see the full catalog.
* **Safe DOM Construction:** Never use `.innerHTML`, `outerHTML`, or `insertAdjacentHTML` when rendering data from `repository.json`. Always use `document.createElement()` and `.textContent`.
* **External Link Hardening:** Every external link (`http://` or `https://`) with `target="_blank"` must include `rel="noopener noreferrer"`.

### 2. HTML5, CSS3 & Accessibility Standards
1. **Document Metadata & Landmarks:** Every HTML page must have `<!DOCTYPE html>`, `<html lang="en">`, `<meta charset="UTF-8">`, `<meta name="viewport" content="width=device-width, initial-scale=1.0">`, non-empty `<meta name="description">`, `<title>`, `<header class="site-header">`, `<main class="container" id="main">`, and `<footer class="site-footer">`.
2. **Image Accessibility:** Every `<img>` element must have a descriptive, non-empty `alt` attribute.
3. **Shared Stylesheet (`assets/css/site.css`):** Use `:root` CSS custom properties (`--primary`, `--bg-dark`, `--card-bg`, `--text-main`, `--text-muted`) and keep responsive rules aligned with the `850px` and `768px` media queries and `prefers-reduced-motion: reduce`.

---

## 5. Automated Validation Standards (`tests/validate_site.py`)

Every change must be verified with the zero-dependency Python validation suite in `tests/validate_site.py`.

### Running Automated Validation
From inside your worktree directory (`.worktrees/issue-<number>`):
```powershell
python tests/validate_site.py
```

### Verification Gate
* **Zero Failures:** All existing and newly added checks must pass (`tests failed: 0`, exit code `0`).
* When adding new pages, assets, or catalog requirements, add corresponding assertions in `tests/validate_site.py`.

---

## 6. Submitting the Pull Request

Once the fix is implemented, validated, and committed with a clean working tree:

### 1. Push Feature Branch
```powershell
git push -u origin HEAD
```

### 2. Create the Pull Request
Submit the PR targeting `main` using the GitHub CLI. Write the PR description to `pr_body.md`, pass `--body-file`, and immediately remove `pr_body.md`:

```powershell
gh pr create --title "<type>: <concise description> (Resolves #<number>)" --body-file pr_body.md --base main
Remove-Item -Path pr_body.md -Force -ErrorAction SilentlyContinue
```

### Required PR Body Structure
Every PR submitted by an Issue Resolver must follow `.github/pull_request_template.md` and include:
1. **Closes / Resolves Link:** `Resolves #<number>`
2. **Summary & Context:** Summary of the issue being addressed and design rationale.
3. **Key Changes & Technical Scope:** Detailed breakdown of modified, added, or deleted files.
4. **Automated Validation & Verification:** Confirmation of `python tests/validate_site.py` execution (`tests passed: X, tests failed: 0`).
5. **Handoff for PR Reviewer & Documentation Agent:**
   * Specific updates needed for `docs/TESTING.md` or `docs/MANUAL_TESTING.md`.
   * Any `README.md` updates if repository structure, pages, or workflows changed.

### 3. Stop and Stand Down
After opening the PR:
* **Do not merge the pull request.**
* **Do not delete the worktree yet** (the PR Reviewer agent will reuse `.worktrees/issue-<number>` to run validation checks and commit documentation updates, and will remove the worktree upon merge).
* Report the PR URL and summary back to the orchestrator or user.
