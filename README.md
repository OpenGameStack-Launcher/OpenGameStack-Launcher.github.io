# Open Game Stack Website

The official public website for the **Open Game Stack** initiative, the universal standard for sovereign, version-controlled open source game development.

**🌐 Live Site:** [opengamestack.org](https://opengamestack.org)

## ⚡ About This Project
This repository hosts the source code for the Open Game Stack web presence, serving as the central hub for the open-source game development ecosystem and the official front door for the OGS Launcher desktop application. Consistent with our philosophy of "Sovereignty Over Subscription," this site is built with **zero dependencies**.

* **No Frameworks:** Pure HTML5 and CSS3.
* **No Build Steps:** What you see is what you get.
* **No Tracking:** Respects user privacy by design.

## 🎨 Design System & Styling Tokens
The site styling (`assets/css/site.css`) implements a Modern Game Studio and Editorial Dark UI built with pure CSS custom properties:
* **Calm Studio Dark Surface Tokens:** Grounded slate surfaces (`--bg-dark: #090d16`, `--bg-surface`, `--card-bg`, `--card-border`) with subtle stationary ambient illumination for fatigue-free reading.
* **Semantic Category Accent Properties:** Standardized color tokens across tooling domains (`--cat-engine`, `--cat-2d`, `--cat-3d`, `--cat-audio`, `--cat-level`, `--cat-code`).
* **Editorial & Catalog Component Library:** Reusable styles for long-form articles (`.prose`, `.article-body`), specification tables (`.spec-table`, `.version-table`), copyable code blocks (`.code-block`), callouts (`.callout`), two-tier status badges (`.badge-tier-frozen`, `.badge-tier-radar`), and catalog filter pills (`.catalog-filters`, `.filter-btn`).
* **Sovereign Privacy & Accessibility:** Self-hosted local fonts (`assets/fonts/`), zero external CDNs or analytics, high-contrast `:focus-visible` outlines, and full `prefers-reduced-motion` compliance.

## 📂 Repository Structure
* `index.html`: The Open Game Stack Hub homepage (`/`).
* `launcher/index.html`: The dedicated OGS desktop launcher application page (`/launcher/`).
* `mission/index.html`: The core philosophy, creator sovereignty, and "Declaration of Digital Sovereignty" (`/mission/`).
* `tools/index.html`: The frozen tool catalog with category, tool id, version, and release links (`/tools/`).
* `examples/index.html`: Living reference implementations and structured project showcase (Sudoku, Letter Logic) built with Open Game Stack (`/examples/`).
* `assets/css/site.css`: Modern game studio dark UI, shared chrome, semantic category tokens, editorial typography, and responsive styles.
* `tests/validate_site.py`: Zero-dependency static site validation suite.
* `docs/`: Canonical workflow guides, testing procedures, and standards.
* `AGENTS.md`: Agent architecture guidelines, coding rules, and workflow entry point.
* `CNAME`: DNS configuration for the custom domain.
* `logo.png` / `favicon.png`: Brand assets.

## 🚀 Local Development
Because we do not use complex build tools (React, Vue, etc.), running this site locally is instant.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/OpenGameStack-Launcher/OpenGameStack-Launcher.github.io.git
    ```
2.  **Open the file:**
    Simply double-click `index.html` or drag it into your browser.

## 🤝 Contributing
We welcome contributions to improve the messaging or design.
1.  Fork the repository.
2.  Create a feature branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes.
4.  Open a Pull Request.

## 📜 License
This project is licensed under the **MIT License** (see the [LICENSE](LICENSE) file for details).

---
*Maintained by the Open Game Stack Initiative.*
