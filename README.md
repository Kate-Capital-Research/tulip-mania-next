# JupyterBook 2 Test Project

This is a test project demonstrating the migration of the Kate Capital documentation from JupyterBook 1 to JupyterBook 2 (alpha version).

## Overview

This project contains all the documentation from the tulip-mania repository, migrated to use JupyterBook 2, which is built on the MyST Document Engine. JupyterBook 2 provides faster builds, modern features, and improved workflows compared to the Sphinx-based JupyterBook 1.

## Project Structure

```
jupyterbook2-test/
├── myst.yml              # JupyterBook 2 configuration file
├── pyproject.toml        # Poetry dependencies
├── poetry.lock           # Poetry lock file
├── _toc.yml              # Table of contents (JupyterBook 1 format, still compatible)
├── intro.md              # Introduction page
├── _static/              # Static assets (logos, images, CSS)
└── notebooks/            # All documentation notebooks and markdown files
    ├── Countries/        # Country-specific analyses
    ├── Markets/          # Market analyses (Equities, Bonds, Currencies, etc.)
    ├── Signals/          # Trading signals
    ├── Oversight/        # Risk management and performance tracking
    └── Other/            # Tutorials and utilities
```

## Prerequisites

- Python 3.8 or higher
- Poetry (Python package manager)
- Node.js 18.0.0 or higher (for MyST)

## Installation

### 1. Install Poetry (if not already installed)

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### 2. Install Dependencies

```bash
poetry install
```

This will install JupyterBook 2 and all its dependencies in a virtual environment managed by Poetry.

## Usage

### Starting the Development Server

To start the JupyterBook 2 development server and view the documentation:

```bash
poetry run jupyter book start
```

This will:
- Build all the pages from markdown and Jupyter notebooks
- Start a local web server on http://localhost:3000
- Watch for changes and automatically rebuild

Open your browser and navigate to http://localhost:3000 to view the documentation.

### Building the Book

To build the book without starting the server:

```bash
poetry run jupyter book build .
```

Note: JupyterBook 2 uses a different build system than JupyterBook 1. The `start` command is the primary way to work with the book during development.

### Exporting to PDF

To export specific pages to PDF:

```bash
poetry run jupyter book build --pdf intro.md
```

## Live Deployment

The latest version of this documentation is automatically deployed to GitHub Pages:

**🌐 Live Site:** https://kate-capital-research.github.io/tulip-mania-next/

The site is automatically built and deployed via GitHub Actions whenever changes are pushed to the `main` branch. You can view the deployed version while developing locally to compare your changes.

## Configuration

### myst.yml

The main configuration file for JupyterBook 2. Key settings include:

- **project**: Metadata about the project (title, description, authors)
- **site**: Website configuration (template, logo, favicon)

### _toc.yml

The table of contents file that defines the structure of the book. This uses the JupyterBook 1 format but is still compatible with JupyterBook 2.

## Migration Notes

### Changes from JupyterBook 1 to JupyterBook 2

1. **Configuration**: JupyterBook 2 uses `myst.yml` instead of `_config.yml`
2. **Build System**: Based on MyST Document Engine instead of Sphinx
3. **CLI Commands**: Uses `jupyter book` commands (e.g., `jupyter book start`)
4. **Development Server**: Built-in development server with hot reloading
5. **Faster Builds**: Significantly faster build times compared to JupyterBook 1

### Known Issues

1. **Case Sensitivity**: File references in `_toc.yml` must match the exact case of the files (e.g., `Correlations.ipynb` not `correlations.ipynb`)
2. **Frontmatter Warnings**: Some JupyterBook 1 frontmatter keys (like `html_theme.sidebar_secondary.remove`) are not recognized by JupyterBook 2 and will show warnings
3. **Internal References**: Some internal references in notebooks may need to be updated to work with JupyterBook 2's reference system

### Content Migrated

All 57 markdown and Jupyter notebook files from the tulip-mania repository have been successfully migrated, including:

- Introduction and overview pages
- Country-specific analyses
- Market analyses (Equities, Bonds, Currencies)
- Trading signals and indicators
- Risk management dashboards
- Performance tracking and attribution
- Tutorials and documentation

## Documentation

- [JupyterBook 2 Documentation](https://next.jupyterbook.org/)
- [MyST Markdown Guide](https://mystmd.org/guide)
- [MyST Document Engine](https://mystmd.org/)

## Original Project

This project is a migration of the documentation from:
- Repository: https://github.com/Kate-Capital-Research/tulip-mania
- Original Site: https://tulip.katecapllc.com

## Author

Ignacio de Ramon - Kate Capital

## License

© 2025 Kate Capital
