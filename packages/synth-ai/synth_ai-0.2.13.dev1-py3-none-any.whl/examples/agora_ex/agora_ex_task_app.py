"""Task app for the Agora EX landing page generation environment."""

from __future__ import annotations

import argparse
import importlib.util
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.requests import Request

from synth_ai.task.auth import (
    is_api_key_header_authorized,
    normalize_environment_api_key,
)
from synth_ai.task.contracts import (
    RolloutMetrics,
    RolloutRequest,
    RolloutResponse,
    RolloutStep,
    RolloutTrajectory,
    TaskInfo,
)
from synth_ai.task.server import TaskAppConfig, create_task_app, run_task_app

try:  # Optional registry integration
    from synth_ai.task.apps import TaskAppEntry, register_task_app
except ImportError:  # pragma: no cover - registry not available in some test harnesses
    TaskAppEntry = None  # type: ignore[assignment]
    register_task_app = None  # type: ignore[assignment]

LOGGER = logging.getLogger("agora_ex.task_app")

APP_ID = "agora-ex-landing-page"
APP_NAME = "Agora EX Landing Page Task App"
APP_DESCRIPTION = (
    "Single-turn Next.js landing page generation task evaluated by the Eames human judge."
)
DATASET_ID = "agora_ex_prompts_v1"
PROMPTS_FILENAME = "user_prompts_CURRENT.jsonl"
SYSTEM_PROMPT_FILENAME = "system_prompt_CURRENT.md"
DEFAULT_MODEL = "Qwen/Qwen3-Coder-30B-A3B-Instruct"
DEFAULT_TEMPERATURE = 0.15
DEFAULT_MAX_TOKENS = 3072
INFERENCE_TIMEOUT_SECONDS = float(os.getenv("AGORA_EX_INFERENCE_TIMEOUT", "120"))


class AgoraPromptDataset:
    """JSONL-backed prompt dataset for Agora EX."""

    def __init__(self, path: Path) -> None:
        self._path = path
        self._prompts = self._load_prompts(path)

    @staticmethod
    def _load_prompts(path: Path) -> List[str]:
        if not path.exists():
            raise FileNotFoundError(f"Prompt file not found: {path}")
        prompts: List[str] = []
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                stripped = line.strip()
                if not stripped:
                    continue
                try:
                    payload = json.loads(stripped)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"Invalid JSONL line in {path}: {stripped}") from exc
                prompt = payload.get("user_prompt")
                if isinstance(prompt, str) and prompt.strip():
                    prompts.append(prompt.strip())
        if not prompts:
            raise ValueError(f"No prompts loaded from {path}")
        return prompts

    def __len__(self) -> int:
        return len(self._prompts)

    def resolve(self, raw_index: int) -> Tuple[int, str]:
        total = len(self._prompts)
        if total == 0:
            raise RuntimeError("Prompt dataset is empty")
        index = raw_index % total if raw_index >= 0 else (total + (raw_index % total)) % total
        return index, self._prompts[index]

    def describe(self) -> Dict[str, Any]:
        return {
            "dataset_id": DATASET_ID,
            "num_prompts": len(self._prompts),
            "source": str(self._path),
            "splits": {"train": len(self._prompts)},
        }


