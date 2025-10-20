# ddoc/plugins/hookspecs.py
from __future__ import annotations
"""
Hook specifications for ddoc plugin system with version tag.
"""
import pluggy
from typing import Any, Dict, Optional, List # List 타입 임포트 추가

hookspec = pluggy.HookspecMarker("ddoc")
hookimpl = pluggy.HookimplMarker("ddoc") 

# Bump this if you change HookSpec signatures in a breaking way.
HOOKSPEC_VERSION = "1.0.0"

class HookSpecs:
    # --- MLOps Core Operations (Implemented by ddoc/core/ops.py) ---
    
    @hookspec
    def data_add(self, name: str, config: str) -> Optional[Dict[str, Any]]:
        """Registers a new dataset version (dvc add, git branch/commit, params update)."""
        
    @hookspec
    def exp_run(self, name: str, params: str, dry_run: bool) -> Optional[Dict[str, Any]]:
        """Updates params.yaml and executes dvc exp run."""
        
    @hookspec
    def exp_show(self, name: Optional[str], baseline: Optional[str]) -> Optional[Dict[str, Any]]:
        """Shows DVC experiment results, optionally comparing two versions."""

    # --- Analytical Operations (Implemented by external plugins) ---

    @hookspec
    def eda_run(self, input_path: str, modality: str, output_path: str) -> Optional[Dict[str, Any]]:
        """Run EDA and write a report to output_path. Return a brief summary."""

    @hookspec
    def transform_apply(self, input_path: str, transform: str, args: Dict[str, Any], output_path: str) -> Optional[Dict[str, Any]]:
        """Apply a named transform and write result to output_path."""

    @hookspec
    def drift_detect(self, ref_path: str, cur_path: str, detector: str, cfg: Optional[Dict[str, Any]], output_path: str) -> Optional[Dict[str, Any]]:
        """Detect drift, write a report, return brief metrics."""

    @hookspec
    def reconstruct_apply(self, input_path: str, method: str, args: Dict[str, Any], output_path: str) -> Optional[Dict[str, Any]]:
        """Reconstruct/Impute/Resample data and write result."""

    @hookspec
    def retrain_run(self, train_path: str, trainer: str, params: Dict[str, Any], model_out: str) -> Optional[Dict[str, Any]]:
        """Retrain model and write model artifact."""

    @hookspec
    def monitor_run(self, source: str, mode: str, schedule: Optional[str]) -> Optional[Dict[str, Any]]:
        """Run monitors once or on schedule."""

    # --- Plugin Metadata Hook (NEW) ---
    @hookspec(firstresult=True)
    def ddoc_get_metadata(self) -> Optional[Dict[str, Any]]:
        """
        Returns structured metadata (name, description, implemented hooks) 
        about the plugin.
        
        Note: firstresult=True is typically not used for gathering, but here 
        we assume the list of results is gathered elsewhere. Since the external 
        plugin returns a full dict, we keep it simple for now. 
        For listing, we gather all results manually (see cli/commands.py).
        """

    # --- Plugin Metadata Hook (NEW) ---
    @hookspec(firstresult=True)
    def ddoc_get_metadata2(self) -> Optional[Dict[str, Any]]:
        """
        Returns structured metadata (name, description, implemented hooks) 
        about the plugin.
        
        Note: firstresult=True is typically not used for gathering, but here 
        we assume the list of results is gathered elsewhere. Since the external 
        plugin returns a full dict, we keep it simple for now. 
        For listing, we gather all results manually (see cli/commands.py).
        """

