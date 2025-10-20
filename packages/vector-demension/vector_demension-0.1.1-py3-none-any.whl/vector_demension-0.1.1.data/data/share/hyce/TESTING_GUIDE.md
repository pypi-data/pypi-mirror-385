vậy # Hướng Dẫn Thiết Lập & Kiểm Thử Bộ Constraint Engine

Tài liệu này giúp bạn chuẩn bị môi trường, hiểu các biến/tính năng quan trọng và chạy bộ test mẫu đi kèm trong thư mục `My_code/tests/`.

---

## 1. Chuẩn Bị Môi Trường

### 1.1. Yêu cầu tối thiểu
- Python 3.9+ (khuyến nghị dùng 3.11).
- Công cụ `pip` để cài đặt gói.
- (Tùy chọn) `python -m venv` nếu muốn tạo môi trường ảo.

### 1.2. Tạo môi trường ảo (khuyến nghị)
```bash
python3 -m venv .venv
source .venv/bin/activate        # macOS/Linux
.venv\Scripts\activate           # Windows PowerShell
```

### 1.3. Cài đặt các gói cần thiết
```bash
python -m pip install --upgrade pip
python -m pip install numpy numba matplotlib pytest
```

> **Lưu ý:** nếu bạn dùng GPU/CPU đặc biệt, hãy cài đúng bản numba/numpy tương thích.

---

## 2. Cấu Trúc Chính & Tính Năng

### 2.1. Lớp `Problem` (`My_code/Core_class.py`)
| Thuộc tính | Ý nghĩa |
|------------|---------|
| `veh_types` | Danh sách loại xe. |
| `vehicles` | Danh sách xe; mỗi xe có `type`, `route` (mảng `int32`). |
| `attr_*` | Tên các thuộc tính theo nhóm `unary/binary/anary`. |
| `UA/UM`, `BA/BM`, `AA/AM` | Tensor dữ liệu sum/max tương ứng. |
| `constraints_dict` | Giới hạn theo từng `(loại xe, thuộc tính)`. |
| `cache_enabled` | Bật cache kết quả `check_constraints_njit`. |

### 2.2. Tính năng đặc biệt
- **Cache kết quả**: bật bằng `problem.enable_cache()`, tắt bằng `problem.disable_cache()` hoặc `problem.disable_cache(clear=True)` để xóa cache.
- **Tự động tách tuyến khi vi phạm**:
  - Khi `check_constraints_njit` phát hiện vi phạm, tuyến sẽ được cắt tại điểm vi phạm và thêm xe mới tiếp tục từ phần còn lại.
  - Depot (node 0) nên có giá trị thuộc tính bằng 0 để tránh vi phạm lặp.
- **`max_data` cho thuộc tính**: khi thêm thuộc tính `agg="max"`, truyền thêm `max_data=` để tùy chỉnh tensor `UM/BM/AM`. Nếu không cung cấp, hệ thống sẽ dùng `data`.

---

## 3. Chạy Các Bộ Test

### 3.1. Test đơn lẻ
```bash
python -m pytest My_code/tests/test_problem_features.py::test_cache_skips_kernel_when_enabled -s
```

### 3.2. Chạy toàn bộ test
```bash
python -m pytest My_code/tests -s
```

### 3.3. Các bộ test sẵn có
| File | Nội dung chính |
|------|----------------|
| `test_problem_features.py` | Kiểm tra đơn vị: thêm thuộc tính, tách tuyến, cache, giới hạn 0. |
| `test_random_export.py` | Sinh dữ liệu ngẫu nhiên và xuất CSV (`My_code/tests/output/random_constraint_runs.csv`). |
| `test_hybrid_kernel_scenarios.py` | Stress-test lớn, in log chi tiết và xuất CSV (`hybrid_scenario_details.csv`). |
| `test_demo_readable.py` | Demo nhỏ dễ chỉnh; chạy với `-s` để xem log gọn. |

---

## 4. Kịch Bản Demo Nhanh

```python
from Core_class import Problem
import numpy as np

P = Problem(n_points=6)
P.add_vehicle_type("Truck")
P.add_vehicle_type("Bike")

P.add_vehicle("Truck", route=[0, 1, 2])
P.add_vehicle("Bike", route=[3, 4])

unary = np.array(
    [[0.0, 2.0, 1.5, 0.5, 0.5, 0.5],
     [0.4, 0.6, 0.7, 0.3, 0.3, 0.3]],
    dtype=np.float32,
)
P.add_attribute("load", kind="unary", data=unary, agg="sum")

P.set_constraint("Truck", "load", value=5.0, mode="add")
P.set_constraint("Bike", "load", value=2.0, mode="add")

P.enable_cache()
violated = P.check_constraints_njit(verbose=True)
print("Vi phạm?", violated)
```

---

## 5. Lưu Ý Khi Tự Viết Test/CODE
1. Luôn thêm loại xe (`add_vehicle_type`) trước khi thêm thuộc tính.
2. Đảm bảo route chỉ chứa `int32` nằm trong `[0, n_points)`.
3. Khi thuộc tính tổng (`sum`) có depot, hãy đặt giá trị ở depot bằng `0.0` nếu muốn tránh vi phạm sau khi quay về kho.
4. Mỗi khi thêm/đổi thuộc tính hoặc constraint, cache sẽ tự vô hiệu (`_invalidate_cache`).
5. Nếu cần kiểm tra kỹ vị trí vi phạm, xem thêm hàm `_find_violation_position` và log từ `test_hybrid_kernel_scenarios.py`.

---

## 6. Sự Cố Thường Gặp
| Triệu chứng | Nguyên nhân & hướng xử lý |
|-------------|---------------------------|
| `RuntimeError: Quá nhiều lần tách tuyến...` | Depot có giá trị khác 0, hoặc constraint quá chặt khiến lặp vô hạn. Giảm tải ở depot hoặc nới constraint. |
| `pytest: command not found` | Môi trường chưa cài `pytest`. Cài bằng `python -m pip install pytest`. |
| `ModuleNotFoundError` khi import | Kiểm tra lại `sys.path.append(str(Path('My_code')))` hoặc chạy test từ thư mục gốc dự án. |

---

Chúc bạn xây dựng và kiểm thử hệ constraint engine hiệu quả. Nếu cần thêm ví dụ hoặc script hỗ trợ, bổ sung ngay tại thư mục `My_code/tests/` để dễ bảo trì. 
