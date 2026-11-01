# GitHub Issue Creation Standard & Guidelines

This document outlines the standard specifications, structure, and workflow for creating GitHub issues for the **Open Game Stack Website** repository (`OpenGameStack-Launcher.github.io`). Adhering to these standards ensures that any contributor, human developer or autonomous agent, can pick up an issue, understand the context and requirements without ambiguity, implement the change, and properly verify their work.

---

## 1. Principles & Quality Bar

Every issue created in this repository must meet the following criteria:
1. **Self-Contained & Actionable:** Provide all necessary context, design decisions, and acceptance criteria. A contributor should never have to guess design intent or search for unlinked resources.
2. **Clear Boundaries:** Group requirements logically by affected pages or components (for example, Landing Page `index.html`, Manifesto `pages/manifesto.html`, Tool Catalog `pages/tools.html`, Examples `examples/index.html`, Shared Styles `assets/css/site.css`, Automated Validation `tests/validate_site.py`, Documentation).
3. **Traceability:** Explicitly list any dependencies (`Depends on #<issue_number>`) and note which documentation files need to be synchronized as part of the implementation.
4. **No Duplicates:** Always search open and closed issues (`gh issue list --state all`) before submitting a new issue.

---

## 2. Standard Issue Structure

All issues filed in `OpenGameStack-Launcher.github.io` must follow this standardized layout. When creating an issue on GitHub, use one of the predefined templates in `.github/ISSUE_TEMPLATE/`:
* **Bug Report (`.github/ISSUE_TEMPLATE/bug_report.md`):** For broken links, outdated release or tool catalog metadata, layout glitches, accessibility defects, or validation failures. Pre-labeled with `bug`.
* **Feature Request (`.github/ISSUE_TEMPLATE/feature_request.md`):** For new pages, sections, visual improvements, cross-repo synchronization enhancements, or validation checks. Pre-labeled with `enhancement`.

Both templates implement the following required markdown structure:

```markdown
**Depends on #<issue_number>** (Include only if this issue has blockers)

### 1. Problem & Context
A concise explanation of the problem, bug, cross-repo sync update, or feature request.
- For bugs: Reproduction steps, observed behavior, and expected behavior.
- For features/enhancements: User story, design motivation, and how the change aligns with OGS sovereignty and zero-dependency web principles.

### 2. Technical Scope & Affected Files
Direct references to the HTML, CSS, asset, or test files that need modification or inspection:
- `index.html` or `pages/<page_name>.html` or `examples/index.html`
- `assets/css/site.css` or `assets/images/<asset_name>.png`
- `tests/validate_site.py`

### 3. Acceptance Criteria
Checklist grouped by page or component responsibility:

#### [Page / Component Area 1]
- [ ] Explicit requirement 1
- [ ] Explicit requirement 2

#### [Page / Component Area 2]
- [ ] Explicit requirement 3

#### Automated Validation & Visual QA (`tests/validate_site.py`)
- [ ] Add or update validation checks in `tests/validate_site.py` if new pages, structural elements, or catalog invariants are introduced.
- [ ] Ensure `python tests/validate_site.py` passes with zero failures (`tests failed: 0`).
- [ ] Verify layout and responsive behavior across desktop and mobile breakpoints (`850px`, `768px`).

#### Documentation Coordination (Mandatory per docs/REVIEWING_AND_MERGING_PRS.md)
- [ ] Update `docs/TESTING.md` and/or `docs/MANUAL_TESTING.md` if new automated checks or manual verification steps were added.
- [ ] Update `README.md` if repository structure, pages, or contributor instructions changed.
```

---

## 3. Title & Labeling Conventions

### Title Format
Titles must be concise and use standard prefixes to indicate the area of the website:
- `Home - <Action/Description>` (e.g., `Home - Update Alpha Download Links to v0.2.0 and Godot 4.7.2`)
- `Tools - <Action/Description>` (e.g., `Tools - Synchronize Static Catalog and Code Category with ogs-frozen-stacks`)
- `Manifesto - <Action/Description>` (e.g., `Manifesto - Add Skip Link Landmark to Manifesto Page`)
- `Examples - <Action/Description>` (e.g., `Examples - Add Project Card Styling for Reference Games`)
- `Design - <Action/Description>` (e.g., `Design - Improve Mobile Header Navigation Spacing`)
- `Sync - <Action/Description>` (e.g., `Sync - Align Project Manifest Filename References with ogs_stack.json`)
- `Tests - <Action/Description>` (e.g., `Tests - Verify Tool Catalog Static Fallback Parity in validate_site.py`)
- `Docs - <Action/Description>` (e.g., `Docs - Update README Clone URL and Repository Structure`)

Conventional commit prefixes (`feat:`, `fix:`, `refactor:`, `docs:`) are also acceptable.

### Labels
Apply at least one standard GitHub label when creating the issue:
- **Primary Category:** `bug`, `enhancement`, `documentation`, `good first issue`, `help wanted`, `audit`
- **Severity (Optional / Audit):** `severity: critical`, `severity: high`, `severity: medium`, `severity: low`
- **Technical Type (Optional):** `type: catalog-sync`, `type: design-css`, `type: accessibility`, `type: security-privacy`

---

## 4. Pre-Creation Checklist (For Authors & Agents)

Before publishing an issue via GitHub:
1. [ ] **Search Existing Issues:** Run `gh issue list --state all --limit 100` inside `C:\Projects\OpenGameStack-Launcher.github.io` to confirm the issue does not already exist or duplicate past work.
2. [ ] **Inspect Codebase & Sibling Repos:** Verify the exact file paths (`index.html`, `pages/...`, `assets/...`, `tests/validate_site.py`), CSS class names, and current state in `C:\Projects\ogs-frozen-stacks\repository.json` or `C:\Projects\ogs-launcher` when logging cross-repo synchronization issues.
3. [ ] **Clarify Design Choices:** Resolve any open design questions before publishing so the issue body contains firm decisions rather than open questions.
4. [ ] **Zero-Dependency & Privacy Guardrails:** Ensure acceptance criteria preserve self-hosted assets, `rel="noopener noreferrer"` on external `target="_blank"` links, safe DOM construction (`textContent`), and offline fallback resilience.
5. [ ] **Include Documentation Acceptance Criteria:** Ensure the mandatory documentation coordination checklist is included per `docs/REVIEWING_AND_MERGING_PRS.md`.

---

## 5. Creating Issues via GitHub CLI

Contributors and agents can create issues directly from the command line using the GitHub CLI (`gh`).

### Option A: Using Predefined Templates
You can invoke the repository issue templates directly with the `--template` flag:
```powershell
Set-Location "C:\Projects\OpenGameStack-Launcher.github.io"
gh issue create --template "bug_report.md"
gh issue create --template "feature_request.md" --title "Tools - Synchronize Catalog with ogs-frozen-stacks"
```

### Option B: Scripted / Headless Creation (Recommended for Agents)
When generating an issue programmatically, an `issue_creator` agent is spun up to create **exactly one** issue per run and is shut down immediately afterward (if multiple issues need to be logged, the orchestrator spawns a separate `issue_creator` agent sequentially for each individual issue). Write the formatted markdown body to a temporary file (`issue_body.md`), create the single issue with `--body-file`, and remove the temporary file right after:

```powershell
Set-Location "C:\Projects\OpenGameStack-Launcher.github.io"
# After writing issue_body.md with native file tools:
gh issue create --title "<Prefix> - <Short Summary>" --body-file issue_body.md --label "<bug|enhancement>"
Remove-Item -Path issue_body.md -Force -ErrorAction SilentlyContinue
```
