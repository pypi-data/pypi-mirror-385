import numpy as np


def build_attr_schema_auto(
    names, kinds, aggs,
    UA, BA, AA
):
    n_attr = len(names)

    n_unary = UA.shape[-1] if UA.size > 0 else 0
    n_binary = BA.shape[-1] if BA.size > 0 else 0
    n_anary = AA.shape[-1] if AA.size > 0 else 0

    unary_idx = np.arange(n_unary, dtype=np.int32)
    binary_idx = np.arange(n_binary, dtype=np.int32)
    anary_idx = np.arange(n_anary, dtype=np.int32)

    ch_idx = np.empty(n_attr, dtype=np.int32)
    u_ptr, b_ptr, a_ptr = 0, 0, 0
    for i in range(n_attr):
        k = kinds[i]
        if k == 0:
            ch_idx[i] = unary_idx[u_ptr];  u_ptr += 1
        elif k == 1:
            ch_idx[i] = binary_idx[b_ptr]; b_ptr += 1
        else:
            ch_idx[i] = anary_idx[a_ptr];  a_ptr += 1

    return (
        np.ascontiguousarray(kinds, dtype=np.int32),
        np.ascontiguousarray(aggs, dtype=np.int32),
        np.ascontiguousarray(ch_idx, dtype=np.int32),
        {nm: i for i, nm in enumerate(names)},
    )

