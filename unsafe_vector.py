
from __future__ import annotations

from functools import cached_property
from math import atan2, cos, hypot, pi, sin, tau
from random import randint, random
from typing import Union

from vector import AngleType

__all__ = ["Vector", "V", "Angle", "A"]

from dataclasses import dataclass


@dataclass(frozen=True)
class Angle:
    """
    An angle in radians. Exposes .degrees, .unit
    """
    _angle: float

    def __repr__(self) -> str:
        return f"R[{self.degrees, self.radians}]"

    def __eq__(self, ia: Angle) -> bool:
        return (ia._angle == self._angle)

    def __lt__(self, ia: Angle) -> bool:
        return (self._angle < ia._angle)

    def __gt__(self, ia: Angle) -> bool:
        return (self._angle > ia._angle)

    def __le__(self, ia: Angle) -> bool:
        return (self._angle < ia._angle)

    def __add__(self, ia: Angle) -> Angle:
        return A(radians=(self.radians + ia.radians))

    def __sub__(self, ia: Angle) -> Angle:
        return A(radians=(self.radians - ia.radians))

    def __round__(self, places: int) -> Angle:
        return A(round(self._angle, places))

    @staticmethod
    def fromvector(vec: Vector) -> Angle:
        return Angle((-((atan2(vec.y, vec.x)))) + (pi / 4))

    @property
    def degrees(self) -> float:
        "this angle as float, measured in degrees and contained in one period"
        return ((self.radians / tau) * 360)

    @property
    def radians(self) -> float:
        "this angle as float, measured in radians and contained in one period"
        return self._angle % tau

    @cached_property
    def unit(self) -> Vector:
        "this angle as Vector, with distance 1 (unit vector)"
        return V.from_angle(self, 1)

@dataclass(frozen=True)
class Vector:
    """
    Vector represents a 2D coordernate on a pixel grid with
    backend values being floats.

    .x: int
    .y: int
    ._x: float
    ._y: float
    """

    _x: float
    _y: float

    def __iter__(self):
        """Yield ._x then ._y for unpacking"""
        yield self._x
        yield self._y

    def __len__(self):
        "length of Vector2 is 2"
        return 2

    def __repr__(self) -> str:
        return f"V({self.x}, {self.y})"

    def __str__(self) -> str:
        "__repr__"
        return repr(self)

    def __getitem__(self, i: int) -> int:
        "x == self[0]; y == self[1]"
        "x, y are rounded ints"
        # treats Vector like a tuple and yields x if i == 0 or y if i == 1
        return (self.x * ((i + 1) % 2) + self.y * i)

    def __round__(self, places: int) -> Vector:
        "round components of self to `places` decimal places"
        return V(round(self._x, places), round(self._y, places))

    def __abs__(self) -> Vector:
        "this Vector as Vector, reflected so _x and _y are positive"
        return Vector(abs(self._x), abs(self._y))

    def __add__(self, ia: VectorType) -> Vector:
        "add to this Vector the Vector `ia.x, ia.y`"
        x, y = ia
        return Vector(self._x + x, self._y + y)

    def __neg__(self) -> Vector:
        "return Vector equal to V(0, 0) - self"
        return V(-self._x, -self._y)

    def __sub__(self, ia: VectorType) -> Vector:
        "subtract from this Vector the Vector `ia.x, ia.y`"
        x, y = ia
        return Vector(self._x - x, self._y - y)

    def __mul__(self, ia: Union[VectorType, Number]) -> Vector:
        "multiply this Vector by scalar `ia` or Vector `ia.x, ia.y`"
        if isinstance(ia, Number):
            return V(self._x * ia, self._y * ia)
        return V(self._x * ia._x, self._y * ia._y)

    def __pow__(self, ia: Number) -> Vector:
        "raise Vector's components to power `ia`"
        return Vector(self._x ** ia, self._y ** ia)

    def __truediv__(self, ia: Union[VectorType, Number]) -> Vector:
        "divide this Vector by scalar `ia` or Vector `ia.x, ia.y`"
        if isinstance(ia, Number):
            return V(self._x / ia, self._y / ia)
        return V(self._x / ia._x, self._y / ia._y)

    def __eq__(self, ia: VectorType) -> bool:
        "unrounded equality with another Vector"
        return self._x == ia._x and self._y == ia._y

    def __mod__(self, ia: Union[VectorType, Number]) -> Vector:
        "apply modulo to Vector's components with Vector `ia.x, ia.y`"
        "or with number `ia`"
        if isinstance(ia, Number):
            return Vector(self.x % ia, self.y % ia)
        return Vector(self.x % ia.x, self.y % ia.y)

    def lobind(self, v: VectorType) -> Vector:
        "(min(v._x, self._x)), (min(v._y, self._y))"
        return Vector((min(v._x, self._x)), (min(v._y, self._y)))

    def hibind(self, v: VectorType) -> Vector:
        "(max(v._x, self._x)), (max(v._y, self._y))"
        return Vector((max(v._x, self._x)), (max(v._y, self._y)))

    def bind(self, lo: VectorType, hi: VectorType) -> Vector:
        "lobind and hibind to force `self` into bounds `lo`, `hi`"
        "inclusive of bounds"
        return self.hibind(lo).lobind(hi)

    def inside(self, lo: Vector, hi: Vector) -> bool:
        "return self "
        return self.bind(lo, hi) == self

    def shift_context(self) -> Vector:
        return V(self._x, -self._y)

    def approach(self, target: Vector, factor: float) -> Vector:
        return self + (target - self) * factor

    def signs(self) -> Vector:
        return V(1 if self.x >= 0 else -1, 1 if self.y >= 0 else -1)

    def force_round(self) -> Vector:
        return V(self.x, self.y)

    def rotate(self, angle: Angle) -> Vector:
        b = angle.radians
        sinb = sin(b)
        cosb = cos(b)
        return V(
            (cosb * self._x) - (sinb * self._y),
            (sinb * self._x) + (cosb * self._y)
        )

    @staticmethod
    def from_vector(vector: VectorType) -> Vector:
        return V(*vector)

    @staticmethod
    def from_angle(angle: AngleType, magnitude: float = 1) -> Vector:
        return V(sin(angle._angle) * magnitude, cos(angle._angle) * magnitude)

    @staticmethod
    def from_random_sign() -> Vector:
        return Vector((randint(0, 1) * 2) - 1, (randint(0, 1) * 2) - 1)

    @staticmethod
    def from_random_square(lo: Vector, hi: Vector) -> Vector:
        dv = hi - lo
        return lo + (dv.vx * random() + dv.vy * random())
     
    @property
    def x(self) -> int:
        """Return ._x as rounded int"""
        return round(self._x)

    @property
    def y(self) -> int:
        """Return ._y as rounded int"""
        return round(self._y)

    @property
    def vx(self) -> Vector:
        return V(self._x, 0)

    @property
    def vy(self) -> Vector:
        return V(0, self._y)

    @cached_property
    def length(self) -> float:
        return hypot(self._x, self._y)
        #return sqrt((self._x ** 2) + (self._y ** 2))
        
    @cached_property
    def normal(self) -> Vector:
        return V(self._x / self.length, self._y / self.length)


# shorthand definition of Vector

V = Vector
A = Angle

Number = (float, int)
VectorType = (Vector)
AngleType = (Angle)



