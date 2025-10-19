import unittest
from src.area_package import Circle, Triangle
import math

class MyTestCase(unittest.TestCase):
    def test_circle(self):
        c = Circle(10)
        expected = math.pi * 10**2
        self.assertAlmostEqual(c.area(), expected, places=5)

    def test_triangle(self):
        t1 = Triangle(3, 4, 5)
        p = (3 + 4 + 5) / 2
        expected = (p * (p - 3) * (p - 4) * (p - 5))**0.5
        self.assertTrue(t1.is_right_triangle())
        self.assertAlmostEqual(t1.area(), expected, places=5)

        t2 = Triangle(2, 3, 4)
        self.assertFalse(t2.is_right_triangle())

if __name__ == '__main__':
    unittest.main()
