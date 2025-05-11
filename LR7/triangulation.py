# triangulation.py
from geometry import circumcircle, is_in_circle, edge_key


class Triangle:
    def __init__(self, p1, p2, p3):
        self.vertices = (p1, p2, p3)
        self.circumcenter, self.r_sq = circumcircle(self.vertices)

    def contains_point_in_circumcircle(self, pt):
        """
        Проверяет, лежит ли точка pt внутри описанной окружности треугольника.
        """
        return is_in_circle(pt, (self.circumcenter, self.r_sq))

    def has_vertex(self, p):
        return p in self.vertices


def delaunay_triangulation(points):
    """
    Выполняет триангуляцию Делоне для списка точек (каждая точка – (x, y)).
    Реализован метод Bowyer–Watson.
    """
    if len(points) < 3:
        return []

    # Определяем границы по точкам и создаём супер-треугольник, который покрывает все точки
    min_x = min(p[0] for p in points)
    max_x = max(p[0] for p in points)
    min_y = min(p[1] for p in points)
    max_y = max(p[1] for p in points)
    dx = max_x - min_x
    dy = max_y - min_y
    delta_max = max(dx, dy)
    midx = (min_x + max_x) / 2
    midy = (min_y + max_y) / 2

    p1 = (midx - 20 * delta_max, midy - delta_max)
    p2 = (midx, midy + 20 * delta_max)
    p3 = (midx + 20 * delta_max, midy - delta_max)
    super_triangle = Triangle(p1, p2, p3)

    # Начинаем с супер-треугольника
    triangles = [super_triangle]

    # Добавляем точки по одной
    for point in points:
        bad_triangles = []
        for triangle in triangles:
            if triangle.contains_point_in_circumcircle(point):
                bad_triangles.append(triangle)

        # Находим все ребра, принадлежащие только одному из плохих треугольников
        edge_count = {}
        for triangle in bad_triangles:
            verts = triangle.vertices
            edges = [(verts[0], verts[1]), (verts[1], verts[2]), (verts[2], verts[0])]
            for edge in edges:
                key = edge_key(*edge)
                edge_count[key] = edge_count.get(key, 0) + 1

        boundary = [edge for edge, count in edge_count.items() if count == 1]

        # Убираем плохие треугольники
        triangles = [t for t in triangles if t not in bad_triangles]

        # Соединяем границу с новой точкой – создаём новые треугольники
        for edge in boundary:
            new_triangle = Triangle(edge[0], edge[1], point)
            triangles.append(new_triangle)

    # Убираем все треугольники, содержащие вершины супер-треугольника
    final_triangles = []
    for triangle in triangles:
        if (super_triangle.vertices[0] in triangle.vertices or
                super_triangle.vertices[1] in triangle.vertices or
                super_triangle.vertices[2] in triangle.vertices):
            continue
        final_triangles.append(triangle)

    return final_triangles
