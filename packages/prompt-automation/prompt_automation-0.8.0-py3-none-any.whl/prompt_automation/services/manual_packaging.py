from __future__ import annotations

import datetime as _dt
import json
import os
import re
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Sequence
from urllib import error as urllib_error
from urllib import request as urllib_request

from ..config import LOG_DIR, ENV_LOG_DIR, HOME_DIR
from ..espanso_sync import _find_repo_root
from .manual_packaging_utils import (
    check_artifact_sizes,
    collect_artifacts,
    guess_content_type,
    log_preview,
    prepare_release_notes,
    update_versions,
)

CommandRunner = Callable[[Sequence[str], Path, dict[str, str] | None], subprocess.CompletedProcess]


class _VersionSnapshot:
    """Capture and restore key release files if packaging fails."""

    def __init__(self, repo: Path) -> None:
        self._repo = repo
        self._contents: dict[Path, bytes] = {}

    def capture(self) -> None:
        for rel in ("pyproject.toml", "CHANGELOG.md", "espanso-package/_manifest.yml"):
            path = self._repo / rel
            if path.exists():
                self._contents[path] = path.read_bytes()

    def restore(self) -> None:
        for path, payload in self._contents.items():
            try:
                path.write_bytes(payload)
            except Exception:
                continue


@dataclass(slots=True)
class ManualPackagingRequest:
    version: str | None = None
    verbose_logs: bool = False
    dry_run: bool = False
    run_tests: bool = True
    release_notes: str | None = None


@dataclass(slots=True)
class PackagingEvent:
    kind: str
    message: str
    level: str = "info"
    data: dict[str, object] | None = None


@dataclass(slots=True)
class PackagingOutcome:
    success: bool
    errors: list[str]
    warnings: list[str]
    artifacts: list[Path]
    release_url: str | None = None
    log_path: Path | None = None


@dataclass(frozen=True)
class ReleaseInfo:
    upload_url: str
    html_url: str
    tag_name: str
    id: int = 0


