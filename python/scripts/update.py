# /// script
# dependencies = ["anthropic", "httpx", "gitpython"]
# ///
"""Update data.json.gz from models.dev.

Usage:
    uv run scripts/update.py [--dry-run]
"""

import argparse
import difflib
import gzip
import json
import os
import re
import sys
from pathlib import Path

import git
import httpx

DATA_URL = "https://models.dev/api.json"
ROOT = Path(__file__).parent.parent.parent
DATA_PATH = ROOT / "python" / "src" / "models_dev" / "data.json.gz"
PYPROJECT_PATH = ROOT / "python" / "pyproject.toml"


def fetch_latest() -> str:
    """Fetch latest data as formatted JSON string."""
    resp = httpx.get(DATA_URL, timeout=30)
    resp.raise_for_status()
    return json.dumps(resp.json(), indent=2, sort_keys=True)


def load_current() -> str:
    """Load current data as formatted JSON string."""
    if not DATA_PATH.exists():
        return ""
    with gzip.open(DATA_PATH, "rt", encoding="utf-8") as f:
        return json.dumps(json.load(f), indent=2, sort_keys=True)


def compute_diff(old: str, new: str) -> str:
    """Compute unified diff."""
    old_lines = old.splitlines(keepends=True)
    new_lines = new.splitlines(keepends=True)
    diff = difflib.unified_diff(old_lines, new_lines, fromfile="old", tofile="new")
    return "".join(diff)


def generate_commit_message(diff: str) -> str:
    """Generate commit message using Anthropic API."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return "chore: update models data"

    import anthropic

    client = anthropic.Anthropic(api_key=api_key)
    prompt = (
        "Generate a commit message for this diff. Use conventional commits. Be concise. "
        "NEVER wrap code in ``` etc. Output just commit message. "
        "ABSOLUTELY no formatting, plain ASCII"
    )
    prompt = f"{prompt}\n\n{diff[:10000]}"
    resp = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.content[0].text.strip()


def get_version() -> str:
    content = PYPROJECT_PATH.read_text()
    match = re.search(r'^version = "(.+)"', content, re.MULTILINE)
    return match.group(1) if match else "0.0.0"


def bump_version() -> str:
    """Bump patch version and return new version."""
    content = PYPROJECT_PATH.read_text()
    old = get_version()
    parts = old.split(".")
    parts[-1] = str(int(parts[-1]) + 1)
    new = ".".join(parts)
    content = re.sub(r'^version = ".+"', f'version = "{new}"', content, flags=re.MULTILINE)
    PYPROJECT_PATH.write_text(content)
    return new


def save_data(data_str: str) -> None:
    """Save data to gzipped JSON."""
    with gzip.open(DATA_PATH, "wt", encoding="utf-8") as f:
        f.write(json.dumps(json.loads(data_str), separators=(",", ":")))


def commit(message: str) -> None:
    """Commit changes."""
    repo = git.Repo(ROOT)
    repo.index.add(["python/pyproject.toml", "python/src/models_dev/data.json.gz"])
    repo.index.commit(message)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    print("Fetching latest data...")
    new_data = fetch_latest()
    old_data = load_current()

    print("Computing diff...")
    diff = compute_diff(old_data, new_data)

    if not diff:
        print("No changes")
        return 0

    print(f"Changes detected ({len(diff)} chars)")
    print(diff[:500])

    print("Generating commit message...")
    message = generate_commit_message(diff)
    print(f"Message: {message}")

    if args.dry_run:
        print("Dry run, stopping")
        return 0

    print("Saving data...")
    save_data(new_data)

    print("Bumping version...")
    version = bump_version()
    print(f"New version: {version}")

    print("Committing...")
    commit(message)

    print("Done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
