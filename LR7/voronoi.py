# voronoi.py
import math


def normalize(vec):
    """
    Нормализует вектор (dx, dy). Если длина равна 0, возвращает (0, 0).
    """
    dx, dy = vec
    norm = math.hypot(dx, dy)
    if norm == 0:
        return (0, 0)
    return (dx / norm, dy / norm)


def intersect_ray_box(origin, direction, bbox):
    """
    Находит точку пересечения луча, заданного точкой origin и направлением direction,
    с прямоугольником bbox = (xmin, ymin, xmax, ymax). Возвращается ближайшая точка пересечения вдоль луча.
    """
    (xmin, ymin, xmax, ymax) = bbox
    t_values = []
    if direction[0] != 0:
        t1 = (xmin - origin[0]) / direction[0]
        t2 = (xmax - origin[0]) / direction[0]
        for t in (t1, t2):
            if t > 0:
                y_hit = origin[1] + t * direction[1]
                if ymin <= y_hit <= ymax:
                    t_values.append(t)
    if direction[1] != 0:
        t3 = (ymin - origin[1]) / direction[1]
        t4 = (ymax - origin[1]) / direction[1]
        for t in (t3, t4):
            if t > 0:
                x_hit = origin[0] + t * direction[0]
                if xmin <= x_hit <= xmax:
                    t_values.append(t)
    if not t_values:
        return origin
    t_min = min(t_values)
    return (origin[0] + t_min * direction[0], origin[1] + t_min * direction[1])


def line_box_intersections(p, d, bbox):
    """
    Находит все точки пересечения бесконечной прямой, проходящей через точку p
    в направлении d с ограничивающим прямоугольником bbox = (xmin, ymin, xmax, ymax).
    Возвращает список уникальных точек пересечения.
    """
    (xmin, ymin, xmax, ymax) = bbox
    intersections = []
    if d[0] != 0:
        t1 = (xmin - p[0]) / d[0]
        pt1 = (p[0] + t1 * d[0], p[1] + t1 * d[1])
        if ymin - 1e-6 <= pt1[1] <= ymax + 1e-6:
            intersections.append(pt1)
        t2 = (xmax - p[0]) / d[0]
        pt2 = (p[0] + t2 * d[0], p[1] + t2 * d[1])
        if ymin - 1e-6 <= pt2[1] <= ymax + 1e-6:
            intersections.append(pt2)
    if d[1] != 0:
        t3 = (ymin - p[1]) / d[1]
        pt3 = (p[0] + t3 * d[0], p[1] + t3 * d[1])
        if xmin - 1e-6 <= pt3[0] <= xmax + 1e-6:
            intersections.append(pt3)
        t4 = (ymax - p[1]) / d[1]
        pt4 = (p[0] + t4 * d[0], p[1] + t4 * d[1])
        if xmin - 1e-6 <= pt4[0] <= xmax + 1e-6:
            intersections.append(pt4)
    # Убираем дубли с учётом числовой точности
    unique = []
    for point in intersections:
        if not any(math.hypot(point[0] - up[0], point[1] - up[1]) < 1e-6 for up in unique):
            unique.append(point)
    return unique


def compute_voronoi_edges(triangles, bbox):
    """
    Вычисляет список ребер диаграммы Вороного по списку треугольников.
    Для ребер, разделяемых двумя треугольниками, просто соединяются центры описанных окружностей.
    Для граничных ребер (принадлежащих только одному треугольнику) выполняется улучшенное замыкание:
      - Определяется внешняя нормаль к ребру на основании третьей вершины треугольника.
      - Множество точек пересечения прямой (из центра описанной окружности в направлении нормали)
        с bbox вычисляется с помощью line_box_intersections.
      - Выбирается точка, наиболее удалённая вдоль этой нормали.
    bbox — ограничивающий прямоугольник в виде (xmin, ymin, xmax, ymax).
    Возвращает список ребер в виде ((x1, y1), (x2, y2)).
    """
    # Построим словарь, где ключ – отсортированное ребро, а значение – список треугольников, содержащих его.
    edges = {}
    for tri in triangles:
        verts = tri.vertices
        for edge in [(verts[0], verts[1]), (verts[1], verts[2]), (verts[2], verts[0])]:
            key = tuple(sorted(edge))
            edges.setdefault(key, []).append(tri)

    voronoi_edges = []
    for edge, tris in edges.items():
        if len(tris) == 2:
            # Ребро, разделяемое двумя треугольниками: соединяем центры их описанных окружностей.
            p1 = tris[0].circumcenter
            p2 = tris[1].circumcenter
            voronoi_edges.append((p1, p2))
        elif len(tris) == 1:
            # Обработка граничного ребра: используем информацию о трёх вершинах треугольника.
            tri = tris[0]
            (p, q) = edge
            # Найдём третью вершину (той, которая не принадлежит ребру).
            r = [v for v in tri.vertices if v not in edge][0]
            midpoint = ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
            edge_vector = (q[0] - p[0], q[1] - p[1])
            # Два возможных нормальных вектора к ребру.
            n1 = normalize((edge_vector[1], -edge_vector[0]))
            n2 = normalize((-edge_vector[1], edge_vector[0]))
            # Выбираем нормаль, которая направлена наружу от треугольника.
            # Для этого сравниваем скалярные произведения с вектором от третьей вершины (r) к середине ребра.
            v = (midpoint[0] - r[0], midpoint[1] - r[1])
            if (v[0] * n1[0] + v[1] * n1[1]) >= (v[0] * n2[0] + v[1] * n2[1]):
                normal = n1
            else:
                normal = n2

            # Улучшенное замыкание: вычисляем все точки пересечения прямой (начиная в tri.circumcenter, движущейся по normal)
            intersections = line_box_intersections(tri.circumcenter, normal, bbox)
            if intersections:
                # Выбираем точку, для которой значение смещения (скалярное произведение) от tri.circumcenter вдоль normal максимально.
                far_point = None
                max_dp = -float('inf')
                for pt in intersections:
                    dp = (pt[0] - tri.circumcenter[0]) * normal[0] + (pt[1] - tri.circumcenter[1]) * normal[1]
                    if dp > max_dp:
                        max_dp = dp
                        far_point = pt
                if far_point:
                    voronoi_edges.append((tri.circumcenter, far_point))
            else:
                # На случай отсутствия пересечений – запасной вариант.
                far_point = intersect_ray_box(tri.circumcenter, normal, bbox)
                voronoi_edges.append((tri.circumcenter, far_point))
    return voronoi_edges
