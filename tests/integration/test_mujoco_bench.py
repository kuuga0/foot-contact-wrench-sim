from pathlib import Path

import numpy as np

from foot_contact_wrench.mujoco_io.bench import load_bench_model, run_free_body_bench


ROOT = Path(__file__).resolve().parents[2]


def test_single_foot_bench_generates_ground_contact():
    model, data = load_bench_model(str(ROOT / "models" / "bench" / "single_foot_bench.xml"))
    records = run_free_body_bench(
        model,
        data,
        duration_s=0.4,
        initial_position=np.array([0.0, 0.0, 0.025]),
    )
    assert any(record["contact_count"] > 0 for record in records)
    final = records[-1]
    assert final["contact_count"] > 0
    assert final["contact_wrench_world"][5] > 0.0
    assert np.isclose(
        sum(final["normal_forces_n"]), 4.0 * 9.81, atol=0.2
    )
