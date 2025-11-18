# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Jupyter Book 2** project for Kate Capital's financial market documentation and interactive dashboards. The project was migrated from Jupyter Book 1 (Sphinx-based) to Jupyter Book 2 (MyST-based) in November 2025.

**Key Technologies:**
- Jupyter Book 2.0.2 (built on MyST Document Engine)
- Python 3.12+ with Poetry for dependency management
- Jupyter notebooks (.ipynb) for interactive financial analyses
- Custom Python utilities in `tulip_mania_next/` package
- Tulip library (Kate Capital's internal financial data package)
- Node.js 18+ required for MyST engine

**Repository Statistics:**
- 56 content files (notebooks and markdown)
- 5 major sections: Countries, Markets, Signals, Oversight, Other
- Automated GitHub Pages deployment via GitHub Actions

## Essential Commands

### Development Server
```bash
# Start development server with hot reload (recommended for development)
poetry run jupyter-book start

# Runs on http://localhost:3000
```

### Building
```bash
# Build HTML output (production)
poetry run jupyter-book build --html

# Rebuild all pages (use after TOC changes)
poetry run jupyter-book build --html --all

# Clean build artifacts
poetry run jupyter-book clean --all
```

### Using the Python Build Script
```bash
# Build with logging (creates logs/book_build_YYYYMMDD.log)
poetry run python main.py --build

# Force rebuild all pages
poetry run python main.py --build-all
```

### Dependency Management
```bash
# Install all dependencies
poetry install

# Add new package
poetry add package-name

# Update dependencies
poetry update
```

## Prerequisites & Environment Setup

### System Requirements
- **Python**: 3.12 or higher (required by pyproject.toml)
- **Node.js**: 18.0.0 or higher (required by MyST Document Engine)
- **Poetry**: Python package manager (install via `curl -sSL https://install.python-poetry.org | python3 -`)
- **Git**: For version control and tulip package installation

### Environment Variables

This project requires several API keys and configuration values. Copy `.env.example` to `.env` and configure:

**AI Service Keys:**
- `ANTHROPIC_API_KEY` - For Claude AI service (ask Ignacio)
- `GEMINI_API_KEY` - For Google Gemini AI service (ask Ignacio)

**Financial Data APIs:**
- `FRED_API_KEY` - Federal Reserve Economic Data API (get from https://fred.stlouisfed.org/)
- `BLOOMBERG_API_KEY` - Bloomberg data access (if applicable)
- `HAVER_API_KEY` - Haver Analytics API (if applicable)
- `JP_DATAQUERY_CLIENT_ID` - JPMorgan Markets QIS access
- `JP_DATAQUERY_CLIENT_SECRET` - JPMorgan Markets QIS secret

**Database Configuration:**
- `PG_USERNAME`, `PG_PASSWORD`, `PG_HOSTNAME`, `PG_DB` - PostgreSQL connection details

**Note:** The `.env` file is gitignored. Never commit API keys or secrets to version control.

### First-Time Setup

```bash
# 1. Clone the repository
git clone https://github.com/Kate-Capital-Research/tulip-mania-next.git
cd tulip-mania-next

# 2. Copy and configure environment variables
cp .env.example .env
# Edit .env with your API keys

# 3. Install dependencies (includes tulip package from GitHub)
poetry install

# 4. Start development server
poetry run jupyter-book start
```

## Architecture & Configuration

### Configuration Files

**myst.yml** - Main Jupyter Book 2 configuration
- Project metadata (title, description, authors, copyright)
- Site settings (template, logos, favicon)
- Must include `extends: - toc.yml` to load the table of contents

**toc.yml** (NOT _toc.yml)** - Table of contents structure
- **CRITICAL:** This file defines the entire book structure
- Uses Jupyter Book 2 syntax (NOT Jupyter Book 1)
- Key syntax differences from JB1:
  - `version: 1` instead of `format: jb-book`
  - `project.toc:` wrapper required
  - `children:` instead of `sections:`
  - `pattern:` instead of `glob:` for wildcard matching
  - File extensions `.ipynb` or `.md` are **required**
  - First entry replaces `root:` field

**pyproject.toml** - Poetry configuration for dependencies
- Python version constraints: `>=3.12,<3.14`
- Main dependencies: `jupyter-book ^2.0.2` and `tulip` (from GitHub)
- Tulip package: Kate Capital's internal library for financial data analysis

### Custom Python Package

**tulip_mania_next/** - Custom utilities for notebook rendering
- `columns_framework.py` - Column-based layout system for Jupyter notebooks
  - `Column` class: Streamlit-like column container for HTML content
  - Methods: `write()`, `markdown()`, `header()`, `image()`, `html()`, `plot()`
  - Supports both Plotly and Matplotlib figures
  - Grid-based responsive layouts
- `utils.py` - Helper functions and utilities
- `__init__.py` - Package initialization

**Usage in Notebooks:**
```python
from tulip_mania_next.columns_framework import columns

# Create multi-column layouts
col1, col2, col3 = columns(3)
col1.header("Column 1")
col2.plot(my_plotly_figure)
col3.markdown("**Bold text**")
```

### Critical TOC Syntax Rules

1. **Pattern matching for multiple files:**
   ```yaml
   - file: notebooks/Countries.ipynb
     children:
       - pattern: notebooks/Countries/*.ipynb  # Expands to all .ipynb in folder
   ```

2. **Nested hierarchies:**
   ```yaml
   - file: notebooks/Markets.ipynb
     children:
       - file: notebooks/Markets/Equities.ipynb
         children:
           - pattern: notebooks/Markets/Equities/Deep Dives/*.ipynb
   ```

3. **File paths must:**
   - Include file extensions (`.ipynb` or `.md`)
   - Match exact case (Windows is case-insensitive, Linux deployment is case-sensitive)
   - Be relative to project root

### Content Organization

```
notebooks/
├── Countries/          # Country-specific analyses (uses pattern matching)
├── Markets/
│   ├── Equities/      # Equity analysis (ERP, EPS, deep dives)
│   ├── Bonds/         # Fixed income (flows, yields, deep dives)
│   ├── Currencies/    # FX analysis
│   └── Dollar Liquidity/
├── Signals/           # Trading signals (CTA, mean reversion)
├── Oversight/         # Risk, performance, attribution
└── Other/
    ├── Tutorials/     # How-to guides
    └── ...            # Data visualizer, curve trades
```

## Important Platform Differences

### Case Sensitivity
**CRITICAL:** Windows filesystems are case-insensitive but Linux (deployment targets like EC2, GitHub Pages) are case-sensitive.

- Always match the exact case in `toc.yml` file references
- Example: If file is `Correlations.ipynb`, use `notebooks/Markets/Correlations.ipynb` NOT `correlations.ipynb`
- This is a common source of "file not found" errors on deployed sites

### File System Paths
- Use forward slashes `/` in `toc.yml` (not backslashes `\`)
- Paths are relative to project root where `myst.yml` lives

## Common Issues & Solutions

### TOC Changes Not Appearing
**Problem:** Modified `toc.yml` but changes don't show in built site
**Solution:** Use `--all` flag to force rebuild:
```bash
poetry run jupyter-book build --html --all
```

### Country/Section Pages Missing
**Problem:** Parent page shows but child pages don't appear
**Cause:** `toc.yml` not loaded (missing `extends:` in `myst.yml`) or incorrect pattern syntax
**Solution:**
1. Verify `myst.yml` has `extends: - toc.yml`
2. Use `pattern:` not `glob:` for wildcard matching
3. Use `children:` not `sections:` for nesting

### Case Sensitivity Errors on Deployment
**Problem:** Works locally on Windows but fails on Linux server
**Solution:** Verify all file references in `toc.yml` match exact case of actual files

### Frontmatter Warnings
**Expected:** Some notebooks have JB1 frontmatter (e.g., `html_theme.sidebar_secondary.remove`)
**Impact:** Cosmetic warnings only, does not affect functionality
**Action:** Can be ignored or updated to JB2 syntax if desired

## Jupyter Book 1 vs Jupyter Book 2 Migration Notes

This project was migrated from JB1. Key differences:

| Aspect | JB1 (Old) | JB2 (New) |
|--------|-----------|-----------|
| Config file | `_config.yml` | `myst.yml` |
| TOC file | `_toc.yml` | `toc.yml` (loaded via `extends:`) |
| Build engine | Sphinx | MyST Document Engine |
| CLI command | `jupyter-book` | `jupyter book` (space not hyphen) |
| TOC root | `root: intro` | First item in `project.toc:` |
| TOC sections | `sections:` | `children:` |
| TOC glob | `glob:` | `pattern:` |
| File extensions | Optional | **Required** (`.ipynb`, `.md`) |
| Build speed | Slower (~20s+) | Faster (~2s) |

## Deployment

The built site in `_build/html/` is static and can be deployed to:
- GitHub Pages (automated via GitHub Actions)
- Netlify
- AWS S3 + CloudFront
- Any static hosting service

**Local Preview Note:** Opening `_build/html/index.html` directly (`file://`) has limited JavaScript functionality due to browser security. Use the development server (`poetry run jupyter-book start`) or Python HTTP server for full functionality:
```bash
python -m http.server 8000 --directory _build/html
```

### GitHub Actions Deployment

This repository includes automated deployment to GitHub Pages via `.github/workflows/deploy.yml`.

**Workflow Trigger:**
- Automatically runs on push to `main` branch
- Can also be triggered manually via GitHub Actions UI

**Workflow Steps:**
1. Checkout repository
2. Setup Node.js 18.x
3. Install Jupyter Book globally via npm: `npm install -g jupyter-book`
4. Build HTML assets: `jupyter-book build --html`
5. Upload artifact to GitHub Pages
6. Deploy to GitHub Pages

**Important Configuration:**
- `BASE_URL` is set to `/${{ github.event.repository.name }}` for proper URL routing
- Requires GitHub Pages to be enabled in repository settings with "GitHub Actions" as source
- Permissions configured: `contents: read`, `pages: write`, `id-token: write`
- Uses concurrency control to prevent conflicting deployments

**Note on Python Dependencies:**
The GitHub Actions workflow uses npm to install Jupyter Book (Node.js version), which doesn't require Python dependencies. However, if notebooks need to be executed during build, you'll need to add Python setup steps:
```yaml
- uses: actions/setup-python@v4
  with:
    python-version: '3.12'
- name: Install Poetry
  run: curl -sSL https://install.python-poetry.org | python3 -
- name: Install dependencies
  run: poetry install
```

## Build Logging

The `main.py` script provides enhanced logging and build utilities:

**Features:**
- Creates timestamped logs in `logs/book_build_YYYYMMDD.log`
- Tracks elapsed time for build operations with millisecond precision
- Captures both stdout and stderr output
- Useful for debugging build issues and performance analysis

**Log Format:**
```
YYYY-MM-DD HH:MM:SS - X.XXX min - LEVEL - MESSAGE
```

**Log Location:**
- Directory: `logs/` (created automatically if not exists)
- Gitignored: Log files are not committed to version control
- Filename pattern: `book_build_YYYYMMDD.log` (one per day)

**Implementation Details:**
- Uses Python's `logging` module with custom `ElapsedFilter` and `ElapsedAdapter`
- Logs to both file and console (stdout)
- Root logger configured to capture all logs at DEBUG level
- Build commands executed via `subprocess` module

## Styling and Customization

### Custom CSS Integration

Add custom styling by defining a `style` option in `myst.yml`:

```yaml
site:
  template: book-theme
  options:
    style: _static/custom.css  # Custom CSS will be bundled during build
```

### Applying CSS Classes

**Method 1: Content Block Classes**
```markdown
:::{note}
:class: custom-highlight
This note has a custom CSS class applied.
:::
```

**Method 2: HTML Elements**
```markdown
<div class="grid-container custom-layout">
Content here
</div>

<span class="highlight" style="color: red;">Inline styled text</span>
```

**Method 3: Directive Class Options**
```markdown
:::{admonition} Custom Title
:class: my-custom-class
Content here
:::
```

### Light and Dark Mode Support

MyST themes include Tailwind CSS for theme-aware styling:

```markdown
<!-- Show only in dark mode -->
<div class="hidden dark:block">
![Dark mode logo](logo-dark.png)
</div>

<!-- Hide in dark mode -->
<div class="dark:hidden">
![Light mode logo](logo-light.png)
</div>
```

**Note:** Tailwind classes require default MyST themes and won't work with custom HTML themes lacking Tailwind support.

### Built-in Grid System

The default HTML themes include a grid system for layout control. Use CSS classes for positioning without custom configuration.

### Responsive Design Configuration

This project implements a comprehensive responsive design strategy optimized for viewing financial charts and data across multiple screen sizes (13" laptops to 2550x1440 monitors).

**Responsive Breakpoints in `_static/custom.css`:**

- **Very Large (>2000px)**: 1800px max content width - Ideal for large monitors
- **Large (1400-2000px)**: 1400px max content width - Standard desktop
- **Medium (1024-1399px)**: 1200px max content width - Laptop (13"-15")
- **Small (768-1023px)**: 100% width - Small laptops/tablets
- **Mobile (<768px)**: 100% width - Mobile devices

**CSS Selectors Used:**

**CORRECT MyST book-theme selectors (use these):**
- `main.article-grid` - The main grid container
- `article.article-grid` - The article grid wrapper
- `article.col-screen` - The content column

**INCORRECT selectors (do NOT use):**
- `.bd-main`, `.bd-content`, `.bd-article-container` - These are Sphinx Book Theme classes, NOT MyST
- Generic `article`, `main`, `.content`, `.page` - Too broad, may not match MyST structure
- `#root`, `#page`, `#main-content` - These IDs don't exist in MyST book-theme

**Critical Lesson Learned:**
MyST Document Engine's book-theme uses a CSS Grid system with specific classes. The DOM structure is:
```html
<main class="article-grid grid-gap">
  <article class="article-grid subgrid-gap col-screen article content">
    <!-- content here -->
  </article>
</main>
```

Generic CSS selectors targeting `article` or `main` without the `.article-grid` class may not work due to CSS specificity. Always use the full selector: `main.article-grid`, `article.article-grid`, `article.col-screen`.

**Investigation Source:** Analysis of `jupyter-book/myst-theme` GitHub repository revealed the actual React components (`/themes/book/app/routes/$.tsx`) and CSS Grid definitions (`/styles/grid-system.css`) used by book-theme.

**Column Framework Integration:**
The `tulip_mania_next/columns_framework.py` includes matching responsive breakpoints that automatically stack side-by-side charts on smaller screens while keeping them side-by-side on larger displays.

**Important:** When modifying layout widths, update both:
1. `_static/custom.css` - Global page layout
2. `tulip_mania_next/columns_framework.py` - Column container breakpoints (if needed)

## Theme Configuration

### Current Theme: book-theme

This project uses `book-theme` configured in `myst.yml`:

```yaml
site:
  template: book-theme
  options:
    favicon: _static/new_tulip.png
    logo: _static/logo_black_over_white.png
    logo_dark: _static/logo_white_over_black.png
    hide_footer_links: true
```

**Key features of book-theme:**
- Multi-page navigation with table of contents
- Support for light/dark mode with separate logos
- Footer customization options
- Optimized for documentation and books with hierarchical structure
- Uses MyST Document Engine (React + Remix framework)

**Important Notes for book-theme:**
- This is the **MyST book-theme** (part of MyST Document Engine), NOT the Sphinx Book Theme
- CSS customization requires targeting MyST-specific selectors (e.g., `article`, `main`, `.content`)
- Layout width is controlled via custom CSS overrides (see `_static/custom.css`)
- Responsive breakpoints are defined for multi-screen support (13" laptops to 2550x1440 monitors)

### Alternative: article-theme

For scientific articles and standalone notebooks, the `article-theme` can be used:

```yaml
site:
  template: article-theme
```

**Key features of article-theme:**
- Lightweight design for scientific articles
- Built with Remix framework and Tailwind CSS
- Optimized for single articles rather than full books
- Best suited for individual research papers or notebooks

### Theme Comparison

| Feature | book-theme | article-theme |
|---------|------------|---------------|
| Use Case | Multi-page books/docs | Single articles/papers |
| Navigation | Full TOC sidebar | Minimal navigation |
| Structure | Hierarchical | Flat |
| Best For | This project | Research papers |

## Jupyter Book 2 Workflow

Jupyter Book 2 follows this development cycle:

1. **Initialize** - Set up project structure (`jupyter-book init`)
2. **Add Content** - Write pages using MyST Markdown or Jupyter notebooks
3. **Build Website** - Compile to HTML (`jupyter-book build --html`)
4. **Export PDF** - Generate static PDFs if needed (`jupyter-book build --pdf`)
5. **Reference** - Link between sections and external resources
6. **Publish** - Deploy to GitHub Pages, Netlify, etc.

### MyST Foundation

Jupyter Book 2 is a distribution of the MyST Document Engine. The underlying capabilities are identical to standalone MyST - only the CLI command differs (`jupyter-book` vs `myst`).

### Version Note

This project uses **Jupyter Book 2**. For Jupyter Book 1 documentation, see jupyterbook.org/v1.

## Development Workflow

### Git Branching Strategy

**Main Branch:**
- `main` - Production branch, triggers GitHub Pages deployment on push
- Protected: All changes should go through pull requests

**Feature Branches:**
- Use descriptive names: `feature/add-new-analysis`, `fix/toc-case-sensitivity`
- Branch from `main`, merge back via pull request
- Delete after merging

**Development Process:**
1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes and test locally with `poetry run jupyter-book start`
3. Build and verify: `poetry run jupyter-book build --html --all`
4. Commit with descriptive messages
5. Push and create pull request
6. After merge, GitHub Actions automatically deploys to GitHub Pages

### Code Quality

**Before Committing:**
- Test notebook changes by running cells and verifying output
- Check for broken internal links
- Verify case sensitivity of file references in `toc.yml`
- Run full build: `poetry run jupyter-book build --html --all`
- Check build logs for warnings or errors

**Notebook Best Practices:**
- Clear cell outputs before committing (unless outputs are intentionally versioned)
- Use meaningful cell execution order
- Document complex code with markdown cells
- Test with fresh kernel: "Restart Kernel and Run All"

### Static Assets Management

**Location:** `_static/` directory

**Files:**
- `logo_black_over_white.png` - Logo for light mode
- `logo_white_over_black.png` - Logo for dark mode
- `new_tulip.png` - Favicon
- `custom.css` - Custom CSS overrides
- `_color.scss` - SASS color definitions

**Adding New Assets:**
1. Place files in `_static/` directory
2. Reference in `myst.yml` for site-wide assets (logos, favicon)
3. Reference in notebooks/markdown: `![Alt text](_static/filename.png)`
4. For CSS: Update `myst.yml` site options to include custom stylesheet

## Troubleshooting & Common Tasks

### Dependency Issues

**Problem:** `poetry install` fails with version conflicts
**Solution:**
```bash
# Update poetry lock file
poetry lock --no-update

# Or force update all dependencies
poetry update

# Check dependency tree
poetry show --tree
```

**Problem:** Tulip package installation fails
**Solution:**
- Ensure you have SSH access to GitHub (tulip is a private repository)
- Configure SSH key: `ssh-keygen` and add to GitHub account
- Test SSH: `ssh -T git@github.com`
- Alternatively, use HTTPS with personal access token

### Build Issues

**Problem:** Build fails with "File not found" errors
**Checklist:**
1. Verify file exists: `ls -la path/to/file.ipynb`
2. Check exact case matches in `toc.yml`
3. Ensure file extension included (`.ipynb` or `.md`)
4. Verify path is relative to project root

**Problem:** TOC changes not reflected
**Solution:**
```bash
# Force rebuild all pages
poetry run jupyter-book build --html --all

# Or clean and rebuild
poetry run jupyter-book clean --all
poetry run jupyter-book build --html
```

**Problem:** Notebook execution errors during build
**Solution:**
- By default, Jupyter Book 2 doesn't execute notebooks during build
- Pre-run notebooks locally before committing
- If execution needed: configure in `myst.yml` under `project.jupyter`

### Development Server Issues

**Problem:** Port 3000 already in use
**Solution:**
```bash
# Find process using port 3000
lsof -ti:3000

# Kill the process
kill -9 $(lsof -ti:3000)

# Or use alternative port (if supported by jupyter-book)
```

**Problem:** Changes not appearing in browser
**Solution:**
- Hard refresh: `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac)
- Clear browser cache
- Restart development server
- Check terminal for build errors

### Adding New Content

**Adding a New Notebook:**
1. Create notebook in appropriate `notebooks/` subdirectory
2. Add entry to `toc.yml` with exact filename (include `.ipynb`)
3. Test build: `poetry run jupyter-book build --html --all`
4. Verify it appears in navigation

**Adding a New Section:**
1. Create parent notebook (e.g., `notebooks/NewSection.ipynb`)
2. Create subdirectory: `notebooks/NewSection/`
3. Add child notebooks in subdirectory
4. Update `toc.yml` with parent-child hierarchy:
   ```yaml
   - file: notebooks/NewSection.ipynb
     children:
       - pattern: notebooks/NewSection/*.ipynb
   ```

### Performance Optimization

**Slow Build Times:**
- Use `jupyter-book start` for development (incremental builds)
- Only use `--all` flag when TOC changes
- Pre-render complex Plotly figures as static images for large datasets
- Consider splitting large notebooks into smaller ones

**Large Repository Size:**
- Use `.gitignore` for `_build/`, `logs/`, `.env`
- Clear notebook outputs before committing (unless needed)
- Optimize images in `_static/` (use appropriate formats and compression)

## Documentation References

- [Jupyter Book 2 Documentation](https://next.jupyterbook.org/)
- [MyST Markdown Guide](https://mystmd.org/guide)
- [MyST Table of Contents](https://mystmd.org/guide/table-of-contents)
- [MyST Website Styling](https://mystmd.org/guide/website-style)
- [Poetry Documentation](https://python-poetry.org/docs/)
- [Tulip Package Repository](https://github.com/Kate-Capital-Research/tulip)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

## Project Metadata

**Repository:** https://github.com/Kate-Capital-Research/tulip-mania-next
**Organization:** Kate Capital Research
**Primary Author:** Ignacio de Ramon
**Project Type:** Financial Documentation & Interactive Dashboards
**License:** © 2025 Kate Capital (Proprietary)

**Original Project:**
- Migrated from: https://github.com/Kate-Capital-Research/tulip-mania
- Original deployment: https://tulip.katecapllc.com

**Migration Details:**
- Migration Date: November 2025
- From: Jupyter Book 1 (Sphinx-based)
- To: Jupyter Book 2 (MyST-based)
- Migration Status: ✅ Complete (57 files, all sections functional)

**Current Status:**
- Development: ✅ Active
- Deployment: ✅ Automated via GitHub Actions
- Documentation: ✅ Complete
- Test Coverage: N/A (documentation project)

## AI Assistant Guidelines

When working with this repository, AI assistants should:

1. **Always verify file case sensitivity** - Linux deployments are case-sensitive
2. **Test builds before committing** - Run `poetry run jupyter-book build --html --all`
3. **Never commit secrets** - API keys, passwords, or `.env` files
4. **Use pattern matching in TOC** - Prefer `pattern:` over individual file entries for scalability
5. **Document changes** - Update this CLAUDE.md if adding new workflows or structures
6. **Follow git workflow** - Feature branches → PR → main → auto-deploy
7. **Check logs** - Review `logs/` directory for build issues
8. **Respect dependencies** - Don't upgrade major versions without testing
9. **Preserve formatting** - Match existing code style and notebook structure
10. **Consider performance** - Large notebooks should be optimized or split

**Quick Health Check:**
```bash
# Verify environment
poetry --version
python --version
node --version

# Install and build
poetry install
poetry run jupyter-book build --html --all

# Should complete in ~2-3 seconds with no errors
```

**Common AI Tasks:**
- Adding new analysis notebooks
- Updating TOC structure
- Fixing broken references
- Optimizing notebook performance
- Debugging build errors
- Updating documentation
- Adding new visualizations

**Key Files to Never Modify Without Review:**
- `myst.yml` - Site configuration
- `toc.yml` - Navigation structure
- `pyproject.toml` - Dependencies
- `.github/workflows/deploy.yml` - Deployment pipeline

---

*Last Updated: November 2025*
*Document Version: 2.0*
*For questions or issues, contact: Ignacio de Ramon (Kate Capital)*
