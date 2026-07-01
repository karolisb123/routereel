import unittest

from routereel.routing import haversine, route_distance, nearest_neighbor, two_opt, optimize


# A simple square: corners 0-1-2-3. Optimal loop visits them in order.
SQUARE = [(0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0)]


class TestHaversine(unittest.TestCase):
    def test_zero_distance(self):
        self.assertAlmostEqual(haversine((0, 0), (0, 0)), 0.0)

    def test_symmetry(self):
        a, b = (41.7, -88.1), (41.5, -88.0)
        self.assertAlmostEqual(haversine(a, b), haversine(b, a))

    def test_known_order_of_magnitude(self):
        # ~1 degree of latitude is roughly 69 miles.
        d = haversine((0, 0), (1, 0))
        self.assertTrue(60 < d < 75)


class TestRouteDistance(unittest.TestCase):
    def test_single_stop(self):
        self.assertEqual(route_distance([0], SQUARE), 0.0)

    def test_loop_longer_than_open(self):
        loop = route_distance([0, 1, 2, 3], SQUARE, return_to_start=True)
        openp = route_distance([0, 1, 2, 3], SQUARE, return_to_start=False)
        self.assertGreater(loop, openp)


class TestNearestNeighbor(unittest.TestCase):
    def test_visits_all(self):
        route = nearest_neighbor(SQUARE, start=0)
        self.assertEqual(sorted(route), [0, 1, 2, 3])

    def test_starts_at_depot(self):
        self.assertEqual(nearest_neighbor(SQUARE, start=2)[0], 2)


class TestTwoOpt(unittest.TestCase):
    def test_never_worsens(self):
        bad = [0, 2, 1, 3]  # a crossing route
        _, improved = two_opt(bad, SQUARE)
        original = route_distance(bad, SQUARE)
        self.assertLessEqual(improved, original + 1e-9)


class TestOptimize(unittest.TestCase):
    def test_finds_square_loop(self):
        route, dist = optimize(SQUARE, start=0)
        # Optimal loop around a unit square in miles.
        self.assertAlmostEqual(dist, route_distance([0, 1, 2, 3], SQUARE), places=1)
        self.assertEqual(len(route), 4)


if __name__ == "__main__":
    unittest.main()
