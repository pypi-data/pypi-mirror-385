#!/usr/bin/env python3

import re
import subprocess
import sys
import os
from datetime import datetime

auto_commit = ["CHANGELOG.md"]

pyproject_path = "pyproject.toml"
cargo_paths = [
    "parser", "python_ext", "toktrie", "toktrie_hf_tokenizers",
    "toktrie_tiktoken", "toktrie_hf_downloader"
]
version_pattern = r'\nversion\s*=\s*"(\d+\.\d+\.\d+)([^"]*)"'


def get_current_version(file_path):
    with open(file_path, "r") as f:
        content = f.read()
    match = re.search(version_pattern, content)
    if match:
        return match.group(1)
    raise ValueError(f"Version not found in {file_path}")


def bump_patch_version(version: str):
    major, minor, patch = map(int, version.split("."))
    patch += 1
    return f"{major}.{minor}.{patch}"


def update_version_in_file(file_path, new_version):
    with open(file_path, "r") as f:
        content = f.read()

    new_content = re.sub(version_pattern, f'\nversion = "{new_version}"',
                         content)

    with open(file_path, "w") as f:
        f.write(new_content)


def check_in_and_tag(version):
    subprocess.run(["git", "add", pyproject_path] +
                   [p + "/Cargo.toml"
                    for p in cargo_paths] + ["Cargo.lock"] + auto_commit,
                   check=True)
    subprocess.run(["git", "commit", "-m", f"Bump version to {version}"],
                   check=True)
    subprocess.run(["git", "tag", f"v{version}"], check=True)
    subprocess.run(["git", "push"], check=True)
    subprocess.run(["git", "push", "--tags"], check=True)


def ensure_clean_working_tree():
    status_output = subprocess.run(["git", "status", "--porcelain"],
                                   capture_output=True,
                                   text=True).stdout
    num_changes = 0
    for l in status_output.splitlines():
        if l[3:] in auto_commit:
            # Ignore changes to CHANGELOG.md etc
            continue
        num_changes += 1
    if num_changes > 0:
        subprocess.run(["git", "status"])
        print(
            "\n\nWorking tree is not clean. Please commit or stash your changes before running this script.\n"
        )
        sys.exit(1)


def generate_changelog(version: str) -> str:
    try:
        result = subprocess.run([
            "auto-changelog", "--stdout", "--commit-limit", "false",
            "--unreleased-only"
        ],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                check=True,
                                text=True)
        text = result.stdout
        start = text.find("#### [Unreleased]")
        if start == -1:
            return ""
        trimmed = text[start:]
        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        replaced = re.sub(r"\[Unreleased\]", f"[v{version}]", trimmed)
        replaced = re.sub(r"\.\.\.HEAD\)", f"...v{version}) {date_str}", replaced)
        return replaced
    except FileNotFoundError:
        return "auto-changelog is not installed. Run `npm install -g auto-changelog` to install it."


def main():
    #subprocess.run(["python3", "./scripts/update-git.py"], check=True)

    current_version = get_current_version(pyproject_path)
    if len(sys.argv) > 1:
        suggested_version = sys.argv[1]
    else:
        suggested_version = bump_patch_version(current_version)

    changelog = generate_changelog(suggested_version)
    print("\n\n" + changelog + "\n\n")

    ensure_clean_working_tree()

    print(f"Current version: {current_version}")
    new_version = (input(f"Enter new version (default: {suggested_version}): ")
                   or suggested_version)

    update_version_in_file(pyproject_path, new_version.replace("-", ""))

    for p in cargo_paths:
        update_version_in_file(p + "/Cargo.toml", new_version)
    subprocess.run(["cargo", "check"], check=True)

    check_in_and_tag(new_version)


if __name__ == "__main__":
    main()
