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
- [ ] **Header & Navigation:** Sticky glassmorphism header remains pinned on scroll; `Home`, `Manifesto`, `Tools`, and `Examples` links navigate cleanly using clean directory URLs (`./`, `manifesto/`, `tools/`, `examples/`).
- [ ] **Skip Link:** Pressing `Tab` on initial page load reveals the `Skip to content` button and focuses `#main` when activated.
- [ ] **Hero Actions & Release Panel:**
  - Primary download button (`Download v0.2.0`) and `Get v0.2.0 Package` button in `#alpha-download` point to `https://github.com/OpenGameStack-Launcher/ogs-launcher/releases/download/v0.2.0/OGS-Launcher-win64-0.2.0.zip`.
  - Engine target note states: `Current target: Windows 10/11 (x64), built with Godot 4.7.2.`.
  - Manifest and configuration references in the release panel list canonical `ogs_stack.json` and `ogs_config.json`.
  - `View on GitHub` opens `https://github.com/OpenGameStack-Launcher/ogs-launcher` in a new tab with `rel="noopener noreferrer"`.
  - `Read the Manifesto` and `Browse Frozen Tools` navigate to `manifesto/` and `tools/` using clean directory URLs without `.html` extensions.
- [ ] **Feature Cards:** The three audience cards (`For Indie Developers`, `For Studios`, `For Defense & Enterprise`) render in a 3-column grid on desktop and stack into a single column on narrow viewports (`<= 768px`).

### 2. Manifesto Page (`manifesto/index.html` -> `/manifesto/`)
- [ ] **Skip Link:** Pressing `Tab` on initial page load reveals the `Skip to content` link and moves focus to `#main` when activated.
- [ ] **Two-Column Layout:** On desktop (`> 850px`), the manifesto article appears on the left and the sticky `Sections` sidebar index appears on the right.
- [ ] **Section Anchors:** Clicking `Sovereignty Over Subscription`, `The Environment is the Artifact`, `Dual-Use by Design`, and `Stability is a Feature` smoothly scrolls to `#sovereignty`, `#environment`, `#dual-use`, and `#stability`.
- [ ] **Responsive Collapse:** At `<= 850px`, the layout collapses cleanly into a single column with the section index below the article.

### 3. Tool Catalog Page (`tools/index.html` -> `/tools/`)
- [ ] **Skip Link:** Pressing `Tab` on initial page load reveals the `Skip to content` link and moves focus to `#main` when activated.
- [ ] **Dynamic Catalog Hydration:** With network access enabled, `tools/index.html` fetches `https://raw.githubusercontent.com/OpenGameStack-Launcher/ogs-frozen-stacks/main/repository.json` and renders 5 categories (`Engine`, `2D`, `3D`, `Audio`, `Code`), 7 tools (`godot`, `gimp`, `krita`, `blender`, `audacity`, `git`, `vscodium`), descriptions, version tags in descending order, `Official release page` links, and `Frozen archive` download links. Verify that all 7 tools, including Git and VSCodium, display crisp PNG logos (140x140 px on desktop, 100x100 px on mobile).
- [ ] **Offline / No-JS Fallback:** With network access blocked (or JavaScript disabled in browser DevTools), `tools/index.html` displays the static HTML tool catalog inside `[data-catalog]` containing all 7 tools across 5 categories in descending version order, rendering their official PNG logos rather than circular text monogram marks, and without broken images or empty containers.

### 4. Examples Page (`examples/index.html` -> `/examples/`)
- [ ] **Skip Link:** Pressing `Tab` on initial page load reveals the `Skip to content` link and moves focus to `#main` when activated.
- [ ] **Reference Projects:** `Sudoku` and `Letter Logic` sections render clearly with working `Source Code` and `Play Online` external links.

---

## 3. Cross-Cutting Visual & Accessibility Checks

- [ ] **Self-Hosted Typography:** Open browser DevTools -> Network tab and confirm `font-01.woff2` through `font-10.woff2` load from local `/assets/fonts/` with **zero** outbound requests to `fonts.googleapis.com` or `fonts.gstatic.com`.
- [ ] **Clean Directory URLs:** Navigate across `Home`, `Manifesto`, `Tools`, and `Examples`. Confirm the browser URL bar displays clean directory URLs (`/`, `/manifesto/`, `/tools/`, `/examples/`) without appending `.html` extensions or exposing legacy `/pages/` directory segments.
- [ ] **Responsive Breakpoints:** Resize viewport across `1280px` (desktop), `800px` (tablet), and `375px` (mobile) and confirm no horizontal scrollbar (`overflow-x`), text clipping, or overlapping buttons.
- [ ] **Reduced Motion:** Emulate `prefers-reduced-motion: reduce` in DevTools and verify background pulse animations and hover transforms are disabled.
