"""Task App configuration for Agora EX landing page generation."""

from __future__ import annotations

import sys
from pathlib import Path

from synth_ai.task.apps import ModalDeploymentConfig, TaskAppEntry, register_task_app

# Add this directory to path to import the task app module
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from agora_ex_task_app import APP_DESCRIPTION, APP_ID, build_config

# Resolve repo root for Modal mounts
def _resolve_repo_root() -> Path:
    """Find repo root from this file's location."""
    candidates = [_HERE.parent.parent.parent]  # examples/agora_ex -> synth-ai
    for candidate in candidates:
        if (candidate / "pyproject.toml").exists():
            return candidate
    return _HERE.parent.parent.parent

REPO_ROOT = _resolve_repo_root()

# Register at module level
register_task_app(
    entry=TaskAppEntry(
        app_id=APP_ID,
        description=APP_DESCRIPTION,
        config_factory=build_config,
        aliases=(APP_ID, "agora-ex", "agora_ex"),
        env_files=(),
        modal=ModalDeploymentConfig(
            app_name="agora-ex-task-app",
            python_version="3.11",
            pip_packages=(
                "fastapi>=0.100.0",
                "uvicorn>=0.23.0",
                "pydantic>=2.0.0",
                "httpx>=0.24.0",
                "python-dotenv>=1.0.1",
                # Tracing/DB runtime deps
                "sqlalchemy>=2.0.42",
                "aiosqlite>=0.21.0",
                "greenlet>=3.2.3",
            ),
            extra_local_dirs=(
                # Mount repo root so local modules resolve when deployed on Modal
                (str(REPO_ROOT), "/opt/synth_ai_repo"),
                (str(REPO_ROOT / "synth_ai"), "/opt/synth_ai_repo/synth_ai"),
                (str(_HERE), "/opt/synth_ai_repo/examples/agora_ex"),
            ),
            secret_names=("groq-api-key", "openai-api-key"),
            memory=8192,   # 8GB memory for inference + judge calls
            cpu=2.0,       # 2 CPUs
            max_containers=10,
        ),
    )
)

__all__ = ["build_config"]

