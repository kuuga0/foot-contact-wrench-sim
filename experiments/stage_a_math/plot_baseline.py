"""Plot two-dimensional projections of the Stage A local wrench set."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial import ConvexHull

from foot_contact_wrench.utils.config import load_yaml, local_set_from_config


ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "configs" / "local_set" / "stage_a_baseline.yml"
OUTPUT_DIR = ROOT / "outputs" / "stage_a_baseline"


def projected_support_polygon(local_set, axes: tuple[int, int], samples: int) -> np.ndarray:
    points: list[np.ndarray] = []
    for angle in np.linspace(0.0, 2.0 * np.pi, samples, endpoint=False):
        direction_2d = np.array([np.cos(angle), np.sin(angle)])
        direction = np.zeros(6)
        direction[list(axes)] = direction_2d
        result = local_set.support(direction)
        if not result.feasible:
            raise RuntimeError(f"support query failed: {result.status}")
        points.append(result.wrench[list(axes)])
    projected = np.asarray(points)
    hull = ConvexHull(projected)
    return projected[hull.vertices]


def main() -> None:
    config = load_yaml(CONFIG_PATH)
    local_set = local_set_from_config(config)
    samples = int(config.get("plot", {}).get("samples", 181))
    projections = config.get("plot", {}).get("projections", [])
    if len(projections) != 2:
        raise ValueError("baseline config must contain two plot projections")

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), constrained_layout=True)
    for axis, projection in zip(axes, projections):
        index_pair = tuple(int(index) for index in projection["axes"])
        polygon = projected_support_polygon(local_set, index_pair, samples)
        axis.fill(polygon[:, 0], polygon[:, 1], color="#4c78a8", alpha=0.18)
        axis.plot(
            np.r_[polygon[:, 0], polygon[0, 0]],
            np.r_[polygon[:, 1], polygon[0, 1]],
            color="#1f4e79",
            linewidth=1.5,
            label="local wrench-set projection",
        )
        axis.set_xlabel(f"{projection['labels'][0]} ({projection['units'][0]})")
        axis.set_ylabel(f"{projection['labels'][1]} ({projection['units'][1]})")
        axis.set_title(projection["name"])
        axis.grid(True, alpha=0.3)
        axis.set_aspect("equal", adjustable="box")
    fig.suptitle(
        "Stage A local contact wrench-set projections\n"
        f"N={local_set.normal_load:g} N; candidate mu={local_set.model.friction[0]:g}"
    )
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT_DIR / "baseline_projections.png", dpi=180)
    plt.close(fig)

    metadata = {
        "config": str(CONFIG_PATH.relative_to(ROOT)),
        "normal_load_n": local_set.normal_load,
        "friction_coefficients": local_set.model.friction.tolist(),
        "projection_axes": [list(map(int, item["axes"])) for item in projections],
    }
    (OUTPUT_DIR / "plot_metadata.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )
    print(f"saved: {(OUTPUT_DIR / 'baseline_projections.png').relative_to(ROOT)}")


if __name__ == "__main__":
    main()
