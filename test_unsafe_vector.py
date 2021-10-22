
from __future__ import annotations

import unittest
from random import randint

from unsafe_vector import A, Angle, V, Vector

LOW, HIGH = -1000000, 1000000

VEC_DIV_VEC_FAILED = "vector div vector test failed"

class VectorTests(unittest.TestCase):

    def test_transitive_addition_subtraction_multiplication(self):
        for _ in range(24000):
            x, y = randint(LOW, HIGH), randint(LOW, HIGH)
            alpha = V(x, y)
            beta = V(y, x)
            gamma = V(x, x * 0.1 + y)
            delta = V(x + y * 0.5, y * 0.25)
            resa = ((alpha + beta + beta + gamma + delta) * 2) - beta - beta
            resb = (alpha + alpha + beta + beta + gamma + gamma + delta + delta + delta + alpha) - delta - alpha
            self.assertEqual(resa.force_round(), resb.force_round())

    def test_addressing(self):
        for _ in range(48000):
            x, y = randint(LOW, HIGH) / 21, randint(LOW, HIGH) / 61
            vec = V(x, y)
            self.assertEqual(vec._x, x)
            self.assertEqual(vec._y, y)
            self.assertEqual(vec.x, round(x))
            self.assertEqual(vec.y, round(y))
            ux, uy = vec
            self.assertEqual(ux, vec._x)
            self.assertEqual(uy, vec._y)
            self.assertEqual(vec.x, vec[0])
            self.assertEqual(vec.y, vec[1])

    def test_abs(self):
        for _ in range(48000):
            x, y = randint(0, HIGH) / 2, randint(0, HIGH) / 5
            self.assertEqual(V(x, y), abs(V(-x, -y)))

    def test_mul(self):
        for _ in range(48000):
            x, y = randint(LOW, HIGH) / 76, randint(LOW, HIGH) / 12
            self.assertEqual(V(x, y) * V(y, x), V(x * y, x * y))

    def test_div(self):
        for _ in range(48000):
            x, y = randint(LOW, HIGH) / 6, randint(LOW, HIGH) / 23
            # prevent division by zero
            x += int(-0.05 < x < 0.05)
            y += int(-0.05 < y < 0.05)
            self.assertEqual(V(x, y) / V(y, x), V(x / y, y / x), VEC_DIV_VEC_FAILED)
        for _ in range(48000):
            x, y = randint(LOW, HIGH) / 10, randint(LOW, HIGH) / 10
            x += int(-0.05 < x < 0.05)
            y += int(-0.05 < y < 0.05)
            self.assertEqual(V(x, y) / y, V(x / y, 1))
        with self.assertRaises(ZeroDivisionError):
            vecTest = V(100, 24) / V(204, 0)
            self.assertEqual(vecTest, vecTest)

    def test_transitive_mul_div(self):
        for _ in range(48000):
            x, y, z, w = randint(LOW, HIGH), randint(LOW, HIGH), randint(LOW, HIGH), randint(LOW, HIGH)
            x += int(-0.05 < x < 0.05)
            y += int(-0.05 < y < 0.05)
            z += int(-0.05 < z < 0.05)
            w += int(-0.05 < w < 0.05)
            a, b = V(x, y), V(z, w)
            self.assertEqual(a * b, (a * a * b * b * b) / (a * b * b))

    def test_neg(self):
        for _ in range(48000):
            x, y = randint(LOW, HIGH) / 13, randint(LOW, HIGH) / 11
            self.assertEqual(-V(x, y), V(-x, -y))

    def test_pow(self):
        for _ in range(48000):
            x, y = randint(LOW, HIGH) / 15, randint(LOW, HIGH) / 352
            vec = V(x, y)
            rvec = vec
            vecPow = vec ** 3
            for _ in range(2):
                vec = vec * rvec
            self.assertAlmostEqual(vecPow._x, vec._x, -1)
            self.assertAlmostEqual(vecPow._y, vec._y, -1)

    def test_mod(self):
        for _ in range(48000):
            x, y, z = randint(1, HIGH), randint(1, HIGH), randint(1, HIGH)
            self.assertEqual(V(0, 0), V(x, y) % V(x, y))
            self.assertEqual(V(x % z, y % z), V(x, y) % z)

    def test_bind(self):
        for _ in range(24000):
            x, y = randint(1, HIGH), randint(1, HIGH)
            vec = V(x, y)
            self.assertEqual(vec.bind(V(0, 0), V(1, 1)), V(1, 1))
            self.assertEqual(vec.bind(V(0, 0), V(HIGH, HIGH)), vec)
            self.assertEqual(vec.bind(V(HIGH, HIGH), V(HIGH + 1, HIGH + 1)), V(HIGH, HIGH))

    def test_v_property(self):
        for _ in range(48000):
            x, y = randint(LOW, HIGH), randint(LOW, HIGH)
            vec = V(x, y)
            self.assertEqual(vec, vec.vx + vec.vy)

    def test_length(self):
        for _ in range(48000):
            x = randint(LOW, HIGH)
            veca, vecb = V(x, 0), V(0, x)
            self.assertAlmostEqual(abs(x), veca.length, 4)
            self.assertAlmostEqual(abs(x), vecb.length, 4)
        self.assertEqual(V(3, 4).length, 5)

    def test_random_square(self):
        for _ in range(48000):
            vec = Vector.from_random_square(V(-4, -4), V(4, 4))
            self.assertEqual(vec, vec.bind(V(-4, -4), V(4, 4)))

    def test_random_sign(self):
        s = V(0, 0)
        for _ in range(48000):
            vec = Vector.from_random_sign()
            s = s + vec
        self.assertAlmostEqual(s.x, 0, -3)
        self.assertAlmostEqual(s.y, 0, -3)

    def test_normalise(self):
        for _ in range(48000):
            x, y = randint(LOW, HIGH) / 21, randint(LOW, HIGH) / 82
            vec = V(x, y)
            self.assertAlmostEqual(1, vec.normal.length, 6)

    def test_upscale(self):
        for _ in range(48000):
            x, y = randint(LOW, HIGH) / 3, randint(LOW, HIGH) / 7
            vec = V(x, y)
            self.assertAlmostEqual(2 * vec.length, (vec * 2).length, 6)
            self.assertAlmostEqual(24, (vec.normal * 24).length, 6)

class AngleTests(unittest.TestCase):

    def test_creation(self):
        with self.assertRaises(TypeError):
            A(radians=V(0, 0))
        with self.assertRaises(TypeError):
            A(degrees=V(0, 0))
        with self.assertRaises(TypeError):
            A(radians=2, degrees=1)

    def test_equality(self):
        self.assertEqual(A(0), A(0))

if __name__ == "__main__":
    unittest.main()

