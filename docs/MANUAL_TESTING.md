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

### 1. Hub Homepage (`index.html` -> `/`)
- [ ] **Header & Navigation:** Sticky glassmorphism header remains pinned on scroll; `Home`, `Tools`, `Launcher`, `Mission`, and `Examples` links navigate cleanly using clean directory URLs (`./`, `tools/`, `launcher/`, `mission/`, `examples/`).
- [ ] **Skip Link:** Pressing `Tab` on initial page load reveals the `Skip to content` button and focuses `#main` when activated.
- [ ] **Hero Actions & Hub CTAs:**
  - `Explore Tools` button navigates to `tools/` using a clean directory URL.
  - `OGS Launcher` button navigates to `launcher/` using a clean directory URL.
  - `Download v0.2.0` button in the hero and `Get v0.2.0 Package` button in `#alpha-download` point to `https://github.com/OpenGameStack-Launcher/ogs-launcher/releases/download/v0.2.0/OGS-Launcher-win64-0.2.0.zip`.
  - `The Mission` button navigates to `mission/` using a clean directory URL.
  - Engine target note states: `Current target: Windows 10/11 (x64), built with Godot 4.7.2.`.
- [ ] **Audience Cards:** The three audience cards (`For Indie Creators`, `For Game Studios`, `For Defense & Enterprise`) render in a 3-column grid on desktop and stack into a single column on narrow viewports (`<= 768px`).
- [ ] **Featured Tools Section:** The five category preview cards (Engine, 2D Pipeline, 3D Pipeline, Audio Production, Code & Versioning) render cleanly with category badges, and `Browse Full Tool Directory` navigates to `tools/`.
- [ ] **Launcher Application Panel:** The release card in `#alpha-download` presents the v0.2.0 package highlights, links to `launcher/` via `Launcher Guide & Details`, and includes the direct zip download button.
- [ ] **Newsletter Subscription Callout:** The Weekly Open-Source Game Dev Newsletter section renders cleanly and includes a working external link to `https://opengamestack.substack.com/` opening in a new tab with `rel="noopener noreferrer"`.
- [ ] **Footer:** Site footer renders clean links to `Mission`, `Tools`, `Launcher`, `Examples`, `Substack`, `GitHub`, `LinkedIn`, and `Email`, displaying the copyright tagline: `© 2026 OpenGameStack.org. Open-source tools and reproducible workflows for game creators.`.

### 2. Dedicated Launcher Page (`launcher/index.html` -> `/launcher/`)
- [ ] **Page Title & Eyebrow:** Page title displays `Launcher | Open Game Stack` and eyebrow reads `The Desktop Application`.
- [ ] **Skip Link:** Pressing `Tab` on initial page load reveals the `Skip to content` link and moves focus to `#main` when activated.
- [ ] **Primary Navigation:** Nav bar links resolve properly to `Home` (`../`), `Tools` (`../tools/`), `Launcher` (`./`), `Mission` (`../mission/`), and `Examples` (`../examples/`).
- [ ] **Hero Actions & Release Links:**
  - Primary `Download v0.2.0` button points to `https://github.com/OpenGameStack-Launcher/ogs-launcher/releases/download/v0.2.0/OGS-Launcher-win64-0.2.0.zip`.
  - `View on GitHub` opens `https://github.com/OpenGameStack-Launcher/ogs-launcher` in a new tab with `rel="noopener noreferrer"`.
  - `Browse Frozen Tools` and `The Mission` navigate to `../tools/` and `../mission/` using clean directory URLs.
  - Platform badges display `Windows 10/11 x64`, `Godot 4.7.2`, `Offline-First`, `Zero Telemetry`, and `Reproducible Stacks`.
- [ ] **System Specifications Table:** The specifications table inside `.table-container` lists Operating System, Application Runtime (Godot 4.7.2), Tool Cache Directory, Network Connectivity, and Distribution Model. On mobile viewports, the table scrolls horizontally without layout breaking.
- [ ] **Core Capabilities Grid:** The four capability cards (`Project Importing`, `Isolated Tool Caching`, `Offline Execution`, `Seal for Delivery`) render in a responsive grid.
- [ ] **Manifest Configuration Blocks:** The configuration cards display preformatted code blocks for `ogs_stack.json` and `ogs_config.json` with syntax styling and horizontal scrolling on narrow screens.
- [ ] **Seal for Delivery Section:** The workflow card explains manifest auditing, binary locking, and distribution archive generation.
- [ ] **Release Panel:** The bottom download panel in `#download` provides the second direct v0.2.0 zip download link and `View Source on GitHub` button.
- [ ] **Footer:** Footer links navigate to `Mission`, `Tools`, `Launcher`, `Examples`, `Substack`, `GitHub`, `LinkedIn`, and `Email`, displaying the copyright tagline: `© 2026 OpenGameStack.org. Open-source tools and reproducible workflows for game creators.`.

