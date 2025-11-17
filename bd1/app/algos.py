from collections import deque
import heapq

def bfs(graph_adj, start, goal):
    if start == goal:
        return [start]

    visited = {start: None}
    queue = deque([start])

    while queue:
        current = queue.popleft()

        for neighbor_id, distance in graph_adj.get(current, []):
            if neighbor_id not in visited:
                visited[neighbor_id] = current
                queue.append(neighbor_id)

                if neighbor_id == goal:
                    path = []
                    node = goal
                    while node is not None:
                        path.append(node)
                        node = visited[node]
                    path.reverse()
                    return path

    return []

def dfs(graph_adj, start, goal, max_paths=10, max_depth=30):
    all_paths = []
    current_path = []
    visited = set()

    def dfs_helper(node, depth):
        if len(all_paths) >= max_paths or depth > max_depth:
            return

        current_path.append(node)
        visited.add(node)

        if node == goal:
            all_paths.append(current_path.copy())
        else:
            for neighbor_id, distance in graph_adj.get(node, []):
                if neighbor_id not in visited:
                    dfs_helper(neighbor_id, depth + 1)

        visited.remove(node)
        current_path.pop()

    dfs_helper(start, 0)
    return all_paths


def dijkstra(graph_adj, start, goal):
    if start == goal:
        return [start], 0.0

    pq = [(0.0, start)]
    distances = {start: 0.0}
    previous = {start: None}
    visited = set()

    while pq:
        current_dist, current = heapq.heappop(pq)

        if current in visited:
            continue
        visited.add(current)

        if current == goal:
            path = []
            node = goal
            while node is not None:
                path.append(node)
                node = previous[node]
            path.reverse()
            return path, current_dist

        for neighbor_id, edge_distance in graph_adj.get(current, []):
            if neighbor_id in visited:
                continue

            new_dist = current_dist + edge_distance
            if new_dist < distances.get(neighbor_id, float("inf")):
                distances[neighbor_id] = new_dist
                previous[neighbor_id] = current
                heapq.heappush(pq, (new_dist, neighbor_id))

    return [], float("inf")