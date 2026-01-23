from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import requests
from packaging.version import InvalidVersion, Version


@dataclass(frozen=True)
class UpdateInfo:
    current_version: str
    latest_version: str
    latest_tag: str
    html_url: Optional[str]

    @property
    def update_available(self) -> bool:
        try:
            return Version(self.latest_version) > Version(self.current_version)
        except InvalidVersion:
            return False


class UpdateCheckError(RuntimeError):
    pass


def _normalize_tag_to_version(tag: str) -> str:
    tag = (tag or "").strip()
    if tag.lower().startswith("v"):
        tag = tag[1:]
    return tag


def get_current_version() -> str:
    # Prefer an explicit env override (useful for ad-hoc builds)
    import os

    env_ver = os.getenv("IMAGE_PROCESSOR_VERSION")
    if env_ver:
        return env_ver.strip()

    # Prefer version.py in repo / bundled app
    try:
        from version import __version__  # type: ignore

        return str(__version__).strip()
    except Exception:
        return "0.0.0.dev0"


def _github_get_json(url: str, timeout_seconds: float = 10.0) -> dict:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "images_py-update-checker",
    }

    try:
        response = requests.get(url, headers=headers, timeout=timeout_seconds)
    except requests.RequestException as exc:
        raise UpdateCheckError(f"GitHub request failed: {exc}") from exc

    # Rate-limit or forbidden
    if response.status_code == 403:
        remaining = response.headers.get("X-RateLimit-Remaining")
        if remaining == "0":
            raise UpdateCheckError("GitHub API rate limit reached. Try again later.")

    if response.status_code >= 400:
        raise UpdateCheckError(f"GitHub API error {response.status_code}: {response.text[:200]}")

    try:
        return response.json()
    except ValueError as exc:
        raise UpdateCheckError("GitHub API returned invalid JSON") from exc


def get_latest_github_release(owner: str, repo: str) -> tuple[str, str, Optional[str]]:
    """Returns (latest_version, latest_tag, html_url).

    Uses releases/latest first; falls back to tags if no releases exist.
    """

    releases_url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
    try:
        payload = _github_get_json(releases_url)
        tag = str(payload.get("tag_name") or "").strip()
        html_url = payload.get("html_url")
        version = _normalize_tag_to_version(tag)
        if version:
            return version, tag, html_url
    except UpdateCheckError:
        # fall back to tags
        pass

    tags_url = f"https://api.github.com/repos/{owner}/{repo}/tags?per_page=1"
    payload = _github_get_json(tags_url)
    if not isinstance(payload, list) or not payload:
        raise UpdateCheckError("No releases or tags found on GitHub")

    tag = str(payload[0].get("name") or "").strip()
    version = _normalize_tag_to_version(tag)
    if not version:
        raise UpdateCheckError("Latest GitHub tag is missing a version")

    # Tags endpoint does not include a nice html_url for a release.
    return version, tag, f"https://github.com/{owner}/{repo}/releases/tag/{tag}"


def check_for_update(owner: str, repo: str, current_version: Optional[str] = None) -> UpdateInfo:
    current = (current_version or get_current_version()).strip()
    latest_version, latest_tag, html_url = get_latest_github_release(owner, repo)

    # Validate versions for comparison; if invalid, still return info.
    try:
        Version(current)
        Version(latest_version)
    except InvalidVersion:
        pass

    return UpdateInfo(
        current_version=current,
        latest_version=latest_version,
        latest_tag=latest_tag,
        html_url=html_url,
    )
