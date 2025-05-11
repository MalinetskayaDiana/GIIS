import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from polygon import Polygon, convex_hull_graham, convex_hull_jarvis, debug_steps, add_debug
import fill_polygon  # импортируем модуль с реализацией алгоритмов заливки

class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ПОСТРОЕНИЕ ПОЛИГОНОВ И ИХ ЗАЛИВКА")
        self.geometry("1200x800")

        # Настроим переменные состояния
        self.mode = tk.StringVar(value="cursor")  # режим: "cursor" или "draw_polygon"
        self.current_polygon = None  # экземпляр Polygon
        self.debug_mode = tk.BooleanVar(value=False)
        self.hull_method = tk.StringVar(value="Грэмма")
        # Обновлённый список алгоритмов заливки:
        self.fill_method = tk.StringVar(value="Развертка (упорядоченный список ребер)")
        self.status_var = tk.StringVar(value="Выберите режим работы из панели инструментов.")

        # Создаем интерфейс
        self.create_widgets()

        # Режим на холсте
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Double-Button-1>", self.on_canvas_double_click)

    def create_widgets(self):
        # Создание основных фреймов: левая, правая панели и нижняя строка статуса
        self.left_frame = tk.Frame(self, width=200, bd=2, relief="groove")
        self.left_frame.pack(side="left", fill="y")

        self.right_frame = tk.Frame(self, width=200, bd=2, relief="groove")
        self.right_frame.pack(side="right", fill="y")

        self.bottom_frame = tk.Frame(self, height=25, bd=1, relief="sunken")
        self.bottom_frame.pack(side="bottom", fill="x")

        self.canvas = tk.Canvas(self, bg="white")
        self.canvas.pack(expand=True, fill="both")

        self.status_label = tk.Label(self.bottom_frame, textvariable=self.status_var, anchor="w")
        self.status_label.pack(fill="x")

        # Левая панель инструментов
        tk.Label(self.left_frame, text="Инструменты:", font=("Arial", 10, "bold")).pack(pady=5)

        btn_cursor = tk.Button(self.left_frame, text="Курсор", command=self.set_cursor_mode)
        btn_cursor.pack(fill="x", padx=5, pady=2)

        btn_draw = tk.Button(self.left_frame, text="Построение полигонов", command=self.set_draw_mode)
        btn_draw.pack(fill="x", padx=5, pady=2)

        btn_normals = tk.Button(self.left_frame, text="Показ нормалей", command=self.show_normals)
        btn_normals.pack(fill="x", padx=5, pady=2)

        # Выпадающее меню для выбора метода построения выпуклой оболочки
        tk.Label(self.left_frame, text="Выпуклая оболочка:", font=("Arial", 9, "bold")).pack(pady=5)
        hull_options = ["Грэмма", "Джарвиса"]
        self.hull_method = tk.StringVar(value="Грэмма")
        self.hull_combo = ttk.Combobox(self.left_frame, values=hull_options, state="readonly",
                                       textvariable=self.hull_method)
        self.hull_combo.pack(fill="x", padx=5, pady=2)

        btn_build_hull = tk.Button(self.left_frame, text="Построить оболочку", command=self.build_convex_hull)
        btn_build_hull.pack(fill="x", padx=5, pady=2)

        # Новый комбобокс для выбора цвета заливки — располагается под кнопкой "Построить оболочку"
        tk.Label(self.left_frame, text="Цвет заливки:", font=("Arial", 9, "bold")).pack(pady=5)
        # Определяем словарь: русские названия → реальные кодовые цвета
        self.fill_color_dict = {
            "Красный": "red",
            "Синий": "blue",
            "Зелёный": "green",
            "Жёлтый": "yellow",
            "Оранжевый": "orange",
            "Голубой": "cyan",
            "Пурпурный": "magenta",
            "Фиолетовый": "purple",
            "Коричневый": "brown",
            "Серый": "gray",
            "Розовый": "pink",
            "Чёрный": "black"
        }
        color_options = list(self.fill_color_dict.keys())
        self.fill_color = tk.StringVar(value="Оранжевый")  # значение по умолчанию
        self.fill_color_combo = ttk.Combobox(self.left_frame, values=color_options, state="readonly",
                                             textvariable=self.fill_color)
        self.fill_color_combo.pack(fill="x", padx=5, pady=2)

        # Выпадающее меню для выбора алгоритма заливки полигона
        tk.Label(self.left_frame, text="Алгоритм заливки:", font=("Arial", 9, "bold")).pack(pady=5)
        fill_options = [
            "Развертка (упорядоченный список ребер)",
            "Развертка (активный список ребер)",
            "Заливка затравкой (простой)",
            "Заливка затравкой (построчная)"
        ]
        self.fill_method = tk.StringVar(value="Развертка (упорядоченный список ребер)")
        self.fill_combo = ttk.Combobox(self.left_frame, values=fill_options, state="readonly",
                                       textvariable=self.fill_method)
        self.fill_combo.pack(fill="x", padx=5, pady=2)

        btn_fill = tk.Button(self.left_frame, text="Заполнить полигон", command=self.fill_polygon)
        btn_fill.pack(fill="x", padx=5, pady=2)

        btn_clear = tk.Button(self.left_frame, text="Очистить рабочее\nпространство", command=self.clear_workspace)
        btn_clear.pack(fill="x", padx=5, pady=5)

        # Правая панель инструментов
        tk.Label(self.right_frame, text="Проверка:", font=("Arial", 10, "bold")).pack(pady=5)

        btn_convexity = tk.Button(self.right_frame, text="Проверка выпуклости", command=self.check_convexity)
        btn_convexity.pack(fill="x", padx=5, pady=2)

        # btn_debug = tk.Button(self.right_frame, text="Отладка", command=self.toggle_debug)
        #btn_debug.pack(fill="x", padx=5, pady=2)

    def set_cursor_mode(self):
        self.mode.set("cursor")
        self.status_var.set("Режим: Курсор. Функция перемещения пока не реализована.")

    def set_draw_mode(self):
        self.mode.set("draw_polygon")
        self.current_polygon = Polygon()
        self.status_var.set("Режим: Построение полигонов. Кликайте для добавления вершин, двойной клик для завершения.")

    def on_canvas_click(self, event):
        if self.mode.get() == "draw_polygon":
            # Если полигон уже построен, новые точки не добавляются
            if self.current_polygon is not None and self.current_polygon.closed:
                self.status_var.set("Полигон уже построен. Новые вершины не добавляются.")
                return

            x, y = event.x, event.y
            self.current_polygon.add_vertex(x, y)
            r = 3
            self.canvas.create_oval(x - r, y - r, x + r, y + r, fill="black")
            if len(self.current_polygon.vertices) > 1:
                x_prev, y_prev = self.current_polygon.vertices[-2]
                self.canvas.create_line(x_prev, y_prev, x, y, fill="blue", width=2)
            self.status_var.set(f"Добавлена вершина: ({x}, {y})")
        elif self.mode.get() == "cursor":
            self.status_var.set("Режим курсора: Пока не реализовано перемещение.")

    def on_canvas_double_click(self, event):
        if self.mode.get() == "draw_polygon" and self.current_polygon is not None:
            verts = self.current_polygon.vertices
            if len(verts) > 2:
                x_first, y_first = verts[0]
                x_last, y_last = verts[-1]
                self.canvas.create_line(x_last, y_last, x_first, y_first, fill="blue", width=2)
                self.current_polygon.close_polygon()
                self.status_var.set("Полигон завершён.")
            else:
                self.status_var.set("Недостаточно вершин для завершения полигона.")

    def show_normals(self):
        if self.current_polygon is None or not self.current_polygon.closed:
            messagebox.showwarning("Показ нормалей", "Полигон не построен или не замкнут!")
            return
        for i, ((x1, y1), (x2, y2)) in enumerate(zip(self.current_polygon.vertices,
                                                     self.current_polygon.vertices[1:] + [
                                                         self.current_polygon.vertices[0]])):
            mx = (x1 + x2) / 2
            my = (y1 + y2) / 2
            nx, ny = self.current_polygon.normals[i]
            multiplier = 20
            self.canvas.create_line(mx, my, mx + nx * multiplier, my + ny * multiplier, fill="red", dash=(4, 2))
        self.status_var.set("Нормали к сторонам полигона отображены.")

    def build_convex_hull(self):
        if self.current_polygon is None or len(self.current_polygon.vertices) < 3:
            messagebox.showwarning("Выпуклая оболочка", "Постройте полигон (минимум 3 вершины)!")
            return
        points = self.current_polygon.vertices
        method = self.hull_method.get()
        if method == "Грэмма":
            hull = convex_hull_graham(points)
        elif method == "Джарвиса":
            hull = convex_hull_jarvis(points)
        else:
            hull = []
        if hull:
            for i in range(len(hull)):
                x1, y1 = hull[i]
                x2, y2 = hull[(i + 1) % len(hull)]
                self.canvas.create_line(x1, y1, x2, y2, fill="green", width=3)
            self.status_var.set(f"Выпуклая оболочка построена методом {method}.")
        else:
            self.status_var.set("Ошибка построения оболочки.")

    def fill_polygon(self):
        if self.current_polygon is None or not self.current_polygon.closed:
            messagebox.showwarning("Закраска", "Сначала постройте и замкните полигон!")
            return

        # Автоматически вычисляем seed‑точку (центроид полигона)
        verts = self.current_polygon.vertices
        seed_x = sum(x for (x, y) in verts) / len(verts)
        seed_y = sum(y for (x, y) in verts) / len(verts)
        seed = (int(seed_x), int(seed_y))

        # Считываем выбранный цвет заливки
        selected_color_name = self.fill_color.get()
        selected_color = self.fill_color_dict.get(selected_color_name, "orange")

        method = self.fill_method.get()
        if method == "Развертка (упорядоченный список ребер)":
            import fill_polygon
            fill_polygon.fill_polygon_scanline(self.canvas, self.current_polygon, fill_color=selected_color)
            self.status_var.set("Полигон заполнен методом растровой развертки (упорядоченный список ребер).")
        elif method == "Развертка (активный список ребер)":
            import fill_polygon
            fill_polygon.fill_polygon_active_edge(self.canvas, self.current_polygon, fill_color=selected_color)
            self.status_var.set("Полигон заполнен методом растровой развертки (активный список ребер).")
        elif method == "Заливка затравкой (простой)":
            import fill_polygon
            fill_polygon.fill_polygon_boundary(self.canvas, self.current_polygon, seed,
                                               fill_color=selected_color, boundary_color="black")
            self.status_var.set("Полигон заполнен методом заливки затравкой (простой).")
        elif method == "Заливка затравкой (построчная)":
            import fill_polygon
            fill_polygon.fill_polygon_line_flood(self.canvas, self.current_polygon, seed,
                                                 fill_color=selected_color, boundary_color="black")
            self.status_var.set("Полигон заполнен методом построчной заливки с затравкой.")
        else:
            self.status_var.set("Неизвестный метод заливки.")

    def check_convexity(self):
        if self.current_polygon is None or not self.current_polygon.closed:
            messagebox.showwarning("Проверка выпуклости", "Сначала постройте и замкните полигон!")
            return
        convex, msg = self.current_polygon.check_convexity()
        messagebox.showinfo("Проверка выпуклости", msg)
        self.status_var.set("Проверка выпуклости выполнена.")

    def clear_workspace(self):
        """Очищает холст и сбрасывает текущие данные."""
        self.canvas.delete("all")
        self.current_polygon = None
        # Очищаем глобальный список отладочных шагов
        debug_steps.clear()
        self.status_var.set("Рабочее пространство очищено.")

    def toggle_debug(self):
        if self.debug_mode.get():
            self.debug_mode.set(False)
            if hasattr(self, "debug_window"):
                self.debug_window.destroy()
            self.status_var.set("Отладочный режим отключён.")
        else:
            self.debug_mode.set(True)
            self.show_debug_window()
            self.status_var.set("Отладочный режим включён.")

    def show_debug_window(self):
        """
        Открывает окно отладки и выводит таблицу с пошаговым решением по заливке.
        Предполагается, что глобальный список debug_steps (из модуля polygon и/или fill_polygon)
        содержит строки, оформленные в виде:
        "Шаг N: Закрашен пиксель (x, y); Стек: [ ... ]"
        """
        self.debug_window = tk.Toplevel(self)
        self.debug_window.title("Отладка - Таблица закрашивания полигонов")
        self.debug_window.geometry("800x600")

        text = tk.Text(self.debug_window, wrap="none")
        text.pack(expand=True, fill="both")

        # Формируем заголовок таблицы
        header = "Шаг\tЗакрашиваемый пиксель\tСтек затравочных пикселей\n"
        header += "-" * 80 + "\n"
        text.insert("end", header)

        # Выводим отладочные сообщения
        for i, msg in enumerate(debug_steps, start=1):
            # Можно форматировать строку, если debug_steps уже содержат информацию
            text.insert("end", f"{i}\t{msg}\n")

        btn_update = tk.Button(self.debug_window, text="Обновить", command=lambda: self.update_debug_window(text))
        btn_update.pack(side="bottom", pady=5)

    def update_debug_window(self, text_widget):
        text_widget.delete("1.0", "end")
        text_widget.insert("end", "Пошаговое решение:\n---------------------\n")
        for i, msg in enumerate(debug_steps, start=1):
            text_widget.insert("end", f"{i:3d}: {msg}\n")


if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()
