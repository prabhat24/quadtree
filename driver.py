from quadtree import Cab, Quad, Point

if __name__ == "__main__":
    root = Quad(Point(100, 100), 100, 100)
    a = Cab("Amit")
    b = Cab("Bhavna")
    c = Cab("Chirag")
    d = Cab("Divya")

    root.insert(a, Point(120, 120))
    root.insert(b, Point(80, 80))
    root.insert(c, Point(150, 150))
    root.insert(d, Point(20, 20))

    query_point = Point(110, 110)
    results = root.find_nearest_cabs(query_point, k=3)
    for r in results:
        print(f"Cab {r['cab'].name} at ({r['loc'].x}, {r['loc'].y}) dist2={r['dist2']}")
