from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from pathlib import Path
import geopandas as gpd

from .graph import build_graph
from .algos import bfs, dfs, dijkstra
from .snap import find_nearest_node, node_to_latlon

app = Flask(__name__)
CORS(app)

graph_distance = None
graph_time = None

BASE_DIR = Path(__file__).parent.parent
WEB_DIR = BASE_DIR / "web"


def load_graph():
    global graph_distance, graph_time

    if graph_distance is not None:
        return

    print("Loading road network...")
    roads_path = BASE_DIR / "data" / "roads_clean.gpkg"

    if not roads_path.exists():
        print("ERROR: roads_clean.gpkg not found!")
        print("Run preprocess.py first!")
        return

    roads = gpd.read_file(roads_path)

    print("\n1. Building DISTANCE graph...")
    graph_distance = build_graph(roads, use_time_weight=False)

    print("\n2. Building TIME graph...")
    graph_time = build_graph(roads, use_time_weight=True)

    print("\n✓ Both graphs loaded successfully!")


def parse_latlng(coord_str):
    try:
        parts = coord_str.split(",")
        lat = float(parts[0].strip())
        lng = float(parts[1].strip())
        return lat, lng
    except Exception:
        raise ValueError(f"Invalid coordinate format: {coord_str}")

@app.route("/")
def home():
    return jsonify(
        {
            "name": "Ulaanbaatar Route Finder API",
            "status": "running",
            "endpoints": [
                "/route/shortest (Dijkstra - distance)",
                "/route/fastest (Dijkstra - travel time)",
                "/route/fewest-steps (BFS)",
                "/route/all (DFS)",
                "/web/ (Frontend)",
            ],
        }
    )

@app.route("/web/")
@app.route("/web/<path:filename>")
def serve_web(filename=None):
    if filename is None:
        filename = "index.html"
    return send_from_directory(WEB_DIR, filename)


@app.route("/route/shortest")
def route_shortest():
    if graph_distance is None:
        return jsonify({"error": "Graph not loaded"}), 500

    try:
        src = request.args.get("src")
        dst = request.args.get("dst")

        if not src or not dst:
            return jsonify({"error": "Missing src or dst parameter"}), 400

        start_lat, start_lng = parse_latlng(src)
        end_lat, end_lng = parse_latlng(dst)

        start_node = find_nearest_node(graph_distance, start_lat, start_lng)
        end_node = find_nearest_node(graph_distance, end_lat, end_lng)

        path, distance = dijkstra(graph_distance.adj, start_node, end_node)

        if not path:
            return jsonify({
                "algorithm": "Dijkstra (Shortest)",
                "found": False,
                "message": "No path found between these points.",
            }), 200

        coordinates = []
        for node_id in path:
            lat, lng = node_to_latlon(graph_distance, node_id)
            coordinates.append([lat, lng])

        return jsonify({
            "algorithm": "Dijkstra (Shortest)",
            "found": True,
            "path": coordinates,
            "distance_m": round(distance, 2),
            "distance_km": round(distance / 1000, 2),
            "steps": len(path) - 1,
            "nodes": len(path),
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/route/fastest")
def route_fastest():
    if graph_time is None:
        return jsonify({"error": "Graph not loaded"}), 500

    try:
        src = request.args.get("src")
        dst = request.args.get("dst")

        if not src or not dst:
            return jsonify({"error": "Missing src or dst parameter"}), 400

        start_lat, start_lng = parse_latlng(src)
        end_lat, end_lng = parse_latlng(dst)

        start_node = find_nearest_node(graph_time, start_lat, start_lng)
        end_node = find_nearest_node(graph_time, end_lat, end_lng)

        path, travel_time = dijkstra(graph_time.adj, start_node, end_node)

        if not path:
            return jsonify({
                "algorithm": "Dijkstra (Fastest)",
                "found": False,
                "message": "No path found between these points.",
            }), 200

        coordinates = []
        for node_id in path:
            lat, lng = node_to_latlon(graph_time, node_id)
            coordinates.append([lat, lng])

        return jsonify({
            "algorithm": "Dijkstra (Fastest)",
            "found": True,
            "path": coordinates,
            "travel_time_min": round(travel_time, 2),
            "travel_time_formatted": f"{int(travel_time)} min {int((travel_time % 1) * 60)} sec",
            "steps": len(path) - 1,
            "nodes": len(path),
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/route/fewest-steps")
def route_fewest_steps():
    if graph_distance is None:
        return jsonify({"error": "Graph not loaded"}), 500

    try:
        src = request.args.get("src")
        dst = request.args.get("dst")

        if not src or not dst:
            return jsonify({"error": "Missing src or dst parameter"}), 400

        start_lat, start_lng = parse_latlng(src)
        end_lat, end_lng = parse_latlng(dst)

        start_node = find_nearest_node(graph_distance, start_lat, start_lng)
        end_node = find_nearest_node(graph_distance, end_lat, end_lng)

        path = bfs(graph_distance.adj, start_node, end_node)

        if not path:
            return jsonify({
                "algorithm": "BFS",
                "found": False,
                "message": "No path found between these points.",
            }), 200

        coordinates = []
        for node_id in path:
            lat, lng = node_to_latlon(graph_distance, node_id)
            coordinates.append([lat, lng])

        return jsonify({
            "algorithm": "BFS",
            "found": True,
            "path": coordinates,
            "steps": len(path) - 1,
            "nodes": len(path),
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/route/all")
def route_all():
    if graph_distance is None:
        return jsonify({"error": "Graph not loaded"}), 500

    try:
        src = request.args.get("src")
        dst = request.args.get("dst")
        max_paths = int(request.args.get("max_paths", 10))
        max_depth = int(request.args.get("max_depth", 40))

        if not src or not dst:
            return jsonify({"error": "Missing src or dst parameter"}), 400

        start_lat, start_lng = parse_latlng(src)
        end_lat, end_lng = parse_latlng(dst)

        start_node = find_nearest_node(graph_distance, start_lat, start_lng)
        end_node = find_nearest_node(graph_distance, end_lat, end_lng)

        paths = dfs(
            graph_distance.adj,
            start_node,
            end_node,
            max_paths=max_paths,
            max_depth=max_depth,
        )

        if not paths:
            return jsonify({
                "algorithm": "DFS",
                "found": False,
                "message": "No paths found between these points.",
            }), 200

        all_coordinates = []
        for path in paths:
            coords = []
            for node_id in path:
                lat, lng = node_to_latlon(graph_distance, node_id)
                coords.append([lat, lng])
            all_coordinates.append(coords)

        return jsonify({
            "algorithm": "DFS",
            "found": True,
            "paths": all_coordinates,
            "count": len(paths),
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    load_graph()
    app.run(host="0.0.0.0", port=8000, debug=True)