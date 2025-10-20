import numpy as np

def as_f32_c(a: np.ndarray) -> np.ndarray:
    """
    Ép mảng về float32 và C-contiguous.
    Giúp đảm bảo Numba và CPU memory alignment ổn định.
    """
    return np.ascontiguousarray(a, dtype=np.float32)

def as_i32_c(a: np.ndarray) -> np.ndarray:
    """
    Ép mảng về int32 và C-contiguous.
    """
    return np.ascontiguousarray(a, dtype=np.int32)

def as_bool_c(a: np.ndarray) -> np.ndarray:
    """
    (Tuỳ chọn) Dùng cho mask boolean khi cần tối ưu branch.
    """
    return np.ascontiguousarray(a, dtype=np.bool_)