class ManualPackagingError(RuntimeError):
    def __init__(self, code: str, message: str, detail: str | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.detail = detail


def _default_command_runner(cmd: Sequence[str], repo: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=str(repo), env=env, text=True, capture_output=True)


class GitHubClient:
    _API = "https://api.github.com"

    def __init__(self, owner_repo: str, token: str) -> None:
        self.owner_repo = owner_repo
        self.token = token.strip()

    def _request(self, method: str, url: str, *, data: bytes | None = None, headers: dict[str, str] | None = None):
        hdrs = {"Authorization": f"Bearer {self.token}", "Accept": "application/vnd.github+json"}
        if headers:
            hdrs.update(headers)
        req = urllib_request.Request(url, data=data, headers=hdrs, method=method)
        return urllib_request.urlopen(req, timeout=30)

    def ensure_release(self, tag: str, name: str, body: str) -> ReleaseInfo:
        url = f"{self._API}/repos/{self.owner_repo}/releases/tags/{tag}"
        try:
            with self._request("GET", url) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
        except urllib_error.HTTPError as exc:
            if exc.code != 404:
                raise
            create_url = f"{self._API}/repos/{self.owner_repo}/releases"
            data = json.dumps({"tag_name": tag, "name": name, "body": body, "draft": False}).encode("utf-8")
            with self._request("POST", create_url, data=data, headers={"Content-Type": "application/json"}) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
        upload = str(payload.get("upload_url", "")).split("{", 1)[0]
        return ReleaseInfo(upload_url=upload, html_url=str(payload.get("html_url", "")), tag_name=str(payload.get("tag_name", tag)), id=int(payload.get("id", 0) or 0))

    def upload_asset(self, release: ReleaseInfo, artifact: Path, *, content_type: str | None = None) -> None:
        url = f"{release.upload_url}?name={artifact.name}"
        with artifact.open("rb") as fh:
            data = fh.read()
        self._request("POST", url, data=data, headers={"Content-Type": content_type or "application/octet-stream"})


class PackagingOrchestrator:
    _SEMVER = re.compile(r"^(\d+)\.(\d+)\.(\d+)(?:[.-]?([A-Za-z0-9]+))?$")

    def __init__(
        self,
        *,
        repo_root: Path | None = None,
        command_runner: CommandRunner | None = None,
        github_client_factory: Callable[[str, str], GitHubClient] | None = None,
        log_dir: Path | None = None,
    ) -> None:
        self._repo_root = Path(repo_root).resolve() if repo_root else None
        self._runner = command_runner or _default_command_runner
        self._factory = github_client_factory or (lambda owner_repo, token: GitHubClient(owner_repo, token))
        if log_dir is not None:
            self._log_dir = Path(log_dir)
        else:
            env_log_dir = os.environ.get(ENV_LOG_DIR)
            self._log_dir = Path(env_log_dir) if env_log_dir else LOG_DIR
        self._listeners: list[Callable[[PackagingEvent], None]] = []
        self._cancel = threading.Event()
        self._log_path: Path | None = None
        self._verbose = False

    def add_listener(self, callback: Callable[[PackagingEvent], None]) -> None:
        if callback not in self._listeners:
            self._listeners.append(callback)

    def cancel(self) -> None:
        self._cancel.set()

    def run(
        self, request: ManualPackagingRequest, listener: Callable[[PackagingEvent], None] | None = None
    ) -> PackagingOutcome:
        if listener:
            self.add_listener(listener)
        self._cancel.clear()
        self._start_log()
        self._verbose = request.verbose_logs
        errors: list[str] = []
        warnings: list[str] = []
        artifacts: list[Path] = []
        release_url: str | None = None
        success = False
        version_snapshot: _VersionSnapshot | None = None
        try:
            repo = (self._repo_root or _find_repo_root(None)).resolve()
            self._repo_root = repo
            self._status(f"Manual packaging started ({repo})")
            self._log("info", "start", repo=str(repo), dry_run=request.dry_run)
            self._ensure_clean(repo)
            remote = self._git_remote(repo)
            owner_repo = self._parse_owner_repo(remote)
            current = self._read_pyproject(repo)
            manifest = self._read_manifest(repo)
            if manifest and manifest != current:
                warnings.append("manifest_version_mismatch")
                self._log("warning", "manifest_mismatch", manifest=manifest, pyproject=current)
            version = self._resolve_version(request.version, current)
            if not request.dry_run:
                version_snapshot = _VersionSnapshot(repo)
                version_snapshot.capture()
            notes = request.release_notes or prepare_release_notes(repo, version, request.dry_run)
            if not request.dry_run:
                try:
                    update_versions(repo, version)
                except ValueError as exc:
                    raise ManualPackagingError("version_missing", str(exc)) from exc
            if request.run_tests:
                self._ensure_test_dependencies()
                result = self._run([sys.executable, "-m", "pytest", "-q"], repo, "tests")
                if result.returncode != 0:
                    errors.append("tests_failed")
                    self._log("error", "tests_failed", stdout=result.stdout, stderr=result.stderr)
                    self._status("Test suite failed", level="error")
                    return PackagingOutcome(False, errors, warnings, artifacts, None, self._log_path)
            env = os.environ.copy()
            env.setdefault("PROMPT_AUTOMATION_REPO", str(repo))
            self._run([sys.executable, "-m", "packagers.build_all"], repo, "packagers", env=env)
            artifacts = collect_artifacts(repo)
            self._log("info", "artifacts", count=len(artifacts))
            warnings.extend(check_artifact_sizes(artifacts, lambda msg: self._status(msg, level="warning")))
            if request.dry_run:
                self._status("Dry run completed", level="info")
                self._log("info", "dry_run_complete", artifacts=[str(a) for a in artifacts])
                return PackagingOutcome(True, errors, warnings, artifacts, None, self._log_path)
            self._git_commit(repo, version)
            tag = f"v{version}"
            self._run(["git", "tag", "-a", tag, "-m", f"release v{version}"], repo, "git_tag")
            self._run(["git", "push", "origin", tag], repo, "git_push_tag")
            token = self._github_token()
            if not token:
                raise ManualPackagingError("github_token", "GitHub token not found. Configure PROMPT_AUTOMATION_GITHUB_TOKEN")
            client = self._factory(owner_repo, token)
            release = client.ensure_release(tag, f"Prompt Automation v{version}", notes)
            for artifact in artifacts:
                client.upload_asset(release, artifact, content_type=guess_content_type(artifact))
            release_url = release.html_url or f"https://github.com/{owner_repo}/releases/tag/{tag}"
            self._status("Manual packaging finished", level="info")
            self._log("info", "complete", release_url=release_url)
            success = True
            return PackagingOutcome(True, errors, warnings, artifacts, release_url, self._log_path)
        except ManualPackagingError as exc:
            msg = f"{exc.code}: {exc}"
            errors.append(msg)
            self._status(msg, level="error")
            self._log("error", "failure", code=exc.code, detail=exc.detail)
        except Exception as exc:
            errors.append(str(exc))
            self._status(str(exc), level="error")
            self._log("error", "exception", message=str(exc))
        finally:
            if version_snapshot and not success:
                version_snapshot.restore()
                self._log("info", "restored_versions")
            self._log("info", "summary", errors=len(errors), warnings=len(warnings))
        return PackagingOutcome(False, errors, warnings, artifacts, release_url, self._log_path)

    def suggest_version(self) -> str:
        repo = (self._repo_root or _find_repo_root(None)).resolve()
        current = self._read_pyproject(repo)
        return self._resolve_version(None, current)

    # --- helpers -----------------------------------------------------
    def _start_log(self) -> None:
        self._log_dir.mkdir(parents=True, exist_ok=True)
        stamp = time.strftime("%Y%m%d-%H%M%S")
        self._log_path = self._log_dir / f"manual-packaging-{stamp}.log"
        self._log_path.write_text(json.dumps({"ts": stamp, "status": "start"}) + "\n", encoding="utf-8")

    def _emit(self, event: PackagingEvent) -> None:
        for callback in list(self._listeners):
            try:
                callback(event)
            except Exception:
                pass

    def _status(self, message: str, *, level: str = "info") -> None:
        self._emit(PackagingEvent(kind="log", message=message, level=level))

    def _log(self, status: str, step: str, **extra: object) -> None:
        entry = {"ts": _dt.datetime.now(_dt.timezone.utc).isoformat(), "status": status, "step": step, **extra}
        if self._log_path:
            with self._log_path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
        if status in {"warning", "error"} or self._verbose:
            self._emit(PackagingEvent(kind="log", message=log_preview(entry), level=status))

    def _run(self, cmd: Sequence[str], repo: Path, step: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
        if self._cancel.is_set():
            raise ManualPackagingError("cancelled", "Packaging cancelled")
        self._status(f"Running {' '.join(cmd)}")
        result = self._runner(cmd, repo, env)
        self._log("info" if result.returncode == 0 else "error", step, command=" ".join(cmd), returncode=result.returncode)
        if result.returncode != 0:
            raise ManualPackagingError(step, f"Command failed with exit code {result.returncode}", detail=result.stderr)
        return result

    def _ensure_test_dependencies(self) -> None:
        try:
            import pytest  # type: ignore
        except ModuleNotFoundError:
            self._status("Installing pytest for manual packaging", level="info")
            install = subprocess.run(
                [sys.executable, "-m", "pip", "install", "pytest"],
                capture_output=True,
                text=True,
            )
            if install.returncode != 0:
                detail = install.stderr.strip() if install.stderr else ""
                raise ManualPackagingError(
                    "tests_deps",
                    "Failed to install pytest; install prompt-automation with the [tests] extra",
                    detail=detail,
                )

    def _ensure_clean(self, repo: Path) -> None:
        res = self._runner(["git", "status", "--porcelain"], repo, None)
        if res.returncode != 0:
            raise ManualPackagingError("git_status", "Failed to read git status", detail=res.stderr)
        if res.stdout.strip():
            raise ManualPackagingError("git_dirty", "Working tree has uncommitted changes")

    def _git_remote(self, repo: Path) -> str:
        res = self._runner(["git", "remote", "get-url", "origin"], repo, None)
        if res.returncode != 0:
            raise ManualPackagingError("git_remote", "Unable to resolve git remote", detail=res.stderr)
        return res.stdout.strip()

    def _parse_owner_repo(self, remote: str) -> str:
        if remote.startswith("git@github.com:"):
            tail = remote.split(":", 1)[1]
        elif remote.startswith("https://github.com/"):
            tail = remote.split("github.com/", 1)[1]
        elif remote.startswith("ssh://") and "github.com" in remote:
            tail = remote.split("github.com", 1)[1].lstrip(":/")
        else:
            raise ManualPackagingError("github_remote", "Remote origin is not a GitHub URL")
        if tail.endswith(".git"):
            tail = tail[:-4]
        if tail.count("/") != 1:
            raise ManualPackagingError("github_remote", "Unable to parse GitHub owner/repo from remote")
        return tail

    def _read_pyproject(self, repo: Path) -> str:
        text = (repo / "pyproject.toml").read_text(encoding="utf-8")
        match = re.search(r"^version\s*=\s*\"([^\"]+)\"", text, re.MULTILINE)
        if not match:
            raise ManualPackagingError("version_missing", "version not found in pyproject.toml")
        return match.group(1)

    def _read_manifest(self, repo: Path) -> str | None:
        path = repo / "espanso-package" / "_manifest.yml"
        if not path.exists():
            return None
        match = re.search(r"version:\s*([0-9A-Za-z_.-]+)", path.read_text(encoding="utf-8"))
        return match.group(1) if match else None

    def _resolve_version(self, requested: str | None, current: str) -> str:
        if requested:
            if not self._SEMVER.match(requested):
                raise ManualPackagingError("version_invalid", "Provided version is not semantic")
            return requested
        match = self._SEMVER.match(current)
        if not match:
            raise ManualPackagingError("version_invalid", "Current version is not semantic")
        major, minor, patch = (int(match.group(i)) for i in range(1, 4))
        return f"{major}.{minor}.{patch + 1}"

    def _git_commit(self, repo: Path, version: str) -> None:
        files = ["pyproject.toml", "CHANGELOG.md", "espanso-package/_manifest.yml"]
        self._run(["git", "add", *files], repo, "git_add")
        res = self._runner(["git", "commit", "-m", f"release: v{version}"], repo, None)
        if res.returncode not in {0, 1}:
            raise ManualPackagingError("git_commit", "Failed to create release commit", detail=res.stderr)
        if res.returncode == 1 and "nothing to commit" not in (res.stderr or "").lower():
            raise ManualPackagingError("git_commit", "Failed to create release commit", detail=res.stderr)
        self._log("info", "git_commit", returncode=res.returncode)

    def _github_token(self) -> str | None:
        for key in ("PROMPT_AUTOMATION_GITHUB_TOKEN", "GITHUB_TOKEN", "GH_TOKEN"):
            val = os.environ.get(key)
            if val:
                return val.strip()
        env_file = HOME_DIR / "environment"
        if env_file.exists():
            for line in env_file.read_text(encoding="utf-8").splitlines():
                if "=" in line and not line.lstrip().startswith("#"):
                    key, value = line.split("=", 1)
                    if key.strip() in {"PROMPT_AUTOMATION_GITHUB_TOKEN", "GITHUB_TOKEN", "GH_TOKEN"}:
                        return value.strip()
        return None


__all__ = [
    "ManualPackagingRequest",
    "PackagingEvent",
    "PackagingOutcome",
    "PackagingOrchestrator",
    "ManualPackagingError",
    "ReleaseInfo",
]