def _load_reward_module() -> Any:
    module_path = Path(__file__).with_name("reward_fn_grpo-human.py")
    if not module_path.exists():
        raise FileNotFoundError(f"Missing reward module: {module_path}")
    spec = importlib.util.spec_from_file_location("agora_ex_reward_module", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load reward module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


REWARD_MODULE = _load_reward_module()
REWARD_FN = getattr(REWARD_MODULE, "reward_fn")
REWARD_RUN_TYPE = getattr(REWARD_MODULE, "RUN_TYPE", "rl_training")
REWARD_RUN_VERSION = getattr(REWARD_MODULE, "RUN_VERSION", 1.0)
REWARD_EXPERIMENT = getattr(REWARD_MODULE, "EXPERIMENT_NAME", APP_ID)
REWARD_USER_PROMPT_VERSION = getattr(REWARD_MODULE, "USER_PROMPT_VERSION", "current")
REWARD_SYSTEM_PROMPT_VERSION = getattr(REWARD_MODULE, "SYSTEM_PROMPT_VERSION", "current")


def _read_system_prompt(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"System prompt file missing: {path}")
    return path.read_text(encoding="utf-8").strip()


def _coerce_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _coerce_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _resolve_inference_url(policy_config: Dict[str, Any]) -> Optional[str]:
    candidate = policy_config.get("inference_url")
    if isinstance(candidate, str) and candidate.strip():
        return candidate.strip()
    env_fallback = os.getenv("AGORA_EX_INFERENCE_URL")
    return env_fallback.strip() if env_fallback else None


def _normalize_chat_url(base_url: str) -> str:
    base = base_url.rstrip("/")
    if base.endswith("/v1/chat/completions"):
        return base
    return f"{base}/v1/chat/completions"


def _base_task_info() -> TaskInfo:
    return TaskInfo(
        task={
            "id": APP_ID,
            "name": "Agora EX Landing Page Generation",
            "description": (
                "Generate a production-ready Next.js landing page that satisfies the Agora EX brief."
            ),
        },
        environments=["default"],
        observation={
            "type": "text",
            "description": "System prompt plus product brief describing the required landing page.",
        },
        action_space={
            "type": "free_text",
            "description": "Return one TSX file wrapped in a single ```tsx code fence.",
        },
        dataset={
            "id": DATASET_ID,
            "default_split": "train",
            "user_prompt_version": REWARD_USER_PROMPT_VERSION,
        },
        rubric={
            "outcome": {"name": "Human Preference Score", "criteria": []},
            "events": {"name": "Design Compliance", "criteria": []},
        },
        inference={"providers": ["vllm", "local"]},
        capabilities={"tools": []},
        limits={
            "max_turns": 1,
            "max_response_tokens": DEFAULT_MAX_TOKENS,
        },
    )


def describe_taskset(dataset: AgoraPromptDataset) -> Dict[str, Any]:
    return {
        "task": APP_NAME,
        "dataset": dataset.describe(),
        "system_prompt_version": REWARD_SYSTEM_PROMPT_VERSION,
        "user_prompt_version": REWARD_USER_PROMPT_VERSION,
    }


def provide_task_instances(dataset: AgoraPromptDataset, seeds: Sequence[int]) -> Iterable[TaskInfo]:
    base = _base_task_info()
    for seed in seeds:
        index, _ = dataset.resolve(seed)
        yield TaskInfo(
            task=base.task,
            environments=base.environments,
            observation=base.observation,
            action_space=base.action_space,
            dataset={**base.dataset, "selected_index": index},
            rubric=base.rubric,
            inference=base.inference,
            capabilities=base.capabilities,
            limits=base.limits,
        )


def _invoke_inference(
    chat_url: str,
    messages: List[Dict[str, Any]],
    model: Optional[str],
    temperature: float,
    max_tokens: int,
) -> Tuple[Optional[str], Dict[str, Any]]:
    payload = {
        "model": model or DEFAULT_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    LOGGER.info(
        "[AGORA] request inference_url=%s model=%s temperature=%.3f max_tokens=%s",
        chat_url,
        payload["model"],
        temperature,
        max_tokens,
    )
    response = httpx.post(chat_url, json=payload, timeout=INFERENCE_TIMEOUT_SECONDS)
    info: Dict[str, Any] = {"status_code": response.status_code}
    if response.status_code != 200:
        info["error_text"] = response.text[:2000]
        LOGGER.error(
            "[AGORA] inference failed status=%s body_preview=%s",
            response.status_code,
            info["error_text"],
        )
        return None, info

    data = response.json()
    info["raw_response"] = data
    choices = data.get("choices") or []
    primary = choices[0] if choices else {}
    message = primary.get("message") or {}
    completion = message.get("content")
    if isinstance(completion, str):
        return completion.strip(), info
    return None, info


async def rollout_executor(request: RolloutRequest, fastapi_request: Request) -> RolloutResponse:
    app_state = fastapi_request.app.state
    dataset: AgoraPromptDataset = app_state.agora_dataset
    system_prompt: str = app_state.system_prompt
    system_prompt_version: str = getattr(app_state, "system_prompt_version", REWARD_SYSTEM_PROMPT_VERSION)
    user_prompt_version: str = getattr(app_state, "user_prompt_version", REWARD_USER_PROMPT_VERSION)

    env_cfg = getattr(request.env, "config", {}) if hasattr(request, "env") else {}
    env_name = getattr(request.env, "env_name", APP_ID) if hasattr(request, "env") else APP_ID
    env_index = _coerce_int(env_cfg.get("index"), _coerce_int(getattr(request.env, "seed", 0), 0))
    resolved_index, user_prompt = dataset.resolve(env_index)

    policy_config = getattr(request.policy, "config", {}) if request.policy else {}
    policy_config = policy_config or {}
    policy_model = policy_config.get("model") if isinstance(policy_config, dict) else None
    policy_name = None
    if request.policy:
        policy_name = getattr(request.policy, "policy_name", None) or getattr(request.policy, "policy_id", None)
    policy_id = policy_name or "policy"

    inference_url = _resolve_inference_url(policy_config if isinstance(policy_config, dict) else {})
    if not inference_url:
        raise HTTPException(
            status_code=502,
            detail="No inference_url provided in policy config",
        )
    chat_url = _normalize_chat_url(inference_url)
    temperature = _coerce_float(policy_config.get("temperature"), DEFAULT_TEMPERATURE)
    max_tokens = _coerce_int(policy_config.get("max_tokens"), DEFAULT_MAX_TOKENS)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    completion, inference_info = _invoke_inference(
        chat_url=chat_url,
        messages=messages,
        model=policy_model if isinstance(policy_model, str) else None,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    reward_score = 0.0
    reward_error: Optional[str] = None
    reward_metadata = {
        "prompt_index": resolved_index,
        "raw_seed": env_index,
        "policy_id": policy_id,
        "policy_model": policy_model,
        "system_prompt_version": system_prompt_version,
        "user_prompt_version": user_prompt_version,
        "inference_status": inference_info.get("status_code"),
        "inference_error": inference_info.get("error_text"),
    }
    reward_kwargs = {
        "run_type": REWARD_RUN_TYPE,
        "run_version": REWARD_RUN_VERSION,
        "experiment": REWARD_EXPERIMENT,
        "model": request.model or policy_model or DEFAULT_MODEL,
        "user_prompt": user_prompt_version,
        "system_prompt": system_prompt_version,
        "metadata": reward_metadata,
    }
    if completion:
        try:
            reward_score = float(REWARD_FN(completion, **reward_kwargs))
        except Exception as exc:  # pragma: no cover - reward service failure
            reward_error = str(exc)
            LOGGER.exception("Reward evaluation failed: %s", exc)
            reward_score = 0.0
    else:
        reward_error = "empty_completion"

    obs_payload = {
        "prompt": user_prompt,
        "prompt_index": resolved_index,
        "system_prompt_version": system_prompt_version,
        "user_prompt_version": user_prompt_version,
        "env_name": env_name,
    }

    info_payload: Dict[str, Any] = {
        "completion_preview": completion[:400] if completion else "",
        "inference": inference_info,
        "reward_score": reward_score,
    }
    if reward_error:
        info_payload["reward_error"] = reward_error

    step = RolloutStep(
        obs=obs_payload,
        tool_calls=[],
        reward=reward_score,
        done=True,
        truncated=False,
        info=info_payload,
    )

    final_info = {
        "score": reward_score,
        "reward_error": reward_error,
        "prompt_index": resolved_index,
        "policy_id": policy_id,
        "model": request.model or policy_model or DEFAULT_MODEL,
    }
    final_observation = {
        "completion": completion,
        "prompt": user_prompt,
        "system_prompt_version": system_prompt_version,
        "prompt_index": resolved_index,
        "env_name": env_name,
    }

    metrics = RolloutMetrics(
        episode_returns=[reward_score],
        mean_return=reward_score,
        num_steps=1,
        num_episodes=1,
        outcome_score=reward_score,
        events_score=None,
        details={
            "prompt_index": resolved_index,
            "policy_id": policy_id,
            "inference_status": inference_info.get("status_code"),
            "env_name": env_name,
        },
    )

    trajectory = RolloutTrajectory(
        env_id=str(env_name),
        policy_id=str(policy_id),
        steps=[step],
        final={
            "observation": final_observation,
            "reward": reward_score,
            "done": True,
            "truncated": False,
            "info": final_info,
        },
        length=1,
    )

    trace_payload = {
        "messages": messages,
        "completion": completion,
        "reward_score": reward_score,
        "prompt_index": resolved_index,
        "policy_id": policy_id,
        "inference": inference_info,
        "env_name": env_name,
    }

    return RolloutResponse(
        run_id=str(getattr(request, "run_id", "run")),
        trajectories=[trajectory],
        metrics=metrics,
        branches={},
        aborted=False,
        ops_executed=0,
        trace=trace_payload,
    )


def build_config() -> TaskAppConfig:
    module_dir = Path(__file__).resolve().parent
    dataset = AgoraPromptDataset(module_dir / PROMPTS_FILENAME)
    system_prompt = _read_system_prompt(module_dir / SYSTEM_PROMPT_FILENAME)

    base_info = _base_task_info()
    app_state: Dict[str, Any] = {
        "agora_dataset": dataset,
        "system_prompt": system_prompt,
        "system_prompt_version": REWARD_SYSTEM_PROMPT_VERSION,
        "user_prompt_version": REWARD_USER_PROMPT_VERSION,
    }

    return TaskAppConfig(
        app_id=APP_ID,
        name=APP_NAME,
        description=APP_DESCRIPTION,
        base_task_info=base_info,
        describe_taskset=lambda: describe_taskset(dataset),
        provide_task_instances=lambda seeds: list(provide_task_instances(dataset, seeds)),
        rollout=rollout_executor,
        dataset_registry=None,
        rubrics=None,
        proxy=None,
        routers=(),
        app_state=app_state,
        cors_origins=["*"],
    )


def fastapi_app() -> FastAPI:
    app = create_task_app(build_config())

    filtered_routes = []
    for route in app.router.routes:
        path = getattr(route, "path", None)
        methods = getattr(route, "methods", set()) or set()
        if path in {"/health", "/health/rollout"} and "GET" in methods:
            continue
        filtered_routes.append(route)
    app.router.routes = filtered_routes

    def _log_env_key_prefix(source: str, env_key: Optional[str]) -> Optional[str]:
        if not env_key:
            return None
        prefix = env_key[: max(1, len(env_key) // 2)]
        LOGGER.info("[%s] expected ENVIRONMENT_API_KEY prefix: %s", source, prefix)
        return prefix

    @app.get("/health")
    async def health(request: Request) -> JSONResponse | Dict[str, Any]:
        env_key = normalize_environment_api_key()
        if not env_key:
            return JSONResponse(
                status_code=503,
                content={"status": "unhealthy", "detail": "Missing ENVIRONMENT_API_KEY"},
            )
        if not is_api_key_header_authorized(request):
            prefix = _log_env_key_prefix("health", env_key)
            content: Dict[str, Any] = {"status": "healthy", "authorized": False}
            if prefix:
                content["expected_api_key_prefix"] = prefix
            return JSONResponse(status_code=200, content=content)
        return {"status": "healthy", "authorized": True}

    @app.get("/health/rollout")
    async def health_rollout(request: Request) -> JSONResponse | Dict[str, Any]:
        env_key = normalize_environment_api_key()
        if not env_key:
            return JSONResponse(
                status_code=503,
                content={"status": "unhealthy", "detail": "Missing ENVIRONMENT_API_KEY"},
            )
        if not is_api_key_header_authorized(request):
            prefix = _log_env_key_prefix("health/rollout", env_key)
            content: Dict[str, Any] = {"status": "healthy", "authorized": False}
            if prefix:
                content["expected_api_key_prefix"] = prefix
            return JSONResponse(status_code=200, content=content)
        return {"ok": True, "authorized": True}

    @app.exception_handler(RequestValidationError)
    async def _on_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        snapshot = {
            "path": str(getattr(request, "url").path),
            "have_x_api_key": bool(request.headers.get("x-api-key")),
            "have_authorization": bool(request.headers.get("authorization")),
            "errors": exc.errors()[:5],
        }
        LOGGER.warning("[422] validation error %s", snapshot)
        return JSONResponse(status_code=422, content={"status": "invalid", "detail": exc.errors()[:5]})

    return app


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Agora EX task app locally")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8101)
    parser.add_argument("--reload", action="store_true")
    parser.add_argument("--env-file", action="append", default=[])
    args = parser.parse_args()

    module_dir = Path(__file__).resolve().parent
    default_env = module_dir / ".env"
    env_files = [str(default_env)] if default_env.exists() else []
    env_files.extend(args.env_file or [])

    run_task_app(
        build_config,
        host=args.host,
        port=args.port,
        reload=args.reload,
        env_files=env_files,
    )


if register_task_app and TaskAppEntry:
    try:
        # Import ModalDeploymentConfig
        from synth_ai.task.apps import ModalDeploymentConfig
        
        # Resolve repo root for Modal mounts
        _HERE = Path(__file__).resolve().parent
        _REPO_ROOT = _HERE.parent.parent  # examples/agora_ex -> synth-ai
        
        register_task_app(
            entry=TaskAppEntry(
                app_id="agora-ex",  # Use string literal for AST discovery
                description=APP_DESCRIPTION,
                config_factory=build_config,
                aliases=("agora-ex", "agora-ex-landing-page", APP_ID),
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
                        (str(_REPO_ROOT), "/opt/synth_ai_repo"),
                        (str(_REPO_ROOT / "synth_ai"), "/opt/synth_ai_repo/synth_ai"),
                        (str(_HERE), "/opt/synth_ai_repo/examples/agora_ex"),
                    ),
                    secret_names=("groq-api-key", "openai-api-key"),
                    memory=8192,   # 8GB memory
                    cpu=2.0,       # 2 CPUs
                    max_containers=10,
                ),
            )
        )
    except Exception as exc:  # pragma: no cover - registry optional
        LOGGER.warning("Failed to register Agora EX task app: %s", exc)


if __name__ == "__main__":
    main()
