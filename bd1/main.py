if __name__ == "__main__":
    print("=" * 60)
    print("Starting Ulaanbaatar Route Finder")
    print("=" * 60)
    print()

    print("Server starting at:")
    print("  API: http://localhost:8000/")
    print("  Web: http://localhost:8000/web/")
    print()

    import app.api as api_module

    api_module.load_graph()
    api_module.app.run(host="0.0.0.0", port=8000, debug=True)