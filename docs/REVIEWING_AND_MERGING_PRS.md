# Pull Request Review, Documentation & Merge Standards

This document establishes the official standards and workflow for reviewing, documenting, and merging Pull Requests in the **Open Game Stack Website** repository (`OpenGameStack-Launcher.github.io`), whether handled by a human developer or an autonomous agent.

---

## 1. Role Overview & Responsibilities

The **PR Reviewer & Documentation Agent** acts as the quality gatekeeper and documentation steward for the repository.

### Primary Responsibilities
1. **Review Diff & Context:** Inspect the Pull Request description, code diff, and automated validation results provided by the Issue Resolver.
2. **Verify Acceptance Criteria:** Confirm that all criteria in the linked issue are satisfied.
3. **Verify Architecture, Privacy & Web Standards:** Audit the diff against semantic HTML5, shared CSS tokens in `assets/css/site.css`, zero external dependencies/CDNs/trackers, `rel="noopener noreferrer"`, image `alt` text, safe DOM methods (`textContent`), and offline fallback resilience (see `.agents/skills/code-review/SKILL.md`).
4. **Independent Validation Execution:** Run `python tests/validate_site.py` inside the worktree and confirm zero failures (`tests failed: 0`).
5. **Synchronize Documentation:** Update `docs/TESTING.md`, `docs/MANUAL_TESTING.md`, and `README.md` as appropriate on the feature branch prior to merge.
6. **Pre-Merge CI Verification Gate:** Manually dispatch the CI workflow (`ci.yml`) on `<headRefName>`, monitor execution to completion, and gate merge approval on exit code 0.
7. **Merge to Main & Clean Up:** Perform a standard Git merge commit (`--merge --delete-branch`), remove all local worktrees for the issue/PR, prune worktrees, and synchronize local `main`.

---

## 2. Review Checklist

Before approving or merging any Pull Request, verify the following:

### 1. Pre-Review & Dependency Check
* [ ] **Dependencies Resolved:** If the linked issue or PR mentions `Depends on #<number>`, confirm that all dependency issues are `CLOSED` and their PRs are already merged into `main`.
* [ ] **Reviewer Handoff Notes:** Check the PR description's **"Handoff for PR Reviewer & Documentation Agent"** section for specific documentation and testing notes provided by the resolver.

### 2. Code Quality, Architecture & Privacy
* [ ] **Zero External Dependencies & Trackers:** No external font CDNs (`fonts.googleapis.com`), JS/CSS CDNs, or analytics/telemetry scripts. All assets are self-hosted.
* [ ] **Semantic HTML5 & Landmarks:** All pages preserve `<!DOCTYPE html>`, `<html lang="en">`, `<meta charset="UTF-8">`, `<meta name="viewport">`, `<meta name="description">`, `<title>`, `<header class="site-header">`, `<main id="main">`, and `<footer class="site-footer">`.
* [ ] **Accessibility & Link Security:** Every `<img>` has a non-empty `alt` attribute; every external `target="_blank"` link includes `rel="noopener noreferrer"`.
* [ ] **Safe DOM & Offline Fallback:** Inline JS uses `document.createElement()` and `.textContent` (never `.innerHTML`), and `pages/tools.html` preserves a complete static HTML tool catalog fallback.
* [ ] **Cross-Repo Accuracy:** Release links/notes in `index.html` and catalog items in `pages/tools.html` match `ogs-launcher` and `ogs-frozen-stacks/repository.json`.

### 3. Validation Verification
* [ ] **Automated Validation Report:** PR body includes evidence that `python tests/validate_site.py` passes (`tests passed: X`, `tests failed: 0`).
* [ ] **Independent Validation Execution:** Reviewer independently runs `python tests/validate_site.py` on the branch and confirms 0 failures.
* [ ] **Pre-Merge Manual CI Verification:** Dispatch CI workflow on the feature branch (`gh workflow run ci.yml --ref <headRefName>`), monitor with `gh run watch <run_id> --exit-status`, and confirm exit status 0 before merging.

---

## 3. PR Inspection & Local Validation Protocol

All review operations, including inspecting code, running validation scripts, and committing documentation updates, must take place within an isolated Git worktree under `.worktrees/`.

### 1. View PR Overview & Diff
Inspect the PR description and diff via the GitHub CLI:

> [!WARNING]
> **NEVER run a bare `gh pr view <pr_number>` command.** Repository token configurations can trigger a `read:project` scope error for the bare command. You must ALWAYS use the `--json` flag:

```powershell
Set-Location "C:\Projects\OpenGameStack-Launcher.github.io"
gh pr view <pr_number> --json number,title,body,state,baseRefName,headRefName,commits,files
gh pr diff <pr_number>
```

