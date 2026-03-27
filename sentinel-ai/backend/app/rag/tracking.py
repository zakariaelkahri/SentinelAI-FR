import logging
from contextlib import contextmanager
from typing import Any, Iterator

from app.core.config import settings


logger = logging.getLogger(__name__)

_mlflow_module: Any | None = None


def _bootstrap_mlflow() -> Any | None:
    global _mlflow_module

    if _mlflow_module is not None:
        return _mlflow_module

    if not settings.RAG_MLFLOW_ENABLED:
        return None

    if not settings.MLFLOW_TRACKING_URI:
        logger.info("RAG MLflow tracking disabled: MLFLOW_TRACKING_URI is empty")
        return None

    try:
        import mlflow  # Imported lazily to keep startup light.
    except Exception as exc:
        logger.warning("RAG MLflow tracking unavailable: %s", exc)
        return None

    try:
        mlflow.set_tracking_uri(settings.MLFLOW_TRACKING_URI)
        mlflow.set_experiment(settings.RAG_MLFLOW_EXPERIMENT_NAME)
        _mlflow_module = mlflow
        logger.info(
            "RAG MLflow tracking enabled (uri=%s, experiment=%s)",
            settings.MLFLOW_TRACKING_URI,
            settings.RAG_MLFLOW_EXPERIMENT_NAME,
        )
    except Exception as exc:
        logger.warning(
            "Failed to initialize RAG MLflow tracking: %s. "
            "If this includes 'Invalid Host header', allow backend hostnames in MLflow server settings.",
            exc,
        )
        _mlflow_module = None

    return _mlflow_module


@contextmanager
def rag_mlflow_run(run_name: str, tags: dict[str, str] | None = None) -> Iterator[Any | None]:
    mlflow = _bootstrap_mlflow()
    if mlflow is None:
        yield None
        return

    started = False

    try:
        mlflow.start_run(run_name=run_name)
        started = True
        mlflow.set_tag("module", "rag")
        if tags:
            mlflow.set_tags(tags)
    except Exception as exc:
        logger.warning("Failed to start RAG MLflow run '%s': %s", run_name, exc)
        yield None
        return

    try:
        yield mlflow
    finally:
        if started:
            try:
                mlflow.end_run()
            except Exception as exc:
                logger.warning("Failed to end RAG MLflow run '%s': %s", run_name, exc)


def log_params(mlflow: Any | None, params: dict[str, Any]) -> None:
    if mlflow is None or not params:
        return
    try:
        normalized = {key: str(value) for key, value in params.items() if value is not None}
        if normalized:
            mlflow.log_params(normalized)
    except Exception as exc:
        logger.warning("Failed to log RAG MLflow params: %s", exc)


def log_metrics(mlflow: Any | None, metrics: dict[str, float], step: int | None = None) -> None:
    if mlflow is None or not metrics:
        return
    try:
        normalized = {
            key: float(value)
            for key, value in metrics.items()
            if value is not None
        }
        if normalized:
            if step is None:
                mlflow.log_metrics(normalized)
            else:
                mlflow.log_metrics(normalized, step=step)
    except Exception as exc:
        logger.warning("Failed to log RAG MLflow metrics: %s", exc)
