"""
ontologia_dagster
-----------------
Dagster definitions for the Ontologia project.

Use `dagster dev -m ontologia_dagster` to launch the UI locally.
"""

from .definitions import defs, pipeline_job

__all__ = ["defs", "pipeline_job"]
