"""Filesystem helpers for ontologia agents."""

from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path


class FilesystemSkill:
    """Read and write ontology definition files."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self.ontology_dir = self.project_root / "ontologia"
        self.object_dir = self.ontology_dir / "object_types"
        self.link_dir = self.ontology_dir / "link_types"

    def ensure_structure(self) -> None:
        for directory in (self.ontology_dir, self.object_dir, self.link_dir):
            directory.mkdir(parents=True, exist_ok=True)

    def iter_yaml_files(self) -> Iterable[Path]:
        for directory in (self.object_dir, self.link_dir):
            if directory.exists():
                yield from directory.glob("*.yml")
                yield from directory.glob("*.yaml")

    def load_catalog(self) -> tuple[list[str], list[str]]:
        objects: list[str] = []
        links: list[str] = []
        for pattern in ("*.yml", "*.yaml"):
            for path in self.object_dir.glob(pattern):
                objects.append(path.stem)
        for pattern in ("*.yml", "*.yaml"):
            for path in self.link_dir.glob(pattern):
                links.append(path.stem)
        return sorted(objects), sorted(links)

    def read_yaml(self, path: Path) -> str:
        return path.read_text(encoding="utf-8")

    def write_file(self, relative_path: str, contents: str) -> Path:
        destination = self.project_root / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(contents, encoding="utf-8")
        return destination

    def describe_catalog(self) -> tuple[str, str]:
        obj_catalog = []
        link_catalog = []
        for pattern in ("*.yml", "*.yaml"):
            for path in self.object_dir.glob(pattern):
                rel = path.relative_to(self.project_root)
                obj_catalog.append(f"- {rel}")
        for pattern in ("*.yml", "*.yaml"):
            for path in self.link_dir.glob(pattern):
                rel = path.relative_to(self.project_root)
                link_catalog.append(f"- {rel}")
        return ("\n".join(obj_catalog) or "(none)", "\n".join(link_catalog) or "(none)")

    def snapshot(self) -> str:
        snapshot = {
            "objects": sorted(
                p.name for pattern in ("*.yml", "*.yaml") for p in self.object_dir.glob(pattern)
            ),
            "links": sorted(
                p.name for pattern in ("*.yml", "*.yaml") for p in self.link_dir.glob(pattern)
            ),
        }
        return json.dumps(snapshot, indent=2)
