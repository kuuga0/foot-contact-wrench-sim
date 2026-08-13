"""MuJoCo helpers for the simplified single-foot digital bench."""

from __future__ import annotations

from dataclasses import dataclass

import mujoco
import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]


@dataclass(frozen=True)
class ContactWrenchSample:
    """Contact force and wrench reported in a named body frame."""

    wrench_world: FloatArray
    normal_forces: FloatArray
    contact_count: int


def load_bench_model(path: str) -> tuple[mujoco.MjModel, mujoco.MjData]:
    model = mujoco.MjModel.from_xml_path(path)
    data = mujoco.MjData(model)
    return model, data


def _contact_force_world(model: mujoco.MjModel, data: mujoco.MjData, index: int) -> FloatArray:
    force_contact = np.zeros(6)
    mujoco.mj_contactForce(model, data, index, force_contact)
    # Use the batched contact arrays. Direct scalar-contact frame access can
    # expose an unpopulated view in the Python binding.
    rotation = np.asarray(data.contact.frame[index], dtype=float).reshape(3, 3)
    force_world = rotation.T @ force_contact[:3]
    torque_world = rotation.T @ force_contact[3:]
    return np.concatenate((torque_world, force_world))


def contact_wrench_about_body(
    model: mujoco.MjModel,
    data: mujoco.MjData,
    body_name: str,
    ground_geom_name: str = "ground",
    contact_geom_prefix: str = "contact_",
) -> ContactWrenchSample:
    """Sum ground-on-foot contacts and express their wrench at body origin.

    MuJoCo's contact frame normal is oriented according to the geom ordering;
    the sign is corrected from body/ground ordering below before accumulation.
    """
    body_id = model.body(body_name).id
    ground_id = model.geom(ground_geom_name).id
    contact_wrench = np.zeros(6)
    normal_forces: list[float] = []
    contact_count = 0
    body_origin = data.xpos[body_id].copy()

    for index in range(data.ncon):
        geom1 = int(data.contact.geom1[index])
        geom2 = int(data.contact.geom2[index])
        foot_geom = None
        # mj_contactForce returns the contact force on geom1 expressed in the
        # contact frame. We want ground-on-foot, so the sign depends on which
        # geom is the foot.
        sign = -1.0
        if geom1 != ground_id and model.geom(geom1).name.startswith(contact_geom_prefix):
            foot_geom = geom1
        elif geom2 != ground_id and model.geom(geom2).name.startswith(contact_geom_prefix):
            foot_geom = geom2
            sign = 1.0
        if foot_geom is None:
            continue

        contact_point = np.asarray(data.contact.pos[index], dtype=float).copy()
        force_contact = np.zeros(6)
        mujoco.mj_contactForce(model, data, index, force_contact)
        rotation = np.asarray(data.contact.frame[index], dtype=float).reshape(3, 3)
        force_world = sign * rotation.T @ force_contact[:3]
        torque_world = sign * rotation.T @ force_contact[3:]
        arm = contact_point - body_origin
        contact_wrench[:3] += np.cross(arm, force_world) + torque_world
        contact_wrench[3:] += force_world
        normal_forces.append(float(max(0.0, force_world[2])))
        contact_count += 1

    return ContactWrenchSample(
        wrench_world=contact_wrench,
        normal_forces=np.asarray(normal_forces, dtype=float),
        contact_count=contact_count,
    )


def run_free_body_bench(
    model: mujoco.MjModel,
    data: mujoco.MjData,
    duration_s: float,
    initial_position: FloatArray,
    initial_linear_velocity: FloatArray | None = None,
    initial_angular_velocity: FloatArray | None = None,
) -> list[dict[str, float | int | list[float]]]:
    """Run the free foot under gravity and record contact truth and IMU state."""
    data.qpos[:3] = np.asarray(initial_position, dtype=float).reshape(3)
    if initial_linear_velocity is not None:
        data.qvel[:3] = np.asarray(initial_linear_velocity, dtype=float).reshape(3)
    if initial_angular_velocity is not None:
        data.qvel[3:6] = np.asarray(initial_angular_velocity, dtype=float).reshape(3)
    mujoco.mj_forward(model, data)

    records: list[dict[str, float | int | list[float]]] = []
    steps = int(np.ceil(duration_s / model.opt.timestep))
    for _ in range(steps):
        mujoco.mj_step(model, data)
        sample = contact_wrench_about_body(model, data, "foot")
        body_id = model.body("foot").id
        records.append(
            {
                "time_s": float(data.time),
                "contact_count": sample.contact_count,
                "normal_forces_n": sample.normal_forces.tolist(),
                "contact_wrench_world": sample.wrench_world.tolist(),
                "position_world_m": data.xpos[body_id].tolist(),
                "linear_velocity_world_mps": data.cvel[body_id, 3:].tolist(),
                "angular_velocity_world_radps": data.cvel[body_id, :3].tolist(),
            }
        )
    return records
