import math

def create_cube(side=1.0):
    """
    Создает куб со стороной side, центрированный в начале координат.
    Возвращает:
      vertices: список вершин (x, y, z)
      faces: список граней, каждая грань - кортеж индексов вершин
    """
    hs = side / 2.0  # половина длины стороны
    vertices = [
        (-hs, -hs, -hs),  # 0
        (hs, -hs, -hs),  # 1
        (hs, hs, -hs),  # 2
        (-hs, hs, -hs),  # 3
        (-hs, -hs, hs),  # 4
        (hs, -hs, hs),  # 5
        (hs, hs, hs),  # 6
        (-hs, hs, hs)  # 7
    ]

    faces = [
        (0, 1, 2, 3),  # Нижняя грань
        (4, 5, 6, 7),  # Верхняя грань
        (0, 1, 5, 4),  # Передняя грань
        (1, 2, 6, 5),  # Правая грань
        (2, 3, 7, 6),  # Задняя грань
        (3, 0, 4, 7)  # Левая грань
    ]
    return vertices, faces


def create_sphere(radius=1.0, lat_steps=10, lon_steps=10):
    """
    Создает сферу с заданным радиусом, количеством параллелей (lat_steps)
    и меридианов (lon_steps). Сфера центрирована в начале координат.

    Возвращает:
      vertices: список вершин (x, y, z)
      faces: список граней. Для внутренних областей — четырехвершинные квадраты,
             для полюсов — треугольники.
    """
    vertices = []
    faces = []

    # Генерация вершин сферических координат
    for i in range(lat_steps + 1):
        theta = math.pi * i / lat_steps  # 0 до pi
        sin_theta = math.sin(theta)
        cos_theta = math.cos(theta)
        for j in range(lon_steps):
            phi = 2 * math.pi * j / lon_steps  # 0 до 2pi
            sin_phi = math.sin(phi)
            cos_phi = math.cos(phi)
            x = radius * sin_theta * cos_phi
            y = radius * sin_theta * sin_phi
            z = radius * cos_theta
            vertices.append((x, y, z))

    # Создаем грани, обходя "ряды" вершин между параллелями
    for i in range(lat_steps):
        for j in range(lon_steps):
            next_j = (j + 1) % lon_steps
            current = i * lon_steps + j
            next_vert = i * lon_steps + next_j
            current_row_next = (i + 1) * lon_steps + j
            next_row_next = (i + 1) * lon_steps + next_j

            # На полюсах формируем треугольники
            if i == 0:
                faces.append((current, next_row_next, current_row_next))
            elif i == lat_steps - 1:
                faces.append((current, next_vert, current_row_next))
            else:
                faces.append((current, next_vert, next_row_next, current_row_next))
    return vertices, faces


def create_cylinder(radius=1.0, height=2.0, segments=20):
    """
    Создает цилиндр с заданным радиусом, высотой и количеством сегментов вокруг основания.
    Цилиндр центрирован вдоль оси Z (нижнее основание на z = -height/2, верхнее на z = height/2).

    Возвращает:
      vertices: список вершин (x, y, z)
      faces: список граней.
             - Нижнее основание: треугольный фан, начиная с центра.
             - Верхнее основание: треугольный фан.
             - Боковые грани: четырехвершинные.
    """
    vertices = []
    faces = []

    # Центры нижнего и верхнего оснований
    bottom_center = (0, 0, -height / 2)
    top_center = (0, 0, height / 2)
    vertices.append(bottom_center)  # индекс 0
    vertices.append(top_center)  # индекс 1

    bottom_indices = []
    top_indices = []

    # Создаем точки окружностей
    for i in range(segments):
        angle = 2 * math.pi * i / segments
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        bottom_indices.append(len(vertices))
        vertices.append((x, y, -height / 2))
    for i in range(segments):
        angle = 2 * math.pi * i / segments
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        top_indices.append(len(vertices))
        vertices.append((x, y, height / 2))

    # Нижнее основание (треугольный фан)
    for i in range(segments):
        next_i = (i + 1) % segments
        faces.append((0, bottom_indices[i], bottom_indices[next_i]))

    # Верхнее основание (треугольный фан) с обратным порядком для корректной нормали
    for i in range(segments):
        next_i = (i + 1) % segments
        faces.append((1, top_indices[next_i], top_indices[i]))

    # Боковые грани (четырехвершинные)
    for i in range(segments):
        next_i = (i + 1) % segments
        faces.append((
            bottom_indices[i],
            bottom_indices[next_i],
            top_indices[next_i],
            top_indices[i]
        ))
    return vertices, faces