### 2. Access or Create the Review Worktree
Determine whether a local worktree for this feature branch already exists (created by the Issue Resolver):
* **If the resolver's worktree already exists locally** (e.g., at `.worktrees/issue-<issue_number>` or `.worktrees/<headRefName>`):
  Perform your review, validation, and documentation commits directly inside that existing worktree directory so you do not create duplicate worktrees or orphan the resolver's worktree.
* **If no worktree exists locally for the branch**:
  Fetch the branch and create a dedicated review worktree:
  ```powershell
  git fetch origin
  git worktree add .worktrees/review-pr-<pr_number> <headRefName>
  ```

### 3. Run Automated Validation Locally
Inside the worktree, run the site validation script:
```powershell
python tests/validate_site.py
```

---

## 4. Documentation Coordination (Mandatory Prior to Merge)

The reviewing agent is the documentation steward and is responsible for synchronizing project documentation with website changes before merging.

### 1. Check Documentation Targets
* **`docs/TESTING.md`:** Update automated check descriptions when new validation rules are added to `tests/validate_site.py`.
* **`docs/MANUAL_TESTING.md`:** Add or update manual browser verification steps when pages, navigation, or catalog interactions change.
* **`README.md`:** Update if repository structure, pages, or local preview instructions changed.

### 2. Commit Documentation Updates (If Needed)
If documentation updates or minor review fixes are needed, commit them directly to the feature branch **prior to merging**:
```powershell
git add -A
git commit -m "docs: synchronize documentation for PR #<pr_number>"
git push origin HEAD:<headRefName>
```
Always run `git status` to verify the worktree is completely clean before proceeding to merge.

---

## 5. Review Decisions & Safe Merge Protocol

### Scenario A: Blocking Changes Required
If the PR fails `python tests/validate_site.py`, violates zero-dependency/privacy rules, or misses core acceptance criteria that require substantial rework by the resolver, **do not merge**. Submit a review requesting changes:
```powershell
gh pr review <pr_number> --request-changes --body "<Detailed description of what needs to be fixed>"
```

### Scenario B: Approved & Ready to Merge
Once all acceptance criteria are met, automated validation passes with 0 failures, and documentation is synchronized on the feature branch, proceed to merge.

#### 1. Pre-Merge Manual CI Verification Gate
After all documentation updates and review commits are pushed to `<headRefName>`, dispatch the CI workflow against the feature branch:
```powershell
Set-Location "C:\Projects\OpenGameStack-Launcher.github.io"
gh workflow run ci.yml --ref <headRefName>
```

Retrieve the workflow run ID and watch execution to completion:
```powershell
$runId = gh run list --workflow=ci.yml --branch <headRefName> --event workflow_dispatch --limit 1 --json databaseId --jq ".[0].databaseId"
gh run watch $runId --exit-status
```

> [!IMPORTANT]
> The PR may ONLY be merged if the dispatched CI workflow run exits with status code 0 (`tests failed: 0`). If CI fails, investigate failures, push fixes to `<headRefName>`, and re-dispatch.

#### 2. Remove Worktrees Before Merging
Return to the repository root (`C:\Projects\OpenGameStack-Launcher.github.io`) and remove any worktrees associated with the issue or PR:

```powershell
Set-Location "C:\Projects\OpenGameStack-Launcher.github.io"

git worktree remove .worktrees/issue-<issue_number> --force -ErrorAction SilentlyContinue
git worktree remove .worktrees/review-pr-<pr_number> --force -ErrorAction SilentlyContinue

if (Test-Path ".worktrees/issue-<issue_number>") {
    Remove-Item -Path ".worktrees/issue-<issue_number>" -Recurse -Force -ErrorAction SilentlyContinue
}
if (Test-Path ".worktrees/review-pr-<pr_number>") {
    Remove-Item -Path ".worktrees/review-pr-<pr_number>" -Recurse -Force -ErrorAction SilentlyContinue
}

git worktree prune
```

#### 3. Merge the Pull Request
Merge using the GitHub CLI with a **standard merge commit** (preserving complete Git history) and delete the remote branch:
```powershell
gh pr merge <pr_number> --merge --delete-branch
```
> [!IMPORTANT]
> **DO NOT squash** (`--squash`) or rebase (`--rebase`). Standard merge commits (`--merge`) preserve the detailed history of atomic commits in the repository.

#### 4. Verify Issue Closure
Confirm that the linked issue (`Resolves #<issue_number>`) has transitioned to `CLOSED`:
```powershell
gh issue view <issue_number> --json state
```
If GitHub did not automatically close the issue, close it explicitly:
```powershell
gh issue close <issue_number> --comment "Resolved and merged via PR #<pr_number>."
```

#### 5. Local Repository Synchronization & Branch Cleanup
From the main project directory (`C:\Projects\OpenGameStack-Launcher.github.io`):
```powershell
git checkout main
git pull origin main
git branch -D <headRefName> -ErrorAction SilentlyContinue
python tests/validate_site.py
```
