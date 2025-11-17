from collections import defaultdict

class Node:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __hash__(self):
        return hash((round(self.x), round(self.y)))

    def __eq__(self, other):
        return round(self.x) == round(other.x) and round(self.y) == round(other.y)


class Graph:
    def __init__(self):
        self.adj = defaultdict(list)

        self.node_map = {}
        self.node_of = []
        self.next_id = 0

    def add_node(self, x, y):
        node = Node(x, y)

        if node not in self.node_map:
            self.node_map[node] = self.next_id
            self.node_of.append(node)
            self.next_id += 1

        return self.node_map[node]

    def add_edge(self, from_id, to_id, weight):
        if from_id != to_id:
            self.adj[from_id].append((to_id, weight))

    def get_neighbors(self, node_id):
        return self.adj[node_id]

    def node_count(self):
        return len(self.node_of)

    def edge_count(self):
        total = 0
        for neighbors in self.adj.values():
            total += len(neighbors)
        return total


def build_graph(roads_gdf, use_time_weight=False):
    graph = Graph()

    print("Building graph...")
    if use_time_weight:
        print("  Weight mode: TRAVEL TIME (minutes)")
    else:
        print("  Weight mode: DISTANCE (meters)")

    for idx, row in roads_gdf.iterrows():
        geom = row.geometry
        if geom is None:
            continue

        is_oneway = bool(row.get("is_oneway", False))
        speed_kmh = float(row.get("speed_kmh", 30))

        if speed_kmh <= 0:
            speed_kmh = 30

        if geom.geom_type == "LineString":
            coords = list(geom.coords)
            if len(coords) < 2:
                continue

            for i in range(len(coords) - 1):
                x1, y1 = coords[i]
                x2, y2 = coords[i + 1]

                node1 = graph.add_node(x1, y1)
                node2 = graph.add_node(x2, y2)

                distance_m = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

                if use_time_weight:
                    weight = (distance_m / 1000) / speed_kmh * 60
                else:
                    weight = distance_m

                graph.add_edge(node1, node2, weight)

                if not is_oneway:
                    graph.add_edge(node2, node1, weight)

        elif geom.geom_type == "MultiLineString":
            for line in geom.geoms:
                coords = list(line.coords)
                if len(coords) < 2:
                    continue

                for i in range(len(coords) - 1):
                    x1, y1 = coords[i]
                    x2, y2 = coords[i + 1]

                    node1 = graph.add_node(x1, y1)
                    node2 = graph.add_node(x2, y2)

                    distance_m = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

                    if use_time_weight:
                        weight = (distance_m / 1000) / speed_kmh * 60
                    else:
                        weight = distance_m

                    graph.add_edge(node1, node2, weight)

                    if not is_oneway:
                        graph.add_edge(node2, node1, weight)

    print(f"Nodes: {graph.node_count()}")
    print(f"Edges: {graph.edge_count()}")

    return graph