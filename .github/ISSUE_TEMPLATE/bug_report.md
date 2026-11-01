---
name: Bug report
about: Report a broken link, outdated release/catalog entry, layout glitch, or accessibility issue
title: ''
labels: 'bug'
assignees: ''
---

<!-- Include if blocked by prior work: **Depends on #<issue_number>** -->

### 1. Problem & Context
A concise explanation of the problem, reproduction steps, observed behavior, and expected behavior.

**Reproduction Steps:**
1. 
2. 
3. 

**Observed Behavior:**
<!-- What actually happened -->

**Expected Behavior:**
<!-- What should have happened per AGENTS.md or cross-repo state -->

### 2. Technical Scope & Affected Files
Direct references to HTML, CSS, asset, or validation files that need modification or investigation:
- `index.html` or `<directory>/index.html` (e.g., `mission/index.html`, `tools/index.html`, `examples/index.html`)
- `assets/css/site.css` or `assets/images/<asset_name>.png`
- `tests/validate_site.py`

### 3. Acceptance Criteria

#### [Page / Component Fix Area]
- [ ] Describe the expected behavior or fix
- [ ] Preserve zero external dependencies, self-hosted assets, `rel="noopener noreferrer"` on external `target="_blank"` links, and safe DOM rendering (`textContent`)

#### Automated Validation (`tests/validate_site.py`)
- [ ] Add or update validation checks in `tests/validate_site.py` verifying the fix.
- [ ] Ensure `python tests/validate_site.py` passes with zero failures (`tests failed: 0`).

#### Documentation Coordination (Mandatory per docs/REVIEWING_AND_MERGING_PRS.md)
- [ ] Update `docs/TESTING.md` and/or `docs/MANUAL_TESTING.md` with regression test cases if applicable.
- [ ] Update `README.md` if repository structure, pages, or user-facing instructions were modified.
