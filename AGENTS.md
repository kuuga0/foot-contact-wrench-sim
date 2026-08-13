# Repository Guidelines

## Project Structure

This repository is a Python/MuJoCo research scaffold. Analytical contact models belong in `src/foot_contact_wrench/contact` and set computations in `src/foot_contact_wrench/optimization`. MuJoCo state and sensor adapters belong in `mujoco_io`; dynamics utilities belong in `dynamics`. Keep stage-specific experiments under `experiments/stage_a_math`, `stage_b_bench`, `stage_c_x1`, and `stage_d_double_support`. Put configuration in `configs/`, tests in `tests/`, and generated results in `outputs/`. The X1 repository is a read-only Git submodule in `external/agibot_x1_infer`.

## Development Commands

Activate the `foot-wrench` Conda environment before working. Run `python -m pytest` for tests and use Jupyter or MuJoCo's viewer for interactive checks. Export a reproducible environment with `conda env export -n foot-wrench --no-builds > environment-lock.yml` after dependency changes.

## Coding Style

Use Python 3.11, four-space indentation, type hints for public functions, and descriptive `snake_case` names. Keep physics parameters in YAML rather than hard-coding them. Format code with Ruff/Black when those tools are introduced; every new module should remain importable without a simulator window.

## Testing Guidelines

Name tests `test_*.py` and keep analytical unit tests independent of MuJoCo. Cover force-to-wrench mapping, unilateral/load bounds, set-membership, frame transforms, and degenerate contact cases. Integration tests may load MJCF models and should be clearly marked.

## Commits and Pull Requests

Use short imperative commit subjects, for example `Add stage A wrench-set solver`. Pull requests should state the model assumptions, changed stage, validation command, and affected configuration. Include plots or screenshots for visual/simulation changes and record the X1 submodule commit when relevant.

## Data and Security

Do not commit robot credentials, private logs, raw large recordings, build folders, or environment secrets. Store large datasets outside Git or use Git LFS only after confirming repository policy.
