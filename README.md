# Open Game Stack Website

The official public website for the **Open Game Stack** initiative, the universal standard for sovereign, version-controlled open source game development.

**🌐 Live Site:** [opengamestack.org](https://opengamestack.org)

## ⚡ About This Project
This repository hosts the source code for the Open Game Stack web presence, serving as the central hub for the open-source game development ecosystem and the official front door for the OGS Launcher desktop application. Consistent with our philosophy of "Sovereignty Over Subscription," this site is built with **zero dependencies**.

* **No Frameworks:** Pure HTML5 and CSS3.
* **No Build Steps:** What you see is what you get.
* **No Tracking:** Respects user privacy by design.

## 🛠️ Two-Tier Open-Source Tool Directory
The website features a filterable two-tier directory at `/tools/`:
* **Tier 1: Frozen in Launcher (7 core tools):** Packaged, frozen, and distributed reproducibly through the OGS Launcher (Godot, Blender, GIMP, Krita, Audacity, Git, VSCodium). Each Tier-1 tool includes a dedicated deep-dive profile page at `/tools/<id>/` detailing its pipeline role, replacement targets, frozen binary releases, `ogs_stack.json` configuration, licensing vital signs, and learning resources.
* **Tier 2: Ecosystem Radar (12 curated tools):** Battle-tested open-source tools serving as future freeze candidates and recommended production companions across 2D, 3D, Audio, and Level Design (Pixelorama, LibreSprite, Inkscape, LDtk, Tiled, TrenchBroom, Material Maker, Blockbench, ArmorPaint, LMMS, Ardour, sfxr).

## 🎨 Design System & Styling Tokens
The site styling (`assets/css/site.css`) implements a Modern Game Studio and Editorial Dark UI built with pure CSS custom properties:
* **Calm Studio Dark Surface Tokens:** Grounded slate surfaces (`--bg-dark: #090d16`, `--bg-surface`, `--card-bg`, `--card-border`) with subtle stationary ambient illumination for fatigue-free reading.
* **Semantic Category Accent Properties:** Standardized color tokens across tooling domains (`--cat-engine`, `--cat-2d`, `--cat-3d`, `--cat-audio`, `--cat-level`, `--cat-code`).
* **Editorial & Catalog Component Library:** Reusable styles for long-form articles (`.prose`, `.article-body`), specification tables (`.spec-table`, `.version-table`), copyable code blocks (`.code-block`), callouts (`.callout`), two-tier status badges (`.badge-tier-frozen`, `.badge-tier-radar`), catalog filter pills (`.catalog-filters`, `.filter-btn`), and tool profile headers (`.tool-profile-header`, `.breadcrumb`).
* **Sovereign Privacy & Accessibility:** Self-hosted local fonts (`assets/fonts/`), zero external CDNs or analytics, high-contrast `:focus-visible` outlines, and full `prefers-reduced-motion` compliance.

## 📂 Repository Structure
* `index.html`: The Open Game Stack Hub homepage (`/`).
* `launcher/index.html`: The dedicated OGS desktop launcher application page (`/launcher/`).
* `mission/index.html`: The core philosophy, creator sovereignty, and "Declaration of Digital Sovereignty" (`/mission/`).
* `tools/index.html`: The filterable two-tier open-source game development directory (7 Tier-1 Launcher frozen tools and 12 Tier-2 Ecosystem Radar tools) with category filters, tool metadata, versions, release links, and direct profile links (`/tools/`).
* `tools/<id>/index.html`: Dedicated deep-dive profile pages for all 7 Tier-1 Launcher tools (`godot`, `blender`, `krita`, `gimp`, `audacity`, `git`, `vscodium`) detailing specifications, manifest syntax, vital signs, and resources.
* `examples/index.html`: Living reference implementations and structured project showcase (Sudoku, Letter Logic) built with Open Game Stack (`/examples/`).
* `content/tools.json`: Canonical structured metadata catalog for Tier-1 (Launcher frozen) and Tier-2 (Ecosystem Radar) tools.
* `scripts/build_content.py`: Zero-dependency Python 3 content builder, metadata validator, and static HTML generator for tool profile pages.
* `assets/css/site.css`: Modern game studio dark UI, shared chrome, semantic category tokens, editorial typography, profile components, and responsive styles.
* `tests/validate_site.py`: Zero-dependency static site validation suite with case-exact disk verification and depth-aware navigation checks.
* `docs/`: Canonical workflow guides, testing procedures, and standards.
* `AGENTS.md`: Agent architecture guidelines, coding rules, and workflow entry point.
* `CNAME`: DNS configuration for the custom domain.
* `logo.png` / `favicon.png`: Brand assets.

## 🚀 Local Development
Because we do not use complex build tools (React, Vue, etc.), running this site locally is instant.

1. **Clone the repository:**
   ```bash
   git clone https://github.com/OpenGameStack-Launcher/OpenGameStack-Launcher.github.io.git
   ```
2. **Open the file:**
   Simply double-click `index.html` or drag it into your browser. Alternatively, serve via Python:
   ```powershell
   python -m http.server 8000 --bind 127.0.0.1
   ```

### Automated Site Validation & Tool Metadata Checks

Run the automated static site validation suite (zero dependencies, Python standard library only, with case-exact path verification on disk):

```powershell
python tests/validate_site.py
```

Validate canonical tool metadata schema integrity and parity against upstream frozen stacks:

```powershell
python scripts/build_content.py --check
```

Generate or rebuild static deep-dive HTML profile pages for Tier-1 tools:

```powershell
python scripts/build_content.py --build
```

## 🤝 Contributing
We welcome contributions to improve the messaging or design.
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/AmazingFeature`).
3. Commit your changes.
4. Open a Pull Request.

## 📜 License
This project is licensed under the **MIT License** (see the [LICENSE](LICENSE) file for details).

---
*Maintained by the Open Game Stack Initiative.*
