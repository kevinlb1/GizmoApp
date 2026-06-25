from __future__ import annotations

from importlib.util import find_spec
from typing import Any


def sklearn_status() -> dict[str, Any]:
    available = find_spec("sklearn") is not None
    return {
        "available": available,
        "package": "scikit-learn",
        "installCommand": "python -m pip install -r server/requirements-ml.txt",
    }


def run_kmeans(payload: dict[str, Any]) -> tuple[dict[str, Any], list[str], int]:
    status = sklearn_status()
    if not status["available"]:
        return {"status": status}, ["scikit-learn is not installed"], 503

    from sklearn.cluster import KMeans

    raw_points = payload.get("points", [])
    cluster_count = int(payload.get("clusters", 2))
    errors: list[str] = []

    if not isinstance(raw_points, list) or len(raw_points) < cluster_count:
        errors.append("points must contain at least as many points as clusters")

    if cluster_count < 1 or cluster_count > 8:
        errors.append("clusters must be between 1 and 8")

    try:
        points = [[float(point[0]), float(point[1])] for point in raw_points]
    except (TypeError, ValueError, IndexError):
        errors.append("points must be two-number coordinate arrays")
        points = []

    if errors:
        return {}, errors, 400

    model = KMeans(n_clusters=cluster_count, n_init="auto", random_state=0)
    labels = model.fit_predict(points)
    return {
        "labels": [int(label) for label in labels],
        "centers": model.cluster_centers_.tolist(),
        "inertia": float(model.inertia_),
        "status": status,
    }, [], 200
