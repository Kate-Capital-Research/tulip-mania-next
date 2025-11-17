# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Jupyter Book 2** project for Kate Capital's financial market documentation and interactive dashboards. The project was migrated from Jupyter Book 1 (Sphinx-based) to Jupyter Book 2 (MyST-based) in November 2025.

**Key Technologies:**
- Jupyter Book 2.0.2 (built on MyST Document Engine)
- Python 3.12+ with Poetry for dependency management
- Jupyter notebooks (.ipynb) for interactive financial analyses

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
- GitHub Pages
- Netlify
- AWS S3 + CloudFront
- Any static hosting service

**Local Preview Note:** Opening `_build/html/index.html` directly (`file://`) has limited JavaScript functionality due to browser security. Use the development server (`poetry run jupyter-book start`) or Python HTTP server for full functionality:
```bash
python -m http.server 8000 --directory _build/html
```

## Build Logging

The `main.py` script provides enhanced logging:
- Creates timestamped logs in `logs/book_build_YYYYMMDD.log`
- Tracks elapsed time for build operations
- Useful for debugging build issues

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

## Documentation References

- [Jupyter Book 2 Documentation](https://next.jupyterbook.org/)
- [MyST Markdown Guide](https://mystmd.org/guide)
- [MyST Table of Contents](https://mystmd.org/guide/table-of-contents)
- [MyST Website Styling](https://mystmd.org/guide/website-style)
- [Poetry Documentation](https://python-poetry.org/docs/)
