import numpy as np


def as_f32_c(a: np.ndarray) -> np.ndarray:
    return np.ascontiguousarray(a, dtype=np.float32)


def as_i32_c(a: np.ndarray) -> np.ndarray:
    return np.ascontiguousarray(a, dtype=np.int32)


def as_bool_c(a: np.ndarray) -> np.ndarray:
    return np.ascontiguousarray(a, dtype=np.bool_)

