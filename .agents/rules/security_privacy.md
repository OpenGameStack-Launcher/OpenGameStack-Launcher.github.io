# Security, Privacy & Zero-Dependency Enforcement

**CRITICAL DIRECTIVES FOR ALL AGENTS:**

1. **ZERO EXTERNAL TRACKING, ANALYTICS, OR THIRD-PARTY CDNS**:
   - `opengamestack.org` is a privacy-first, sovereign web property. Never add analytics scripts, tracking pixels, telemetry beacons, or third-party embeds.
   - Never link to external font or CSS/JS CDNs (`fonts.googleapis.com`, `fonts.gstatic.com`, `unpkg.com`, `jsdelivr.net`, `cdnjs.cloudflare.com`). All fonts (`assets/fonts/*.woff2`) and stylesheets (`assets/css/site.css`) must remain self-hosted in this repository.

2. **SAFE DOM CONSTRUCTION & UNTRUSTED JSON HANDLING**:
   - Treat external JSON catalogs (such as `repository.json` fetched in `tools/index.html`) as untrusted input.
   - Validate the schema and field types before rendering (`isValidCatalog()`).
   - Construct DOM nodes exclusively with `document.createElement()` and populate text with `.textContent`. Never use `.innerHTML`, `outerHTML`, `insertAdjacentHTML`, or `eval()`.

3. **EXTERNAL LINK HARDENING**:
   - Every external anchor tag (`href` starting with `http://` or `https://`) that opens in a new tab (`target="_blank"`) MUST include `rel="noopener noreferrer"`.

4. **OFFLINE-RESILIENT PROGRESSIVE ENHANCEMENT**:
   - Every page must remain usable and complete when viewed offline (`file://` or local HTTP server without internet access) or with JavaScript disabled.
   - Never remove the static HTML tool catalog fallback inside `tools/index.html`.

5. **NEVER COMMIT SECRETS OR LOCAL ENVIRONMENT ARTIFACTS**:
   - Never commit API tokens, credentials, `.venv/` files, `.worktrees/`, or personal filesystem paths to the repository.
   - Preserve `CNAME` (`opengamestack.org`) at the repository root so GitHub Pages custom domain routing is never disrupted.
