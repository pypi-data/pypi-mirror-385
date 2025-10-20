import numpy as np
from numba import njit

KIND_UNARY = 0
KIND_BINARY = 1
KIND_ANARY = 2
AGG_SUM = 0
AGG_MAX = 1


@njit(fastmath=True, cache=True)
def _compute_sum_max_for_route(
    kind: int, ch: int, vt: int,
    route: np.ndarray, rlen: int,
    UA: np.ndarray, UM: np.ndarray,
    BA: np.ndarray, BM: np.ndarray,
    AA: np.ndarray, AM: np.ndarray,
):
    if kind == KIND_UNARY:
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

    else:
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


@njit(fastmath=True, cache=True)
def _njit_check_once(
    UA, UM, BA, BM, AA, AM,
    routes, route_sizes,
    kinds, limits, modes, attr_orders,
    veh_types_of_vehicle,
    ch_idx,
):
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
            a = attr_orders[v, k]
            lim = limits[v, a]
            if not np.isfinite(lim):
                continue
            kind = int(kinds[a])
            mode = int(modes[v, a])
            ch = int(ch_idx[a])
            s, mx = _compute_sum_max_for_route(kind, ch, vt, route, rlen, UA, UM, BA, BM, AA, AM)
            sums[v, a] = s
            maxs[v, a] = mx
            if (mode == AGG_SUM and s > lim) or (mode == AGG_MAX and mx > lim):
                violated[v] = True
                first_fail[v] = a
                break

    return sums, maxs, violated, first_fail


_check_once_core = _njit_check_once

