#!/usr/bin/env python3
"""
Main script for building and managing the JupyterBook 2 site.

This script provides utilities for building the book with proper logging.
Excludes version management and version-switcher functionality to keep it simple.
"""

import sys
import time
import logging
import argparse
from datetime import datetime
from pathlib import Path


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
    parser = argparse.ArgumentParser(description="Build the JupyterBook 2 site")
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

    args = parser.parse_args()
    if args.build_all:
        args.build = True

    start_time = time.perf_counter()
    logger = setup_logging(start_time)
    
    logger.info("Starting the book build process...")

    try:
        if args.build:
            logger.info("Building the book")
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
        logger.info(f"Process finished. It took {time_taken_min:.1f} min")

    except Exception:
        logger.exception("Unexpected error occurred")
        sys.exit(1)
