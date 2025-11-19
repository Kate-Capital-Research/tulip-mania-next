#!/usr/bin/env python3
"""
Main script for building and managing the JupyterBook 2 site.

This script provides utilities for:
- Executing notebooks in parallel with error tracking
- Checking notebooks for execution errors
- Building the book with proper logging
"""

import sys
import time
import logging
import argparse
from datetime import datetime
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import List, Tuple, Optional
import multiprocessing


class ElapsedFilter(logging.Filter):
    """Filter that adds elapsed time to log records."""

    def __init__(self, start):
        super().__init__()
        self.start = start

    def filter(self, record):
        record.elapsed_min = (time.perf_counter() - self.start) / 60
        return True


class ElapsedAdapter(logging.LoggerAdapter):
    """Logger adapter that adds elapsed time to log messages."""

    def __init__(self, logger, start):
        super().__init__(logger, {})
        self.start = start

    def process(self, msg, kwargs):
        elapsed_min = (time.perf_counter() - self.start) / 60
        extra = kwargs.get("extra", {})
        extra["elapsed_min"] = elapsed_min
        kwargs["extra"] = extra
        return msg, kwargs


def setup_logging(start_time):
    """Set up logging with elapsed time tracking."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    filename = log_dir / f"book_build_{datetime.now():%Y%m%d}.log"

    fmt = "%(asctime)s - %(elapsed_min).3f min - %(levelname)s - %(message)s"
    formatter = logging.Formatter(fmt)

    # Create filter for elapsed time
    elapsed_filter = ElapsedFilter(start_time)

    file_h = logging.FileHandler(filename)
    file_h.setFormatter(formatter)
    file_h.addFilter(elapsed_filter)

    stream_h = logging.StreamHandler(sys.stdout)
    stream_h.setFormatter(formatter)
    stream_h.addFilter(elapsed_filter)

    # Configure root logger to capture all logs
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_h)
    root_logger.addHandler(stream_h)

    base_logger = logging.getLogger("jupyterbook")

    logger = ElapsedAdapter(base_logger, start_time)

    return logger


def find_notebooks(exclude_patterns: Optional[List[str]] = None) -> List[Path]:
    """
    Find all Jupyter notebooks in the project.

    Args:
        exclude_patterns: List of path patterns to exclude (default: ['_build', '.ipynb_checkpoints'])

    Returns:
        List of Path objects for found notebooks
    """
    if exclude_patterns is None:
        exclude_patterns = ['_build', '.ipynb_checkpoints']

    project_root = Path.cwd()
    notebooks = []

    for notebook_path in project_root.rglob("*.ipynb"):
        # Check if any exclude pattern is in the path
        if any(pattern in str(notebook_path) for pattern in exclude_patterns):
            continue
        notebooks.append(notebook_path)

    return sorted(notebooks)


def execute_notebook(notebook_path: Path, timeout: int = 600) -> Tuple[Path, bool, str]:
    """
    Execute a single notebook in-place using nbclient.

    Args:
        notebook_path: Path to the notebook
        timeout: Timeout in seconds for notebook execution

    Returns:
        Tuple of (notebook_path, success, error_message)
    """
    try:
        import nbformat
        from nbclient import NotebookClient
        from nbclient.exceptions import CellExecutionError

        # Read the notebook
        with open(notebook_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)

        # Execute the notebook
        client = NotebookClient(
            nb,
            timeout=timeout,
            kernel_name='python3',
            allow_errors=False  # Stop on first error
        )

        try:
            client.execute()

            # Write the executed notebook back
            with open(notebook_path, 'w', encoding='utf-8') as f:
                nbformat.write(nb, f)

            return (notebook_path, True, "")

        except CellExecutionError as e:
            error_msg = f"Cell execution error: {str(e)}"
            return (notebook_path, False, error_msg)

    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        return (notebook_path, False, error_msg)


def execute_all_notebooks(
    notebooks: List[Path],
    max_workers: Optional[int] = None,
    timeout: int = 600,
    logger: Optional[logging.Logger] = None
) -> Tuple[int, int, List[Tuple[Path, str]]]:
    """
    Execute all notebooks in parallel.

    Args:
        notebooks: List of notebook paths to execute
        max_workers: Maximum number of parallel workers (default: CPU count)
        timeout: Timeout per notebook in seconds
        logger: Logger instance for output

    Returns:
        Tuple of (successful_count, failed_count, list of (failed_path, error_message))
    """
    if max_workers is None:
        max_workers = multiprocessing.cpu_count()

    if logger:
        logger.info(f"Executing {len(notebooks)} notebooks with {max_workers} workers")

    successful = 0
    failed = 0
    failures = []

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submit all notebook executions
        future_to_notebook = {
            executor.submit(execute_notebook, nb, timeout): nb
            for nb in notebooks
        }

        # Process results as they complete
        for future in as_completed(future_to_notebook):
            notebook_path = future_to_notebook[future]
            try:
                path, success, error_msg = future.result()

                if success:
                    successful += 1
                    if logger:
                        logger.info(f"✓ Executed: {path.relative_to(Path.cwd())}")
                else:
                    failed += 1
                    failures.append((path, error_msg))
                    if logger:
                        logger.error(f"✗ Failed: {path.relative_to(Path.cwd())}")
                        logger.error(f"  Error: {error_msg}")

            except Exception as e:
                failed += 1
                error_msg = f"Execution exception: {str(e)}"
                failures.append((notebook_path, error_msg))
                if logger:
                    logger.error(f"✗ Exception: {notebook_path.relative_to(Path.cwd())}")
                    logger.error(f"  Error: {error_msg}")

    return successful, failed, failures


def check_notebook_errors(notebook_path: Path) -> Tuple[Path, bool, List[str]]:
    """
    Check a notebook for error cells.

    Args:
        notebook_path: Path to the notebook

    Returns:
        Tuple of (notebook_path, has_errors, list of error descriptions)
    """
    try:
        import nbformat

        # Read the notebook
        with open(notebook_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)

        errors = []

        # Check each cell for errors
        for idx, cell in enumerate(nb.cells):
            if cell.cell_type == 'code':
                # Check outputs for errors
                if hasattr(cell, 'outputs'):
                    for output in cell.outputs:
                        if output.output_type == 'error':
                            error_name = output.get('ename', 'Unknown')
                            error_value = output.get('evalue', 'Unknown error')
                            error_desc = f"Cell {idx + 1}: {error_name}: {error_value}"
                            errors.append(error_desc)

        has_errors = len(errors) > 0
        return (notebook_path, has_errors, errors)

    except Exception as e:
        error_msg = f"Failed to check notebook: {str(e)}"
        return (notebook_path, True, [error_msg])


def check_all_notebooks(
    notebooks: List[Path],
    logger: Optional[logging.Logger] = None
) -> Tuple[int, int, List[Tuple[Path, List[str]]]]:
    """
    Check all notebooks for errors.

    Args:
        notebooks: List of notebook paths to check
        logger: Logger instance for output

    Returns:
        Tuple of (clean_count, error_count, list of (notebook_path, error_list))
    """
    if logger:
        logger.info(f"Checking {len(notebooks)} notebooks for errors")

    clean = 0
    with_errors = 0
    error_notebooks = []

    for notebook_path in notebooks:
        path, has_errors, errors = check_notebook_errors(notebook_path)

        if has_errors:
            with_errors += 1
            error_notebooks.append((path, errors))
            if logger:
                logger.error(f"✗ Errors found: {path.relative_to(Path.cwd())}")
                for error in errors:
                    logger.error(f"    {error}")
        else:
            clean += 1
            if logger:
                logger.info(f"✓ Clean: {path.relative_to(Path.cwd())}")

    return clean, with_errors, error_notebooks


def build_book(rebuild=False):
    """
    Build the JupyterBook 2 site.

    Args:
        rebuild: If True, rebuild all pages regardless of modification status
    """
    import subprocess

    cmd = ["jupyter", "book", "build", "--html"]
    if rebuild:
        cmd.append("--all")

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error building book: {e}")
        print(e.stderr)
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Build the JupyterBook 2 site with notebook execution and validation"
    )

    # Build options
    parser.add_argument(
        "--build",
        action="store_true",
        default=False,
        help="Build the book with jupyter-book build",
    )
    parser.add_argument(
        "--build-all",
        action="store_true",
        default=False,
        help="Rebuild all pages regardless of modification status",
    )

    # Notebook execution options
    parser.add_argument(
        "--skip-regeneration",
        action="store_true",
        default=False,
        help="Skip notebook execution before building",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=None,
        help="Maximum number of parallel workers for notebook execution (default: CPU count)",
    )
    parser.add_argument(
        "--notebook-timeout",
        type=int,
        default=600,
        help="Timeout per notebook in seconds (default: 600)",
    )

    # Notebook checking options
    parser.add_argument(
        "--check-notebooks",
        action="store_true",
        default=False,
        help="Check all notebooks for errors (no execution or build)",
    )

    args = parser.parse_args()

    # If --build-all is set, enable --build
    if args.build_all:
        args.build = True

    start_time = time.perf_counter()
    logger = setup_logging(start_time)

    logger.info("=" * 70)
    logger.info("Starting Jupyter Book build process")
    logger.info("=" * 70)

    try:
        # Find all notebooks
        notebooks = find_notebooks()
        logger.info(f"Found {len(notebooks)} notebooks")

        # Check notebooks for errors only
        if args.check_notebooks:
            logger.info("-" * 70)
            logger.info("Checking notebooks for errors")
            logger.info("-" * 70)

            clean, with_errors, error_notebooks = check_all_notebooks(notebooks, logger)

            logger.info("-" * 70)
            logger.info(f"Check complete: {clean} clean, {with_errors} with errors")
            logger.info("-" * 70)

            if with_errors > 0:
                logger.error(f"Found {with_errors} notebooks with errors")
                sys.exit(1)
            else:
                logger.info("All notebooks are clean!")
                sys.exit(0)

        # Execute notebooks (unless skipped)
        if not args.skip_regeneration:
            logger.info("-" * 70)
            logger.info("Executing notebooks")
            logger.info("-" * 70)

            successful, failed, failures = execute_all_notebooks(
                notebooks,
                max_workers=args.max_workers,
                timeout=args.notebook_timeout,
                logger=logger
            )

            logger.info("-" * 70)
            logger.info(f"Execution complete: {successful} successful, {failed} failed")
            logger.info("-" * 70)

            if failed > 0:
                logger.error(f"Failed to execute {failed} notebooks:")
                for path, error_msg in failures:
                    logger.error(f"  - {path.relative_to(Path.cwd())}: {error_msg}")

                # Continue to build even with failures (user can inspect)
                logger.warning("Continuing to build with failed notebooks...")
        else:
            logger.info("Skipping notebook regeneration (--skip-regeneration flag)")

        # Build the book
        if args.build:
            logger.info("-" * 70)
            logger.info("Building the book")
            logger.info("-" * 70)

            rebuild = args.build_all
            logger.info(f"Rebuild all pages: {rebuild}")

            build_success = build_book(rebuild=rebuild)
            logger.info(f"Build completed: {build_success}")

            if not build_success:
                logger.error("Book build failed")
                sys.exit(1)
        else:
            logger.info("No build requested (use --build to enable)")

        time_taken_min = (time.perf_counter() - start_time) / 60
        logger.info("=" * 70)
        logger.info(f"Process finished successfully in {time_taken_min:.1f} min")
        logger.info("=" * 70)

    except Exception:
        logger.exception("Unexpected error occurred")
        sys.exit(1)
