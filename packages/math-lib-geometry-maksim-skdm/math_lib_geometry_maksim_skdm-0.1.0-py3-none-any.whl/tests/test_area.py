import unittest
import math
from typing import List, Tuple

from math_lib.area import Triangle, Circle, calculate_area, ShapeFactory


class TestTriangle(unittest.TestCase):
    """Тесты для класса Triangle."""

    def test_valid_triangle_area(self) -> None:
        """Проверка вычисления площади валидного треугольника."""
        triangle = Triangle(3, 4, 5)
        self.assertAlmostEqual(triangle.area(), 6.0)

    def test_equilateral_triangle_area(self) -> None:
        """Проверка площади равностороннего треугольника."""
        triangle = Triangle(2, 2, 2)
        expected_area = math.sqrt(3)
        self.assertAlmostEqual(triangle.area(), expected_area)

    def test_invalid_triangle_negative_sides(self) -> None:
        """Проверка треугольника с отрицательными сторонами."""
        triangle = Triangle(-1, 2, 3)
        self.assertFalse(triangle.is_valid())
        with self.assertRaises(ValueError):
            triangle.area()

    def test_invalid_triangle_zero_sides(self) -> None:
        """Проверка треугольника с нулевыми сторонами."""
        triangle = Triangle(0, 2, 3)
        self.assertFalse(triangle.is_valid())
        with self.assertRaises(ValueError):
            triangle.area()

    def test_invalid_triangle_inequality(self) -> None:
        """Проверка нарушения неравенства треугольника."""
        test_cases: List[Tuple[float, float, float]] = [
            (1, 1, 3),
            (1, 2, 3),
            (2, 2, 4),
            (1, 3, 1),
        ]

        for sides in test_cases:
            with self.subTest(sides=sides):
                triangle = Triangle(*sides)
                self.assertFalse(triangle.is_valid())
                with self.assertRaises(ValueError):
                    triangle.area()

    def test_right_triangle_detection(self) -> None:
        """Проверка идентификации прямоугольных треугольников."""
        right_triangles: List[Tuple[float, float, float]] = [
            (3, 4, 5),
            (5, 12, 13),
            (6, 8, 10),
            (7, 24, 25),
        ]

        for sides in right_triangles:
            with self.subTest(sides=sides):
                triangle = Triangle(*sides)
                self.assertTrue(triangle.is_right_triangle())

    def test_non_right_triangle_detection(self) -> None:
        """Проверка идентификации непрямоугольных треугольников."""
        non_right_triangles: List[Tuple[float, float, float]] = [
            (3, 3, 3),
            (2, 3, 4),
            (5, 5, 8),
        ]

        for sides in non_right_triangles:
            with self.subTest(sides=sides):
                triangle = Triangle(*sides)
                self.assertFalse(triangle.is_right_triangle())


class TestCircle(unittest.TestCase):
    """Тесты для класса Circle."""

    def test_valid_circle_area(self) -> None:
        """Проверка вычисления площади валидной окружности."""
        circle = Circle(1)
        self.assertAlmostEqual(circle.area(), math.pi)

        circle = Circle(2)
        self.assertAlmostEqual(circle.area(), 4 * math.pi)

    def test_invalid_circle_negative_radius(self) -> None:
        """Проверка окружности с отрицательным радиусом."""
        circle = Circle(-1)
        self.assertFalse(circle.is_valid())
        with self.assertRaises(ValueError):
            circle.area()

    def test_invalid_circle_zero_radius(self) -> None:
        """Проверка окружности с нулевым радиусом."""
        circle = Circle(0)
        self.assertFalse(circle.is_valid())
        with self.assertRaises(ValueError):
            circle.area()


class TestShapeFactory(unittest.TestCase):
    """Тесты для фабрики фигур."""

    def test_create_circle(self) -> None:
        """Проверка создания окружности через фабрику."""
        circle = ShapeFactory.create_shape("circle", 5)
        self.assertIsInstance(circle, Circle)
        self.assertEqual(circle.radius, 5)

    def test_create_triangle(self) -> None:
        """Проверка создания треугольника через фабрику."""
        triangle = ShapeFactory.create_shape("triangle", 3, 4, 5)
        self.assertIsInstance(triangle, Triangle)
        self.assertEqual(triangle.sides, [3, 4, 5])

    def test_create_unknown_shape(self) -> None:
        """Проверка создания неизвестной фигуры."""
        with self.assertRaises(ValueError):
            ShapeFactory.create_shape("square", 4)


class TestPolymorphism(unittest.TestCase):
    """Тесты полиморфного поведения."""

    def test_calculate_area_function(self) -> None:
        """Проверка функции calculate_area с разными фигурами."""
        triangle = Triangle(3, 4, 5)
        circle = Circle(2)

        triangle_area = calculate_area(triangle)
        circle_area = calculate_area(circle)

        self.assertAlmostEqual(triangle_area, 6.0)
        self.assertAlmostEqual(circle_area, 4 * math.pi)

    def test_calculate_area_with_invalid_object(self) -> None:
        """Проверка функции calculate_area с не-фигурой."""

        class NotAShape:
            def area(self) -> float:
                """
                Вычисляет площадь фигуры.

                :return: площадь фигуры
                :rtype: float
                """
                return 5.1
        not_a_shape = NotAShape
        with self.assertRaises(TypeError):
            calculate_area(not_a_shape)

    def test_polymorphic_collection(self) -> None:
        """Проверка работы с коллекцией разных фигур."""
        shapes = [
            Triangle(3, 4, 5),
            Circle(1),
            Triangle(2, 2, 2),
            Circle(3),
        ]

        areas = [calculate_area(shape) for shape in shapes]
        self.assertEqual(len(areas), 4)

        self.assertAlmostEqual(areas[0], 6.0)
        self.assertAlmostEqual(areas[1], math.pi)
        self.assertAlmostEqual(areas[2], math.sqrt(3))
        self.assertAlmostEqual(areas[3], 9 * math.pi)

    def test_shape_interface(self) -> None:
        """Проверка, что все фигуры реализуют обязательные методы."""
        shapes = [Triangle(3, 4, 5), Circle(2)]

        for shape in shapes:
            with self.subTest(shape=type(shape).__name__):
                self.assertTrue(hasattr(shape, 'area'))
                self.assertTrue(hasattr(shape, 'is_valid'))
                self.assertTrue(callable(shape.area))
                self.assertTrue(callable(shape.is_valid))
