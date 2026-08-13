# Foot Contact Wrench Simulation

Simulation workspace for the first-stage study of a single-foot local contact wrench set during slow walking with unexpected partial footholds.

## Scope

- `stage_a_math`: analytical contact-force and wrench-set validation.
- `stage_b_bench`: simplified single-foot MuJoCo test bench.
- `stage_c_x1`: single-support experiments using the X1 MJCF model.
- `stage_d_double_support`: later extension to paired contact wrenches.

The current model treats the foot as a rigid body with discrete candidate contact points. It separates the current observed wrench, the local contact capability set, and whole-body instantaneous feasibility. Sensor uncertainty and learning models are intentionally deferred.

## Environment

The reference environment uses Python 3.11, MuJoCo 3.1.3, NumPy, SciPy, CVXPY, Matplotlib, PyYAML, pytest, and Jupyter. See `environment.yml` for the portable specification. The X1 source is tracked as a Git submodule under `external/agibot_x1_infer`.

## Reproducibility

Keep configuration in `configs/`, raw and processed data in `data/`, and generated figures/results in `outputs/`. Do not commit generated output, local virtual environments, credentials, or large recordings. Pin experiment settings and record the submodule commit used for each result.

## Status

The repository currently contains the project scaffold. Stage A should be implemented and validated before adding the X1 model or learning components.
