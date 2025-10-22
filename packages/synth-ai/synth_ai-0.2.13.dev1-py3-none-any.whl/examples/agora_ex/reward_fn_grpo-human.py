import logging
import requests
from typing import Any, Dict, Union

# ---------------------------------------------------------------------------
# Run configuration defaults (override via kwargs when invoking reward_fn)
# ---------------------------------------------------------------------------
RUN_TYPE: str = "rl_training_human"
RUN_VERSION: float = 3.5
MODEL_NAME: str = "Qwen3-30B-A3B-Instruct"
EXPERIMENT_NAME: str = "qwen3_30b_human"
USER_PROMPT_VERSION: str = "5.0"
SYSTEM_PROMPT_VERSION: str = "4.0"

logger = logging.getLogger(__name__)


def _coerce_step_value(value: Any) -> Union[int, None]:
    try:
        if value is None:
            return None
        return int(value)
    except (TypeError, ValueError):
        return None


def _build_metadata(kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """Compose the metadata payload sent with the evaluation request."""
    base_metadata: Dict[str, Any] = {
        "model": kwargs.get("model", MODEL_NAME),
        "experiment": kwargs.get("experiment", EXPERIMENT_NAME),
        "step_number": kwargs.get("step_number"),
        "user_prompt": kwargs.get("user_prompt", USER_PROMPT_VERSION),
        "batch_number": kwargs.get("batch_number"),
        "prompt_index": kwargs.get("prompt_index"),
        "rollout_group": kwargs.get("rollout_group"),
        "system_prompt": kwargs.get("system_prompt", SYSTEM_PROMPT_VERSION),
    }

    step_metadata = kwargs.get("metadata") or {}
    if isinstance(step_metadata, dict):
        # Map common harness metadata onto our schema when present
        step_value = _coerce_step_value(
            step_metadata.get("step") or step_metadata.get("step_number")
        )
        if step_value is not None:
            base_metadata["step_number"] = step_value

        rollout_value = step_metadata.get("rollout_group")
        if rollout_value is not None:
            base_metadata["rollout_group"] = rollout_value

        extras = step_metadata.get("extras")
        if extras:
            base_metadata["extras"] = extras

        # Preserve any additional custom metadata fields
        for key, value in step_metadata.items():
            if key in {"step", "step_number", "rollout_group", "extras"}:
                continue
            if key not in base_metadata or base_metadata.get(key) is None:
                base_metadata[key] = value

    # Strip keys that remain None so the JSON is clean
    return {key: value for key, value in base_metadata.items() if value is not None}


def reward_fn(
    completion: str,
    **kwargs,
) -> float:
    """Evaluate the model response and return a reward score (0.0-1.0)."""
    run_type = kwargs.get("run_type", RUN_TYPE)
    run_version = kwargs.get("run_version", RUN_VERSION)
    metadata = _build_metadata(kwargs)

    payload = {
        "code": completion,
        "run_type": run_type,
        "run_version": run_version,
        "metadata": metadata,
    }

    try:
        response = requests.post(
            "https://eames-judge-api-769874896543.us-central1.run.app/evaluations-human",
            json=payload,
            timeout=1800,  # 30 minute timeout for screenshot generation
        )
        response.raise_for_status()
        result = response.json()

        logger.info("Evaluation complete:")
        logger.info("  Score: %s", result.get("score", 0.0))
        logger.info("  Feedback: %s", result.get("explanation", "N/A"))
        logger.info("  Processing Time (ms): %s", result.get("processing_time_ms", "N/A"))
        logger.info("  Worker ID: %s", result.get("worker_id", "N/A"))
        logger.info("  Success: %s", result.get("success", False))
        if metadata:
            logger.info("  Metadata sent: %s", metadata)

        screenshot_urls = result.get("screenshot_urls", {}) or {}
        if screenshot_urls:
            logger.info("  Screenshot URLs:")
            for key, url in screenshot_urls.items():
                logger.info("    %s: %s", key.capitalize(), url)

        score = result.get("score", 0.0)
        if not isinstance(score, (int, float)):
            logger.warning("Invalid score type: %s. Defaulting to 0.0", type(score))
            return 0.0

        return max(0.0, min(1.0, float(score)))

    except requests.exceptions.Timeout:
        logger.error("Request to evaluation server timed out")
        return 0.0

    except requests.exceptions.RequestException as exc:
        logger.error("Request to evaluation server failed: %s", exc)
        return 0.0

    except (KeyError, ValueError, TypeError) as exc:
        logger.error("Error parsing evaluation server response: %s", exc)
        return 0.0

    except Exception as exc:  # pylint: disable=broad-except
        logger.error("Unexpected error in reward_fn: %s", exc)
        return 0.0