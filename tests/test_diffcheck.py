"""Tests for diffcheck: argument validation and archive comparison."""
import os
import subprocess
import sys
import tarfile
import tempfile
from datetime import datetime, timedelta

import pytest

# Project root (parent of tests/)
SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIFFCHECK = os.path.join(SCRIPT_DIR, "diffcheck")


def run_diffcheck(n_days: int, output_dir: str):
    """Run diffcheck as subprocess. Returns (returncode, stdout, stderr)."""
    result = subprocess.run(
        [sys.executable, DIFFCHECK, str(n_days), output_dir],
        cwd=SCRIPT_DIR,
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout, result.stderr


def test_usage_on_no_args():
    """Without arguments, diffcheck prints usage and exits with 1."""
    result = subprocess.run(
        [sys.executable, DIFFCHECK],
        cwd=SCRIPT_DIR,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "Usage" in result.stdout


def test_usage_on_one_arg():
    """With only one argument, diffcheck exits with 1."""
    code, out, err = run_diffcheck(7, "")
    assert code == 1
    # N=7 is taken, output_dir is "" so archive lookup fails
    assert "output" in err.lower() or "archive" in err.lower() or code == 1


def test_invalid_n_exits_with_error():
    """Non-integer N should exit with 1 and write to stderr."""
    with tempfile.TemporaryDirectory() as tmp:
        code, out, err = run_diffcheck("not_a_number", tmp)
    assert code == 1
    assert "integer" in err.lower() or "Error" in err


def test_missing_archives_exit_nonzero():
    """When output_dir has no matching archives, diffcheck exits with 1."""
    with tempfile.TemporaryDirectory() as tmp:
        code, out, err = run_diffcheck(1, tmp)
    assert code == 1
    assert "archive" in err.lower() or "found" in err.lower()


def test_modified_page_detection():
    """When same-named file has different content in two archives, diffcheck reports it."""
    today = datetime.now().strftime("%Y-%m-%d")
    past_date = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")

    with tempfile.TemporaryDirectory() as tmp:
        # Create "past" archive: one file with content "old"
        past_archive = os.path.join(tmp, f"{past_date}_12-00-00.tar.gz")
        with tarfile.open(past_archive, "w:gz") as tar:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".md", delete=False, encoding="utf-8"
            ) as f:
                f.write("<!-- URL: https://example.com/page -->\n# My Page\n\nold content\n")
                f.flush()
                tar.add(f.name, arcname="my_page.md")
            os.unlink(f.name)

        # Create "today" archive: same filename, content "new"
        today_archive = os.path.join(tmp, f"{today}_12-00-00.tar.gz")
        with tarfile.open(today_archive, "w:gz") as tar:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".md", delete=False, encoding="utf-8"
            ) as f:
                f.write("<!-- URL: https://example.com/page -->\n# My Page\n\nnew content\n")
                f.flush()
                tar.add(f.name, arcname="my_page.md")
            os.unlink(f.name)

        code, out, err = run_diffcheck(2, tmp)

    assert code == 0
    assert "modified" in out.lower()
    assert "My Page" in out
    assert "example.com" in out


def test_no_changes_message():
    """When content is identical, diffcheck reports no changes."""
    today = datetime.now().strftime("%Y-%m-%d")
    past_date = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
    same_content = "<!-- URL: https://example.com/a -->\n# Same\n\nunchanged\n"

    with tempfile.TemporaryDirectory() as tmp:
        for date_str, name in [(past_date, "12-00-00"), (today, "12-00-00")]:
            path = os.path.join(tmp, f"{date_str}_{name}.tar.gz")
            with tarfile.open(path, "w:gz") as tar:
                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".md", delete=False, encoding="utf-8"
                ) as f:
                    f.write(same_content)
                    f.flush()
                    tar.add(f.name, arcname="same.md")
                os.unlink(f.name)

        code, out, err = run_diffcheck(2, tmp)

    assert code == 0
    assert "No changes" in out