### 3. Mission Page (`mission/index.html` -> `/mission/`)
- [ ] **Page Title & Eyebrow:** Page title displays `Mission | Open Game Stack` and eyebrow header reads `Mission`.
- [ ] **Skip Link:** Pressing `Tab` on initial page load reveals the `Skip to content` link and moves focus to `#main` when activated.
- [ ] **Navigation & Footer:** Primary nav includes `Launcher` (`../launcher/`) and footer includes `Launcher` and `Substack`.
- [ ] **Two-Column Layout:** On desktop (`> 850px`), the mission article appears on the left and the sticky `Sections` sidebar index appears on the right.
- [ ] **Section Anchors & Index:** Clicking `Sovereignty Over Subscription`, `The Environment is the Artifact`, `Dual-Use by Design`, and `Stability is a Feature` in the `.section-index` smoothly scrolls to `#sovereignty`, `#environment`, `#dual-use`, and `#stability` on both desktop and mobile viewports.
- [ ] **Responsive Collapse:** At `<= 850px`, the layout collapses cleanly into a single column with the section index below the article.
- [ ] **Creator Sovereignty Prose:** Verify the declaration emphasizes creator ownership, environment preservation, and studio resilience for indie developers, educators, and studios, with dual-use framed as high-reliability engineering accessible to all creators.
- [ ] **Footer Copyright:** Site footer displays the updated tagline: `© 2026 OpenGameStack.org. Open-source tools and reproducible workflows for game creators.`.

### 4. Tool Catalog Page (`tools/index.html` -> `/tools/`)
- [ ] **Skip Link:** Pressing `Tab` on initial page load reveals the `Skip to content` link and moves focus to `#main` when activated.
- [ ] **Navigation & Footer:** Primary nav includes `Launcher` (`../launcher/`) and footer includes `Launcher` and `Substack`.
- [ ] **Category Accent Bars & Badges:** Verify that category containers display their distinctive left accent bar matching their semantic category token (Engine: cyan, 2D: emerald, 3D: amber, Audio: violet, Level Design: rose, Code: blue). Verify that tier badges (`.badge-tier-frozen`, `.badge-tier-radar`) and license badges (`.badge-license`) render with clear contrast.
- [ ] **Dedicated Profile Page Navigation Links:**
  - Verify clicking the tool name link (`.tool-title-link`) on each of the 7 Tier-1 tool cards (`godot`, `gimp`, `krita`, `blender`, `audacity`, `git`, `vscodium`) navigates directly to the dedicated profile page (`./<id>/`).
  - Verify clicking the `Deep Dive →` action button (`.tool-profile-link`) in the card header also navigates directly to `./<id>/`.
  - Verify that Tier-2 radar tools do not display profile subpage links, keeping tool headings as text.
- [ ] **Two-Tier Directory Filtering:**
  - Click `Frozen in Launcher` tier filter: verify only the 7 Tier-1 tools display and empty categories hide.
  - Click `Ecosystem Radar` tier filter: verify only the 12 Tier-2 tools display.
  - Click `All Tools` tier filter: verify all 19 tools across all 6 categories display.
  - Click individual Category pills (Engine, 2D, 3D, Audio, Level Design, Code): verify only cards from the selected category display.
  - Click combination of Tier and Category pills (for example, `Frozen in Launcher` + `2D`): verify only Godot, GIMP, and Krita cards display as expected.
  - Test keyboard navigation (`Tab` and `Enter`/`Space`) across all filter buttons, verifying `:focus-visible` outline and `aria-pressed` attribute toggling.
