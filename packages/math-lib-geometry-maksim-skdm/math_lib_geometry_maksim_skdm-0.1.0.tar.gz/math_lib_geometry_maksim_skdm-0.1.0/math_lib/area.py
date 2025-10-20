from abc import ABC, abstractmethod
import math
from typing import List


class Shape(ABC):
    """Абстрактный базовый класс для всех геометрических фигур."""

    @abstractmethod
    def area(self) -> float:
        """
        Вычисляет площадь фигуры.

        :return: площадь фигуры
        :rtype: float
        """
        pass

    @abstractmethod
    def is_valid(self) -> bool:
        """
        Проверяет, является ли фигура валидной.

        :return: True если фигура валидна, иначе False
        :rtype: bool
        """
        pass


class Triangle(Shape):
    """Класс для работы с треугольниками."""

    def __init__(self, side1: float, side2: float, side3: float) -> None:
        """
        Инициализирует треугольник с тремя сторонами.

        :param side1: первая сторона
        :type side1: float
        :param side2: вторая сторона
        :type side2: float
        :param side3: третья сторона
        :type side3: float
        """
        self.sides: List[float] = [side1, side2, side3]
        self.sides.sort()

    def is_valid(self) -> bool:
        """
        Проверяет, может ли треугольник существовать.

        :return: True если треугольник валиден, иначе False
        :rtype: bool
        """
        a, b, c = self.sides
        if not (a > 0 and b > 0 and c > 0):
            return False
        return (a + b > c) and (a + c > b) and (b + c > a)

    def area(self) -> float:
        """
        Вычисляет площадь треугольника по формуле Герона.

        :return: площадь треугольника
        :rtype: float

        :raises ValueError: если треугольник невалиден
        """
        if not self.is_valid():
            raise ValueError("Invalid triangle sides")

        a, b, c = self.sides
        p = (a + b + c) / 2
        return math.sqrt(p * (p - a) * (p - b) * (p - c))

    def is_right_triangle(self) -> bool:
        """
        Проверяет, является ли треугольник прямоугольным.

        :return: True если треугольник прямоугольный, иначе False
        :rtype: bool
        """
        if not self.is_valid():
            return False

        a, b, c = self.sides
        return a ** 2 + b ** 2 == c ** 2


class Circle(Shape):
    """Класс для работы с окружностями."""

    def __init__(self, radius: float) -> None:
        """
        Инициализирует окружность с заданным радиусом.

        :param radius: радиус окружности
        :type radius: float
        """
        self.radius: float = radius

    def is_valid(self) -> bool:
        """
        Проверяет, является ли окружность валидной.

        :return: True если радиус положительный, иначе False
        :rtype: bool
        """
        return self.radius > 0

    def area(self) -> float:
        """
        Вычисляет площадь окружности.

        :return: площадь окружности
        :rtype: float

        :raises ValueError: если радиус невалиден
        """
        if not self.is_valid():
            raise ValueError("Invalid circle radius")

        return math.pi * (self.radius ** 2)


class ShapeFactory:
    """Фабрика для создания геометрических фигур."""

    @staticmethod
    def create_shape(shape_type: str, *args: float) -> Shape:
        """
        Создает фигуру указанного типа.

        :param shape_type: тип фигуры ('circle' или 'triangle')
        :type shape_type: str
        :param args: параметры фигуры
        :type args: float
        :return: созданная фигура
        :rtype: Shape

        :raises ValueError: если указан неизвестный тип фигуры
        """
        if shape_type == "circle":
            return Circle(*args)
        elif shape_type == "triangle":
            return Triangle(*args)
        else:
            raise ValueError(f"Unknown shape type: {shape_type}")


def calculate_area(shape: Shape) -> float:
    """
    Вычисляет площадь фигуры без знания ее конкретного типа.

    :param shape: объект фигуры, наследованный от Shape
    :type shape: Shape
    :return: площадь фигуры
    :rtype: float

    :raises TypeError: если переданный объект не является фигурой
    """
    if isinstance(shape, Shape):
        return shape.area()
    else:
        raise TypeError("Object must be a Shape")
