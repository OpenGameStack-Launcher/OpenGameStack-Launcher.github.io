# Pull Request Review and Merge Workflow

When reviewing and merging Pull Requests in `OpenGameStack-Launcher.github.io`, adhere to the canonical standards in [docs/REVIEWING_AND_MERGING_PRS.md](../../docs/REVIEWING_AND_MERGING_PRS.md) and `.agents/skills/code-review/SKILL.md`.

## 1. Discovery and Inspection
- Fetch open PRs using `gh pr list --state open`.
- **CRITICAL:** Never run a bare `gh pr view <ID>` command without `--json` (to avoid `read:project` token scope errors). Always inspect PR metadata and diffs using:
  ```powershell
  gh pr view <PR_ID> --json number,title,body,state,baseRefName,headRefName,commits,files
  gh pr diff <PR_ID>
  ```
- Audit the changes against:
  - **Acceptance Criteria & Dependencies:** All issue checklist items met; any `Depends on #X` issues closed and merged.
  - **OGS Website Standards:** Semantic HTML5, shared CSS tokens in `assets/css/site.css`, zero external dependencies/CDNs/trackers, `rel="noopener noreferrer"` on external `target="_blank"` links, non-empty `alt` text on images, safe DOM construction (`textContent` instead of `innerHTML`), and static fallback parity in `pages/tools.html`.
  - **Test Coverage:** Adequate validation checks in `tests/validate_site.py`.

## 2. Worktree Reuse or Creation
- First check if the resolver's worktree already exists locally (e.g., `.worktrees/issue-<issue_number>` or `.worktrees/<headRefName>`).
  - **If it exists locally:** Perform your review, test execution, and documentation commits directly inside that existing worktree so you do not orphan it.
  - **If it does not exist locally:** Fetch the branch and create `.worktrees/review-pr-<PR_ID>`:
    ```powershell
    git fetch origin
    git worktree add .worktrees/review-pr-<PR_ID> <headRefName>
    ```

## 3. Independent Validation Execution
- Inside the worktree, run the automated static site validator:
  ```powershell
  python tests/validate_site.py
  ```
- Confirm 0 failures (`tests failed: 0`, exit code `0`).

## 4. Documentation Coordination & Fixes (Prior to Merge)
- As the **Documentation Steward**, review the PR's "Handoff for PR Reviewer & Documentation Agent" section and synchronize `docs/TESTING.md`, `docs/MANUAL_TESTING.md`, and `README.md` as needed.
- If the PR needs documentation updates or minor review fixes, apply them inside the worktree, re-run `python tests/validate_site.py`, verify `git status` is clean, commit, and push to the PR branch:
  ```powershell
  git add -A
  git commit -m "docs: synchronize documentation and review updates for PR #<PR_ID>"
  git push origin HEAD:<headRefName>
  ```

## 5. Safe Merge and Complete Cleanup
Once validation checks pass and documentation is pushed:
1. Dispatch and monitor the manual CI pre-merge gate against the feature branch:
   ```powershell
   gh workflow run ci.yml --ref <headRefName>
   $runId = gh run list --workflow=ci.yml --branch <headRefName> --event workflow_dispatch --limit 1 --json databaseId --jq ".[0].databaseId"
   gh run watch $runId --exit-status
   ```
   Confirm the run exits with status code 0 before proceeding.
2. Return to the repository root:
   ```powershell
   Set-Location "C:\Projects\OpenGameStack-Launcher.github.io"
   ```
3. Remove any local worktrees for this issue/PR and prune worktree metadata:
   ```powershell
   git worktree remove .worktrees/issue-<issue_number> --force -ErrorAction SilentlyContinue
   git worktree remove .worktrees/review-pr-<PR_ID> --force -ErrorAction SilentlyContinue
   if (Test-Path ".worktrees/issue-<issue_number>") { Remove-Item -Path ".worktrees/issue-<issue_number>" -Recurse -Force -ErrorAction SilentlyContinue }
   if (Test-Path ".worktrees/review-pr-<PR_ID>") { Remove-Item -Path ".worktrees/review-pr-<PR_ID>" -Recurse -Force -ErrorAction SilentlyContinue }
   git worktree prune
   ```
4. Merge the PR using a standard merge commit (never squash or rebase):
   ```powershell
   gh pr merge <PR_ID> --merge --delete-branch
   ```
5. Synchronize `main`, delete the local feature branch, run `python tests/validate_site.py` on `main`, and confirm the issue is closed:
   ```powershell
   git checkout main
   git pull origin main
   git branch -D <headRefName> -ErrorAction SilentlyContinue
   python tests/validate_site.py
   ```
