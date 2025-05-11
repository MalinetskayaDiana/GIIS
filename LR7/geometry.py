# geometry.py
import math

def distance_sq(p1, p2):
    """
    Вычисляет квадрат евклидова расстояния между точками p1 и p2.
    """
    return (p1[0] - p2[0])**2 + (p1[1] - p2[1])**2

def circumcircle(triangle):
    """
    Вычисляет центр и квадрат радиуса описанной окружности для треугольника.
    triangle – кортеж из трёх точек ((x1, y1), (x2, y2), (x3, y3)).
    Если точки коллинеарны, возвращается окружность с бесконечно большим радиусом.
    """
    (x1, y1), (x2, y2), (x3, y3) = triangle
    d = 2 * (x1*(y2 - y3) + x2*(y3 - y1) + x3*(y1 - y2))
    if d == 0:
        # Коллинеарные точки – возвращаем "бесконечно большую" окружность
        return ((0, 0), float('inf'))
    ux = ((x1**2 + y1**2)*(y2 - y3) +
          (x2**2 + y2**2)*(y3 - y1) +
          (x3**2 + y3**2)*(y1 - y2)) / d
    uy = ((x1**2 + y1**2)*(x3 - x2) +
          (x2**2 + y2**2)*(x1 - x3) +
          (x3**2 + y3**2)*(x2 - x1)) / d
    center = (ux, uy)
    r_sq = distance_sq(center, (x1, y1))
    return (center, r_sq)

def is_in_circle(pt, circle):
    """
    Проверяет, принадлежит ли точка pt (x,y) окружности, представленной как (center, r_sq).
    """
    center, r_sq = circle
    return distance_sq(pt, center) <= r_sq

def edge_key(p1, p2):
    """
    Возвращает ключ для ребра (независимо от порядка точек).
    """
    return tuple(sorted([p1, p2]))
