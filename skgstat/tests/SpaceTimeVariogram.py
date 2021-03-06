import unittest

import numpy as np
from numpy.testing import assert_array_almost_equal

from skgstat import SpaceTimeVariogram


class TestSpaceTimeVariogramInitialization(unittest.TestCase):
    def setUp(self):
        np.random.seed(42)
        self.c = np.random.gamma(10, 6, (60, 3))
        np.random.seed(42)
        self.v = np.random.normal(15, 4, (60, 8))

    def test_default_init(self):
        V = SpaceTimeVariogram(self.c, self.v)

        # test first 5 and
        assert_array_almost_equal(
            V.experimental[:5],
            np.array([14.527, 16.275, 16.195, 14.464, 12.619]),
            decimal=3
        )

        # and last 5
        assert_array_almost_equal(
            V.experimental[-5:],
            np.array([13.911, 10.76 , 10.623,  9.434, 15.402]),
            decimal=3
        )

    def test_values_setter(self):
        V = SpaceTimeVariogram(self.c, self.v)

        # get the differences
        diff = V.values

        # delete and reset by setter
        V._values = None
        self.assertIsNone(V.values)
        V.values = self.v

        # assert
        assert_array_almost_equal(V.values, diff, decimal=5)

    def test_set_values_raises_AttributeError(self):
        V = SpaceTimeVariogram(self.c, self.v)

        with self.assertRaises(AttributeError) as e:
            V.set_values(['string', 'don\'t', 'work'])
            self.assertEqual(
                str(e),
                'values cannot be converted to a proper '
                '(m,n) shaped array.'
            )

    def test_set_values_raises_shape_error(self):
        V = SpaceTimeVariogram(self.c, self.v)

        with self.assertRaises(ValueError) as e:
            V.set_values(np.random.normal(10, 5, (55, 8)))
            self.assertEqual(
                str(e), 'The values shape do not match coordinates.'
            )

    def test_set_value_raises_timeseries_error(self):
        V = SpaceTimeVariogram(self.c, self.v)

        with self.assertRaises(ValueError) as e:
            V.set_values(np.random.normal(0, 1, (60, 1)))
            self.assertEqual(
                str(e),
                'A SpaceTimeVariogram needs more than one '
                'observation on the time axis.'
            )


class TestSpaceTimeVariogramArgumets(unittest.TestCase):
    def setUp(self):
        np.random.seed(1306)
        self.c = np.random.gamma(20, 10, (60, 3))
        np.random.seed(1306)
        self.v = np.random.power(5, (60, 5))

    def test_xdist_func(self):
        # use Manhattan distance
        V = SpaceTimeVariogram(self.c, self.v, xdist_func='cityblock')

        self.assertEqual(V.xdistance.size, 1770)
        # test arbitrary elements
        assert_array_almost_equal(
            V.xdistance[[10,  15, 492, 1023, 1765]],
            np.array([184.245, 162.17 ,  46.296, 138.417,  91.457]),
            decimal=3
        )

    def test_xdist_func_raises_ValueError(self):
        with self.assertRaises(ValueError) as e:
            V = SpaceTimeVariogram(self.c, self.v)
            V.xdist_func = lambda x: x**2

            self.assertEqual(
                str(e), 'For now only str arguments are supported.'
            )

    def test_tdist_func(self):
        V = SpaceTimeVariogram(self.c, self.v, tdist_func='jaccard')

        # with jaccard, all shoud disagree
        self.assertTrue(all([_ == 1. for _ in V.tdistance]))

    def test_tdist_func_raises_ValueError(self):
        with self.assertRaises(ValueError) as e:
            V = SpaceTimeVariogram(self.c, self.v)
            V.tdist_func = 55.4

            self.assertEqual(
                str(e), 'For now only str arguments are supported.'
            )

    def test_x_lags(self):
        V = SpaceTimeVariogram(self.c, self.v)

        self.assertEqual(V.x_lags, 10)
        V.x_lags = 25
        self.assertEqual(len(V.xbins), 25)

    def test_x_lags_raises_ValueError(self):
        with self.assertRaises(ValueError) as e:
            SpaceTimeVariogram(self.c, self.v, x_lags=15.4)

            self.assertEqual(
                str(e), 'Only integers are supported as lag counts.'
            )

    def test_t_lags(self):
        V = SpaceTimeVariogram(self.c, self.v, t_lags=2)

        self.assertEqual(V.t_lags, 2)
        self.assertEqual(len(V.tbins), 2)
        V.t_lags = 'max'
        # this is still a bug, needs to be fixed one day
        self.assertEqual(V.t_lags, 4)
        self.assertEqual(len(V.tbins), 4)

    def test_t_lags_unkown(self):
        with self.assertRaises(ValueError) as e:
            SpaceTimeVariogram(self.c, self.v, t_lags='min')

            self.assertEqual(
                str(e), "Only 'max' supported as string argument."
            )


if __name__ == '__main__':
    unittest.main()
