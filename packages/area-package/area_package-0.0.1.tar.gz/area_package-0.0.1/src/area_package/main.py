import math
from abc import ABC, abstractmethod
class Shape():
    @abstractmethod
    def area(self):
        pass

class Circle(Shape):
    def __init__(self, rad):
        self.rad = rad

    def area(self):
        return math.pi * self.rad**2

class Triangle(Shape):
    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c

    def area(self):
        p = (self.a + self.b + self.c) / 2
        return (p * (p - self.a) * (p - self.b) * (p - self.c))**0.5

    def is_right_triangle(self):
        sides = sorted([self.a, self.b, self.c])
        return math.isclose(sides[0]**2 + sides[1]**2, sides[2]**2)
