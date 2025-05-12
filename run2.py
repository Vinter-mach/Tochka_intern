import sys
import collections
from heapq import heappush, heappop


# Константы для символов ключей и дверей
keys_char = [chr(i) for i in range(ord('a'), ord('z') + 1)]
doors_char = [k.upper() for k in keys_char]
deltas = [(-1, 0), (0, -1), (1, 0), (0, 1)]
num_robots = 4


def get_input():
    """Чтение данных из стандартного ввода."""
    return [list(line.strip()) for line in sys.stdin]


def check_cell(r, c, n, m):
    return 0 <= r and r < n and 0 <= c and c < m


# A-Star estimation (not finished)
def calc_estimator(v1, v2, v3, v4, vertices, n, m, data):
    return 0

    used = [[0] * m for _ in range(n)]
    bfs_dist = [[0] * m for _ in range(n)]
    q = collections.deque()

    for i, v in enumerate([v1, v2, v3, v4], 1):
        _, r, c = vertices[v]
        used[r][c] = i
        bfs_dist[r][c] = 0
        q.append((r, c))

    max_steps = [0] * (num_robots + 1)
    while len(q) > 0:
        r, c = q.popleft()
        max_steps[used[r][c]] = max(max_steps[used[r][c]], bfs_dist[r][c])

        for dr, dc in deltas:
            nr, nc = r + dr, c + dc
            if not check_cell(nr, nc, n, m) or used[nr][nc] != 0:
                continue

            if data[nr][nc] == '#':
                continue

            if nr == vertices[v2][1] and nc == vertices[v2][2]:
                continue
            if nr == vertices[v3][1] and nc == vertices[v3][2]:
                continue
            if nr == vertices[v4][1] and nc == vertices[v4][2]:
                continue

            used[nr][nc] = used[r][c]
            bfs_dist[nr][nc] = bfs_dist[r][c] + 1
            q.append((nr, nc))

    return sum(max_steps)


def relax_state(r, c, cur_dist, cur_mask, v1, v2, v3, v4, vertices, v_idx, n, m, data, pq, dist):
    if v_idx[r][c] < 0:
        return

    key_idx = ord(data[r][c]) - ord('a')
    new_mask = cur_mask | (1 << key_idx)
    nv1, nv2, nv3, nv4 = sorted([v_idx[r][c], v2, v3, v4])

    if (new_mask, nv1, nv2, nv3, nv4) not in dist or dist[(new_mask, nv1, nv2, nv3, nv4)] > cur_dist:
        dist[(new_mask, nv1, nv2, nv3, nv4)] = cur_dist

        estimator = calc_estimator(nv1, nv2, nv3, nv4, vertices, n, m, data)
        heappush(pq, (cur_dist + estimator, cur_dist, new_mask, nv1, nv2, nv3, nv4))


def walk(cur_mask, v1, v2, v3, v4, vertices, v_idx, cnt_keys, cur_dist, n, m, data, pq, dist):
    cur_keys = set()
    for i in range(cnt_keys):
        if cur_mask & (1 << i) != 0:
            cur_keys.add(chr(i + ord('a')))

    used = [[False] * m for _ in range(n)]
    bfs_dist = [[0] * m for _ in range(n)]
    q = collections.deque()

    _, r, c = vertices[v1]
    used[r][c] = True
    bfs_dist[r][c] = 0
    q.append((r, c))

    while len(q) > 0:
        r, c = q.popleft()
        relax_state(r, c, cur_dist + bfs_dist[r][c], cur_mask, v1, v2, v3, v4, vertices, v_idx, n, m, data, pq, dist)

        for dr, dc in deltas:
            nr, nc = r + dr, c + dc
            if not check_cell(nr, nc, n, m) or used[nr][nc]:
                continue

            if data[nr][nc] == '#':
                continue

            if data[nr][nc] in doors_char and data[nr][nc].lower() not in cur_keys:
                continue

            if nr == vertices[v2][1] and nc == vertices[v2][2]:
                continue
            if nr == vertices[v3][1] and nc == vertices[v3][2]:
                continue
            if nr == vertices[v4][1] and nc == vertices[v4][2]:
                continue

            used[nr][nc] = True
            bfs_dist[nr][nc] = bfs_dist[r][c] + 1
            q.append((nr, nc))


def solve(data):
    n, m = len(data), len(data[0])

    vertices = []
    for i, line in enumerate(data):
        for j, ch in enumerate(line):
            if ch == '@':
                vertices.append((ch, i, j))
            elif ch in keys_char:
                vertices.insert(0, (ch, i, j))

    assert(len(vertices) >= num_robots and all(map(lambda v: v[0] == '@', vertices[-num_robots:])))

    cnt_keys = len(vertices) - num_robots
    all_keys_mask = 2**cnt_keys - 1


    v_idx = [[-num_robots - 1] * m for _ in range(n)]
    for i, (ch, r, c) in enumerate(vertices):
        v_idx[r][c] = (i + num_robots) % len(vertices) - num_robots

    pq = []
    dist = dict()
    used = set()
    # state: (mask, v1, v2, v3, v4)
    dist[(0, -4, -3, -2, -1)] = 0
    heappush(pq, (calc_estimator(-4, -3, -2, -1, vertices, n, m, data), 0, 0, -4, -3, -2, -1))

    while len(pq) > 0:
        _, cur_dist, cur_mask, v1, v2, v3, v4 = heappop(pq)
        if (cur_mask, v1, v2, v3, v4) in used:
            continue

        used.add((cur_mask, v1, v2, v3, v4))

        if cur_mask == all_keys_mask:
            return cur_dist

        walk(cur_mask, v1, v2, v3, v4, vertices, v_idx, cnt_keys, cur_dist, n, m, data, pq, dist)
        walk(cur_mask, v2, v1, v3, v4, vertices, v_idx, cnt_keys, cur_dist, n, m, data, pq, dist)
        walk(cur_mask, v3, v1, v2, v4, vertices, v_idx, cnt_keys, cur_dist, n, m, data, pq, dist)
        walk(cur_mask, v4, v1, v2, v3, vertices, v_idx, cnt_keys, cur_dist, n, m, data, pq, dist)


def main():
    data = get_input()
    result = solve(data)
    print(result)


if __name__ == '__main__':
    main()
