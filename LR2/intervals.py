import math

def draw_pixel(canvas, x, y, intensity=1, size=1):
    """
    Рисует пиксель (точку) на канве.

    Параметры:
      canvas      - объект Canvas.
      x, y        - координаты.
      intensity   - интенсивность (от 0 до 1), где 0 – белый, 1 – черный.
      size        - размер пикселя.
    """
    x = int(round(x))
    y = int(round(y))
    intensity = max(0, min(1, intensity))
    shade = int(255 * (1 - intensity))
    color = f"#{shade:02x}{shade:02x}{shade:02x}"
    canvas.create_rectangle(x, y, x + size, y + size, outline=color, fill=color)


def draw_line_dda(canvas, x0, y0, x1, y1, debug=False):
    """
    Строит линию по алгоритму ЦДА.
    Если debug=True, возвращает таблицу итераций, содержащую:
        Итерация, x, y, Отобр. координаты (округлённые)
    """
    dx = x1 - x0
    dy = y1 - y0
    steps = int(max(abs(dx), abs(dy)))

    if steps == 0:
        draw_pixel(canvas, x0, y0)
        return [] if debug else None

    x_inc = dx / steps
    y_inc = dy / steps
    x, y = x0, y0

    table = [] if debug else None

    for i in range(steps + 1):
        displayed = (int(round(x)), int(round(y)))
        if debug:
            # Формат: Итерация, x, y, Отобр. координаты
            table.append((i, x, y, displayed))
        draw_pixel(canvas, x, y)
        x += x_inc
        y += y_inc

    return table if debug else None


def draw_line_bresenham(canvas, x0, y0, x1, y1, debug=False):
    """
    Строит линию по алгоритму Брезенхэма.
    Если debug=True, возвращает таблицу итераций, содержащую:
        Итерация, x, y, e, e′, Отобр. координаты
    где:
      - x, y – текущие координаты (целые),
      - e – значение ошибки до корректировки,
      - e′ – ошибка после внесения изменений на данном шаге.
    """
    x0, y0, x1, y1 = map(round, (x0, y0, x1, y1))
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    table = [] if debug else None
    iteration = 0

    while True:
        cur_x, cur_y = x0, y0
        cur_err = err  # значение ошибки до изменения

        # Если достигли конечной точки, записываем итерацию и завершаем цикл.
        if cur_x == x1 and cur_y == y1:
            if debug:
                table.append((iteration, cur_x, cur_y, cur_err, cur_err, (cur_x, cur_y)))
            draw_pixel(canvas, cur_x, cur_y)
            break

        e2 = 2 * err
        new_x, new_y = cur_x, cur_y

        # Корректировка по x
        if e2 > -dy:
            err -= dy
            new_x = cur_x + sx
        # Корректировка по y
        if e2 < dx:
            err += dx
            new_y = cur_y + sy

        corrected_err = err  # значение ошибки после корректировки

        if debug:
            # Формируем строку: итерация, cur_x, cur_y, cur_err, corrected_err, отображаемые координаты
            table.append((iteration, cur_x, cur_y, cur_err, corrected_err, (cur_x, cur_y)))
        draw_pixel(canvas, cur_x, cur_y)

        # Переходим к следующему пикселю
        x0, y0 = new_x, new_y
        iteration += 1

    return table if debug else None


def draw_line_wu(canvas, x0, y0, x1, y1, debug=False):
    """
    Строит линию по алгоритму Ву (антиалиасинг).
    Если debug=True, возвращает таблицу итераций, содержащую:
         Итерация, x, y, e, e′, Отобр. координаты
    Здесь:
         x – целочисленная координата (отображаемая);
         y – ipart(intery) (определяет верхний пиксель);
         e – значение, равное rfpart(intery) (интенсивность для пикселя с координатами y);
         e′ – значение fpart(intery) (интенсивность для пикселя с координатами y+1).
    """
    def ipart(x): return int(math.floor(x))
    def round_val(x): return int(math.floor(x + 0.5))
    def fpart(x): return x - math.floor(x)
    def rfpart(x): return 1 - fpart(x)

    steep = abs(y1 - y0) > abs(x1 - x0)
    if steep:
        # Меняем местами x и y
        x0, y0, x1, y1 = y0, x0, y1, x1
    if x0 > x1:
        x0, x1, y0, y1 = x1, x0, y1, y0

    dx = x1 - x0
    dy = y1 - y0
    gradient = dy / dx if dx != 0 else 0

    table = [] if debug else None
    iteration = 0

    intery = y0 + gradient * (round_val(x0) - x0)
    # Проходим по x от округленного начального значения до округленного конечного
    for x in range(round_val(x0), round_val(x1)):
        y = ipart(intery)
        # В данном алгоритме:
        # e   = rfpart(intery) – интенсивность для пикселя (x, y)
        # e′  = fpart(intery) – интенсивность для пикселя (x, y+1)
        e = rfpart(intery)
        e_prime = fpart(intery)
        displayed = (x, y)
        if debug:
            table.append((iteration, x, y, e, e_prime, displayed))
        draw_pixel(canvas, x, y, intensity=e)
        draw_pixel(canvas, x, y + 1, intensity=e_prime)
        intery += gradient
        iteration += 1

    return table if debug else None