- [ ] **Dynamic Catalog Hydration:** With network access enabled, `tools/index.html` fetches `https://raw.githubusercontent.com/OpenGameStack-Launcher/ogs-frozen-stacks/main/repository.json` and safely updates Tier-1 version lists in-place in descending order (`Official release page` and `Frozen archive` download links) using `document.createElement()` and `.textContent` without clobbering Tier-2 cards or active filter selections, preserving title and deep dive links to `./<id>/`.
- [ ] **Offline / No-JS Fallback:** With network access blocked (or JavaScript disabled in browser DevTools), `tools/index.html` displays the static HTML tool catalog inside `[data-catalog]` containing all 19 tools across 6 categories, rendering their official vector SVG or PNG logos without broken images, empty containers, or generic text monograms. Verify that replaces chips (`.tool-replaces`), profile links (`./<id>/`), and upstream website/repo links render completely.

### 5. Dedicated Tool Profile Pages (`tools/<id>/index.html` -> `/tools/<id>/`)
- [ ] **Breadcrumb Back-Link Navigation:** Pressing or clicking `< Back to Tool Catalog` (`.back-link`) navigates back to `/tools/`.
- [ ] **Page Title & Metadata:** Verify browser tab displays `<Tool Name> - Open Game Stack Profile | Open Game Stack`.
- [ ] **Tool Header & Hero Details:** Visual preview renders the tool's official icon, name, category badge, license badge, and brief tagline. Action buttons link to the official website and source repository in new tabs with `rel="noopener noreferrer"`.
- [ ] **Section Anchor IDs & Prose:** Confirm the profile page presents all four required sections:
  - `#role`: Production pipeline role description and proprietary software replacement targets (for example, Photoshop, Maya, 3ds Max, Premiere).
  - `#launcher-integration`: Frozen binary release specification table and preformatted `ogs_stack.json` configuration snippet.
  - `#vital-signs`: Open-source vital signs table with software license, supported platform badges, stack category, and links.
  - `#resources`: Curated learning resources list with links to official documentation, tutorials, and community hubs.
- [ ] **Release Specifications & Checksums:** Verify that table columns (Frozen Version, Download Size, SHA-256 Checksum, Executable Path, Release Notes, Download ZIP) display correct metadata matching `content/tools.json`.
- [ ] **Project Manifest Snippet:** Verify preformatted `ogs_stack.json` code block shows correct JSON syntax for declaring the tool and version.
- [ ] **Table Responsiveness & Mobile Formatting:** Verify specification tables inside `.table-container` support smooth horizontal scrolling without layout breaking on viewports at `<= 768px` and `<= 850px`. Tool header grid collapses from 2 columns to a single column on mobile.
- [ ] **Security Hardening on External Links:** Verify that all external links (official website, source repository, release notes, download zip, learning resources) specify `target="_blank"` and `rel="noopener noreferrer"`.

### 6. Examples Page (`examples/index.html` -> `/examples/`)
- [ ] **Page Title & Eyebrow:** Page title displays `Examples | Open Game Stack` and eyebrow reads `Example Projects`.
- [ ] **Skip Link:** Pressing `Tab` on initial page load reveals the `Skip to content` link and moves focus to `#main` when activated.
- [ ] **Navigation & Footer:** Primary nav includes `Launcher` (`../launcher/`) and footer links include `Mission`, `Tools`, `Launcher`, `Examples`, and `Substack`, with the updated copyright tagline.
- [ ] **Hero Section:** Hero displays `Living Reference Implementations` with introductory text explaining project sovereignty and environment preservation.
- [ ] **Structured Project Showcase Cards:** Verify `Sudoku` and `Letter Logic` render inside a responsive `.grid` as glassmorphic `.card project-card` containers.
- [ ] **Tool Stack Badges:** Verify `.card-badges` display `.badge-tier-frozen` tags for `Godot 4`, `Git`, and `Krita` on both project cards.
- [ ] **Action Buttons & Security Hardening:**
  - `Source Code` button (`.btn-outline btn-sm`) includes SVG code icon and opens the respective GitHub repository (`https://github.com/OpenGameStack/sudoku`, `https://github.com/OpenGameStack/letter-logic`) in a new tab with `rel="noopener noreferrer"`.
  - `Play Online` button (`.btn btn-sm`) includes SVG play icon and opens the respective playable web demo (`https://audrain.games/sudoku`, `https://audrain.games/letter-logic`) in a new tab with `rel="noopener noreferrer"`.
