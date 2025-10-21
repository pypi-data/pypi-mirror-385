from __future__ import annotations

import datetime as _dt
import json
import re
from pathlib import Path
from typing import Callable, Iterable


def prepare_release_notes(repo: Path, version: str, dry_run: bool) -> str:
    path = repo / "CHANGELOG.md"
    if not path.exists():
        return f"Prompt Automation {version}"
    lines = path.read_text(encoding="utf-8").splitlines()
    try:
        idx = next(i for i, line in enumerate(lines) if line.strip().lower() == "## unreleased")
    except StopIteration:
        idx = None
    collected: list[str] = []
    end = len(lines)
    if idx is not None:
        i = idx + 1
        while i < len(lines) and not lines[i].startswith("## "):
            collected.append(lines[i])
            i += 1
        end = i
    collected = _trim(collected)
    if not collected:
        collected = ["- (no notable changes)"]
    today = _dt.date.today().isoformat()
    new_section = [f"## {version} - {today}"] + collected + [""]
    placeholder = ["## Unreleased", "- (no changes yet)", ""]
    if idx is None:
        new_lines = placeholder + new_section + lines
    else:
        new_lines = lines[:idx] + placeholder + lines[end:]
        insert = idx + len(placeholder)
        new_lines = new_lines[:insert] + new_section + new_lines[insert:]
    if not dry_run:
        path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    return "\n".join(collected)


def update_versions(repo: Path, version: str) -> None:
    pyproject = repo / "pyproject.toml"
    text = pyproject.read_text(encoding="utf-8")
    new_text, count = re.subn(r"^version\s*=\s*\"[^\"]+\"", f"version = \"{version}\"", text, count=1, flags=re.MULTILINE)
    if count == 0:
        raise ValueError("version key not found in pyproject.toml")
    pyproject.write_text(new_text, encoding="utf-8")
    manifest = repo / "espanso-package" / "_manifest.yml"
    if manifest.exists():
        data, mcount = re.subn(r"(version:\s*)([^\s]+)", rf"\g<1>{version}", manifest.read_text(encoding="utf-8"), count=1)
        if mcount:
            manifest.write_text(data, encoding="utf-8")


def collect_artifacts(repo: Path) -> list[Path]:
    dist = repo / "dist" / "packagers"
    return sorted(p for p in dist.rglob("*") if p.is_file()) if dist.exists() else []


def check_artifact_sizes(paths: Iterable[Path], warn: Callable[[str], None]) -> list[str]:
    warnings: list[str] = []
    for path in paths:
        size_mb = path.stat().st_size / (1024 * 1024)
        if path.suffix.lower() == ".exe" and size_mb > 150:
            msg = f"{path.name} exceeds 150MB ({size_mb:.1f}MB)"
            warnings.append(msg)
            warn(msg)
        if path.suffix.lower() in {".pkg", ".dmg"} and size_mb > 200:
            msg = f"{path.name} exceeds 200MB ({size_mb:.1f}MB)"
            warnings.append(msg)
            warn(msg)
    return warnings


def guess_content_type(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".exe":
        return "application/vnd.microsoft.portable-executable"
    if suffix in {".msi", ".msp"}:
        return "application/x-msi"
    if suffix == ".pkg":
        return "application/vnd.apple.installer+xml"
    if suffix == ".dmg":
        return "application/x-apple-diskimage"
    if suffix in {".zip", ".whl"}:
        return "application/zip"
    if suffix in {".gz", ".tgz", ".tar"}:
        return "application/gzip"
    return "application/octet-stream"


def _trim(lines: list[str]) -> list[str]:
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return lines


def log_preview(entry: dict[str, object]) -> str:
    return json.dumps(entry, ensure_ascii=False)


__all__ = [
    "prepare_release_notes",
    "update_versions",
    "collect_artifacts",
    "check_artifact_sizes",
    "guess_content_type",
    "log_preview",
]

