# /// script
# dependencies = ["anthropic", "httpx"]
# ///
"""Update data.json.gz and generate commit message.

Usage:
    uv run scripts/update.py [--dry-run]

Environment variables:
    ANTHROPIC_API_KEY - Required for generating commit messages

Outputs (for CI):
    changed=true/false
    version=X.Y.Z
    commit_message=...
"""

import argparse
import gzip
import json
import os
import re
import sys
from pathlib import Path

import httpx

DATA_URL = "https://models.dev/api.json"
DATA_PATH = Path(__file__).parent.parent / "src" / "models_dev" / "data.json.gz"
PYPROJECT_PATH = Path(__file__).parent.parent / "pyproject.toml"


def fetch_latest() -> dict:
    """Fetch latest data from models.dev."""
    resp = httpx.get(DATA_URL, timeout=30)
    resp.raise_for_status()
    return resp.json()


def load_current() -> dict | None:
    """Load current data.json.gz if it exists."""
    if not DATA_PATH.exists():
        return None
    with gzip.open(DATA_PATH, "rt", encoding="utf-8") as f:
        return json.load(f)


def compute_diff(old: dict | None, new: dict) -> dict:
    """Compute diff between old and new data."""
    if old is None:
        return {
            "added_providers": list(new.keys()),
            "removed_providers": [],
            "added_models": sum(len(p["models"]) for p in new.values()),
            "removed_models": 0,
            "changed_models": 0,
        }

    old_providers = set(old.keys())
    new_providers = set(new.keys())

    added_providers = new_providers - old_providers
    removed_providers = old_providers - new_providers

    added_models = 0
    removed_models = 0
    changed_models = 0

    for pid in new_providers & old_providers:
        old_models = set(old[pid]["models"].keys())
        new_models = set(new[pid]["models"].keys())

        added_models += len(new_models - old_models)
        removed_models += len(old_models - new_models)

        for mid in old_models & new_models:
            if old[pid]["models"][mid] != new[pid]["models"][mid]:
                changed_models += 1

    for pid in added_providers:
        added_models += len(new[pid]["models"])

    for pid in removed_providers:
        removed_models += len(old[pid]["models"])

    return {
        "added_providers": list(added_providers),
        "removed_providers": list(removed_providers),
        "added_models": added_models,
        "removed_models": removed_models,
        "changed_models": changed_models,
    }


def generate_commit_message(diff: dict) -> str:
    """Generate commit message using Anthropic API."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return _fallback_commit_message(diff)

    import anthropic

    client = anthropic.Anthropic(api_key=api_key)

    prompt = f"""Generate a short git commit message for a data update to models.dev package.

Changes:
- Added providers: {diff['added_providers'] or 'none'}
- Removed providers: {diff['removed_providers'] or 'none'}
- Added models: {diff['added_models']}
- Removed models: {diff['removed_models']}
- Changed models: {diff['changed_models']}

Rules:
- Use conventional commits format (chore: or feat:)
- Be concise, one line, under 72 chars
- Focus on what's most significant
- Don't mention version numbers"""

    resp = client.messages.create(
        model="claude-haiku-4-20250514",
        max_tokens=100,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.content[0].text.strip()


def _fallback_commit_message(diff: dict) -> str:
    """Fallback commit message when API unavailable."""
    parts = []
    if diff["added_providers"]:
        parts.append(f"add {', '.join(diff['added_providers'][:3])}")
    if diff["added_models"]:
        parts.append(f"+{diff['added_models']} models")
    if diff["removed_models"]:
        parts.append(f"-{diff['removed_models']} models")
    if diff["changed_models"]:
        parts.append(f"~{diff['changed_models']} updated")

    if parts:
        return f"chore: update data ({', '.join(parts)})"
    return "chore: update data"


def get_current_version() -> str:
    """Get current version from pyproject.toml."""
    content = PYPROJECT_PATH.read_text()
    match = re.search(r'^version = "(.+)"', content, re.MULTILINE)
    if not match:
        raise ValueError("Could not find version in pyproject.toml")
    return match.group(1)


def bump_patch_version(version: str) -> str:
    """Bump patch version."""
    parts = version.split(".")
    parts[-1] = str(int(parts[-1]) + 1)
    return ".".join(parts)


def set_version(version: str) -> None:
    """Update version in pyproject.toml."""
    content = PYPROJECT_PATH.read_text()
    content = re.sub(r'^version = ".+"', f'version = "{version}"', content, flags=re.MULTILINE)
    PYPROJECT_PATH.write_text(content)


def save_data(data: dict) -> None:
    """Save data to gzipped JSON."""
    with gzip.open(DATA_PATH, "wt", encoding="utf-8") as f:
        json.dump(data, f, separators=(",", ":"))


def output_github(key: str, value: str) -> None:
    """Output value for GitHub Actions."""
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a") as f:
            if "\n" in value:
                # Multiline value
                f.write(f"{key}<<EOF\n{value}\nEOF\n")
            else:
                f.write(f"{key}={value}\n")
    print(f"{key}={value}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Update models.dev data")
    parser.add_argument("--dry-run", action="store_true", help="Don't write changes")
    args = parser.parse_args()

    print("Fetching latest data...")
    new_data = fetch_latest()
    old_data = load_current()

    print("Computing diff...")
    diff = compute_diff(old_data, new_data)

    has_changes = (
        diff["added_providers"]
        or diff["removed_providers"]
        or diff["added_models"]
        or diff["removed_models"]
        or diff["changed_models"]
    )

    if not has_changes:
        print("No changes detected")
        output_github("changed", "false")
        return 0

    print(f"Changes: {diff}")
    output_github("changed", "true")

    current_version = get_current_version()
    new_version = bump_patch_version(current_version)
    output_github("version", new_version)

    print("Generating commit message...")
    commit_message = generate_commit_message(diff)
    output_github("commit_message", commit_message)

    if args.dry_run:
        print("Dry run, not writing changes")
        return 0

    print(f"Saving data and bumping version to {new_version}...")
    save_data(new_data)
    set_version(new_version)

    return 0


if __name__ == "__main__":
    sys.exit(main())