- [ ] **Responsive Grid Layout:** On desktop viewports, cards render in a 2-column grid; on mobile viewports (`<= 768px`), cards stack vertically with full-width button rows.

### 7. Tool Metadata & Content Builder Verification (`content/tools.json` & `scripts/build_content.py`)
- [ ] **CLI Schema & Upstream Parity Check:** Run `python scripts/build_content.py --check` in PowerShell. Confirm exit code `0` and success output: `[PASS] Tools metadata validation succeeded: 6 categories, 19 tools (7 frozen, 12 radar).`.
- [ ] **Static Profile Page Generation Check:** Run `python scripts/build_content.py --build` in PowerShell. Confirm exit code `0` and verify that all 7 profile pages are generated idempotently with clean git status.
- [ ] **Tier-1 Frozen Tools Schema Inspection:** Verify `content/tools.json` defines all 7 Tier-1 tools (`godot`, `gimp`, `krita`, `blender`, `audacity`, `git`, `vscodium`) with `tier: "frozen"`, non-empty version lists, positive `size_bytes`, 64-character hex `sha256` checksums, and secure `https://` archive and info URLs matching `ogs-frozen-stacks/repository.json`.
- [ ] **Tier-2 Ecosystem Radar Tools Schema Inspection:** Verify `content/tools.json` defines all 12 Tier-2 tools (`pixelorama`, `libresprite`, `inkscape`, `ldtk`, `tiled`, `trenchbroom`, `material-maker`, `blockbench`, `armorpaint`, `lmms`, `ardour`, `sfxr`) with `tier: "radar"`, rich summaries, replacement targets, strengths, licenses, and verified `https://` website and source repository URLs.
- [ ] **Curated Learning Resources Inspection:** Verify all tools include curated learning resource objects with non-empty `title`, `type` (`Documentation`, `Tutorial`, `Assets`, `Community`), and secure `https://` URLs.

---

## 3. Cross-Cutting Visual & Accessibility Checks

- [ ] **Sitewide Navigation & Footer Consistency:** Confirm primary navigation (`Home`, `Tools`, `Launcher`, `Mission`, `Examples`) and footer links (`Mission`, `Tools`, `Launcher`, `Examples`, `Substack`, `GitHub`, `LinkedIn`, `Email`) are uniform across all site pages, with every page displaying the copyright tagline: `Open-source tools and reproducible workflows for game creators.`.
- [ ] **Depth-Aware Navigation Resolution:** Confirm that nested pages like `tools/<id>/index.html` link correctly to `../../launcher/`, `../../mission/`, and `../../examples/` without broken relative references.
- [ ] **Ambient Studio Canvas:** Confirm the root canvas uses calm, stationary ambient illumination via subtle radial background gradients on `body::before` with no continuous pulse animations, eye strain, or background flickering.
- [ ] **Editorial Typography & Prose:** In sections using `.prose` or `.article-body`, verify line length conforms to readable widths (around 72 characters), line height is comfortable (1.75), and blockquotes, headings, and links maintain high contrast and clear visual hierarchy.
- [ ] **Code Blocks & Specification Tables:** Verify that `.code-block` preformatted code containers and `.spec-table` / `.version-table` inside `.table-container` support smooth horizontal overflow scrolling on narrow viewports without expanding the main page layout or triggering document-level horizontal scrollbars.
- [ ] **Self-Hosted Typography:** Open browser DevTools -> Network tab and confirm `font-01.woff2` through `font-10.woff2` load from local `/assets/fonts/` with **zero** outbound requests to `fonts.googleapis.com` or `fonts.gstatic.com`.
- [ ] **Clean Directory URLs:** Navigate across `Home`, `Tools`, `Launcher`, `Mission`, `Examples`, and individual tool profile pages. Confirm the browser URL bar displays clean directory URLs (`/`, `/tools/`, `/tools/godot/`, `/launcher/`, `/mission/`, `/examples/`) without appending `.html` extensions or exposing legacy `/pages/` directory segments.
- [ ] **Responsive Breakpoints:** Resize viewport across `1280px` (desktop), `800px` (tablet), and `375px` (mobile) and confirm no horizontal scrollbar (`overflow-x`), text clipping, or overlapping buttons.
- [ ] **Reduced Motion:** Emulate `prefers-reduced-motion: reduce` in DevTools and verify all transform transitions and hover animations are disabled or minimized.
