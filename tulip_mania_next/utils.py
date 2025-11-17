#!/usr/bin/env python3
"""
Scan Jupyter notebooks in a folder and report any cells that contain errors.
Produces a pandas DataFrame and (optionally) a CSV, plus a readable console summary.
"""

from __future__ import annotations

import shutil
import os


# "C:\Users\IgnaciodeRamónJacob-\AppData\Local\Temp\EBWebView"


def delete_temp_folder():
    """Delete the temporary folder used by EBWebView."""

    temp_path = os.path.join(os.environ["TEMP"], "EBWebView")
    if os.path.exists(temp_path):
        try:
            shutil.rmtree(temp_path)
            print(f"Successfully deleted {temp_path}")
        except Exception as e:
            print(f"Error deleting {temp_path}: {e}")
