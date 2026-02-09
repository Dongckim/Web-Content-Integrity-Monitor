"""Tests for html2md: argument validation and CSV handling."""
import os
import subprocess
import sys

import pytest

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML2MD = os.path.join(SCRIPT_DIR, "html2md")
FIXTURES = os.path.join(SCRIPT_DIR, "tests", "fixtures")


def run_html2md(csv_file: str, output_dir: str):
    """Run html2md as subprocess. Returns (returncode, stdout, stderr)."""
    result = subprocess.run(
        [sys.executable, HTML2MD, csv_file, output_dir],
        cwd=SCRIPT_DIR,
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout, result.stderr


def test_usage_on_no_args():
    """Without arguments, html2md exits with 1."""
    result = subprocess.run(
        [sys.executable, HTML2MD],
        cwd=SCRIPT_DIR,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "Usage" in result.stderr or "csv" in result.stderr.lower()


def test_missing_csv_exits_with_error():
    """When CSV file does not exist, html2md exits with 1."""
    with __import__("tempfile").TemporaryDirectory() as tmp:
        code, out, err = run_html2md("/nonexistent/input.csv", tmp)
    assert code == 1
    assert "not found" in err.lower() or "CSV" in err or "No such" in err


def test_local_html_conversion():
    """With a file:// URL to local HTML (mw-parser-output), html2md converts and creates archive."""
    import tempfile

    fixtures = os.path.join(SCRIPT_DIR, "tests", "fixtures")
    html_path = os.path.join(fixtures, "minimal_mw.html")
    if not os.path.isfile(html_path):
        pytest.skip("fixtures/minimal_mw.html not found")

    # file:// URL must be absolute
    file_url = "file://" + html_path
    if os.name == "nt":
        file_url = "file:///" + html_path.replace("\\", "/")

    with tempfile.TemporaryDirectory() as tmp:
        csv_path = os.path.join(tmp, "input.csv")
        with open(csv_path, "w", encoding="utf-8") as f:
            f.write(f"Sample Page|{file_url}|2020-01-01\n")

        code, out, err = run_html2md(csv_path, tmp)

    assert code == 0
    assert "Converted" in out
    assert "sample_page.md" in out or "Sample Page" in out
    assert "Archive created" in out or "tar.gz" in out
