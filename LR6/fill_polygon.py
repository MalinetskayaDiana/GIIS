import tkinter.messagebox as mb
import math

def point_in_polygon(x, y, verts):
    """
    Определяет, принадлежит ли точка (x, y) полигона, заданного списком вершин verts.
    Использует алгоритм лучевого пересечения (Ray Casting).
    """
    n = len(verts)
    inside = False
    j = n - 1
    for i in range(n):
        xi, yi = verts[i]
        xj, yj = verts[j]
        # Если y попадает между y[i] и y[j] и x меньше пересечения луча с ребром
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi + 1e-10) + xi):
            inside = not inside
        j = i
    return inside

def fill_polygon_scanline(canvas, polygon, fill_color):
    """
    Алгоритм растровой развертки с упорядоченным списком ребер.
    Перебираем сканирующие строки от минимального до максимального y,
    для каждой строки находим пересечения ребер полигона, сортируем их по x
    и закрашиваем получившиеся интервалы.
    """
    verts = polygon.vertices
    if not polygon.closed or len(verts) < 3:
        mb.showwarning("Ошибка заливки", "Полигон не закрыт или содержит менее 3 вершин.")
        return

    ys = [int(round(y)) for (x, y) in verts]
    min_y = min(ys)
    max_y = max(ys)
    n = len(verts)

    for y in range(min_y, max_y + 1):
        intersections = []
        for i in range(n):
            x1, y1 = verts[i]
            x2, y2 = verts[(i + 1) % n]
            if y1 < y2:
                y_lower, y_upper = y1, y2
                x_lower, x_upper = x1, x2
            else:
                y_lower, y_upper = y2, y1
                x_lower, x_upper = x2, x1
            if y_lower <= y < y_upper:
                if y_upper - y_lower != 0:
                    x_int = x_lower + (y - y_lower) * (x_upper - x_lower) / (y_upper - y_lower)
                    intersections.append(x_int)
        intersections.sort()
        for j in range(0, len(intersections), 2):
            if j + 1 < len(intersections):
                x_start = intersections[j]
                x_end = intersections[j + 1]
                canvas.create_line(x_start, y, x_end, y, fill=fill_color)

def fill_polygon_active_edge(canvas, polygon, fill_color):
    """
    Алгоритм растровой развертки с использованием списка активных ребер.
    Для каждой сканирующей строки поддерживается список ребер, пересекающих её,
    который обновляется по мере продвижения по строкам.
    """
    verts = polygon.vertices
    if not polygon.closed or len(verts) < 3:
        mb.showwarning("Ошибка заливки", "Полигон не закрыт или содержит менее 3 вершин.")
        return

    ys = [int(round(y)) for (x, y) in verts]
    min_y = min(ys)
    max_y = max(ys)
    n = len(verts)
    edges = []
    for i in range(n):
        x1, y1 = verts[i]
        x2, y2 = verts[(i + 1) % n]
        if y1 == y2:
            continue
        if y1 < y2:
            y_min = y1; y_max = y2; x_start = x1
            inv_slope = (x2 - x1) / (y2 - y1)
        else:
            y_min = y2; y_max = y1; x_start = x2
            inv_slope = (x1 - x2) / (y1 - y2)
        edges.append({
            "y_min": int(round(y_min)),
            "y_max": int(round(y_max)),
            "x": x_start,
            "inv_slope": inv_slope
        })

    active_edges = []
    for y in range(min_y, max_y + 1):
        for edge in edges:
            if edge["y_min"] == y:
                active_edges.append(edge)
        active_edges = [edge for edge in active_edges if y < edge["y_max"]]
        active_edges.sort(key=lambda e: e["x"])
        for i in range(0, len(active_edges), 2):
            if i + 1 < len(active_edges):
                x_start = active_edges[i]["x"]
                x_end = active_edges[i + 1]["x"]
                canvas.create_line(x_start, y, x_end, y, fill=fill_color)
        for edge in active_edges:
            edge["x"] += edge["inv_slope"]

def fill_polygon_boundary(canvas, polygon, seed, fill_color, boundary_color):
    """
    Простой алгоритм заливки затравкой (boundary fill) с проверкой принадлежности точки полигону.
    Здесь используется итеративный подход с использованием стека.
    Для каждого пикселя перед заливкой проверяется, находится ли он внутри полигона.
    Если затравочная точка находится вне полигона, заливка не выполняется.
    """
    verts = polygon.vertices
    if not point_in_polygon(seed[0], seed[1], verts):
        mb.showwarning("Заливка", "Затравочная точка находится вне полигона!")
        return

    width = canvas.winfo_width()
    height = canvas.winfo_height()
    stack = [seed]
    filled = set()

    while stack:
        cx, cy = stack.pop()
        if cx < 0 or cx >= width or cy < 0 or cy >= height:
            continue
        if (cx, cy) in filled:
            continue
        if not point_in_polygon(cx, cy, verts):
            continue

        canvas.create_rectangle(cx, cy, cx+1, cy+1, outline=fill_color, fill=fill_color)
        filled.add((cx, cy))

        stack.append((cx+1, cy))
        stack.append((cx-1, cy))
        stack.append((cx, cy+1))
        stack.append((cx, cy-1))

def fill_polygon_line_flood(canvas, polygon, seed, fill_color, boundary_color):
    """
    Построчный алгоритм заливки с затравкой.
    Заполняется горизонтальный интервал (строка), затем для интервала сверху и снизу запускается заливка.
    Перед заполнением каждой точки проверяется принадлежность точке полигону.
    """
    verts = polygon.vertices
    if not point_in_polygon(seed[0], seed[1], verts):
        mb.showwarning("Заливка", "Затравочная точка находится вне полигона!")
        return

    width = canvas.winfo_width()
    height = canvas.winfo_height()
    filled = set()
    stack = [seed]

    while stack:
        x, y = stack.pop()
        # Найдем левый край интервала
        x_left = x
        while x_left >= 0 and (x_left, y) not in filled and point_in_polygon(x_left, y, verts):
            x_left -= 1
        x_left += 1
        # Найдем правый край интервала
        x_right = x
        while x_right < width and (x_right, y) not in filled and point_in_polygon(x_right, y, verts):
            x_right += 1

        for xi in range(x_left, x_right):
            canvas.create_rectangle(xi, y, xi+1, y+1, outline=fill_color, fill=fill_color)
            filled.add((xi, y))

        for xi in range(x_left, x_right):
            if y-1 >= 0 and (xi, y-1) not in filled and point_in_polygon(xi, y-1, verts):
                stack.append((xi, y-1))
            if y+1 < height and (xi, y+1) not in filled and point_in_polygon(xi, y+1, verts):
                stack.append((xi, y+1))
