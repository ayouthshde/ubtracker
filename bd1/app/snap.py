import pyproj

def find_nearest_node(graph, lat, lng):
    transformer = pyproj.Transformer.from_crs(
        "EPSG:4326", "EPSG:3857", always_xy=True
    )
    x, y = transformer.transform(lng, lat)

    nearest_id = 0
    min_distance = float("inf")

    for node_id, node in enumerate(graph.node_of):
        dx = node.x - x
        dy = node.y - y
        distance = (dx * dx + dy * dy) ** 0.5

        if distance < min_distance:
            min_distance = distance
            nearest_id = node_id

    return nearest_id


def node_to_latlon(graph, node_id):
    node = graph.node_of[node_id]

    transformer = pyproj.Transformer.from_crs(
        "EPSG:3857", "EPSG:4326", always_xy=True
    )
    lng, lat = transformer.transform(node.x, node.y)

    return lat, lng