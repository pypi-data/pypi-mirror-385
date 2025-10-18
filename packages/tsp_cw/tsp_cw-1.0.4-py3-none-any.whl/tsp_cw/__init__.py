
"""
# 🧭 tsp_cw — Numba-Accelerated TSP Solver

**`tsp_cw`** là thư viện Python nhẹ, được tối ưu bằng **Numba** cho các bài toán  
**Travelling Salesman Problem (TSP)** và các biến thể heuristic.  
Nó cung cấp ba giải thuật chính: **Clarke–Wright**, **Greedy**, và **Greedy + λ**,  
cùng thuật toán **2-opt local search** để cải thiện lời giải.

---

## 🚀 Tính năng nổi bật

- **Hiệu năng cực nhanh**: mọi thuật toán được biên dịch JIT bằng Numba.  
- **Tự động warmup**: chỉ cần gọi `tsp_cw.warmup()` để biên dịch trước khi chạy thực tế.  
- **Ba giải thuật TSP chính**:
  - 🧩 Clarke–Wright Savings heuristic  
  - ⚡ Greedy nearest-neighbor  
  - 🔀 Greedy + λ (linear combination heuristic)
- **Local search 2-opt** có thể bật/tắt tùy chọn.  
- **Colab-safe optimization**: tránh crash kernel khi chạy trong môi trường Google Colab.

---

## 📦 Cài đặt

### Từ PyPI
```bash
pip install tsp-cw
```

### Hoặc cài thủ công (nếu bạn đang phát triển)
```bash
git clone https://github.com/thucnc7/tsp-cw.git
cd tsp-cw
pip install -e .
```

---

## 🧠 Cấu trúc thư viện

```
tsp_cw/
├── __init__.py          # export các hàm public
├── tsp_cw.py            # code chính chứa heuristic và 2-opt
└── README.md            # tài liệu này
```

Các hàm quan trọng:

| Hàm | Mô tả |
|-----|-------|
| `clarke_wright(D)` | Clarke–Wright savings heuristic |
| `greedy_tsp(D)` | Greedy nearest-neighbor heuristic |
| `greedy_lambda_tsp(D, λ)` | Greedy + λ heuristic |
| `two_opt(D, route)` | Local search 2-opt cải thiện lời giải |
| `tour_length_from_D(D, route)` | Tính tổng chiều dài route |
| `build_tsp_route(D, algo_id, ...)` | Hàm tổng hợp chọn thuật toán |
| `warmup()` | Compile sẵn toàn bộ kernel Numba |

---

## ⚡ Hướng dẫn sử dụng cơ bản

```python
import numpy as np
from tsp_cw import build_tsp_route, tour_length_from_D

D = np.array([
    [0, 2, 9, 10],
    [1, 0, 6, 4],
    [15, 7, 0, 8],
    [6, 3, 12, 0]
], dtype=np.float64)

route = build_tsp_route(D, algo_id=0, local_search=True)
print("Best route:", route)
print("Total distance:", tour_length_from_D(D, route))
```

---

## ☁️ Hướng dẫn cho Google Colab

Colab thường gây crash khi Numba ghi cache ra `/root`.  
Hãy đặt 3 dòng này **trước khi import thư viện**:

```python
import os
os.environ["PYDEVD_DISABLE_FILE_VALIDATION"] = "1"
os.environ["PYDEVD_USE_FRAME_EVAL"] = "NO"
os.environ["NUMBA_CACHE_DIR"] = "/tmp"
```

> 👉 Sau đó import và gọi `warmup()`:
```python
from tsp_cw import warmup
warmup()
```

→ Kernel sẽ không restart, cache an toàn, tốc độ giữ nguyên.

---

## 🧪 Benchmark nhỏ

| n (điểm) | Clarke–Wright | Greedy | Greedy + λ | 2-opt improve |
|-----------|----------------|--------|-------------|---------------|
| 50 | ~2 ms | ~1 ms | ~3 ms | ~4 ms |
| 200 | ~8 ms | ~6 ms | ~10 ms | ~12 ms |
| 500 | ~25 ms | ~18 ms | ~32 ms | ~40 ms |

> (chạy trên macOS M1, Python 3.12, Numba 0.60)

---

## ⚙️ Tham số trong `build_tsp_route`

| Tên | Mặc định | Ý nghĩa |
|------|-----------|----------|
| `algo_id` | 0 | 0=Clarke–Wright, 1=Greedy, 2=Greedy + λ |
| `lambda_value` | 0.5 | hệ số λ trong Greedy + λ |
| `local_search` | True | bật/tắt 2-opt |
| `max_iter` | 1000 | giới hạn lặp 2-opt |
| `seed` | 42 | random seed để reproducible |

---

## 🪶 Giấy phép

MIT License © 2025 Le Sy Thuc  
Tự do sử dụng cho học tập, nghiên cứu và thương mại.

---

✅ **Tác giả**: *Lê Sỹ Thức*  
🎓 *Khoa Học Máy Tính & Thông Tin – Đại Học Khoa Học Tự Nhiên – ĐHQGHN*  
🧪 *Dự án SAHUS Lab — Smart Logistics Optimization*

"""
# tsp_cw/__init__.py

from .tsp_cw import build_tsp_route, build_tsp_route_from_param, tour_length_from_D

__version__ = "1.0.4"
__author__ = "Le Sy Thuc"
__email__ = "thuc@example.com"

def help():
    """Hiển thị hướng dẫn nhanh cho tsp_cw."""
    print(
        """
🧭 tsp_cw — Numba-Accelerated TSP Solver
-----------------------------------------
Các hàm chính:
  • clarke_wright(D)        — Clarke–Wright savings heuristic
  • greedy_tsp(D)           — Greedy nearest neighbor
  • greedy_lambda_tsp(D, λ) — Hybrid Greedy + λ
  • two_opt(D, route)       — Local search 2-opt
  • build_tsp_route(...)    — Tự động chọn và chạy thuật toán
  • tour_length_from_D(...) — Tính chiều dài route
  • warmup()                — Compile Numba kernels trước khi chạy

Ví dụ sử dụng:
  >>> import numpy as np
  >>> from tsp_cw import build_tsp_route, tour_length_from_D
  >>> D = np.array([
  ...     [0, 2, 9, 10],
  ...     [1, 0, 6, 4],
  ...     [15, 7, 0, 8],
  ...     [6, 3, 12, 0]
  ... ])
  >>> route = build_tsp_route(D, algo_id=0, local_search=True)
  >>> print("Route:", route)
  >>> print("Length:", tour_length_from_D(D, route))

Chi tiết thêm xem README.md
"""
    )
