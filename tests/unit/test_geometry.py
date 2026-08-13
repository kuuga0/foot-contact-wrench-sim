import numpy as np

from foot_contact_wrench.geometry.wrench import force_to_wrench_matrix


def test_force_at_origin_has_no_moment():
    mapping = force_to_wrench_matrix([0.0, 0.0, 0.0])
    assert np.allclose(mapping @ np.array([1.0, 2.0, 3.0]), [0.0, 0.0, 0.0, 1.0, 2.0, 3.0])


def test_force_to_wrench_uses_r_cross_f():
    mapping = force_to_wrench_matrix([0.1, 0.0, 0.0])
    assert np.allclose(mapping @ np.array([0.0, 0.0, 10.0]), [0.0, -1.0, 0.0, 0.0, 0.0, 10.0])
