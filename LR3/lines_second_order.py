import math
from intervals import draw_pixel

def draw_circle(canvas, cx, cy, R, debug=False):
    """
    Строит окружность по алгоритму Брезенхэма.
    В отладочном режиме возвращает таблицу итераций с полями:
      Шаг | di | δ | δ* | Пиксель | x | y | di+1 | Отобр. координаты
    Для "δ" берем разность между ошибкой следующего шага и текущей,
    для "δ*" оставляем 0 (если нет иной информации).
    """
    x = 0
    y = R
    d = 3 - 2 * R
    table = [] if debug else None
    iteration = 0
    prev_d = d  # для расчета δ, на первом шаге не рассчитываем, можем принять δ = 0
    # Пока x <= y (отрезаем восьмую часть) – стандартное условие алгоритма Брезенхэма
    while x <= y:
        # Записываем точки (отражения)
        pts = [
            (cx + x, cy + y), (cx - x, cy + y),
            (cx + x, cy - y), (cx - x, cy - y),
            (cx + y, cy + x), (cx - y, cy + x),
            (cx + y, cy - x), (cx - y, cy - x)
        ]
        for pt in pts:
            draw_pixel(canvas, pt[0], pt[1])

        # Предполагаем, что в качестве пикселя возьмем первую точку отражения
        pixel = (cx + x, cy + y)
        # Пока не рассчитываем di+1, задаем его равным текущей ошибке d, а δ и δ* как разность 0
        delta = 0.0
        di_next = d  # если не вычисляем следующее значение отдельно
        delta_star = 0.0

        if debug:
            # Записываем текущую строку отладочной информации.
            # Шаг (iteration), d_i, δ, δ*, пиксель, x, y, di+1, Plot(x,y)
            table.append((iteration, d, delta, delta_star, pixel, x, y, di_next, pixel))

        # Выполняем обновление ошибки по алгоритму Брезенхэма:
        if d < 0:
            d = d + 4 * x + 6
        else:
            d = d + 4 * (x - y) + 10
            y -= 1

        # Можно вычислить δ как разность нового d и предыдущего (если iteration > 0)
        if iteration > 0:
            delta = d - prev_d
        prev_d = d

        x += 1
        iteration += 1

    return table if debug else None

def draw_ellipse(canvas, cx, cy, rx, ry, debug=False):
    """
    Строит эллипс (центр (cx,cy), полуоси rx и ry) по алгоритму средней точки.
    Если debug=True, возвращает таблицу записей в следующем формате (9 элементов):
         Шаг | di | δ | δ* | Пиксель | x | y | di+1 | Plot (x, y)
    где:
      - di – текущая ошибка (или параметр, определяющий решение),
      - δ – разность нового и старого значения,
      - δ* – дополнительная корректировка (здесь берется 0.0),
      - Пиксель и Plot (x, y) – выбранные координаты точки (отражённой) для отрисовки.
    """
    x = 0
    y = ry
    rx2 = rx * rx
    ry2 = ry * ry
    # Начальное значение решения для области 1
    p1 = ry2 - rx2 * ry + 0.25 * rx2
    table = [] if debug else None
    iteration = 0

    # Область 1: пока 2*ry2*x < 2*rx2*y
    while (2 * ry2 * x) < (2 * rx2 * y):
        # Отрисовка симметричных точек эллипса
        pts = [
            (cx + x, cy + y), (cx - x, cy + y),
            (cx + x, cy - y), (cx - x, cy - y)
        ]
        for pt in pts:
            draw_pixel(canvas, pt[0], pt[1])

        if debug:
            old_p = p1

        # Обновление решения для области 1
        if p1 < 0:
            # Изменяется только x, y остаётся
            new_p = p1 + 2 * ry2 * (x + 1) + ry2
            x = x + 1
        else:
            new_p = p1 + 2 * ry2 * (x + 1) - 2 * rx2 * (y - 1) + ry2
            x = x + 1
            y = y - 1

        if debug:
            delta = new_p - old_p
            delta_star = 0.0  # Дополнительную корректировку можем задать нулём
            pixel = (cx + x, cy + y)  # выбираем первую отражённую точку
            plot_coords = pixel  # отображаемые координаты совпадают
            table.append((iteration, old_p, delta, delta_star, pixel, x, y, new_p, plot_coords))

        p1 = new_p
        iteration += 1

    # Область 2
    p2 = ry2 * (x + 0.5) ** 2 + rx2 * (y - 1) ** 2 - rx2 * ry2
    while y >= 0:
        pts = [
            (cx + x, cy + y), (cx - x, cy + y),
            (cx + x, cy - y), (cx - x, cy - y)
        ]
        for pt in pts:
            draw_pixel(canvas, pt[0], pt[1])

        if debug:
            old_p = p2

        if p2 > 0:
            new_p = p2 - 2 * rx2 * (y - 1) + rx2
            y = y - 1
        else:
            new_p = p2 + 2 * ry2 * (x + 1) - 2 * rx2 * (y - 1) + rx2
            x = x + 1
            y = y - 1

        if debug:
            delta = new_p - old_p
            delta_star = 0.0
            pixel = (cx + x, cy + y)
            plot_coords = pixel
            table.append((iteration, old_p, delta, delta_star, pixel, x, y, new_p, plot_coords))

        p2 = new_p
        iteration += 1

    return table if debug else None

