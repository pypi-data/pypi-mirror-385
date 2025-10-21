"""Hierarchical variable storage utilities."""

from .resolver import (
    EspansoDiscoveryAdapter,
    GlobalVariableResolver,
    RepoEspansoDiscoveryAdapter,
    StubEspansoDiscoveryAdapter,
)
from .storage import HierarchicalVariableStore, HIERARCHICAL_VARIABLES_FILE
from .storage import bootstrap_hierarchical_globals

__all__ = [
    "EspansoDiscoveryAdapter",
    "GlobalVariableResolver",
    "RepoEspansoDiscoveryAdapter",
    "StubEspansoDiscoveryAdapter",
    "HierarchicalVariableStore",
    "HIERARCHICAL_VARIABLES_FILE",
    "bootstrap_hierarchical_globals",
]
