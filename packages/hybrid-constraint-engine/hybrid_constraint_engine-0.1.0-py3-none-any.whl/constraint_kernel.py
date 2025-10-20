import numpy as np
from numba import njit

# ----- Constants (khớp với code của bạn) -----
KIND_UNARY  = 0
KIND_BINARY = 1
KIND_ANARY  = 2
AGG_SUM = 0
AGG_MAX = 1


# =====================================================================
#  TÍNH CẢ SUM & MAX CHO 1 ROUTE + 1 ATTR (KHÔNG SCALE)
# =====================================================================
@njit(fastmath=True, cache=True)
def _compute_sum_max_for_route(
    kind: int, ch: int, vt: int,
    route: np.ndarray, rlen: int,
    UA: np.ndarray, UM: np.ndarray,
    BA: np.ndarray, BM: np.ndarray,
    AA: np.ndarray, AM: np.ndarray,
):
    """
    Trả về (sum_val, max_val) cho 1 thuộc tính (kind, ch) trên 1 route.
    - vt: vehicle-type index của chiếc xe đang xét.
    - UA/UM, BA/BM, AA/AM: tensor theo đúng layout bạn đang dùng:
        UA.shape = (n_vehicle_types, n_points, n_unary_channels)
        BA.shape = (n_vehicle_types, n_points, n_points, n_binary_channels)
        AA.shape = (n_vehicle_types, n_points, n_points, n_anary_channels)
      UM/BM/AM là bản 'max-channel' tương ứng.
    (Không dùng scale)
    """

    if kind == KIND_UNARY:
        # Skip depot (node 0) for unary attributes
        s = 0.0
        m = -np.inf
        for i in range(rlen):
            p = route[i]
            if p == 0:
                continue
            s += UA[vt, p, ch]
            v = UM[vt, p, ch]
            if v > m:
                m = v
        if m == -np.inf:
            m = 0.0
        return s, m

    elif kind == KIND_BINARY:
        s = 0.0
        m = -np.inf
        for i in range(rlen - 1):
            a = route[i]
            b = route[i + 1]
            s += BA[vt, a, b, ch]
            v = BM[vt, a, b, ch]
            if v > m:
                m = v
        return s, m

    else:  # KIND_ANARY
        s = 0.0
        m = -np.inf
        for i in range(rlen):
            ai = route[i]
            for j in range(rlen):
                if i == j:
                    continue
                aj = route[j]
                s += AA[vt, ai, aj, ch]
                v = AM[vt, ai, aj, ch]
                if v > m:
                    m = v
        return s, m


# =====================================================================
#  KERNEL CHÍNH: CHECK (không scale)
# =====================================================================
@njit(fastmath=True, cache=True)
def _njit_check_once(
    UA, UM, BA, BM, AA, AM,
    routes, route_sizes,
    kinds, limits, modes, attr_orders,
    veh_types_of_vehicle,
    ch_idx,
):
    """
    Parameters
    ----------
    UA,UM,BA,BM,AA,AM : float32 contiguous
        Tensors theo layout: (vt, ...) như mô tả phía trên.
    routes        : int32 [m, Lmax]
    route_sizes   : int32 [m]
    kinds         : int32 [n_attr] (0/1/2)
    limits        : float32 [m, n_attr] (np.inf nếu không đặt)
    modes         : int32 [m, n_attr] (0=ADD(sum), 1=MAX)
    attr_orders   : int32 [m, n_attr]  thứ tự duyệt thuộc tính
    veh_types_of_vehicle : int32 [m]   map mỗi vehicle -> vt index
    Returns
    -------
    sums        : float32 [m, n_attr]
    maxs        : float32 [m, n_attr]
    violated    : bool   [m]
    first_fail  : int64  [m]  (attr index đầu tiên vi phạm, hoặc -1)
    """
    m = route_sizes.shape[0]
    n_attr = kinds.shape[0]

    sums = np.zeros((m, n_attr), dtype=np.float32)
    maxs = np.zeros((m, n_attr), dtype=np.float32)
    violated = np.zeros(m, dtype=np.bool_)
    first_fail = -np.ones(m, dtype=np.int64)

    for v in range(m):
        rlen = route_sizes[v]
        route = routes[v, :rlen]
        vt = int(veh_types_of_vehicle[v])

        for k in range(n_attr):
            a = attr_orders[v, k]          # attr index
            lim = limits[v, a]
            # Bỏ qua nếu không có limit (inf)
            if not np.isfinite(lim):
                continue

            kind = int(kinds[a])
            mode = int(modes[v, a])

            # Channel index lấy từ ch_idx theo attr index
            ch = int(ch_idx[a])
            # Tính sum & max cho attr (kind, channel=ch) trên route
            s, mx = _compute_sum_max_for_route(
                kind, ch, vt, route, rlen,
                UA, UM, BA, BM, AA, AM,
            )
            sums[v, a] = s
            maxs[v, a] = mx

            # Kiểm tra vi phạm theo mode
            if (mode == AGG_SUM and s > lim) or (mode == AGG_MAX and mx > lim):
                violated[v] = True
                first_fail[v] = a
                break  # dừng ở attr đầu tiên vi phạm

    return sums, maxs, violated, first_fail


# Giữ tên cũ cho tương thích import trong lớp Problem
_check_once_core = _njit_check_once
