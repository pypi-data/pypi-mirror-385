from __future__ import annotations

import logging
import os
import tomllib
from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ProjectConfig(BaseModel):
    name: str = "ontologia"
    version: str = "0.1.0"
    definitions_dir: str = "example_project/ontology"


class ApiConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8000
    ontology: str = "default"

    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"


class DataConfig(BaseModel):
    duckdb_path: str = "data/local.duckdb"
    kuzu_path: str = "data/graph.kuzu"


class ServicesConfig(BaseModel):
    postgres_port: int = 5432
    temporal_port: int = 7233
    temporal_web_port: int = 8233


class SdkConfig(BaseModel):
    output_dir: str = "ontologia_sdk/ontology"
    auto_generate_on_apply: bool = True


class FeaturesConfig(BaseModel):
    use_unified_graph: bool = True
    use_graph_reads: bool = True
    use_graph_writes: bool = False
    use_temporal_actions: bool = False


class OntologiaConfig(BaseModel):
    project: ProjectConfig = Field(default_factory=ProjectConfig)
    api: ApiConfig = Field(default_factory=ApiConfig)
    data: DataConfig = Field(default_factory=DataConfig)
    services: ServicesConfig = Field(default_factory=ServicesConfig)
    sdk: SdkConfig = Field(default_factory=SdkConfig)
    features: FeaturesConfig = Field(default_factory=FeaturesConfig)


def _load_raw_config(path: Path) -> dict[str, Any]:
    try:
        with path.open("rb") as fh:
            return tomllib.load(fh)
    except FileNotFoundError:
        return {}


@lru_cache
def load_config(base_path: Path | None = None) -> OntologiaConfig:
    root = base_path or Path.cwd()
    path = root / "ontologia.toml"
    raw = _load_raw_config(path)
    try:
        return OntologiaConfig.model_validate(raw)
    except Exception:
        return OntologiaConfig()


def _config_root() -> Path:
    root_env = os.getenv("ONTOLOGIA_CONFIG_ROOT")
    if root_env:
        try:
            return Path(root_env).resolve()
        except OSError:
            return Path(root_env)
    return Path.cwd()


def use_unified_graph_enabled() -> bool:
    env_override = os.getenv("USE_UNIFIED_GRAPH")
    if env_override is not None and env_override not in ("1", "true", "True"):
        logger.warning(
            "Unified graph mode is now mandatory; ignoring USE_UNIFIED_GRAPH override '%s'.",
            env_override,
        )
    config = load_config(_config_root())
    if not config.features.use_unified_graph:
        logger.warning(
            "Unified graph mode is now mandatory; ignoring features.use_unified_graph = false in ontologia.toml."
        )
    return True


def use_graph_reads_enabled() -> bool:
    env_override = os.getenv("USE_GRAPH_READS")
    if env_override is not None:
        return env_override in ("1", "true", "True")
    config = load_config(_config_root())
    return bool(config.features.use_graph_reads)


def use_graph_writes_enabled() -> bool:
    env_override = os.getenv("USE_GRAPH_WRITES")
    if env_override is not None:
        return env_override in ("1", "true", "True")
    config = load_config(_config_root())
    return bool(config.features.use_graph_writes)
