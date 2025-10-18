import os
import sys
import platform
import numpy as np
from numba import njit

# ---------- Colab-safe: đổi nơi cache Numba để an toàn ----------
try:
    # Colab có module google.colab, tránh ghi cache vào chỗ bất ổn
    import google.colab  # type: ignore
    os.environ.setdefault("NUMBA_CACHE_DIR", "/tmp")
    from numba import config as _numba_config  # noqa: E402
    _numba_config.CACHE_DIR = os.environ["NUMBA_CACHE_DIR"]
    print("[tsp_cw] Colab detected → using NUMBA_CACHE_DIR=/tmp")
except Exception:
    pass

# ---------- Defaults ----------
DEFAULT_ALGO_ID = 0
DEFAULT_LAMBDA = 0.5
DEFAULT_LOCAL_SEARCH = True
DEFAULT_SEED = 42
DEFAULT_MAX_ITER = 1000

# ---------- Core cost ----------
@njit(fastmath=True, cache=True, nopython=True, parallel=False)
def tour_length_from_D(D, tour):
    total = 0.0
    for i in range(len(tour) - 1):
        total += D[tour[i], tour[i + 1]]
    total += D[tour[-1], tour[0]]
    return total

# ---------- Heuristics ----------
@njit(fastmath=True, cache=True, nopython=True, parallel=False)
def greedy_tsp(D):
    n = D.shape[0]
    visited = np.zeros(n, dtype=np.bool_)
    route = np.zeros(n, dtype=np.int64)
    route[0] = 0
    visited[0] = True
    for i in range(1, n):
        best_j = -1
        best_dist = 1e18
        prev = route[i - 1]
        for j in range(n):
            if (not visited[j]) and (D[prev, j] < best_dist):
                best_j = j
                best_dist = D[prev, j]
        route[i] = best_j
        visited[best_j] = True
    return route

# Lưu ý: clarke_wright dùng list + sort; Numba đã hỗ trợ pattern này trong nopython.
@njit(fastmath=True, cache=True, nopython=True, parallel=False)
def clarke_wright(D):
    n = D.shape[0]
    depot = 0
    savings = []  # list[tuple(float,int,int)]
    for i in range(1, n):
        for j in range(i + 1, n):
            s = D[depot, i] + D[depot, j] - D[i, j]
            savings.append((s, i, j))
    # sort theo s giảm dần
    savings.sort(key=lambda x: x[0], reverse=True)

    # mỗi khách ban đầu là một chuỗi [i, depot]
    routes = []  # list[list[int]]
    for i in range(1, n):
        routes.append([i, depot])

    for k in range(len(savings)):
        _, i, j = savings[k]
        ri = -1
        rj = -1
        # tìm route chứa i và j ở đúng đầu/cuối để có thể nối
        for idx in range(len(routes)):
            r = routes[idx]
            if r[0] == i or r[-2] == i:
                ri = idx
            if r[0] == j or r[-2] == j:
                rj = idx
        if (ri != -1) and (rj != -1) and (ri != rj):
            r_left = routes[ri]
            r_right = routes[rj]
            # chỉ nối khi i ở đuôi (trước depot) và j ở đầu (sau depot)
            if r_left[-2] == i and r_right[0] == j:
                # merge: bỏ depot cuối của r_left rồi nối r_right
                merged = []
                for t in range(len(r_left) - 1):
                    merged.append(r_left[t])
                for t in range(len(r_right)):
                    merged.append(r_right[t])
                # xóa và thêm
                # swap pop để giữ O(1) khi remove theo index
                if ri > rj:
                    routes.pop(ri)
                    routes.pop(rj)
                else:
                    routes.pop(rj)
                    routes.pop(ri)
                routes.append(merged)

    best_route = [depot]
    for idx in range(len(routes)):
        r = routes[idx]
        # bỏ depot cuối
        for t in range(len(r) - 1):
            if r[t] != depot:
                best_route.append(r[t])
    best_route.append(depot)
    return np.array(best_route, dtype=np.int64)

@njit(fastmath=True, cache=True, nopython=True, parallel=False)
def greedy_lambda_tsp(D, lambda_value=0.5):
    n = D.shape[0]
    depot = 0
    visited = np.zeros(n, dtype=np.bool_)
    route = np.zeros(n, dtype=np.int64)
    route[0] = depot
    visited[depot] = True
    for i in range(1, n):
        best_j = -1
        best_cost = 1e18
        prev = route[i - 1]
        for j in range(n):
            if visited[j]:
                continue
            cost = lambda_value * D[prev, j] + (1.0 - lambda_value) * (
                D[depot, prev] + D[depot, j] - D[prev, j]
            )
            if cost < best_cost:
                best_cost = cost
                best_j = j
        route[i] = best_j
        visited[best_j] = True
    return route

# ---------- Local search: 2-opt (Colab-safe, không concatenate trong vòng lặp) ----------
@njit(fastmath=True, cache=True, nopython=True, parallel=False)
def two_opt(D, route, max_iter=1000):
    n = len(route)
    best_route = route.copy()
    best_length = tour_length_from_D(D, best_route)
    improved = True
    iteration = 0

    # buffer tạm để tránh cấp phát liên tục
    temp = np.empty_like(best_route)

    while improved and iteration < max_iter:
        improved = False
        iteration += 1

        for i in range(1, n - 2):
            for j in range(i + 1, n - 1):
                if j - i == 1:
                    continue
                # copy prefix
                for p in range(i):
                    temp[p] = best_route[p]
                # reverse đoạn [i, j)
                k = 0
                for idx in range(i, j):
                    temp[i + k] = best_route[j - 1 - k]
                    k += 1
                # copy suffix
                for p in range(j, n):
                    temp[p] = best_route[p]

                new_len = tour_length_from_D(D, temp)
                if new_len < best_length:
                    best_length = new_len
                    # commit
                    for p in range(n):
                        best_route[p] = temp[p]
                    improved = True
    return best_route

# ---------- High-level builder ----------
def build_tsp_route(
    D,
    algo_id=DEFAULT_ALGO_ID,
    local_search=DEFAULT_LOCAL_SEARCH,
    lambda_value=DEFAULT_LAMBDA,
    max_iter=DEFAULT_MAX_ITER,
    seed=DEFAULT_SEED,
):
    np.random.seed(seed)
    if algo_id == 0:
        route = clarke_wright(D)
    elif algo_id == 1:
        route = greedy_tsp(D)
    elif algo_id == 2:
        route = greedy_lambda_tsp(D, lambda_value)
    else:
        raise ValueError("Invalid algo_id (0=Clarke–Wright, 1=Greedy, 2=Greedy+Lambda)")

    if local_search:
        route = two_opt(D, route, max_iter=max_iter)
    return route

# ---------- Warmup ----------
def warmup():
    print("[tsp_cw] Warming up Numba kernels...")
    D = np.random.rand(8, 8)
    D = (D + D.T) / 2
    np.fill_diagonal(D, 0)
    build_tsp_route(D, algo_id=0, local_search=True)
    build_tsp_route(D, algo_id=1, local_search=False)
    build_tsp_route(D, algo_id=2, lambda_value=0.5)
    tour_length_from_D(D, np.arange(8, dtype=np.int64))
    print("[tsp_cw] Kernels ready and cached!")

if __name__ == "__main__":
    warmup()
    print("[tsp_cw] Example run finished.")
