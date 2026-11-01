# Git Workflow Rules

When working on `OpenGameStack-Launcher.github.io`, you MUST follow these Git workflow rules to prevent merge conflicts, file locks, and orphaned branches:

1. **Use Git Worktrees (Never Work Directly on `main`)**:
   - Instead of checking out feature or fix branches directly in the main repository root (`C:\Projects\OpenGameStack-Launcher.github.io`), **ALWAYS** use isolated Git worktrees inside `.worktrees/`.
   - First, fetch the latest remote changes:
     ```powershell
     git fetch origin
     ```
   - Create your worktree based on `origin/main`:
     - For resolving an issue:
       ```powershell
       git worktree add .worktrees/issue-<number> -b fix/issue-<number>-<short-description> origin/main
       ```
       *(Use `feature/issue-<number>-<short-description>` for enhancements or new pages/sections).*
     - For reviewing a remote PR when `.worktrees/issue-<number>` does not already exist locally:
       ```powershell
       git worktree add .worktrees/review-pr-<pr_number> <remote-branch-name>
       ```
   - Run all commands (validation scripts, local previews, commits) inside that worktree directory.

2. **Clean Working Tree Check**:
   - After running `git commit` and BEFORE pushing or creating a Pull Request, you **MUST** run `git status` inside the worktree.
   - Ensure there are **no modified files** and **no untracked files** remaining.
   - Delete any temporary scratch files (such as `issue_body.md`, `pr_body.md`, or temporary screenshots) before finishing.

3. **Complete Worktree & Branch Cleanup**:
   - Worktrees and temporary local branches must never be left lingering after a PR is merged or a task is finished.
   - Return to the repository root (`Set-Location "C:\Projects\OpenGameStack-Launcher.github.io"`), remove both the issue worktree and any review worktree, prune git worktree metadata, and delete the local feature branch:
     ```powershell
     git worktree remove .worktrees/issue-<number> --force -ErrorAction SilentlyContinue
     git worktree remove .worktrees/review-pr-<pr_number> --force -ErrorAction SilentlyContinue
     if (Test-Path ".worktrees/issue-<number>") { Remove-Item -Path ".worktrees/issue-<number>" -Recurse -Force -ErrorAction SilentlyContinue }
     if (Test-Path ".worktrees/review-pr-<pr_number>") { Remove-Item -Path ".worktrees/review-pr-<pr_number>" -Recurse -Force -ErrorAction SilentlyContinue }
     git worktree prune
     git checkout main
     git pull origin main
     git branch -D <branch-name> -ErrorAction SilentlyContinue
     ```
