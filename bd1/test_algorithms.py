from collections import defaultdict
from app.algos import bfs, dijkstra, dfs

def create_test_graph():
    adj = defaultdict(list)

    adj[0].append((1, 100))
    adj[0].append((2, 200))

    adj[1].append((3, 50))
    adj[1].append((4, 150))

    adj[2].append((4, 200))

    adj[3].append((4, 100))

    return adj

def test_bfs():
    print("Testing BFS (Fewest Steps)...")
    adj = create_test_graph()

    path = bfs(adj, 0, 4)
    print(f"  Path from 0 to 4: {path}")
    assert len(path) == 3, f"Expected 3 nodes, got {len(path)}"
    print("  ✓ Test passed")

    path = bfs(adj, 4, 0)
    print(f"  Path from 4 to 0 (no path): {path}")
    assert len(path) == 0, "Expected no path"
    print("  ✓ Test passed")

    print("✓ BFS tests passed!\n")

def test_dijkstra():
    print("Testing Dijkstra (Shortest Path)...")
    adj = create_test_graph()

    path, dist = dijkstra(adj, 0, 4)
    print(f"  Path from 0 to 4: {path}, distance: {dist}m")
    assert dist == 250, f"Expected 250m, got {dist}m"
    print("  ✓ Test passed")

    path, dist = dijkstra(adj, 0, 3)
    print(f"  Path from 0 to 3: {path}, distance: {dist}m")
    assert dist == 150, f"Expected 150m, got {dist}m"
    print("  ✓ Test passed")

    print("✓ Dijkstra tests passed!\n")

def test_dfs():
    print("Testing DFS (All Paths)...")
    adj = create_test_graph()

    paths = dfs(adj, 0, 4, max_paths=10)
    print(f"  Found {len(paths)} paths from 0 to 4:")
    for i, path in enumerate(paths, 1):
        print(f"    Path {i}: {path}")

    assert len(paths) >= 3, f"Expected at least 3 paths, got {len(paths)}"
    print("  ✓ Test passed")

    print("✓ DFS tests passed!\n")

def run_all_tests():
    print("=" * 60)
    print("ALGORITHM UNIT TESTS")
    print("=" * 60)
    print()

    try:
        test_bfs()
        test_dijkstra()
        test_dfs()

        print("=" * 60)
        print("✓ ALL TESTS PASSED!")
        print("=" * 60)
        return True
    except AssertionError as e:
        print(f"\n TEST FAILED: {e}")
        return False

if __name__ == "__main__":
    run_all_tests()