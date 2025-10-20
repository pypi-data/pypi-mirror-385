"""
ontologia_sdk
--------------
Python SDK for the Ontology API.

This package provides a lightweight client (`OntologyClient`) and (optionally) statically
generated, strongly-typed classes under `ontologia_sdk.ontology` via the `ontologia-cli generate-sdk`
command.
"""

from .client import OntologyClient

__all__ = ["OntologyClient"]
