# Manual Testing & Visual QA Guide

This guide covers manual browser verification and visual quality assurance for the **Open Game Stack Website** (`OpenGameStack-Launcher.github.io`).

---

## 1. Starting a Local Preview Server

While static pages can be opened directly from disk, serving the repository over a local HTTP server accurately mirrors GitHub Pages path resolution and CORS behavior:

```powershell
Set-Location "C:\Projects\OpenGameStack-Launcher.github.io"
python -m http.server 8000 --bind 127.0.0.1
```

Open `http://127.0.0.1:8000` in your browser. When finished, stop the server (`Ctrl+C` or terminate the background task).

---

## 2. Page-by-Page Verification Checklist

### 1. Landing Page (`index.html`)
- [ ] **Header & Navigation:** Sticky glassmorphism header remains pinned on scroll; `Home`, `Manifesto`, `Tools`, and `Examples` links navigate cleanly.
- [ ] **Skip Link:** Pressing `Tab` on initial page load reveals the `Skip to content` button and focuses `#main` when activated.
- [ ] **Hero Actions & Release Panel:**
  - Primary download button (`Download Alpha ...`) and `Get Alpha ... Package` button in `#alpha-download` point to a valid, published GitHub Release asset in `OpenGameStack-Launcher/ogs-launcher`.
  - `View on GitHub` opens `https://github.com/OpenGameStack-Launcher/ogs-launcher` in a new tab.
  - `Read the Manifesto` and `Browse Frozen Tools` navigate to `pages/manifesto.html` and `pages/tools.html`.
- [ ] **Feature Cards:** The three audience cards (`For Indie Developers`, `For Studios`, `For Defense & Enterprise`) render in a 3-column grid on desktop and stack into a single column on narrow viewports (`<= 768px`).

### 2. Manifesto Page (`pages/manifesto.html`)
- [ ] **Two-Column Layout:** On desktop (`> 850px`), the manifesto article appears on the left and the sticky `Sections` sidebar index appears on the right.
- [ ] **Section Anchors:** Clicking `Sovereignty Over Subscription`, `The Environment is the Artifact`, `Dual-Use by Design`, and `Stability is a Feature` smoothly scrolls to `#sovereignty`, `#environment`, `#dual-use`, and `#stability`.
- [ ] **Responsive Collapse:** At `<= 850px`, the layout collapses cleanly into a single column with the section index below the article.

### 3. Tool Catalog Page (`pages/tools.html`)
- [ ] **Dynamic Catalog Hydration:** With network access enabled, `pages/tools.html` fetches `https://raw.githubusercontent.com/OpenGameStack-Launcher/ogs-frozen-stacks/main/repository.json` and renders categories, tool icons/monograms, descriptions, version tags, `Official release page` links, and `Frozen archive` download links.
- [ ] **Offline / No-JS Fallback:** With network access blocked (or JavaScript disabled in browser DevTools), `pages/tools.html` displays the static HTML tool catalog inside `[data-catalog]` without broken images or empty containers.

### 4. Examples Page (`examples/index.html`)
- [ ] **Reference Projects:** `Sudoku` and `Letter Logic` sections render clearly with working `Source Code` and `Play Online` external links.

---

## 3. Cross-Cutting Visual & Accessibility Checks

- [ ] **Self-Hosted Typography:** Open browser DevTools -> Network tab and confirm `font-01.woff2` through `font-10.woff2` load from local `/assets/fonts/` with **zero** outbound requests to `fonts.googleapis.com` or `fonts.gstatic.com`.
- [ ] **Responsive Breakpoints:** Resize viewport across `1280px` (desktop), `800px` (tablet), and `375px` (mobile) and confirm no horizontal scrollbar (`overflow-x`), text clipping, or overlapping buttons.
- [ ] **Reduced Motion:** Emulate `prefers-reduced-motion: reduce` in DevTools and verify background pulse animations and hover transforms are disabled.
