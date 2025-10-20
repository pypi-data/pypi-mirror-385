import unittest
import random
import math

from grid_sort import sorting as sort
from tests.fixtures.containers import WithXY, WithxyLower, Nested, WithPropsUpper
from types import SimpleNamespace


class TestSortModule(unittest.TestCase):
    def test_find_xy_container_direct(self):
        o = WithXY(1, 2)
        c = sort.find_xy_container(o)
        self.assertIs(c, o)

    def test_find_xy_container_lowercase(self):
        o = WithxyLower(3, 4)
        c = sort.find_xy_container(o)
        self.assertIs(c, o)

    def test_find_xy_container_nested(self):
        o = Nested(5, 6)
        c = sort.find_xy_container(o)
        # container should be the inner object
        self.assertIs(c, o.inner)

    def test_get_xy_and_set_xy(self):
        o = WithXY(7, 8)
        x, y = sort.get_xy(o)
        self.assertEqual((x, y), (7, 8))
        sort.set_xy(o, 10, 11)
        self.assertEqual((o.X, o.Y), (10, 11))

    def test_set_xy_nested(self):
        o = Nested(1, 2)
        sort.set_xy(o, 20, 21)
        c = sort.find_xy_container(o)
        self.assertEqual(
            (getattr(c, 'X', None) or getattr(c, 'x', None),
             getattr(c, 'Y', None) or getattr(c, 'y', None)),
            (20, 21)
        )

    def test_get_xy_missing(self):
        o = SimpleNamespace(a=1)
        with self.assertRaises(AttributeError):
            sort.get_xy(o)

    def test_sort_by_xy_simple(self):
        objs = [WithXY(2, 2), WithXY(1, 5), WithXY(1, 2), WithXY(2, 1)]
        sorted_objs = sort.sort_by_xy(objs, 1)
        coords = [sort.get_xy(o) for o in sorted_objs]
        self.assertEqual(coords, [(1, 5), (1, 2), (2, 1), (2, 2)])

    def test_empty_and_single(self):
        self.assertEqual(sort.sort_by_xy([], 0.5), [])
        single = WithXY(3, 4)
        res = sort.sort_by_xy([single], 0.5)
        self.assertEqual([sort.get_xy(o) for o in res], [(3, 4)])

    def test_property_accessors(self):
        o = WithPropsUpper(5, 6)
        x, y = sort.get_xy(o)
        self.assertEqual((x, y), (5, 6))
        sort.set_xy(o, 7, 8)
        self.assertEqual((o.X, o.Y), (7, 8))

    # def test_threshold_boundary(self):
    #     # endpoints at (0,0) and (10,0); point at (5,2.0) is exactly at distance 2.0
    #     a = WithXY(0, 0)
    #     b = WithXY(10, 0)
    #     c_on = WithXY(5, 2.0)
    #     # default threshold: ensure the endpoints come first
    #     res_default = sort.sort_by_xy([a, b, c_on], 0.5)
    #     coords_default = [sort.get_xy(o) for o in res_default]
    #     # The first two entries should be the left and right endpoints in order.
    #     self.assertEqual(coords_default[:2], [(0, 0), (10, 0)])

    #     # Slightly larger threshold includes the point in the row between endpoints
    #     res_inclusive = sort.sort_by_xy([a, b, c_on], 0.51)
    #     coords_inclusive = [sort.get_xy(o) for o in res_inclusive]
    #     self.assertEqual(coords_inclusive, [(0, 0), (5, 2.0), (10, 0)])

    def test_duplicates_and_stability(self):
        a = WithXY(1, 1)
        b = WithXY(1, 1)
        c = WithXY(2, 2)
        res = sort.sort_by_xy([c, b, a], 0.5)
        coords = [sort.get_xy(o) for o in res]
        # duplicates with same coords should appear before (2,2)
        self.assertEqual(coords[:2], [(1, 1), (1, 1)])
        self.assertEqual(len(coords), 3)

    def test_multi_row(self):
        # two horizontal rows: y=0 (top) and y=10 (below)
        top = [WithXY(x, 0) for x in range(3)]
        bot = [WithXY(x, 10) for x in range(3)]
        mixed = top + bot
        random.shuffle(mixed)
        res = sort.sort_by_xy(mixed, 0.5)
        coords = [sort.get_xy(o) for o in res]
        expected = [(0, 0), (1, 0), (2, 0), (0, 10), (1, 10), (2, 10)]
        self.assertEqual(coords, expected)


if __name__ == '__main__':
    unittest.main()
