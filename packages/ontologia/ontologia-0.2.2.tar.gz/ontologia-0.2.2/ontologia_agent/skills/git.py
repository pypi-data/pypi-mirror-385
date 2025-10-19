"""Git helpers for ontologia agents."""

from __future__ import annotations

import re
from collections.abc import Iterable
from pathlib import Path

from git import Actor, Repo
from git.exc import InvalidGitRepositoryError, NoSuchPathError


def _slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value)
    return value.strip("-") or "change"


class GitSkill:
    """Lightweight wrapper around GitPython for agent automation."""

    def __init__(self, root: Path) -> None:
        try:
            self.repo = Repo(root)
        except (InvalidGitRepositoryError, NoSuchPathError):
            self.repo = Repo.init(root)
        self.root = root

    def ensure_branch(self, raw_name: str) -> str:
        normalized = raw_name.strip()
        if "/" not in normalized:
            normalized = f"feat/{_slugify(normalized)}"
        existing = next((head for head in self.repo.heads if head.name == normalized), None)
        branch = existing or self.repo.create_head(normalized)
        branch.checkout()
        return normalized

    def stage(self, file_paths: Iterable[Path]) -> None:
        rel_paths = [str(path.relative_to(self.root)) for path in file_paths]
        self.repo.index.add(rel_paths)

    def commit(self, message: str, *, author: str | None = None, email: str | None = None) -> None:
        actor = Actor(author, email) if author and email else None
        self.repo.index.commit(message, author=actor, committer=actor)

    def has_changes(self) -> bool:
        return self.repo.is_dirty(untracked_files=True)
