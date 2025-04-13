import math
from intervals import draw_pixel


def draw_hermite(canvas, p1, p4, r1, r4, dt=0.01, debug=False):
    """
    Рисует кривую методом интерполяции Эрмита.

    Входные параметры:
      • p1, p4 – концевые точки (кортежи (x, y))
      • r1, r4 – касательные (векторы) в точках p1 и p4
      • dt – шаг изменения параметра t (по умолчанию 0.01)
      • debug – если True, функция возвращает таблицу отладки

    Эрмитовы базисные функции:
      h00(t) = 2t³ − 3t² + 1
      h10(t) = t³ − 2t² + t
      h01(t) = −2t³ + 3t²
      h11(t) = t³ − t²
    """
    table = [] if debug else None
    t = 0.0
    step = 0
    while t <= 1.0:
        h00 = 2 * t ** 3 - 3 * t ** 2 + 1
        h10 = t ** 3 - 2 * t ** 2 + t
        h01 = -2 * t ** 3 + 3 * t ** 2
        h11 = t ** 3 - t ** 2

        x = h00 * p1[0] + h10 * r1[0] + h01 * p4[0] + h11 * r4[0]
        y = h00 * p1[1] + h10 * r1[1] + h01 * p4[1] + h11 * r4[1]

        # Отрисовка вычисленной точки
        draw_pixel(canvas, int(round(x)), int(round(y)))

        if debug:
            pixel = (int(round(x)), int(round(y)))
            # Здесь поля di, δ и di+1 не вычисляются – заполняем нулями
            table.append((step, t, 0.0, 0.0, pixel, x, y, 0.0, pixel))

        step += 1
        t += dt
    return table if debug else None


def draw_bezier(canvas, p1, p2, p3, p4, dt=0.01, debug=False):
    """
    Рисует кубическую кривую Безье по имеющимся четырем контрольным точкам.

    Используется стандартная формула:
      B(t) = (1-t)³ * p1 + 3t(1-t)² * p2 + 3t²(1-t) * p3 + t³ * p4,  t ∈ [0,1]

    Входные параметры:
      • p1, p2, p3, p4 – контрольные точки (каждая как кортеж (x, y))
      • dt – шаг изменения параметра t (по умолчанию 0.01)
      • debug – если True, возвращается таблица отладки

    Если debug=True, для каждой итерации возвращается запись:
       (шаг, t, 0.0, 0.0, пиксель, x, y, 0.0, пиксель)
    """
    table = [] if debug else None
    t = 0.0
    step = 0
    while t <= 1.0:
        one_minus_t = 1 - t
        x = (one_minus_t ** 3 * p1[0] +
             3 * t * (one_minus_t ** 2) * p2[0] +
             3 * t ** 2 * one_minus_t * p3[0] +
             t ** 3 * p4[0])
        y = (one_minus_t ** 3 * p1[1] +
             3 * t * (one_minus_t ** 2) * p2[1] +
             3 * t ** 2 * one_minus_t * p3[1] +
             t ** 3 * p4[1])

        draw_pixel(canvas, int(round(x)), int(round(y)))

        if debug:
            pixel = (int(round(x)), int(round(y)))
            table.append((step, t, 0.0, 0.0, pixel, x, y, 0.0, pixel))

        step += 1
        t += dt
    return table if debug else None


def draw_bspline(canvas, points, dt=0.01, debug=False):
    """
    Рисует равномерный кубический B-сплайн по заданному набору контрольных точек.

    Входные параметры:
      • points – список контрольных точек (каждая точка – кортеж (x, y)); должно быть не менее 4 точек.
      • dt – шаг изменения параметра t (по умолчанию 0.01)
      • debug – если True, возвращается таблица отладки

    Для каждой группы из 4 подряд идущих точек (p0, p1, p2, p3) вычисляется сегмент по формуле:

      P(t) = [t³, t², t, 1] * (1/6) * M * G,  где

      M = [ [-1,  3, -3,  1],
            [ 3, -6,  3,  0],
            [-3,  0,  3,  0],
            [ 1,  4,  1,  0] ]

      G – вектор координат контрольных точек (например, для x: [p0_x, p1_x, p2_x, p3_x]ᵀ).

    Если debug=True, для каждой итерации записывается:
         (шаг, t, 0.0, 0.0, пиксель, x, y, 0.0, пиксель)
    """
    if len(points) < 4:
        raise ValueError("Для построения B-сплайна требуется минимум 4 контрольные точки.")

    # Определяем матрицу B-сплайна
    M = [
        [-1, 3, -3, 1],
        [3, -6, 3, 0],
        [-3, 0, 3, 0],
        [1, 4, 1, 0]
    ]
    table = [] if debug else None
    step = 0
    # Для каждого сегмента (группы из 4 точек)
    for i in range(len(points) - 3):
        p0, p1, p2, p3 = points[i], points[i + 1], points[i + 2], points[i + 3]
        Gx = [p0[0], p1[0], p2[0], p3[0]]
        Gy = [p0[1], p1[1], p2[1], p3[1]]
        t = 0.0
        while t <= 1.0:
            T_vec = [t ** 3, t ** 2, t, 1]
            # Вычисляем промежуточный вектор A = T_vec * M
            A = [0.0, 0.0, 0.0, 0.0]
            for j in range(4):
                for k in range(4):
                    A[j] += T_vec[k] * M[k][j]
            # Вычисляем координаты, затем делим на 6 согласно формуле
            x = sum(A[j] * Gx[j] for j in range(4)) / 6.0
            y = sum(A[j] * Gy[j] for j in range(4)) / 6.0

            draw_pixel(canvas, int(round(x)), int(round(y)))

            if debug:
                pixel = (int(round(x)), int(round(y)))
                table.append((step, t, 0.0, 0.0, pixel, x, y, 0.0, pixel))
            step += 1
            t += dt
    return table if debug else None
