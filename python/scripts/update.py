# /// script
# dependencies = ["anthropic", "httpx", "gitpython", "models-dev"]
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
NODE_PACKAGE_PATH = ROOT / "node" / "package.json"


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


MODEL_ID = "claude-haiku-4-5-20251001"


def generate_commit_message(diff: str) -> tuple[str, int, int]:
    """Generate commit message using Anthropic API. Returns (message, in_tokens, out_tokens)."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return "chore: update models data", 0, 0

    import anthropic

    client = anthropic.Anthropic(api_key=api_key)
    prompt = (
        "Generate a commit message for this diff. Use conventional commits. Be concise. "
        "NEVER wrap code in ``` etc. Output just commit message. "
        "ABSOLUTELY no formatting, plain ASCII"
    )
    prompt = f"{prompt}\n\n{diff[:10000]}"
    resp = client.messages.create(
        model=MODEL_ID,
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.content[0].text.strip(), resp.usage.input_tokens, resp.usage.output_tokens


def print_token_stats(input_tokens: int, output_tokens: int) -> None:
    """Print token usage and cost using models-dev pricing."""
    from models_dev import get_model_by_id

    model = get_model_by_id("anthropic", MODEL_ID)
    if not model.cost:
        print(f"Tokens: {input_tokens} in, {output_tokens} out (no pricing data)")
        return

    input_cost = (input_tokens / 1_000_000) * (model.cost.input or 0)
    output_cost = (output_tokens / 1_000_000) * (model.cost.output or 0)
    total_cost = input_cost + output_cost

    print(f"Tokens: {input_tokens} in, {output_tokens} out")
    print(f"Cost: ${total_cost:.6f} (${model.cost.input}/M in, ${model.cost.output}/M out)")


def get_version() -> str:
    content = PYPROJECT_PATH.read_text()
    match = re.search(r'^version = "(.+)"', content, re.MULTILINE)
    return match.group(1) if match else "0.0.0"


def bump_version() -> str:
    """Bump patch version in pyproject.toml and package.json. Returns new version."""
    content = PYPROJECT_PATH.read_text()
    old = get_version()
    parts = old.split(".")
    parts[-1] = str(int(parts[-1]) + 1)
    new = ".".join(parts)
    content = re.sub(r'^version = ".+"', f'version = "{new}"', content, flags=re.MULTILINE)
    PYPROJECT_PATH.write_text(content)

    # Update node package.json
    pkg = json.loads(NODE_PACKAGE_PATH.read_text())
    pkg["version"] = new
    NODE_PACKAGE_PATH.write_text(json.dumps(pkg, indent=2) + "\n")

    return new


def save_data(data_str: str) -> None:
    """Save data to gzipped JSON."""
    with gzip.open(DATA_PATH, "wt", encoding="utf-8") as f:
        f.write(json.dumps(json.loads(data_str), separators=(",", ":")))


def get_action_url() -> str | None:
    """Get GitHub Action run URL from environment."""
    server = os.environ.get("GITHUB_SERVER_URL")
    repo = os.environ.get("GITHUB_REPOSITORY")
    run_id = os.environ.get("GITHUB_RUN_ID")
    if server and repo and run_id:
        return f"{server}/{repo}/actions/runs/{run_id}"
    return None


def commit(message: str) -> None:
    """Commit changes."""
    action_url = get_action_url()
    if action_url:
        message = f"{message}\n\nAction: {action_url}"

    repo = git.Repo(ROOT)
    repo.index.add([
        "python/pyproject.toml",
        "python/src/models_dev/data.json.gz",
        "node/package.json",
    ])
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

    # Signal to GitHub Actions that changes occurred
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a") as f:
            f.write("changes=true\n")

    print(f"Changes detected ({len(diff)} chars)")
    print(diff[:500])

    print("Generating commit message...")
    message, input_tokens, output_tokens = generate_commit_message(diff)
    print(f"Message: {message}")
    print_token_stats(input_tokens, output_tokens)

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
