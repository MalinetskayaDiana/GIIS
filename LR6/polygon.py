# polygon.py
import math

# Глобальный список для отладочных сообщений (пошаговое решение)
debug_steps = []

def add_debug(message):
    debug_steps.append(message)

class Polygon:
    def __init__(self):
        self.vertices = []  # список вершин в виде (x, y)
        self.closed = False
        self.normals = []  # список нормалей к сторонам полигона

    def add_vertex(self, x, y):
        if not self.closed:
            self.vertices.append((x, y))
            add_debug(f"Добавлена вершина: ({x:.2f}, {y:.2f})")

    def close_polygon(self):
        if len(self.vertices) >= 3:
            self.closed = True
            add_debug("Полигон замкнут")
            self.compute_normals()
        else:
            add_debug("Недостаточно вершин для замыкания полигона (требуется минимум 3).")

    def compute_normals(self):
        """Вычисление нормалей каждой стороны по формуле: n = (-dy, dx) с нормировкой."""
        self.normals = []
        n = len(self.vertices)
        for i in range(n):
            x1, y1 = self.vertices[i]
            x2, y2 = self.vertices[(i + 1) % n]
            dx = x2 - x1
            dy = y2 - y1
            mag = math.hypot(dx, dy)
            if mag != 0:
                nx = -dy / mag
                ny = dx / mag
            else:
                nx, ny = 0, 0
            self.normals.append((nx, ny))
            add_debug(f"Нормаль для стороны {i}: ({nx:.2f}, {ny:.2f})")

    def check_convexity(self):
        """
        Проверка выпуклости полигона по знакам векторных произведений
        между последовательными сторонами (см. методичку).
        """
        n = len(self.vertices)
        if n < 3:
            return False, "Полигон не определён (менее 3 вершин)"
        sign = None
        for i in range(n):
            x1, y1 = self.vertices[i]
            x2, y2 = self.vertices[(i + 1) % n]
            x3, y3 = self.vertices[(i + 2) % n]
            # Вычисляем Z-компоненту векторного произведения:
            cross = (x2 - x1) * (y3 - y2) - (y2 - y1) * (x3 - x2)
            add_debug(f"Векторное произведение для вершин {i},{(i+1)%n},{(i+2)%n} = {cross:.2f}")
            if abs(cross) < 1e-6:
                continue
            current_sign = cross > 0
            if sign is None:
                sign = current_sign
            elif sign != current_sign:
                return False, "Полигон вогнутый"
        return True, "Полигон выпуклый"

def convex_hull_graham(points):
    """
    Построение выпуклой оболочки методом Грэмма.
    Алгоритм:
      1. Выбрать точку с минимальной y (при равенстве – минимальная x).
      2. Отсортировать остальные точки по полярному углу относительно выбранной точки.
      3. Пройти по отсортированному списку, удаляя «не левосторонние» повороты.
    """
    add_debug("Начало построения выпуклой оболочки (Грэмма)")
    if len(points) <= 1:
        return points[:]
    start = min(points, key=lambda p: (p[1], p[0]))
    add_debug(f"Экстремальная точка: {start}")
    def polar_angle(p):
        return math.atan2(p[1] - start[1], p[0] - start[0])
    sorted_points = sorted(points, key=lambda p: (polar_angle(p), (p[0]-start[0])**2 + (p[1]-start[1])**2))
    hull = []
    for p in sorted_points:
        while len(hull) >= 2:
            cross = ((hull[-1][0] - hull[-2][0]) * (p[1] - hull[-2][1]) -
                     (hull[-1][1] - hull[-2][1]) * (p[0] - hull[-2][0]))
            if cross <= 0:
                add_debug(f"Удаление точки {hull[-1]} из оболочки, т.к. cross={cross:.2f} не положительный")
                hull.pop()
            else:
                break
        hull.append(p)
        add_debug(f"Точка {p} добавлена в оболочку")
    add_debug("Построение выпуклой оболочки (Грэмма) завершено")
    return hull

def convex_hull_jarvis(points):
    """
    Построение выпуклой оболочки методом Джарвиса («заворачивания подарка»).
    Алгоритм:
      1. Выбрать левейшую точку.
      2. Итерировать, выбирая точку, которая наиболее левее относительно текущей.
      3. Продолжать до замыкания оболочки.
    """
    add_debug("Начало построения выпуклой оболочки (Джарвиса)")
    if len(points) < 3:
        return points[:]
    # Выберем точку с минимальным x (если несколько ‒ с минимальным y)
    leftmost = min(points, key=lambda p: (p[0], p[1]))
    hull = []
    p = leftmost
    while True:
        hull.append(p)
        q = points[0]
        for r in points:
            if r == p:
                continue
            # Вычисляем векторное произведение (p->q) x (p->r)
            cross = (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
            # Если q равно p или r расположена левее, обновляем q
            if q == p or cross < 0:
                q = r
        add_debug(f"Следующая точка оболочки: {q}")
        p = q
        if p == leftmost:
            break
    add_debug("Построение выпуклой оболочки (Джарвиса) завершено")
    return hull