def draw_parabola(canvas, xc, yc, ex, ey, debug=False):
    """
    Строит вертикальную параболу через вершину (xc, yc) и вторую точку (ex, ey)
    по формуле:
         y = a * (x - xc)^2 + yc,
    где коэффициент a = (ey - yc)/((ex - xc)^2).

    Если debug=True, возвращается таблица отладки в формате:
         (Шаг, di, δ, δ*, Пиксель, x, y, di+1, Plot (x, y))
    где:
      - di = (y - yc)  (смещение по y относительно вершины),
      - δ = di_next - di,
      - δ* = 0.0.
    """
    if ex == xc:
        raise ValueError("Вторая точка не должна совпадать по x с вершиной, чтобы избежать деления на ноль.")

    a = (ey - yc) / ((ex - xc) ** 2)
    table = [] if debug else None
    iteration = 0

    canvas_width = int(canvas["width"])
    canvas_height = int(canvas["height"])

    for x in range(0, canvas_width, 1):
        dx = x - xc
        y = a * (dx ** 2) + yc
        if y < 0 or y > canvas_height:
            continue

        # Рисуем две симметричные точки
        draw_pixel(canvas, x, y)
        draw_pixel(canvas, xc - dx, y)

        if debug:
            # Определяем текущую параметрическую величину: di = y - yc
            di = y - yc
            # Попытаемся вычислить значение для следующего шага (при x+1)
            if x + 1 < canvas_width:
                next_dx = (x + 1) - xc
                next_y = a * (next_dx ** 2) + yc
                di_next = next_y - yc
            else:
                di_next = di
            delta = di_next - di
            delta_star = 0.0
            pixel = (x, int(round(y)))  # выбираем правую точку
            plot_coords = pixel
            table.append((iteration, di, delta, delta_star, pixel, x, y, di_next, plot_coords))

        iteration += 1

    return table if debug else None

def draw_hyperbola(canvas, xc, yc, x2, y2, direction, debug=False):
    """
    Рисует гиперболу с центром (xc, yc). Полуоси определяются как:
         - a = |x2 - xc| (горизонтальная полуось),
         - b = |y2 - yc| (вертикальная полуось).

    Выбор уравнения зависит от направления:
         - "horizontal": (x - xc)^2/a^2 - (y - yc)^2/b^2 = 1,
         - "vertical":   (y - yc)^2/b^2 - (x - xc)^2/a^2 = 1.

    При debug=True формируется таблица отладки в формате:
         (Шаг, di, δ, δ*, Пиксель, x, y, di+1, Plot (x, y))
    Для "horizontal" направления в качестве di возьмём вычисленное x-координату правой верхней точки.
    Для "vertical" – аналогично, будем использовать y-координату правой верхней точки.
    """
    a_val = abs(x2 - xc)  # Горизонтальная полуось
    b_val = abs(y2 - yc)  # Вертикальная полуось

    T = 2.0  # Максимальное значение параметра t
    dt = 0.01  # Шаг изменения параметра t

    table = [] if debug else None
    iteration = 0
    t = -T

    while t <= T:
        if direction == "horizontal":
            # Гипербола вдоль оси X:
            x_right = xc + a_val * math.cosh(t)
            y_top = yc + b_val * math.sinh(t)
            x_left = xc - a_val * math.cosh(t)
            y_bottom = yc - b_val * math.sinh(t)
            # Для отладки возьмем di = x_right (как параметрическая координата)
            di = x_right
            # Вычисляем следующую точку (при t+dt)
            next_t = t + dt
            next_x_right = xc + a_val * math.cosh(next_t)
            di_next = next_x_right
        elif direction == "vertical":
            # Гипербола вдоль оси Y:
            x_right = xc + b_val * math.sinh(t)
            y_top = yc + a_val * math.cosh(t)
            x_left = xc - b_val * math.sinh(t)
            y_bottom = yc - a_val * math.cosh(t)
            # Для вертикальной гиперболы возьмём di = y_top
            di = y_top
            next_t = t + dt
            next_y_top = yc + a_val * math.cosh(next_t)
            di_next = next_y_top
        else:
            raise ValueError("Invalid direction. Use 'horizontal' or 'vertical'.")

        delta = di_next - di
        delta_star = 0.0
        # В качестве пикселя для отладки берем правую верхнюю точку
        pixel = (int(round(x_right)), int(round(y_top)))
        plot_coords = pixel

        # Отрисовываем точки четырьмя вызовами
        draw_pixel(canvas, x_right, y_top)  # Правая верхняя
        draw_pixel(canvas, x_left, y_top)  # Левая верхняя
        draw_pixel(canvas, x_right, y_bottom)  # Правая нижняя
        draw_pixel(canvas, x_left, y_bottom)  # Левая нижняя

        if debug:
            table.append((iteration, di, delta, delta_star, pixel, x_right, y_top, di_next, plot_coords))

        t += dt
        iteration += 1

    return table if debug else None
