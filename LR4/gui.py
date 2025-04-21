import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from transformation import (
    create_translation_matrix,
    create_scaling_matrix,
    create_rotation_matrix,
    create_perspective_projection_matrix
)
from file_manager import read_object

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("3D Transformations App")
        self.geometry("1000x800")
        self.current_tool = "не выбран"  # Начальное значение текущего инструмента
        self.brush_color = "black"

        self.active_object = None  # Активный 3D-объект, по умолчанию его нет
        self.transform_matrix = np.eye(4)  # Единичная матрица преобразований (4x4)
        self.persp_distance = 500  # Расстояние до экрана для перспективной проекции

        # Новый атрибут для переключения режима отображения:
        self.use_perspective = False

        self.create_menu()
        self.create_toolbar()
        self.create_canvas()
        self.create_status_bar()
        self.draw_axes_indicator()

        self.bind("<Key>", self.on_key)

    def create_menu(self):
        menubar = tk.Menu(self)

        # Меню "Файл"
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Открыть", command=self.open_file)
        file_menu.add_command(label="Очистить", command=self.clear_workspace)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.quit)
        menubar.add_cascade(label="Файл", menu=file_menu)

        #Меню "Кисть"
        brush_menu = tk.Menu(menubar, tearoff=0)
        brush_menu.add_command(label="Красный", command=lambda: self.change_brush_color("red"))
        brush_menu.add_command(label="Зеленый", command=lambda: self.change_brush_color("green"))
        brush_menu.add_command(label="Синий", command=lambda: self.change_brush_color("blue"))
        brush_menu.add_command(label="Желтый", command=lambda: self.change_brush_color("yellow"))
        brush_menu.add_command(label="Оранжевый", command=lambda: self.change_brush_color("orange"))
        brush_menu.add_command(label="Фиолетовый", command=lambda: self.change_brush_color("purple"))
        brush_menu.add_command(label="Черный", command=lambda: self.change_brush_color("black"))
        brush_menu.add_command(label="Белый", command=lambda: self.change_brush_color("white"))
        brush_menu.add_command(label="Розовый", command=lambda: self.change_brush_color("pink"))
        brush_menu.add_command(label="Коричневый", command=lambda: self.change_brush_color("brown"))

        menubar.add_cascade(label="Кисть", menu=brush_menu)

        # Меню "Помощь"
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Документация", command=self.show_documentation)
        menubar.add_cascade(label="Помощь", menu=help_menu)

        self.config(menu=menubar)

    def create_toolbar(self):
        # Панель инструментов располагается сверху
        toolbar = tk.Frame(self, bd=1, relief=tk.RAISED)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        # Кнопки для выбора инструментов/режимов (выравниваются слева)
        btn_cursor = tk.Button(toolbar, text="Курсор", command=lambda: self.select_tool("Курсор"))
        btn_cube = tk.Button(toolbar, text="Куб", command=lambda: self.select_tool("Куб"))
        btn_sphere = tk.Button(toolbar, text="Сфера", command=lambda: self.select_tool("Сфера"))
        btn_cylinder = tk.Button(toolbar, text="Цилиндр", command=lambda: self.select_tool("Цилиндр"))
        btn_transform = tk.Button(toolbar, text="3D-Преобразование", command=lambda: self.select_tool("Преобразование"))

        btn_cursor.pack(side=tk.LEFT, padx=2, pady=2)
        btn_cube.pack(side=tk.LEFT, padx=2, pady=2)
        btn_sphere.pack(side=tk.LEFT, padx=2, pady=2)
        btn_cylinder.pack(side=tk.LEFT, padx=2, pady=2)
        btn_transform.pack(side=tk.LEFT, padx=2, pady=2)

        # Чекбокс для отображения сетки в правом верхнем углу панели инструментов
        self.show_grid_var = tk.BooleanVar(value=False)
        grid_checkbox = tk.Checkbutton(
            toolbar,
            text="Показывать сетку",
            variable=self.show_grid_var,
            command=self.draw_grid
        )
        grid_checkbox.pack(side=tk.RIGHT, padx=2, pady=2)

    def create_status_bar(self):
        """Создает статусную панель в нижней части окна, где выводится текущий инструмент."""
        status_frame = tk.Frame(self, bd=1, relief=tk.SUNKEN)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_label = tk.Label(status_frame, text="Текущий инструмент: " + self.current_tool, anchor="w")
        self.status_label.pack(fill=tk.X, padx=5, pady=2)

    def center_window(self, window, width, height):
        """Центрирует окно 'window' относительно главного окна."""
        self.update_idletasks()  # Обновляем геометрию главного окна
        parent_x = self.winfo_x()
        parent_y = self.winfo_y()
        parent_width = self.winfo_width()
        parent_height = self.winfo_height()

        pos_x = parent_x + (parent_width - width) // 2
        pos_y = parent_y + (parent_height - height) // 2
        window.geometry(f"{width}x{height}+{pos_x}+{pos_y}")

    def create_canvas(self):
        # Создаём область для отображения 3D-сцены и отрисовки сетки
        self.canvas = tk.Canvas(self, bg="gray")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        # Привязываем событие изменения размера для обновления сетки
        self.canvas.bind("<Configure>", self.draw_grid)

    def select_tool(self, tool_name):
        """
        Обновляет текущий инструмент и статусную строку.
        Если выбран один из инструментов для построения фигур ("Куб", "Сфера", "Цилиндр"),
        фигура будет построена в центре.
        Если выбран "Преобразование" (или "3D-Преобразование"), открывается панель преобразований.
        """
        valid_tools = {"Куб", "Сфера", "Цилиндр"}
        self.current_tool = tool_name
        self.status_label.config(text="Текущий инструмент: " + self.current_tool)

        self.canvas.update_idletasks()
        cx = self.canvas.winfo_width() / 2
        cy = self.canvas.winfo_height() / 2

        if tool_name in valid_tools:
            if tool_name == "Куб":
                self.cube_center = (cx, cy)
                self.status_label.config(text=f"Инструмент: Куб. Фигура будет построена в центре: ({cx:.0f}, {cy:.0f})")
                self.open_cube_dialog()
            elif tool_name == "Сфера":
                self.sphere_center = (cx, cy)
                self.status_label.config(
                    text=f"Инструмент: Сфера. Фигура будет построена в центре: ({cx:.0f}, {cy:.0f})")
                self.open_sphere_dialog()
            elif tool_name == "Цилиндр":
                self.cylinder_center = (cx, cy)
                self.status_label.config(
                    text=f"Инструмент: Цилиндр. Фигура будет построена в центре: ({cx:.0f}, {cy:.0f})")
                self.open_cylinder_dialog()
        elif tool_name in {"Преобразование", "3D-Преобразование"}:
            self.open_transformation_menu()
        else:
            self.canvas.unbind("<Button-1>")

    def open_transformation_menu(self):
        """
        Создает окно с панелью преобразований, которое появляется справа от главного окна и имеет фиксированный размер по высоте.
        В панели представлены секции для: перемещения, поворота, масштабирования, перспективы и отображения.
        """
        trans_window = tk.Toplevel(self)
        trans_window.title("Параметры преобразований")
        trans_window.resizable(False, False)

        # Определяем позицию правее главного окна, с такой же высотой
        self.update_idletasks()
        parent_x = self.winfo_x()
        parent_y = self.winfo_y()
        parent_width = self.winfo_width()
        parent_height = self.winfo_height()
        fixed_width = 300
        fixed_height = parent_height
        pos_x = parent_x + parent_width  # окно справа
        pos_y = parent_y
        trans_window.geometry(f"{fixed_width}x{fixed_height}+{pos_x}+{pos_y}")

        # --- Секция перемещения ---
        frame_translate = tk.LabelFrame(trans_window, text="Перемещение (dx, dy, dz)")
        frame_translate.pack(fill=tk.X, padx=10, pady=5)
        entry_dx = tk.Entry(frame_translate, width=5)
        entry_dy = tk.Entry(frame_translate, width=5)
        entry_dz = tk.Entry(frame_translate, width=5)
        entry_dx.insert(0, "0")
        entry_dy.insert(0, "0")
        entry_dz.insert(0, "0")
        entry_dx.pack(side=tk.LEFT, padx=5, pady=5)
        entry_dy.pack(side=tk.LEFT, padx=5, pady=5)
        entry_dz.pack(side=tk.LEFT, padx=5, pady=5)
        btn_apply_translate = tk.Button(frame_translate, text="Применить",
                                        command=lambda: self.apply_translation(entry_dx.get(), entry_dy.get(),
                                                                               entry_dz.get()))
        btn_apply_translate.pack(side=tk.LEFT, padx=5, pady=5)

        # --- Секция поворота ---
        frame_rotate = tk.LabelFrame(trans_window, text="Поворот (Rx, Ry, Rz) (°)")
        frame_rotate.pack(fill=tk.X, padx=10, pady=5)
        entry_rx = tk.Entry(frame_rotate, width=5)
        entry_ry = tk.Entry(frame_rotate, width=5)
        entry_rz = tk.Entry(frame_rotate, width=5)
        entry_rx.insert(0, "0")
        entry_ry.insert(0, "0")
        entry_rz.insert(0, "0")
        entry_rx.pack(side=tk.LEFT, padx=5, pady=5)
        entry_ry.pack(side=tk.LEFT, padx=5, pady=5)
        entry_rz.pack(side=tk.LEFT, padx=5, pady=5)
        btn_apply_rotate = tk.Button(frame_rotate, text="Применить",
                                     command=lambda: self.apply_rotation(entry_rx.get(), entry_ry.get(),
                                                                         entry_rz.get()))
        btn_apply_rotate.pack(side=tk.LEFT, padx=5, pady=5)

        # --- Секция масштабирования ---
        frame_scale = tk.LabelFrame(trans_window, text="Масштабирование (Sx, Sy, Sz)")
        frame_scale.pack(fill=tk.X, padx=10, pady=5)
        entry_sx = tk.Entry(frame_scale, width=5)
        entry_sy = tk.Entry(frame_scale, width=5)
        entry_sz = tk.Entry(frame_scale, width=5)
        entry_sx.insert(0, "1")
        entry_sy.insert(0, "1")
        entry_sz.insert(0, "1")
        entry_sx.pack(side=tk.LEFT, padx=5, pady=5)
        entry_sy.pack(side=tk.LEFT, padx=5, pady=5)
        entry_sz.pack(side=tk.LEFT, padx=5, pady=5)
        btn_apply_scale = tk.Button(frame_scale, text="Применить",
                                    command=lambda: self.apply_scaling(entry_sx.get(), entry_sy.get(), entry_sz.get()))
        btn_apply_scale.pack(side=tk.LEFT, padx=5, pady=5)

        # --- Секция перспективы ---
        frame_persp = tk.LabelFrame(trans_window, text="Перспектива")
        frame_persp.pack(fill=tk.X, padx=10, pady=5)
        # Создаём переменную для чекбокса перспективы. Значение по умолчанию берём из self.use_perspective.
        self.perspective_var = tk.BooleanVar(value=self.use_perspective)
        check_persp = tk.Checkbutton(frame_persp,
                                     text="Перспектива",
                                     variable=self.perspective_var,
                                     command=self.toggle_perspective)
        # --- Секция видов объекта ---
        frame_view = tk.LabelFrame(trans_window, text="Виды объекта")
        frame_view.pack(fill=tk.X, padx=10, pady=5)

        # Создаем строковую переменную для выбора вида.
        self.view_radio_var = tk.StringVar(value="Передний")
        # Виды объекта: Передний, Задний, Слева, Справа, Сверху, Снизу.
        views = ["Передний", "Задний", "Слева", "Справа", "Сверху", "Снизу"]
        for view in views:
            rb = tk.Radiobutton(
                frame_view,
                text=view,
                variable=self.view_radio_var,
                value=view,
                command=lambda: self.apply_view(self.view_radio_var.get())
            )
            rb.pack(anchor="w", padx=5, pady=2)  # Упаковка в столбик, выравнивание по левому краю

        check_persp.pack(side=tk.LEFT, padx=5, pady=5)

    def open_cube_dialog(self):
        """Открывает диалоговое окно для ввода параметра 'Длина стороны' куба и задаёт его в центре главного окна."""
        self.cube_center = (self.canvas.winfo_width() / 2, self.canvas.winfo_height() / 2)
        dialog = tk.Toplevel(self)
        dialog.title("Параметры куба")
        self.center_window(dialog, width=250, height=150)  # Центрируем диалоговое окно

        label = tk.Label(dialog, text="Длина стороны:")
        label.pack(padx=10, pady=10)

        side_entry = tk.Entry(dialog)
        side_entry.insert(0, "200")  # Значение по умолчанию
        side_entry.pack(padx=10, pady=5)

        def build_cube():
            try:
                side = float(side_entry.get())
            except ValueError:
                tk.messagebox.showerror("Ошибка", "Введите корректное число для стороны")
                return
            self.draw_cube_at(self.cube_center, side)
            dialog.destroy()

        build_btn = tk.Button(dialog, text="Построить", command=build_cube)
        build_btn.pack(padx=10, pady=10)

    def draw_cube_at(self, center, side):
        """
        Создает куб со стороной side, используя функцию create_cube из модуля objects_3d.
        Сохраняет исходные вершины и грани в self.active_object, задаёт начальное смещение,
        и вызывает redraw_object для отрисовки объекта с учетом накопленной матрицы преобразований.
        """
        from objects_3d import create_cube
        # Предполагается, что create_cube возвращает куб, центрированный в (0,0,0)
        vertices, faces = create_cube(side=side)
        import numpy as np
        self.active_object = {"vertices": np.array(vertices), "faces": faces}

        # Вычисляем центр Canvas
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        cx = canvas_width / 2
        cy = canvas_height / 2

        # Вычисляем смещение, чтобы переместить объект из его локальных координат (0,0,0)
        # туда, где выбран пользовательский центр (center)
        dx = center[0] - cx
        dy = center[1] - cy

        # Задаем начальную матрицу преобразований через перевод на (dx, dy, 0)
        from transformation import create_translation_matrix
        T0 = create_translation_matrix(dx, dy, 0)
        self.transform_matrix = T0

        # Перерисовываем объект с учетом накопленной матрицы преобразований
        self.redraw_object()
        self.status_label.config(
            text="Построен куб в точке ({}, {}) с длиной стороны {}".format(center[0], center[1], side)
        )

    def open_sphere_dialog(self):
        """
        Открывает диалоговое окно для ввода параметра "Радиус сферы".
        Окно центрируется относительно главного окна.
        После нажатия кнопки "Построить" вызывается метод draw_sphere_at.
        """
        self.sphere_center = (self.canvas.winfo_width() / 2, self.canvas.winfo_height() / 2)

        dialog = tk.Toplevel(self)
        dialog.title("Параметры сферы")
        self.center_window(dialog, 250, 150)  # Центрируем диалоговое окно (ширина=250, высота=150)

        label = tk.Label(dialog, text="Радиус сферы:")
        label.pack(padx=10, pady=10)

        radius_entry = tk.Entry(dialog)
        radius_entry.insert(0, "100")  # Значение по умолчанию
        radius_entry.pack(padx=10, pady=5)

        def build_sphere():
            try:
                radius = float(radius_entry.get())
            except ValueError:
                tk.messagebox.showerror("Ошибка", "Введите корректное число для радиуса")
                return
            self.draw_sphere_at(self.sphere_center, radius)
            dialog.destroy()

        build_btn = tk.Button(dialog, text="Построить", command=build_sphere)
        build_btn.pack(padx=10, pady=10)

    def draw_sphere_at(self, center, radius):
        """
        Создает сферу с заданным радиусом, используя функцию create_sphere из модуля objects_3d.
        Сохраняет исходные вершины и грани в self.active_object, задаёт начальное смещение,
        и вызывает redraw_object для отрисовки объекта с учетом накопленной матрицы преобразований.
        """
        from objects_3d import create_sphere
        # Используем, например, 20 шагов по широте и долготе для более сглаженной сферы
        vertices, faces = create_sphere(radius=radius, lat_steps=20, lon_steps=20)
        import numpy as np
        self.active_object = {"vertices": np.array(vertices), "faces": faces}

        # Вычисляем центр Canvas
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        cx = canvas_width / 2
        cy = canvas_height / 2

        # Смещение по осям, чтобы центр объекта (0,0,0) оказался в выбранной точке
        dx = center[0] - cx
        dy = center[1] - cy

        from transformation import create_translation_matrix
        T0 = create_translation_matrix(dx, dy, 0)
        self.transform_matrix = T0

        self.redraw_object()
        self.status_label.config(
            text="Построена сфера в точке ({}, {}) с радиусом {}".format(center[0], center[1], radius)
        )

    def open_cylinder_dialog(self):
        """
        Открывает диалоговое окно для ввода параметров цилиндра: "Радиус" и "Высота".
        Окно центрируется относительно главного окна.
        После нажатия кнопки "Построить" вызывается метод draw_cylinder_at.
        """
        self.cylinder_center = (self.canvas.winfo_width() / 2, self.canvas.winfo_height() / 2)

        dialog = tk.Toplevel(self)
        dialog.title("Параметры цилиндра")
        self.center_window(dialog, 250, 200)  # Центрируем диалог (ширина=250, высота=200)

        label_radius = tk.Label(dialog, text="Радиус:")
        label_radius.pack(padx=10, pady=5)

        radius_entry = tk.Entry(dialog)
        radius_entry.insert(0, "100")  # Значение по умолчанию
        radius_entry.pack(padx=10, pady=5)

        label_height = tk.Label(dialog, text="Высота:")
        label_height.pack(padx=10, pady=5)

        height_entry = tk.Entry(dialog)
        height_entry.insert(0, "200")  # Значение по умолчанию
        height_entry.pack(padx=10, pady=5)

        def build_cylinder():
            try:
                radius = float(radius_entry.get())
                height = float(height_entry.get())
            except ValueError:
                tk.messagebox.showerror("Ошибка", "Введите корректные числовые значения для радиуса и высоты")
                return
            self.draw_cylinder_at(self.cylinder_center, radius, height)
            dialog.destroy()

        build_btn = tk.Button(dialog, text="Построить", command=build_cylinder)
        build_btn.pack(padx=10, pady=10)

    def draw_cylinder_at(self, center, radius, height):
        """
        Создает цилиндр с заданными радиусом и высотой, используя функцию create_cylinder из модуля objects_3d.
        Сохраняет исходные данные объекта в self.active_object, задаёт начальное смещение,
        и вызывает redraw_object для отрисовки объекта с учетом накопленной матрицы преобразований.
        """
        from objects_3d import create_cylinder
        segments = 20  # число сегментов для аппроксимации окружности
        vertices, faces = create_cylinder(radius=radius, height=height, segments=segments)
        import numpy as np
        self.active_object = {"vertices": np.array(vertices), "faces": faces}

        # Вычисляем центр Canvas
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        cx = canvas_width / 2
        cy = canvas_height / 2

        # Вычисляем смещение: перемещаем объект из его локальной системы координат (центр в (0,0,0))
        # в выбранную точку
        dx = center[0] - cx
        dy = center[1] - cy

        from transformation import create_translation_matrix
        T0 = create_translation_matrix(dx, dy, 0)
        self.transform_matrix = T0

        self.redraw_object()
        self.status_label.config(
            text="Построен цилиндр в точке ({:.0f}, {:.0f}) с радиусом {} и высотой {}".format(center[0], center[1],
                                                                                               radius, height)
        )

    def draw_grid(self, event=None):
        self.canvas.delete("grid_line")
        if not self.show_grid_var.get():
            return
        # Вызываем отрисовку объёмной сетки, диапазоны вычисляются автоматически
        self.draw_volume_grid(spacing=50, num_layers=2)

    def draw_volume_grid(self, event=None, spacing=50, num_layers=5, plane_range=None):
        """
        Отрисовывает объемную сетку, охватывающую всё рабочее пространство (Canvas).

        Сетка состоит из нескольких слоев вдоль оси Z. Для каждого слоя автоматически вычисляется
        диапазон по осям X и Y на основе размеров Canvas. Узлы между слоями соединяются линиями,
        создавая ощущение объёма. Проекция узлов зависит от выбранного режима (перспективный или ортографический).

        Аргументы:
          event      - объект события (не обязателен)
          spacing    - шаг между узлами в мировых координатах (по умолчанию 50)
          num_layers - число слоев вдоль оси Z (по умолчанию 5)
          plane_range- если не передано (None), диапазон по осям X и Y вычисляется автоматически
        """
        # Удаляем предыдущие линии сетки
        self.canvas.delete("grid_line")

        # Получаем размеры Canvas и вычисляем центр
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        cx = width / 2
        cy = height / 2
        d = self.persp_distance  # дистанция до экрана

        # Если plane_range не передан, используем половину ширины и половину высоты канвы,
        # чтобы диапазон по оси X был от -cx до cx, а по оси Y от -cy до cy.
        if plane_range is None:
            extend_factor = 1.5
            plane_range_x = int(cx * extend_factor)
            plane_range_y = int(cy * extend_factor)
        else:
            plane_range_x = plane_range
            plane_range_y = plane_range

        layers = []
        # Формируем слои вдоль оси Z, каждый слой представляет "пластину" сетки
        for layer in range(num_layers):
            z_val = layer * spacing  # уровень по оси Z для данного слоя
            layer_dict = {}
            # Перебираем узлы по оси X и Y на полном экране
            for x in range(-plane_range_x, plane_range_x + 1, spacing):
                for y in range(-plane_range_y, plane_range_y + 1, spacing):
                    # Если включен перспективный режим, вычисляем коэффициент масштабирования
                    if self.use_perspective:
                        factor = d / (d + z_val) if (d + z_val) != 0 else 1
                    else:
                        factor = 1
                    # Преобразуем мировые координаты (x, y) с учетом перспективы
                    X = x * factor + cx
                    Y = -y * factor + cy
                    layer_dict[(x, y)] = (X, Y)
            layers.append(layer_dict)

        # Отрисовка линий внутри каждого слоя
        for layer_dict in layers:
            # Горизонтальные линии: группируем узлы по значению y
            rows = {}
            for (x, y), scr in layer_dict.items():
                rows.setdefault(y, []).append((x, scr))
            for y_val, row in rows.items():
                row_sorted = sorted(row, key=lambda item: item[0])
                coords = []
                for _, scr in row_sorted:
                    coords.extend(scr)
                self.canvas.create_line(coords, fill="lightgray", tags="grid_line")

            # Вертикальные линии: группируем узлы по значению x
            cols = {}
            for (x, y), scr in layer_dict.items():
                cols.setdefault(x, []).append((y, scr))
            for x_val, col in cols.items():
                col_sorted = sorted(col, key=lambda item: item[0])
                coords = []
                for _, scr in col_sorted:
                    coords.extend(scr)
                self.canvas.create_line(coords, fill="lightgray", tags="grid_line")

        # Соединяем узлы между слоями для создания объёмного эффекта
        if len(layers) >= 2:
            base_keys = layers[0].keys()
            for key in base_keys:
                coords = []
                for layer_dict in layers:
                    if key in layer_dict:
                        coords.extend(layer_dict[key])
                self.canvas.create_line(coords, fill="lightgray", tags="grid_line")

    from file_manager import read_object  # Импортируем функцию из отдельного файла

    def open_file(self):
        # Открытие текстового файла с координатами 3D объекта
        filename = filedialog.askopenfilename(
            title="Открыть файл с 3D объектом",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if filename:
            try:
                object_data = read_object(filename)
                # Преобразуем список вершин в numpy-массив, если требуется.
                import numpy as np
                self.active_object = {
                    "vertices": np.array(object_data["vertices"]),
                    "faces": object_data["faces"]
                }
                self.redraw_object()
                self.status_label.config(text=f"Загружен 3D объект из файла: {filename}")
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

    def show_documentation(self):
        """
        Функция открывает файл documentation.txt из корневой директории и отображает его содержимое
        в новом окне с прокручиваемым текстом.
        """
        try:
            with open("documentation.txt", "r", encoding="utf-8") as f:
                doc_content = f.read()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть documentation.txt:\n{e}")
            return

        # Создание нового окна для отображения документации
        doc_window = tk.Toplevel(self)
        doc_window.title("Документация")
        doc_window.geometry("1000x800")

        # Создание текстового виджета с прокруткой для отображения содержимого
        text = tk.Text(doc_window, wrap=tk.WORD, font=("Arial", 12))
        text.insert(tk.END, doc_content)
        text.config(state="disabled")  # делаем виджет только для чтения
        scrollbar = tk.Scrollbar(doc_window, command=text.yview)
        text.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def redraw_object(self):
        """
        Пересчитывает координаты вершин из self.active_object, применяя
        накопленную матрицу преобразований (self.transform_matrix), выполняет
        простую (перспективную или ортографическую) проекцию и отрисовывает 3D‑объект на Canvas.
        """
        import numpy as np
        if self.active_object is None:
            return

        # Очищаем предыдущую отрисовку
        self.canvas.delete("object")

        # Центр канвы и параметр перспективы
        cx = self.canvas.winfo_width() / 2
        cy = self.canvas.winfo_height() / 2
        d = self.persp_distance

        transformed_vertices = []
        for vertex in self.active_object["vertices"]:
            v = np.array([vertex[0], vertex[1], vertex[2], 1])
            vt = self.transform_matrix @ v
            transformed_vertices.append(vt)

        for face in self.active_object["faces"]:
            points = []
            for idx in face:
                vt = transformed_vertices[idx]
                x, y, z, _ = vt
                # Если режим перспективный, применяем d/(d+z). Если режим ортографический – масштаб не меняется.
                if self.use_perspective:
                    factor = d / (d + z) if (d + z) != 0 else 1
                else:
                    factor = 1
                X = x * factor + cx
                Y = -y * factor + cy  # инвертируем Y для корректного отображения
                points.extend([X, Y])
            self.canvas.create_polygon(points, outline=self.brush_color, fill="", width=2, tags="object")

    def apply_translation(self, dx_str, dy_str, dz_str):
        """Обрабатывает ввод для перемещения по осям x, y, z.
        Считывает значения, создаёт матрицу перемещения и обновляет текущую матрицу преобразований.
        """
        try:
            dx = float(dx_str)
            dy = float(dy_str)
            dz = float(dz_str)
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные числовые значения для перемещения")
            return
        T = create_translation_matrix(dx, dy, dz)
        self.transform_matrix = T @ self.transform_matrix
        self.redraw_object()
        self.status_label.config(text=f"Перемещение: dx={dx}, dy={dy}, dz={dz}")

    def apply_rotation(self, rx_str, ry_str, rz_str):
        """Обрабатывает ввод для поворота вокруг осей x, y, z (в градусах).
        Считывает значения, создает составную матрицу поворота и обновляет текущую матрицу преобразований.
        """
        try:
            rx = float(rx_str)
            ry = float(ry_str)
            rz = float(rz_str)
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные числовые значения для поворота")
            return
        R = create_rotation_matrix(rx, ry, rz)  # порядок: R = Rz * Ry * Rx
        self.transform_matrix = R @ self.transform_matrix
        self.redraw_object()
        self.status_label.config(text=f"Поворот: Rx={rx}°, Ry={ry}°, Rz={rz}°")

    def apply_scaling(self, sx_str, sy_str, sz_str):
        """Обрабатывает ввод для масштабирования по осям x, y и z.
        Считывает коэффициенты масштабирования, создает матрицу масштабирования и обновляет текущую матрицу преобразований.
        """
        try:
            sx = float(sx_str)
            sy = float(sy_str)
            sz = float(sz_str)
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные числовые значения для масштабирования")
            return
        S = create_scaling_matrix(sx, sy, sz)
        self.transform_matrix = S @ self.transform_matrix
        self.redraw_object()
        self.status_label.config(text=f"Масштабирование: Sx={sx}, Sy={sy}, Sz={sz}")

    def toggle_perspective(self):
        """
        Переключает режим отображения: если был перспективный, становится ортографическим, и наоборот.
        После переключения обновляются статусная строка, отрисовка объекта и сетки.
        """
        self.use_perspective = not self.use_perspective
        mode = "Перспективный" if self.use_perspective else "Ортографический"
        self.status_label.config(text=f"Режим отображения: {mode}")
        self.redraw_object()
        self.draw_grid()

    def apply_view(self, view_name):
        """
        Применяет выбранный вид объекта путём установки фиксированного поворота.
        Для каждого вида задаются следующие углы (в градусах):
          Передний — (0, 0, 0)
          Задний  — (0, 180, 0)
          Слева   — (0, 90, 0)
          Справа  — (0, -90, 0)
          Сверху  — (90, 0, 0)
          Снизу   — (-90, 0, 0)
        После установки поворота обновляется матрица преобразований, объект перерисовывается и
        в статусной строке отображается текущий вид.
        """
        # Словарь, сопоставляющий название вида с углами поворота.
        views = {
            "Передний": (0, 0, 0),
            "Задний": (0, 180, 0),
            "Слева": (0, 90, 0),
            "Справа": (0, -90, 0),
            "Сверху": (90, 0, 0),
            "Снизу": (-90, 0, 0)
        }
        angles = views.get(view_name, (0, 0, 0))
        from transformation import create_rotation_matrix
        R = create_rotation_matrix(*angles)
        self.transform_matrix = R  # Здесь заменяем накопленную матрицу на новый поворот.
        self.redraw_object()
        self.status_label.config(text=f"Вид объекта: {view_name}")

    def on_key(self, event):
        if event.keysym == "Tab":
            self.open_transformation_menu()
        elif event.keysym.lower() == "c":
            self.clear_workspace()
        elif event.keysym == "1":
            self.open_cube_dialog()
        elif event.keysym == "2":
            self.open_sphere_dialog()
        elif event.keysym == "3":
            self.open_cylinder_dialog()
        elif event.keysym.lower() == "d":
            self.show_documentation()
        elif event.keysym == "Escape":
            self.quit()
        elif event.keysym.lower() == "o":
            self.open_file()
        elif event.keysym.lower() == "g":
            self.show_grid_var.set(not self.show_grid_var.get())
            self.draw_grid()
        elif event.keysym.lower() == "p":
            self.use_perspective = not self.use_perspective
            mode = "Перспективный" if self.use_perspective else "Ортографический"
            self.status_label.config(text=f"Режим отображения: {mode}")
            self.redraw_object()
            self.draw_grid()

    def draw_axes_indicator(self):
        """
        Отрисовывает в левом верхнем углу Canvas индикатор направлений осей:
          X – красный (вправо),
          Y – зелёный (вверх),
          Z – синий (диагонально, имитируя ось, выходящую из плоскости).
        Функция удаляет предыдущий индикатор (с тегом "axes_indicator")
        и рисует новые стрелки с метками.
        """
        # Удаляем предыдущий индикатор, если он есть
        self.canvas.delete("axes_indicator")

        # Отступ от верхнего левого угла
        margin_x = 20
        margin_y = 80
        # Длина стрелок
        length = 40

        # Опорная точка для начала осей
        x0, y0 = margin_x, margin_y

        # Ось X: красная, направлена вправо
        self.canvas.create_line(x0, y0, x0 + length, y0, fill="red", width=2,
                                arrow=tk.LAST, tags="axes_indicator")
        self.canvas.create_text(x0 + length + 10, y0, text="X", fill="red",
                                font=("Arial", 10), tags="axes_indicator")

        # Ось Y: зелёная, направлена вверх (в Canvas меньшее значение y – выше)
        self.canvas.create_line(x0, y0, x0, y0 - length, fill="green", width=2,
                                arrow=tk.LAST, tags="axes_indicator")
        self.canvas.create_text(x0, y0 - length - 10, text="Y", fill="green",
                                font=("Arial", 10), tags="axes_indicator")

        # Ось Z: синяя, диагональная. Здесь выбрано направление вниз-вправо,
        # что часто используется для иллюстрации оси, выходящей из экрана.
        self.canvas.create_line(x0, y0, x0 + length, y0 + length, fill="blue", width=2,
                                arrow=tk.LAST, tags="axes_indicator")
        self.canvas.create_text(x0 + length + 10, y0 + length, text="Z", fill="blue",
                                font=("Arial", 10), tags="axes_indicator")

    def change_brush_color(self, color):
        self.brush_color = color

    def clear_workspace(self):
        """
        Очищает канву, удаляя все отрисованные элементы.
        После очистки, если чекбокс отображения сетки включён, сетка перерисовывается.
        Также обновляется статусная строка.
        """
        self.canvas.delete("all")
        self.status_label.config(text="Рабочее пространство очищено")
        self.draw_grid()  # Если сетка включена, она будет перерисована после очистки
        self.draw_axes_indicator()


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
