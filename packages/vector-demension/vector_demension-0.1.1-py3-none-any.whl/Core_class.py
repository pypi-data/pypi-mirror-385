import numpy as np
from numba import njit
from constraint_kernel import _check_once_core   # Kernel: no-scale version
from build_attr_schema_auto import build_attr_schema_auto
from dtype_utils import *

class Problem:
    def __init__(self, n_points: int):
        self.n_points = n_points
        self.veh_types: list[str] = []
        self.vehicles: list[dict] = []

        # Danh sách thuộc tính theo nhóm (để người dùng tiện quản lý)
        self.attr_unary: list[str] = []
        self.attr_binary: list[str] = []
        self.attr_anary: list[str] = []

        # Constraint & thống kê học
        self.constraints_dict: dict[tuple[str, str], dict] = {}
        self.constraint_stat: dict[tuple[str, str], int] = {}
        self.total_violations = 0
        self.reorder_every = 10
        self.batch_learn_interval = 1

        # Schema Auto (Phase 3)
        self.attr_names: list[str] = []
        self.attr_kinds = np.zeros(0, dtype=np.int32)  # 0=unary, 1=binary, 2=anary
        self.attr_aggs  = np.zeros(0, dtype=np.int32)  # 0=sum, 1=max
        self.attr_ch_idx= np.zeros(0, dtype=np.int32)  # chỉ số channel trong UA/BA/AA
        self.name_to_idx: dict[str, int] = {}

        # Tensors (float32, C-order) — Hybrid layout: (n_vehicle_types, ...)
        self.UA = np.zeros((0, n_points, 0), dtype=np.float32, order="C")
        self.UM = np.zeros((0, n_points, 0), dtype=np.float32, order="C")
        self.BA = np.zeros((0, n_points, n_points, 0), dtype=np.float32, order="C")
        self.BM = np.zeros((0, n_points, n_points, 0), dtype=np.float32, order="C")
        self.AA = np.zeros((0, n_points, n_points, 0), dtype=np.float32, order="C")
        self.AM = np.zeros((0, n_points, n_points, 0), dtype=np.float32, order="C")

        # No hybrid scale arrays

        # Cache configuration
        self.cache_enabled = False
        self._route_cache: dict = {}
        self._cache_token = 0

        # Khoảng cách (tùy chọn) dùng cho việc xoay lại route theo nút xa depot nhất
        self.dist_matrix = None


    # ---------------- THÊM DỮ LIỆU CƠ BẢN ----------------
    def add_vehicle_type(self, name: str):
        if name in self.veh_types:
            return
        self.veh_types.append(name)
        # No scale expansion


    def add_vehicle(self, veh_type: str, route):
        if veh_type not in self.veh_types:
            raise ValueError("⚠️ Loại xe chưa tồn tại.")
        self.vehicles.append({
            "idx": len(self.vehicles),
            "type": veh_type,
            "route": np.array(route, dtype=np.int32, order="C")
        })
        self._invalidate_cache()


    def add_attribute(self, name: str, kind: str, data=None, agg: str = "sum", max_data=None):
        """
        Thêm thuộc tính mới (với dữ liệu kênh) vào tensor tương ứng và cập nhật schema.
        - name: tên thuộc tính
        - kind: "unary" | "binary" | "anary"
        - data: mảng dữ liệu cho kênh mới (dùng cho phép cộng).
        - max_data: dữ liệu để tính toán max (nếu None sẽ dùng lại `data`).
        Hybrid layout:
            unary : (n_vehicle_types, n_points)
            binary: (n_vehicle_types, n_points, n_points)
            anary : (n_vehicle_types, n_points, n_points)
        - agg : "sum" | "max"
        """
        if len(self.veh_types) == 0:
            raise ValueError("Bạn phải thêm ít nhất một loại xe trước khi thêm thuộc tính.")

        kind = kind.lower()
        agg  = agg.lower()
        kind_map = {"unary": 0, "binary": 1, "anary": 2}
        agg_map  = {"sum": 0, "max": 1}

        n_types = len(self.veh_types)
        if agg not in agg_map:
            raise ValueError("agg phải là 'sum' hoặc 'max'")

        if data is not None:
            data = as_f32_c(np.ascontiguousarray(data))
        if max_data is not None:
            max_data = as_f32_c(np.ascontiguousarray(max_data))

        def _check_shape(arr, expected_shape, label):
            if arr is None:
                return False
            if arr.shape != expected_shape:
                raise ValueError(f"{label} phải có shape {expected_shape}, got {arr.shape}")
            return True

        if kind == "unary":
            self.attr_unary.append(name)
            if self.UA.shape[0] == 0:
                self.UA = np.zeros((n_types, self.n_points, 0), dtype=np.float32, order="C")
                self.UM = np.zeros((n_types, self.n_points, 0), dtype=np.float32, order="C")

            newA = np.zeros((n_types, self.n_points, 1), dtype=np.float32, order="C")
            newM = np.zeros((n_types, self.n_points, 1), dtype=np.float32, order="C")
            self.UA = as_f32_c(np.concatenate([self.UA, newA], axis=2))
            self.UM = as_f32_c(np.concatenate([self.UM, newM], axis=2))

            expected = (n_types, self.n_points)
            if agg == "sum":
                if _check_shape(data, expected, "UA data"):
                    self.UA[:, :, -1] = data
                if max_data is not None:
                    _check_shape(max_data, expected, "UM max_data")
                    self.UM[:, :, -1] = max_data
                elif data is not None:
                    self.UM[:, :, -1] = data
            else:  # agg == "max"
                effective = max_data if max_data is not None else data
                if effective is None:
                    raise ValueError("Cần cung cấp max_data hoặc data khi agg='max'")
                _check_shape(effective, expected, "UM data")
                self.UM[:, :, -1] = effective
                if data is not None:
                    self.UA[:, :, -1] = data

            idx = self.UA.shape[2] - 1

        elif kind == "binary":
            self.attr_binary.append(name)
            if self.BA.shape[0] == 0:
                self.BA = np.zeros((n_types, self.n_points, self.n_points, 0), dtype=np.float32, order="C")
                self.BM = np.zeros((n_types, self.n_points, self.n_points, 0), dtype=np.float32, order="C")

            newA = np.zeros((n_types, self.n_points, self.n_points, 1), dtype=np.float32, order="C")
            newM = np.zeros((n_types, self.n_points, self.n_points, 1), dtype=np.float32, order="C")
            self.BA = as_f32_c(np.concatenate([self.BA, newA], axis=3))
            self.BM = as_f32_c(np.concatenate([self.BM, newM], axis=3))

            expected_shape = (n_types, self.n_points, self.n_points)
            if agg == "sum":
                if _check_shape(data, expected_shape, "BA data"):
                    self.BA[:, :, :, -1] = data
                if max_data is not None:
                    _check_shape(max_data, expected_shape, "BM max_data")
                    self.BM[:, :, :, -1] = max_data
                elif data is not None:
                    self.BM[:, :, :, -1] = data
            else:
                effective = max_data if max_data is not None else data
                if effective is None:
                    raise ValueError("Cần cung cấp max_data hoặc data khi agg='max'")
                _check_shape(effective, expected_shape, "BM data")
                self.BM[:, :, :, -1] = effective
                if data is not None:
                    self.BA[:, :, :, -1] = data

            idx = self.BA.shape[3] - 1

        elif kind == "anary":
            self.attr_anary.append(name)
            if self.AA.shape[0] == 0:
                self.AA = np.zeros((n_types, self.n_points, self.n_points, 0), dtype=np.float32, order="C")
                self.AM = np.zeros((n_types, self.n_points, self.n_points, 0), dtype=np.float32, order="C")

            newA = np.zeros((n_types, self.n_points, self.n_points, 1), dtype=np.float32, order="C")
            newM = np.zeros((n_types, self.n_points, self.n_points, 1), dtype=np.float32, order="C")
            self.AA = as_f32_c(np.concatenate([self.AA, newA], axis=3))
            self.AM = as_f32_c(np.concatenate([self.AM, newM], axis=3))

            expected_shape = (n_types, self.n_points, self.n_points)
            if agg == "sum":
                if _check_shape(data, expected_shape, "AA data"):
                    self.AA[:, :, :, -1] = data
                if max_data is not None:
                    _check_shape(max_data, expected_shape, "AM max_data")
                    self.AM[:, :, :, -1] = max_data
                elif data is not None:
                    self.AM[:, :, :, -1] = data
            else:
                effective = max_data if max_data is not None else data
                if effective is None:
                    raise ValueError("Cần cung cấp max_data hoặc data khi agg='max'")
                _check_shape(effective, expected_shape, "AM data")
                self.AM[:, :, :, -1] = effective
                if data is not None:
                    self.AA[:, :, :, -1] = data

            idx = self.AA.shape[3] - 1

        else:
            raise ValueError("kind phải là 'unary' / 'binary' / 'anary'")

        # Cập nhật schema
        self.attr_names.append(name)
        self.attr_kinds = np.append(self.attr_kinds, kind_map[kind]).astype(np.int32, copy=False)
        self.attr_aggs  = np.append(self.attr_aggs,  agg_map[agg]).astype(np.int32, copy=False)
        self.attr_ch_idx= np.append(self.attr_ch_idx, idx).astype(np.int32, copy=False)
        self.name_to_idx[name] = len(self.attr_names) - 1

        # Khởi tạo thống kê vi phạm (nếu dùng học tự động)
        for vt in self.veh_types:
            self.constraint_stat[(vt, name)] = 0

        self._invalidate_cache()



    def set_constraint(self, veh_type: str, attr_name: str, value: float, mode="add"):
        """ mode: 'add' → sum, 'max' → max """
        self.constraints_dict[(veh_type, attr_name)] = {"type": mode.lower(), "value": value}


    # ---------------- HỌC & CẤU TRÚC ----------------
    def reset_schema(self):
        self.attr_names.clear()
        self.attr_kinds = np.zeros(0, np.int32)
        self.attr_aggs  = np.zeros(0, np.int32)
        self.attr_ch_idx= np.zeros(0, np.int32)
        self.name_to_idx.clear()
        self._invalidate_cache()

    def _sanitize_inputs(self, *arrays):
        for a in arrays:
            if not a.flags['C_CONTIGUOUS']:
                raise RuntimeError(f"{a.shape} not contiguous")
            if a.dtype == np.float64:
                raise RuntimeError("float64 detected; use float32")


    # ---------------- Vector hoá build constraints (Phase 5) ----------------
    def build_constraints_auto(self):
        """
        Trả:
            limits: float32 [m, n_attr] (np.inf nếu không đặt)
            modes : int32   [m, n_attr] (0=ADD/sum, 1=MAX), mặc định broadcast từ self.attr_aggs
        """
        m = len(self.vehicles)
        n_attr = len(self.attr_names)

        vt_index = {vt: i for i, vt in enumerate(self.veh_types)}
        veh_types_of_vehicle = np.fromiter((vt_index[v["type"]] for v in self.vehicles),
                                           count=m, dtype=np.int32)

        # Gom theo loại xe
        per_type_attr_idx = {}
        per_type_limits = {}
        per_type_modes = {}
        for (veh_type, attr_name), conf in self.constraints_dict.items():
            vt = vt_index.get(veh_type, None)
            if vt is None:
                continue
            aidx = self.name_to_idx.get(attr_name, None)
            if aidx is None:
                continue
            per_type_attr_idx.setdefault(vt, []).append(aidx)
            per_type_limits.setdefault(vt, []).append(np.float32(conf["value"]))
            mode_flag = 0 if conf.get("type", "add") == "add" else 1
            per_type_modes.setdefault(vt, []).append(np.int32(mode_flag))

        limits = np.full((m, n_attr), np.inf, dtype=np.float32, order="C")
        modes  = np.broadcast_to(self.attr_aggs.astype(np.int32), (m, n_attr)).copy(order="C")

        for vt, cols in per_type_attr_idx.items():
            cols = np.asarray(cols, dtype=np.int32)
            vals = np.asarray(per_type_limits[vt], dtype=np.float32)
            mode_vals = np.asarray(per_type_modes[vt], dtype=np.int32)
            mask = (veh_types_of_vehicle == vt)
            if mask.any():
                limits[np.ix_(mask, cols)] = vals
                modes[np.ix_(mask, cols)] = mode_vals

        return limits, modes


    def _build_routes(self):
        m = len(self.vehicles)
        routes = np.zeros((m, self.n_points), dtype=np.int32, order="C")
        route_sizes = np.zeros(m, dtype=np.int32, order="C")
        for i, v in enumerate(self.vehicles):
            r = np.asarray(v["route"], dtype=np.int32, order="C")
            L = r.shape[0]
            routes[i, :L] = r
            route_sizes[i] = L
        return routes, route_sizes


    def _build_attr_orders(self, names):
        """
        Xếp thứ tự thuộc tính cho mỗi xe dựa theo thống kê vi phạm theo loại.
        """
        m = len(self.vehicles)
        n_attr = len(names)
        orders = np.empty((m, n_attr), dtype=np.int32, order="C")

        vt_index = {vt: i for i, vt in enumerate(self.veh_types)}
        veh_types_of_vehicle = np.fromiter((vt_index[v["type"]] for v in self.vehicles),
                                           count=m, dtype=np.int32)

        # Tạo order chuẩn theo loại xe
        per_type_order = {}
        for vt_name, vt_i in vt_index.items():
            scores = np.zeros(n_attr, dtype=np.int64)
            for a_idx, a_name in enumerate(names):
                scores[a_idx] = self.constraint_stat.get((vt_name, a_name), 0)
            per_type_order[vt_i] = np.argsort(-scores, kind="stable").astype(np.int32)

        # Gán order cho từng xe theo loại
        for vt_i in vt_index.values():
            mask = (veh_types_of_vehicle == vt_i)
            if mask.any():
                orders[mask] = per_type_order[vt_i]

        return orders


    def _build_inputs(self):
        # Phase 3 – schema (kinds/aggs/ch_idx)
        names = self.attr_names
        kinds, aggs, ch_idx, name_to_idx = build_attr_schema_auto(
            names, self.attr_kinds, self.attr_aggs, self.UA, self.BA, self.AA
        )

        # routes
        routes, route_sizes = self._build_routes()

        # constraints
        limits, modes = self.build_constraints_auto()

        # dtype/layout ép contiguous
        kinds  = as_i32_c(kinds)
        aggs   = as_i32_c(aggs)
        ch_idx = as_i32_c(ch_idx)
        routes = as_i32_c(routes)
        route_sizes = as_i32_c(route_sizes)
        limits = as_f32_c(limits)
        modes  = as_i32_c(modes)

        self._sanitize_inputs(
            self.UA, self.UM, self.BA, self.BM, self.AA, self.AM,
            routes, route_sizes, limits, modes, kinds, aggs, ch_idx,
        )
        return names, kinds, aggs, ch_idx, routes, route_sizes, limits, modes

    # ---------------- CACHE HELPERS ----------------
    def enable_cache(self):
        self.cache_enabled = True

    def disable_cache(self, clear=False):
        self.cache_enabled = False
        if clear:
            self.clear_cache()

    def clear_cache(self):
        self._route_cache.clear()

    def _invalidate_cache(self):
        self._cache_token += 1
        self.clear_cache()

    def _make_cache_key(self, vt_idx: int, route: np.ndarray, rlen: int, attr_order_row: np.ndarray):
        route_key = tuple(int(route[i]) for i in range(rlen))
        order_key = tuple(int(x) for x in attr_order_row.tolist()) if attr_order_row.size else ()
        return (self._cache_token, int(vt_idx), route_key, order_key)

    def _find_violation_position(
        self,
        kind: int,
        mode: int,
        channel: int,
        vt_idx: int,
        route: np.ndarray,
        rlen: int,
        limit: float,
    ):
        if rlen <= 0:
            return None
        limit = float(limit)

        if rlen <= 1:
            return None

        if mode == 0:  # sum
            if kind == 0:  # unary (skip depot=0)
                total = 0.0
                for idx in range(rlen):
                    node = int(route[idx])
                    if node == 0:
                        continue
                    if vt_idx >= self.UA.shape[0] or channel >= self.UA.shape[2]:
                        return None
                    total += float(self.UA[vt_idx, node, channel])
                    if total > limit:
                        return idx
            elif kind == 1:  # binary
                total = 0.0
                if rlen < 2:
                    return 0
                for idx in range(rlen - 1):
                    a = int(route[idx])
                    b = int(route[idx + 1])
                    if vt_idx >= self.BA.shape[0] or channel >= self.BA.shape[3]:
                        return None
                    total += float(self.BA[vt_idx, a, b, channel])
                    if total > limit:
                        return idx + 1
            else:  # anary
                total = 0.0
                if rlen < 2:
                    return 0
                for i in range(rlen):
                    ai = int(route[i])
                    for j in range(rlen):
                        if i == j:
                            continue
                        aj = int(route[j])
                        if vt_idx >= self.AA.shape[0] or channel >= self.AA.shape[3]:
                            return None
                        total += float(self.AA[vt_idx, ai, aj, channel])
                        if total > limit:
                            return max(i, j)
        else:  # mode == 1 (max)
            if kind == 0:  # unary (skip depot=0)
                for idx in range(rlen):
                    node = int(route[idx])
                    if node == 0:
                        continue
                    if vt_idx >= self.UM.shape[0] or channel >= self.UM.shape[2]:
                        return None
                    value = float(self.UM[vt_idx, node, channel])
                    if value > limit:
                        return idx
            elif kind == 1:
                if rlen < 2:
                    return 0
                for idx in range(rlen - 1):
                    a = int(route[idx])
                    b = int(route[idx + 1])
                    if vt_idx >= self.BM.shape[0] or channel >= self.BM.shape[3]:
                        return None
                    value = float(self.BM[vt_idx, a, b, channel])
                    if value > limit:
                        return idx + 1
            else:
                if rlen < 2:
                    return 0
                for i in range(rlen):
                    ai = int(route[i])
                    for j in range(rlen):
                        if i == j:
                            continue
                        aj = int(route[j])
                        if vt_idx >= self.AM.shape[0] or channel >= self.AM.shape[3]:
                            return None
                        value = float(self.AM[vt_idx, ai, aj, channel])
                        if value > limit:
                            return max(i, j)
        return rlen - 1

    def _apply_split_requests(self, split_requests):
        if not split_requests:
            return False
        applied = False
        for req in split_requests:
            v_idx = req["vehicle_index"]
            if v_idx >= len(self.vehicles):
                continue
            original_nodes = req["original_nodes"]
            if not original_nodes:
                continue

            fail_pos = int(req["fail_pos"])
            fail_pos = max(1, min(fail_pos, len(original_nodes) - 1))

            prefix = original_nodes[:fail_pos]
            remaining = [int(node) for node in original_nodes[fail_pos:] if int(node) != 0]

            # Nếu không còn gì để chia
            if not remaining or len(prefix) == 0:
                continue

            # Route hiện tại (đảm bảo kết thúc bằng depot)
            new_route_existing = [int(x) for x in prefix if int(x) != 0]
            new_route_existing.insert(0, 0)
            if new_route_existing[-1] != 0:
                new_route_existing.append(0)
            self.vehicles[v_idx]["route"] = np.array(new_route_existing, dtype=np.int32, order="C")

            # Route mới (đảm bảo bắt đầu và kết thúc bằng depot)
            veh_type = self.vehicles[v_idx]["type"]
            new_route_new = [0] + remaining + [0]
            if len(new_route_new) > 2:  # bỏ qua nếu chỉ là [0,0]
                self.add_vehicle(veh_type, new_route_new)
            applied = True

        if applied:
            self._invalidate_cache()
        return applied


    # ---------------- SUBPROBLEM / BATCH ----------------
    def _make_subproblem(self, sub_veh):
        P = Problem(self.n_points)
        P.veh_types = list(self.veh_types)
        P.attr_unary, P.attr_binary, P.attr_anary = list(self.attr_unary), list(self.attr_binary), list(self.attr_anary)
        P.constraints_dict = dict(self.constraints_dict)

        # tensors (ép contiguous)
        P.UA = as_f32_c(self.UA)
        P.UM = as_f32_c(self.UM)
        P.BA = as_f32_c(self.BA)
        P.BM = as_f32_c(self.BM)
        P.AA = as_f32_c(self.AA)
        P.AM = as_f32_c(self.AM)

        # schema
        P.attr_names   = list(self.attr_names)
        P.attr_kinds   = as_i32_c(np.copy(self.attr_kinds))
        P.attr_aggs    = as_i32_c(np.copy(self.attr_aggs))
        P.attr_ch_idx  = as_i32_c(np.copy(self.attr_ch_idx))
        P.name_to_idx  = dict(self.name_to_idx)

        # no scales

        P.vehicles = sub_veh
        return P


    # ---------------- HÀM KIỂM TRA CHÍNH ----------------
    def check_constraints_njit(self, verbose=True):
        iteration = 0
        max_iterations = max(50, self.n_points * 4 + len(self.vehicles) * 6 + 10)

        prev_state_key = None
        while True:
            iteration += 1
            if iteration > max_iterations:
                raise RuntimeError("Quá nhiều lần tách tuyến do vi phạm constraint; vui lòng kiểm tra dữ liệu.")

            names, kinds, aggs, ch_idx, routes, route_sizes, limits, modes = self._build_inputs()
            attr_orders = self._build_attr_orders(names)

            vt_index = {vt: i for i, vt in enumerate(self.veh_types)}
            veh_types_of_vehicle = np.fromiter((vt_index[v["type"]] for v in self.vehicles),
                                               count=len(self.vehicles), dtype=np.int32)
            veh_types_of_vehicle = as_i32_c(veh_types_of_vehicle)

            m = len(self.vehicles)
            n_attr = len(self.attr_names)
            use_cache = self.cache_enabled and n_attr > 0
            all_cached = False
            cache_keys = [None] * m
            cached_rows = {}

            if use_cache:
                all_cached = True
                for v_idx in range(m):
                    rlen = int(route_sizes[v_idx])
                    vt_i = int(veh_types_of_vehicle[v_idx])
                    key = self._make_cache_key(vt_i, routes[v_idx], rlen, attr_orders[v_idx])
                    cache_keys[v_idx] = key
                    entry = self._route_cache.get(key)
                    if entry is None:
                        all_cached = False
                    else:
                        cached_rows[v_idx] = entry

            if not use_cache or not all_cached:
                sums, maxs, violated, first_fail = _check_once_core(
                    self.UA, self.UM, self.BA, self.BM, self.AA, self.AM,
                    routes, route_sizes,
                    kinds, limits, modes, attr_orders,
                    veh_types_of_vehicle,
                    ch_idx,
                )

                if use_cache:
                    for v_idx in range(m):
                        key = cache_keys[v_idx]
                        if key is None:
                            continue
                        self._route_cache[key] = {
                            "sums": np.array(sums[v_idx], copy=True),
                            "maxs": np.array(maxs[v_idx], copy=True)
                        }
            else:
                sums = np.zeros((m, n_attr), dtype=np.float32)
                maxs = np.zeros((m, n_attr), dtype=np.float32)
                violated = np.zeros(m, dtype=np.bool_)
                first_fail = -np.ones(m, dtype=np.int64)

                for v_idx in range(m):
                    entry = cached_rows[v_idx]
                    sums[v_idx] = entry["sums"]
                    maxs[v_idx] = entry["maxs"]

                    for attr_idx in attr_orders[v_idx]:
                        limit = limits[v_idx, attr_idx]
                        if not np.isfinite(limit):
                            continue
                        mode = int(modes[v_idx, attr_idx])
                        value = sums[v_idx, attr_idx] if mode == 0 else maxs[v_idx, attr_idx]
                        if value > limit:
                            violated[v_idx] = True
                            first_fail[v_idx] = int(attr_idx)
                            break

            split_requests = []
            for v_idx in range(m):
                if not violated[v_idx]:
                    continue
                attr_idx = int(first_fail[v_idx])
                if attr_idx < 0:
                    continue
                fail_pos = self._find_violation_position(
                    kind=int(kinds[attr_idx]),
                    mode=int(modes[v_idx, attr_idx]),
                    channel=int(ch_idx[attr_idx]),
                    vt_idx=int(veh_types_of_vehicle[v_idx]),
                    route=routes[v_idx],
                    rlen=int(route_sizes[v_idx]),
                    limit=float(limits[v_idx, attr_idx]),
                )
                if fail_pos is None:
                    continue
                original_nodes = routes[v_idx, :int(route_sizes[v_idx])].astype(np.int32).tolist()
                split_requests.append({
                    "vehicle_index": v_idx,
                    "fail_pos": fail_pos,
                    "original_nodes": original_nodes,
                })

            if split_requests:
                if self._apply_split_requests(split_requests):
                    # Keep iteration cap fixed to avoid runaway loops
                    continue

            if verbose:
                self._print_report(names, limits, modes, sums, maxs, violated, first_fail)

            for v_idx, v in enumerate(self.vehicles):
                if violated[v_idx]:
                    a_idx = first_fail[v_idx]
                    if a_idx >= 0:
                        attr = names[a_idx]
                        key = (v["type"], attr)
                        self.constraint_stat[key] = self.constraint_stat.get(key, 0) + 1
                        self.total_violations += 1

            # Guard: detect no progress across iterations while still violated
            state_key = tuple(tuple(int(x) for x in v["route"]) for v in self.vehicles)
            if np.any(violated) and state_key == prev_state_key:
                # Build a brief diagnostic for the first violating vehicle
                first_v = int(np.argmax(violated))
                a_idx = int(first_fail[first_v]) if first_fail[first_v] >= 0 else -1
                attr_name = names[a_idx] if 0 <= a_idx < len(names) else "?"
                mode_name = "ADD" if modes[first_v, a_idx] == 0 else "MAX" if a_idx >= 0 else "?"
                val = float(sums[first_v, a_idx] if modes[first_v, a_idx] == 0 else maxs[first_v, a_idx]) if a_idx >= 0 else float("nan")
                lim = float(limits[first_v, a_idx]) if a_idx >= 0 else float("nan")
                raise RuntimeError(
                    f"Vòng lặp không tiến triển khi tách tuyến. Xe #{first_v} tiếp tục vi phạm '{attr_name}' (mode={mode_name}) "
                    f"giá trị={val:.3f} > giới hạn={lim:.3f}. Hãy kiểm tra dữ liệu/giới hạn hoặc attr liên quan."
                )
            prev_state_key = state_key

            self._update_learning()
            return violated


    # ---------------- BÁO CÁO / HỌC LẠI ----------------
    def _print_report(self, all_attrs, limits, modes, sums, maxs, violated, first_fail):
        print("\n📘 KẾT QUẢ KIỂM TRA CONSTRAINTS (Batch)\n")
        for v_idx, v in enumerate(self.vehicles):
            route = v["route"].tolist()
            vtype = v["type"]
            print(f"🚗 Xe #{v_idx} ({vtype}) | Route: {route}")
            stop_flag = False
            for a_idx, attr in enumerate(all_attrs):
                if not np.isfinite(limits[v_idx, a_idx]):  # không đặt limit
                    continue
                mode = "ADD" if modes[v_idx, a_idx] == 0 else "MAX"
                val_sum, val_max, limit = sums[v_idx, a_idx], maxs[v_idx, a_idx], limits[v_idx, a_idx]
                violated_flag = (mode == "ADD" and val_sum > limit) or (mode == "MAX" and val_max > limit)
                if stop_flag:
                    print(f"   ⏩ {attr:<14} | Bỏ qua (đã vi phạm trước)")
                    continue
                status = "❌ VI PHẠM" if violated_flag else "✅ OK"
                print(f"   - {attr:<14} | Mode: {mode:<3} | Tổng: {val_sum:6.2f} | Max: {val_max:5.2f} | Giới hạn: {limit:6.2f} → {status}")
                if violated_flag:
                    stop_flag = True
                    print(f"⚠️  → Xe #{v_idx} vi phạm tại '{attr}' (mode={mode})\n")
            if not stop_flag:
                print("✅ Xe này hợp lệ hoàn toàn.\n")

    def _update_learning(self):
        if self.total_violations and self.total_violations % self.reorder_every == 0:
            print(f"🔄 Học lại thứ tự sau {self.total_violations} lần vi phạm.")

    # ---------------- RERoot ROUTES (xoay route bắt đầu từ nút xa depot nhất) ----------------
    def set_distance_matrix(self):
        distance_idx = self.name_to_idx.get("distance", None)
        if distance_idx is None or self.attr_kinds[distance_idx] != 1:
            raise ValueError("Cần có thuộc tính 'distance' kiểu binary để thiết lập dist_matrix.")
        
        dist = np.asarray(dist)
        if dist.ndim != 2 or dist.shape != (self.n_points, self.n_points):
            raise ValueError(f"dist_matrix phải có shape ({self.n_points}, {self.n_points})")
        self.dist_matrix = np.ascontiguousarray(dist, dtype=np.float32)
        for i in range(self.n_points):
            self.dist_matrix[i, i] = 0.0
        # Symmetrize the matrix without any scaling
        for i in range(self.n_points):
            for j in range(i + 1, self.n_points):
                d = 0.5 * (self.dist_matrix[i, j] + self.dist_matrix[j, i])
                self.dist_matrix[i, j] = self.dist_matrix[j, i] = d

    def reroot_routes_by_farthest_from(self, depot: int = 0, keep_single_depot_at_end: bool = True, include_depot_in_choice: bool = False):
        if self.dist_matrix is None:
            raise RuntimeError("Chưa thiết lập dist_matrix; hãy gọi set_distance_matrix trước.")
        if depot < 0 or depot >= self.n_points:
            raise ValueError("depot ngoài phạm vi n_points")

        changed = False
        for v in self.vehicles:
            r = v["route"].astype(np.int32)
            if r.size == 0:
                continue
            # danh sách index ứng viên để chọn xa nhất
            if include_depot_in_choice:
                candidates = list(range(r.size))
            else:
                candidates = [i for i in range(r.size) if int(r[i]) != depot]
            if not candidates:
                continue
            far_idx = max(candidates, key=lambda i: float(self.dist_matrix[depot, int(r[i])]))

            # xoay route để bắt đầu từ far_idx
            new_route = np.concatenate([r[far_idx:], r[:far_idx]]).tolist()
            if keep_single_depot_at_end:
                if any(int(x) == depot for x in new_route):
                    new_route = [int(x) for x in new_route if int(x) != depot]
                    new_route.append(int(depot))
            v["route"] = np.array(new_route, dtype=np.int32, order="C")
            changed = True

        if changed:
            self._invalidate_cache()
