import tkinter as tk
import math
from intervals import draw_line_dda, draw_line_bresenham, draw_line_wu

class GraphicEditorApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Элементарный графический редактор")
        self.root.resizable(False, False)
        self.current_mode = "Не выбран"                 # Текущий выбор (действие)
        self.current_event = "Не выбран"                # Текущая фигура
        self.selected_algorithm_title = "Не выбран"     # Текущий алгоритм (название)
        self.selected_algorithm = None                  # Алгоритм не установлен
        self.selected_curve_type_title = "Не выбран"    # Текущая кривая (название)
        self.selected_curve_type = None                 # Кривая не выбрана
        self.curve_control_points = []
        self.selected_curve_form_title = "Не выбран"    # Текущая форма для построения кривой
        self.selected_curve_form = None                 # Форма кривой не выбрана
        self.debug_mode = False                         # Режим отладки отключён
        self.start_point = None
        self.init_gui()

    def init_gui(self):
        self.create_menu()
        self.create_toolbar()
        self.create_canvas()
        self.create_status_bar()

    def create_menu(self):
        menubar = tk.Menu(self.root)

        # Меню "Файл"
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Очистить экран", command=self.clear_canvas)
        file_menu.add_command(label="Выход", command=self.root.quit)
        menubar.add_cascade(label="Файл", menu=file_menu)

        # Меню "Помощь"
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Документация", command=self.show_help)
        menubar.add_cascade(label="Помощь", menu=help_menu)

        self.root.config(menu=menubar)

    def create_toolbar(self):
        self.toolbar = tk.Frame(self.root, bd=1, relief=tk.RAISED)

        # Кнопка "Курсор" для перехода в режим курсора
        btn_cursor = tk.Button(self.toolbar, text="Курсор", command=self.select_cursor_mode)
        btn_cursor.pack(side=tk.LEFT, padx=2, pady=2)

        # Меню для выбора алгоритма построения отрезка
        self.line_menu_button = tk.Menubutton(self.toolbar, text="Отрезок", relief=tk.RAISED)
        self.line_menu = tk.Menu(self.line_menu_button, tearoff=0)
        self.line_menu.add_command(label="Алгоритм ЦДА", command=lambda: self.select_line_mode_with_algorithm("DDA"))
        self.line_menu.add_command(label="Алгоритм Брезенхэма", command=lambda: self.select_line_mode_with_algorithm("Bresenham"))
        self.line_menu.add_command(label="Алгоритм Ву", command=lambda: self.select_line_mode_with_algorithm("Wu"))
        self.line_menu_button.config(menu=self.line_menu)
        self.line_menu_button.pack(side=tk.LEFT, padx=2, pady=2)

        # Меню для выбора кривых второго порядка
        self.lines_second_order_menu_button = tk.Menubutton(self.toolbar, text="Линии 2-го порядка", relief=tk.RAISED)
        self.lines_second_order = tk.Menu(self.lines_second_order_menu_button, tearoff=0)
        self.lines_second_order.add_command(label="Окружность", command=lambda: self.select_lines_second_order_with_type("circle"))
        self.lines_second_order.add_command(label="Эллипс", command=lambda: self.select_lines_second_order_with_type("ellipse"))
        self.lines_second_order.add_command(label="Гипербола", command=lambda: self.select_lines_second_order_with_type("hyperbola"))
        self.lines_second_order.add_command(label="Парабола", command=lambda: self.select_lines_second_order_with_type("parabola"))
        self.lines_second_order_menu_button.config(menu=self.lines_second_order)
        self.lines_second_order_menu_button.pack(side=tk.LEFT, padx=2, pady=2)

        # Новое выпадающее меню для выбора кривых
        self.curve_menu_button = tk.Menubutton(self.toolbar, text="Кривые", relief=tk.RAISED)
        self.curve_menu = tk.Menu(self.curve_menu_button, tearoff=0)
        self.curve_menu.add_command(label="Форма Эмирта", command=lambda: self.select_curve_form_with_type("еmmitt form"))
        self.curve_menu.add_command(label="Форма Безье", command=lambda: self.select_curve_form_with_type("bezier form"))
        self.curve_menu.add_command(label="B-сплайн", command=lambda: self.select_curve_form_with_type("b-spline"))
        self.curve_menu_button.config(menu=self.curve_menu)
        self.curve_menu_button.pack(side=tk.LEFT, padx=2, pady=2)

        # Кнопка "Отладка"
        btn_debug = tk.Button(self.toolbar, text="Отладка", command=self.select_debug_mode)
        btn_debug.pack(side=tk.RIGHT, padx=2, pady=2)

        self.toolbar.pack(side=tk.TOP, fill=tk.X)

    def create_canvas(self):
        self.canvas = tk.Canvas(self.root, bg="white", width=800, height=600)
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def create_status_bar(self):
        self.status_var = tk.StringVar()
        self.status_var.set("История: Пуста")
        self.status_bar = tk.Label(self.root, textvariable=self.status_var,
                                   bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def update_status(self, mode, is_error=False):
        self.current_mode = mode
        if is_error:
            self.status_bar.config(fg="red")
            self.status_var.set(self.current_mode)
        else:
            self.status_bar.config(fg="black")
            self.status_var.set(f"История: {self.current_mode}")

    def show_help(self):
        try:
            with open("documentation.txt", "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            content = f"Не удалось открыть файл с документацией.\nОшибка: {e}"

        help_window = tk.Toplevel(self.root)
        help_window.title("Документация")
        help_window.geometry("1000x600")

        # Создаём текстовое поле с прокруткой
        text = tk.Text(help_window, wrap=tk.WORD, font=("Arial", 12))
        scrollbar = tk.Scrollbar(help_window, command=text.yview)
        text.configure(yscrollcommand=scrollbar.set)

        text.insert(tk.END, content)
        text.config(state=tk.DISABLED)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def run(self):
        self.root.mainloop()

    # Режимы: Курсор, Отладка и выбор алгоритмов
    def select_cursor_mode(self):
        # Если мы сейчас рисуем кривую, финализируем её перед переходом


        self.start_point = None
        # Здесь удаляем (или скрываем) только контрольные точки (визуальные маркеры),
        # оставляя объекты финальной кривой нетронутыми.
        for curve in self.curve_control_points:
            for cp in curve[0]:  # curve[0] – список опорных точек
                cp_id, pt = cp
                self.canvas.itemconfigure(cp_id, state="hidden")
        self.canvas.unbind("<Button-1>")
        self.canvas.update()  # Принудительное обновление канвы
        self.update_status("Режим курсора активирован")

    def select_debug_mode(self):
        """
        Переключает режим отладки. При включении рисуется дискретная сетка, а при отключении
        – удаляется.
        """
        if self.debug_mode:
            self.debug_mode = False
            self.update_status("Режим отладки отключен.")
            self.canvas.delete("grid")
            self.canvas.unbind("<Button-1>")
            self.canvas.bind("<Button-1>", self.on_canvas_click)
        else:
            self.debug_mode = True
            self.update_status("Режим отладки активирован.")
            self.draw_grid()
            self.canvas.bind("<Button-1>", self.on_canvas_click)

        #self.select_cursor_mode()

    def draw_grid(self, grid_size=20):
        """Рисует дискретную сетку на канве, все линии получают тег 'grid'."""
        w = int(self.canvas['width'])
        h = int(self.canvas['height'])
        for x in range(0, w + 1, grid_size):
            self.canvas.create_line(x, 0, x, h, fill="lightgray", tags="grid")
        for y in range(0, h + 1, grid_size):
            self.canvas.create_line(0, y, w, y, fill="lightgray", tags="grid")

    # Выбор алгоритмов для отрезков
    def select_dda(self):
        from intervals import draw_line_dda
        self.selected_algorithm = draw_line_dda
        self.selected_algorithm_title = "Алгоритм ЦДА"
        self.update_status("Алгоритм ЦДА выбран")

    def select_bresenham(self):
        from intervals import draw_line_bresenham
        self.selected_algorithm = draw_line_bresenham
        self.selected_algorithm_title = "Алгоритм Брезенхэма"
        self.update_status("Алгоритм Брезенхэма выбран")

    def select_wu(self):
        from intervals import draw_line_wu
        self.selected_algorithm = draw_line_wu
        self.selected_algorithm_title = "Алгоритм Ву"
        self.update_status("Алгоритм Ву выбран")

    def select_line_mode_with_algorithm(self, algo):
        if algo == "DDA":
            from intervals import draw_line_dda
            self.selected_algorithm = draw_line_dda
            self.selected_algorithm_title = "Алгоритм ЦДА"
        elif algo == "Bresenham":
            from intervals import draw_line_bresenham
            self.selected_algorithm = draw_line_bresenham
            self.selected_algorithm_title = "Алгоритм Брезенхэма"
        elif algo == "Wu":
            from intervals import draw_line_wu
            self.selected_algorithm = draw_line_wu
            self.selected_algorithm_title = "Алгоритм Ву"
        self.update_status(f"{self.selected_algorithm_title} выбран. Режим построения отрезков активирован.")
        self.current_event = "Отрезок"
        self.start_point = None
        self.canvas.bind("<Button-1>", self.on_canvas_click)

    # Выбор кривых второго порядка
    def select_lines_second_order_with_type(self, curve_type):
        self.current_event = "Линия 2-ого порядка"
        self.selected_curve_type = curve_type
        titles = {
            "circle": "Окружность",
            "ellipse": "Эллипс",
            "hyperbola": "Гипербола",
            "parabola": "Парабола"
        }
        self.selected_curve_type_title = titles.get(curve_type, "Не выбран")
        self.update_status(f"{self.selected_curve_type_title} выбран. Выберите первую точку.")
        self.start_point = None
        if curve_type == "circle":
            self.canvas.bind("<Motion>", self.on_circle_motion)
        elif curve_type == "ellipse":
            self.canvas.bind("<Motion>", self.on_ellipse_motion)
        elif curve_type == "parabola":
            self.canvas.bind("<Motion>", self.on_parabola_motion)
        elif curve_type == "hyperbola":
            self.canvas.bind("<Motion>", self.on_hyperbola_motion)
        self.canvas.bind("<Button-1>", self.on_canvas_click)

    def select_curve_form_with_type(self, curve_type):
        self.current_event = "Кривая"
        self.selected_curve_form = curve_type
        titles = {
            "еmmitt form": "Форма Эмирта",
            "bezier form": "Форма Безье",
            "b-spline": "B-сплайн",
        }
        # Перед началом новой кривой делаем видимыми все контрольные точки уже существующих кривых (если вдруг они были скрыты)
        for curve in self.curve_control_points:
            for cp in curve[0]:
                cp_id, _ = cp
                self.canvas.itemconfigure(cp_id, state="normal")
        self.selected_curve_form_title = titles.get(curve_type, "Не выбран")
        self.update_status(f"{self.selected_curve_form_title} выбран. Теперь размещайте опорные точки кликом.")
        self.start_point = None
        # Добавляем новую запись: (список точек, список отрисованных объектов, форма)
        self.curve_control_points.append(([], [], self.selected_curve_form))
        self.canvas.unbind("<Motion>")
        self.canvas.unbind("<Button-1>")
        self.canvas.bind("<Button-1>", self.handle_curve_click)

    def on_canvas_click(self, event):
        if self.current_event == "Отрезок":
            self.handle_line_click(event)
        elif self.current_event == "Линия 2-ого порядка":
            self.handle_lines_second_order_click(event)
        elif self.current_event == "Кривая":
            if self.debug_mode and self.curve_control_points:
                # Проверяем только точки активной кривой (последней тройки)
                current_curve = self.curve_control_points[-1]
                for i, (cp_id, pt) in enumerate(current_curve[0]):
                    if math.hypot(event.x - pt[0], event.y - pt[1]) <= 6:
                        # Сохраняем кортеж (текущая кривая, индекс точки)
                        self.dragging_index = (current_curve, i)
                        self.canvas.bind("<B1-Motion>", self.on_control_point_motion)
                        self.canvas.bind("<ButtonRelease-1>", self.on_control_point_release)
                        return
            # Если не найдено ни одной подходящей точки – добавляем новую
            self.handle_curve_click(event)
        else:
            self.update_status("Ошибка: не выбран режим построения фигуры", is_error=True)

    def handle_line_click(self, event):
        if self.selected_algorithm is None:
            self.update_status("Ошибка: выберите режим построения отрезков!", is_error=True)
            return

        if self.debug_mode:
            if self.start_point is None:
                self.start_point = (event.x, event.y)
                self.update_status(f"Отладка (Линия): начальная точка ({event.x}, {event.y}) выбрана, выберите конечную.")
                self.canvas.bind("<Motion>", self.on_line_motion)
            else:
                self.canvas.unbind("<Motion>")
                self.canvas.delete("preview_line")
                x0, y0 = self.start_point
                x1, y1 = event.x, event.y
                table = self.selected_algorithm(self.canvas, x0, y0, x1, y1, debug=True)
                self.show_debug_table(table)
                self.update_status(f"Отладка ({self.selected_algorithm_title}): линия от ({x0}, {y0}) до ({x1}, {y1}) построена.")
                self.start_point = None
        else:
            if self.start_point is None:
                self.start_point = (event.x, event.y)
                self.update_status(f"Линия: начальная точка ({event.x}, {event.y}) выбрана, выберите конечную.")
                self.canvas.bind("<Motion>", self.on_line_motion)
            else:
                self.canvas.unbind("<Motion>")
                self.canvas.delete("preview_line")
                x0, y0 = self.start_point
                x1, y1 = event.x, event.y
                self.selected_algorithm(self.canvas, x0, y0, x1, y1)
                self.update_status(f"Линия: построен отрезок: ({x0}, {y0}) -> ({x1}, {y1}).")
                self.start_point = None

    def on_line_motion(self, event):
        if self.start_point is None:
            return
        self.canvas.delete("preview_line")
        x0, y0 = self.start_point
        self.canvas.create_line(x0, y0, event.x, event.y, fill="gray", dash=(2, 2), tags="preview_line")

    def handle_lines_second_order_click(self, event):
        if self.start_point is None:
            self.start_point = (event.x, event.y)
            self.update_status(
                f"{self.selected_curve_type_title}: начальная точка ({event.x}, {event.y}) выбрана. Теперь выберите вторую точку."
            )
        else:
            x0, y0 = self.start_point  # Первая точка (вершина параболы)
            x1, y1 = event.x, event.y  # Вторая точка
            self.canvas.delete(f"preview_{self.selected_curve_type}")

            from lines_second_order import draw_circle, draw_ellipse, draw_parabola, draw_hyperbola

            if self.selected_curve_type == "circle":
                # Вычисляем радиус и рисуем окружность
                r = int(math.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2))
                table = draw_circle(self.canvas, x0, y0, r, debug=self.debug_mode)
                self.update_status(f"Окружность построена. Центр: ({x0}, {y0}), радиус: {r}.")
            elif self.selected_curve_type == "ellipse":
                # Вычисляем полуоси и рисуем эллипс
                rx = abs(x1 - x0)
                ry = abs(y1 - y0)
                table = draw_ellipse(self.canvas, x0, y0, rx, ry, debug=self.debug_mode)
                self.update_status(f"Эллипс построен. Центр: ({x0}, {y0}), полуоси: rx={rx}, ry={ry}.")
            elif self.selected_curve_type == "parabola":
                # Передаём вершину и вторую точку
                table = draw_parabola(self.canvas, x0, y0, x1, y1, debug=self.debug_mode)
                self.update_status(f"Парабола построена. Вершина: ({x0}, {y0}), вторая точка: ({x1}, {y1}).")
            elif self.selected_curve_type == "hyperbola":
                # Определяем направление и рисуем гиперболу
                direction = "horizontal" if abs(x1 - x0) >= abs(y1 - y0) else "vertical"
                table = draw_hyperbola(self.canvas, x0, y0, x1, y1, direction=direction, debug=self.debug_mode)
                self.update_status(
                    f"Гипербола построена. Центр: ({x0}, {y0}), полуоси: a={abs(x1 - x0)}, b={abs(y1 - y0)}."
                )
            else:
                # Ошибка, если тип кривой неизвестен
                self.update_status("Ошибка: неизвестный тип кривой!", is_error=True)
                table = None

            # Отображаем таблицу, если она была сформирована
            if table:
                self.show_debug_table(table)

            # Сбрасываем начальную точку
            self.start_point = None

    # Предварительные обработчики движения для кривых
    def on_circle_motion(self, event):
        if self.start_point is None:
            return
        self.canvas.delete("preview_circle")
        x0, y0 = self.start_point
        r = ((event.x - x0) ** 2 + (event.y - y0) ** 2) ** 0.5
        self.canvas.create_oval(x0 - r, y0 - r, x0 + r, y0 + r,
                                outline="gray", dash=(2, 2), tags="preview_circle")

    def on_ellipse_motion(self, event):
        if self.start_point is None:
            return
        self.canvas.delete("preview_ellipse")
        x0, y0 = self.start_point
        rx = abs(event.x - x0)
        ry = abs(event.y - y0)
        self.canvas.create_oval(x0 - rx, y0 - ry, x0 + rx, y0 + ry,
                                outline="gray", dash=(2, 2), tags="preview_ellipse")

    def on_parabola_motion(self, event):
        if self.start_point is None:
            return
        self.canvas.delete("preview_parabola")
        x0, y0 = self.start_point
        if event.x == x0:
            return
        a = (event.y - y0) / ((event.x - x0) ** 2)
        width = int(self.canvas['width'])
        coords = []
        for x in range(width):
            y = a * ((x - x0) ** 2) + y0
            coords.extend([x, y])
        self.canvas.create_line(coords, fill="gray", dash=(2, 2), tags="preview_parabola")

    def on_hyperbola_motion(self, event):
        """
        Отображение предварительного вида гиперболы с использованием центра и текущей позиции мыши.
        Центр гиперболы — это self.start_point. Текущая позиция мыши определяет направление и размеры полуосей.
        """
        if self.start_point is None:
            return
        self.canvas.delete("preview_hyperbola")

        xc, yc = self.start_point  # Центр гиперболы
        x2, y2 = event.x, event.y  # Текущая позиция мыши (определяет размеры и направление)

        # Вычисляем направление гиперболы
        dx = abs(x2 - xc)
        dy = abs(y2 - yc)
        direction = "horizontal" if dx >= dy else "vertical"

        # Вычисляем параметры a и b
        a = abs(x2 - xc)
        b = abs(y2 - yc)
        T = 2.0
        dt = 0.05
        t = -T

        coords_right = []
        coords_left = []

        while t <= T:
            if direction == "horizontal":
                # Гипербола вдоль оси X
                x_right = xc + a * math.cosh(t)
                y_right = yc + b * math.sinh(t)
                x_left = xc - a * math.cosh(t)
                y_left = yc + b * math.sinh(t)
            else:
                # Гипербола вдоль оси Y
                x_right = xc + b * math.sinh(t)
                y_right = yc + a * math.cosh(t)
                x_left = xc - b * math.sinh(t)
                y_left = yc + a * math.cosh(t)

            coords_right.extend([x_right, y_right])
            coords_left.extend([x_left, y_left])
            t += dt

        self.canvas.create_line(coords_right, fill="gray", dash=(2, 2), tags="preview_hyperbola")
        self.canvas.create_line(coords_left, fill="gray", dash=(2, 2), tags="preview_hyperbola")

    def handle_curve_click(self, event):
        if self.current_event != "Кривая":
            return

        # Берём текущую кривую (последнюю тройку в списке)
        current_curve = self.curve_control_points[-1]
        # Для форм Эмирта и Безье допускаем ровно 4 точки
        if current_curve[2] in ("еmmitt form", "bezier form") and len(current_curve[0]) >= 4:
            self.update_status(f"Для формы {self.selected_curve_form_title} можно задать только 4 точки.",
                               is_error=True)
            return

        r = 5  # Радиус для визуального отображения точки
        pt = (event.x, event.y)
        circle_id = self.canvas.create_oval(pt[0] - r, pt[1] - r, pt[0] + r, pt[1] + r,
                                            fill="red", outline="black")
        # Добавляем точку в список точек текущей кривой (из тройки)
        current_curve[0].append((circle_id, pt))
        self.update_status(f"Добавлена опорная точка: ({pt[0]}, {pt[1]}). Всего точек: {len(current_curve[0])}")
        self.update_curve()

    def update_curve(self):
        import intervals

        # Получаем текущую кривую (последнюю тройку)
        current_curve = self.curve_control_points[-1]
        # Удаляем отрисованные объекты, используя второй элемент тройки (current_curve[1])
        for obj_id in current_curve[1]:
            self.canvas.delete(obj_id)
        # Очищаем список отрисованных объектов для текущей кривой
        current_curve[1].clear()

        old_draw_pixel = intervals.draw_pixel

        # Здесь tracked_draw_pixel сразу добавляет id объектов во второй элемент тройки,
        # а не в отдельный список self.current_curve_ids.
        def tracked_draw_pixel(canvas, x, y, intensity=1, size=1):
            x = int(round(x))
            y = int(round(y))
            intensity = max(0, min(1, intensity))
            shade = int(255 * (1 - intensity))
            color = f"#{shade:02x}{shade:02x}{shade:02x}"
            obj_id = canvas.create_rectangle(x, y, x + size, y + size, outline=color, fill=color)
            current_curve[1].append(obj_id)
            self.curve_control_points[-1][1].append(obj_id)
            return obj_id

        intervals.draw_pixel = tracked_draw_pixel

        # Извлекаем координаты точек (первый элемент тройки)
        points = [pt for _, pt in current_curve[0]]
        # Отрисовываем кривую согласно выбранной форме
        if current_curve[2] == "еmmitt form" and len(points) == 4:
            from curves import draw_hermite
            p1, p4 = points[0], points[1]
            r1 = (points[2][0] - p1[0], points[2][1] - p1[1])
            r4 = (points[3][0] - p4[0], points[3][1] - p4[1])
            draw_hermite(self.canvas, p1, p4, r1, r4, dt=0.01)
        elif current_curve[2] == "bezier form" and len(points) == 4:
            from curves import draw_bezier
            draw_bezier(self.canvas, *points, dt=0.01)
        elif current_curve[2] == "b-spline" and len(points) >= 4:
            from curves import draw_bspline
            draw_bspline(self.canvas, points, dt=0.01)

        intervals.draw_pixel = old_draw_pixel
        self.update_status(f"{self.selected_curve_form_title}: кривая обновлена.")

    import math

    def find_selected_control_point(self, event, tolerance=6):
        """
        Функция перебирает все кривые и их опорные точки.
        Если расстояние между event.(x,y) и точкой меньше tolerance,
        возвращает кортеж (curve_index, point_index):
            - curve_index — индекс кривой в self.curve_control_points,
            - point_index — индекс опорной точки внутри списка точки этой кривой.
        Если подходящая точка не найдена, возвращает None.
        """
        for curve_index, curve in enumerate(self.curve_control_points):
            # curve[0] — список опорных точек данной кривой
            for point_index, (cp_id, pt) in enumerate(curve[0]):
                if math.hypot(event.x - pt[0], event.y - pt[1]) <= tolerance:
                    return (curve_index, point_index)
        return None

    def on_control_point_motion(self, event):
        if not self.debug_mode or self.dragging_index is None:
            return
        r = 5
        # self.dragging_index теперь кортеж (curve, i)
        curve, i = self.dragging_index
        cp_id, _ = curve[0][i]  # curve[0] – список точек
        self.canvas.coords(cp_id, event.x - r, event.y - r, event.x + r, event.y + r)
        # Обновляем координаты для соответствующей точки в списке точек текущей кривой
        curve[0][i] = (cp_id, (event.x, event.y))
        self.update_curve()

    def on_control_point_release(self, event):
        self.dragging_index = None
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")

    def show_debug_table(self, table):
        """
        Открывает новое окно с отладочной таблицей.
        Если запись таблицы содержит 4 элемента, выводятся поля:
             Итерация, x, y, Отобр. координаты.
        Если запись содержит 6 элементов, выводятся:
             Итерация, x, y, e, e′, Отобр. координаты.
        Если запись содержит 9 элементов (для кривых), выводятся поля:
             Шаг | di | δ | δ* | Пиксель | x | y | di+1 | Plot (x, y)
        """
        import tkinter as tk
        window = tk.Toplevel(self.root)
        window.title(f"Отладочная таблица")
        window.geometry("1000x400")

        text = tk.Text(window, font=("Courier", 10))
        text.pack(fill=tk.BOTH, expand=True)

        if not table:
            text.insert(tk.END, "Нет данных для отображения")
            return

        cols = len(table[0])
        if cols == 4:
            header = f"{'Итерация':>9} | {'x':>10} | {'y':>10} | {'Отобр. координаты':>20}\n"
            separator = "-" * 60 + "\n"
            text.insert(tk.END, header)
            text.insert(tk.END, separator)
            for row in table:
                i, x, y, disp = row
                text.insert(tk.END, f"{i:9d} | {x:10.2f} | {y:10.2f} | ({disp[0]:3d}, {disp[1]:3d})\n")
        elif cols == 6:
            header = f"{'Итерация':>9} | {'x':>10} | {'y':>10} | {'e':>10} | {'e\'':>10} | {'Отобр. координаты':>20}\n"
            separator = "-" * 90 + "\n"
            text.insert(tk.END, header)
            text.insert(tk.END, separator)
            for row in table:
                i, x, y, e, e_prime, disp = row
                text.insert(tk.END,
                            f"{i:9d} | {x:10.2f} | {y:10.2f} | {e:10.2f} | {e_prime:10.2f} | ({disp[0]:3d}, {disp[1]:3d})\n")
        elif cols == 9:
            header = f"{'Шаг':>5} | {'di':>8} | {'δ':>8} | {'δ*':>8} | {'Пиксель':>10} | {'x':>10} | {'y':>10} | {'di+1':>8} | {'Plot (x,y)':>15}\n"
            separator = "-" * 110 + "\n"
            text.insert(tk.END, header)
            text.insert(tk.END, separator)
            for row in table:
                # Каждая запись должна включать 9 элементов:
                # (Шаг, di, δ, δ*, Пиксель, x, y, di+1, Plot (x,y))
                step, di, delta, delta_star, pixel, x_val, y_val, di_next, plot = row
                text.insert(tk.END,
                            f"{step:5d} | {di:8.2f} | {delta:8.2f} | {delta_star:8.2f} | ({pixel[0]:3d}, {pixel[1]:3d}) | {x_val:10.2f} | {y_val:10.2f} | {di_next:8.2f} | ({plot[0]:3d}, {plot[1]:3d})\n")
        else:
            text.insert(tk.END, "Неподдерживаемый формат таблицы\n")

        text.config(state=tk.DISABLED)

    def clear_canvas(self):
        self.canvas.delete("all")
        self.curve_control_points = []
        self.select_cursor_mode()
        if self.debug_mode:
            self.draw_grid()
        self.update_status("Экран очищен")

if __name__ == "__main__":
    app = GraphicEditorApp()
    app.run()
