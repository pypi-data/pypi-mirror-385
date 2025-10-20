"""
MathLib - Библиотека для вычисления площадей геометрических фигур.

Библиотека предоставляет:
- Вычисление площади круга по радиусу
- Вычисление площади треугольника по трем сторонам
- Проверку треугольника на прямоугольность
- Легкое добавление новых фигур
- Полиморфную работу с фигурами
"""

from math_lib.area import Circle, Shape, ShapeFactory, Triangle, calculate_area
from math_lib.version import __version__

__all__ = [
    "Shape",
    "Triangle",
    "Circle",
    "ShapeFactory",
    "calculate_area",
    "__version__",
]
