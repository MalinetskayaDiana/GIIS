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

        # Кнопка "Курсор" для отключения режима рисования
        btn_cursor = tk.Button(self.toolbar, text="Курсор", command=self.select_cursor_mode)
        btn_cursor.pack(side=tk.LEFT, padx=2, pady=2)

        # Меню для выбора алгоритма построения отрезка (выпадающий список)
        self.line_menu_button = tk.Menubutton(self.toolbar, text="Отрезок", relief=tk.RAISED)
        self.line_menu = tk.Menu(self.line_menu_button, tearoff=0)
        self.line_menu.add_command(label="Алгоритм ЦДА", command=lambda: self.select_line_mode_with_algorithm("DDA"))
        self.line_menu.add_command(label="Алгоритм Брезенхэма",
                                   command=lambda: self.select_line_mode_with_algorithm("Bresenham"))
        self.line_menu.add_command(label="Алгоритм Ву", command=lambda: self.select_line_mode_with_algorithm("Wu"))
        self.line_menu_button.config(menu=self.line_menu)
        self.line_menu_button.pack(side=tk.LEFT, padx=2, pady=2)

        # Кнопка "Отладка"
        btn_debug = tk.Button(self.toolbar, text="Отладка", command=self.select_debug_mode)
        btn_debug.pack(side=tk.RIGHT, padx=2, pady=2)

        self.toolbar.pack(side=tk.TOP, fill=tk.X)

    def select_line_mode_with_algorithm(self, algo):
        if algo == "DDA":
            self.selected_algorithm = draw_line_dda
            self.selected_algorithm_title = "Алгоритм ЦДА"
        elif algo == "Bresenham":
            self.selected_algorithm = draw_line_bresenham
            self.selected_algorithm_title = "Алгоритм Брезенхэма"
        elif algo == "Wu":
            self.selected_algorithm = draw_line_wu
            self.selected_algorithm_title = "Алгоритм Ву"
        self.update_status(f"{self.selected_algorithm_title} выбран. Режим построения отрезков активирован.")
        # Активируем режим построения отрезков
        self.current_event = "Отрезок"
        self.start_point = None
        self.canvas.bind("<Button-1>", self.on_canvas_click)

    def select_debug_mode(self):
        """
        Переключает режим отладки.
        При включении:
          - обновляется статус,
          - отрисовывается дискретная сетка.
        При выключении:
          - статус меняется,
          - сетка удаляется,
          - возвращается обычный обработчик кликов.
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

    def draw_grid(self, grid_size=20):
        """
        Рисует дискретную сетку на канве.
        Все линии получают тег "grid" для удобного удаления.
        """
        w = int(self.canvas['width'])
        h = int(self.canvas['height'])
        for x in range(0, w + 1, grid_size):
            self.canvas.create_line(x, 0, x, h, fill="lightgray", tags="grid")
        for y in range(0, h + 1, grid_size):
            self.canvas.create_line(0, y, w, y, fill="lightgray", tags="grid")

    def create_canvas(self):
        self.canvas = tk.Canvas(self.root, bg="white", width=800, height=600)
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def create_status_bar(self):
        self.status_var = tk.StringVar()
        self.status_var.set("История: Пуста")
        self.status_bar = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def update_status(self, mode, is_error=False):
        self.current_mode = mode
        if is_error:
            self.status_bar.config(fg="red")
            self.status_var.set(self.current_mode)
        else:
            self.status_bar.config(fg="black")
            self.status_var.set(f"История: {self.current_mode}")

    def run(self):
        self.root.mainloop()

    # Выбор алгоритмов
    def select_dda(self):
        self.selected_algorithm = draw_line_dda
        self.selected_algorithm_title = "Алгоритм ЦДА"
        self.update_status("Алгоритм ЦДА")

    def select_bresenham(self):
        self.selected_algorithm = draw_line_bresenham
        self.selected_algorithm_title = "Алгоритм Брезенхэма"
        self.update_status("Алгоритм Брезенхэма")

    def select_wu(self):
        self.selected_algorithm = draw_line_wu
        self.selected_algorithm_title = "Алгоритм Ву"
        self.update_status("Алгоритм Ву")

    def select_line_mode(self):
        self.update_status(f"Режим построения отрезков ({self.selected_algorithm_title}). Выберите первую точку.")
        self.current_event = "Отрезок"
        self.start_point = None
        self.canvas.bind("<Button-1>", self.on_canvas_click)

    def select_cursor_mode(self):
        self.start_point = None
        self.canvas.unbind("<Button-1>")
        self.update_status("Режим курсора активирован")

    def on_canvas_click(self, event):
        """
        Универсальный обработчик клика по канве.
        Делегирует обработку события в зависимости от выбранного режима (фигура):
          - "Отрезок" – построение линии (с отладкой, если включено).
          - "Кривая"  – построение кривой. Внутри вызывается конкретный обработчик,
                       например, для типа "Окружность".
        Если режим не выбран, выводится сообщение об ошибке.
        """
        if self.current_event == "Отрезок":
            self.handle_line_click(event)
        else:
            self.update_status("Ощибка: Не выбран режим построения фигур.", is_error=True)

    def handle_line_click(self, event):
        """
        Обработка клика в режиме построения линии (отрезка).
        Если включён режим отладки, затем при первом клике сохраняется начальная точка
        и подписывается обработчик предварительного отображения, а при втором клике:
          - отписывается обработчик движения мыши,
          - удаляется предварительный отрезок,
          - вызывается выбранный алгоритм с параметром debug=True (он и отрисовывает линию, и возвращает таблицу),
          - вызывается функция отображения отладочной таблицы.
        """
        if self.selected_algorithm is None:
            self.update_status("Ошибка: выберите режим построения отрезков!", is_error=True)
            return

        if self.debug_mode:
            if self.start_point is None:
                self.start_point = (event.x, event.y)
                self.update_status(
                    f"Отладка (Линия): выбрана начальная точка ({event.x}, {event.y}). Выберите конечную точку.")
                self.canvas.bind("<Motion>", self.on_line_motion)
            else:
                self.canvas.unbind("<Motion>")
                self.canvas.delete("preview_line")
                x0, y0 = self.start_point
                x1, y1 = event.x, event.y
                # Вызываем выбранный алгоритм с debug=True (однократно)
                table = self.selected_algorithm(self.canvas, x0, y0, x1, y1, debug=True)
                self.show_debug_table(table)
                self.update_status(
                    f"Отладка ({self.selected_algorithm_title}): линия от ({x0}, {y0}) до ({x1}, {y1}) построена, таблица выведена.")
                self.start_point = None
        else:
            if self.start_point is None:
                self.start_point = (event.x, event.y)
                self.update_status(
                    f"Линия: выбрана начальная точка ({event.x}, {event.y}), выберите конечную.")
                self.canvas.bind("<Motion>", self.on_line_motion)
            else:
                self.canvas.unbind("<Motion>")
                self.canvas.delete("preview_line")
                x0, y0 = self.start_point
                x1, y1 = event.x, event.y
                self.selected_algorithm(self.canvas, x0, y0, x1, y1)
                self.update_status(f"Линия: построен отрезок: ({x0}, {y0}) -> ({x1}, {y1}).")
                self.start_point = None

    def show_debug_table(self, table):
        """
        Открывает новое окно с отладочной таблицей.
        Если запись таблицы содержит 4 элемента, выводятся поля:
             Итерация, x, y, Отобр. координаты.
        Если запись содержит 6 элементов, выводятся:
             Итерация, x, y, e, e′, Отобр. координаты.
        """
        window = tk.Toplevel(self.root)
        window.title(f"Отладочная таблица ({self.selected_algorithm_title})")
        window.geometry("800x400")

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
                # disp предполагается как кортеж (rx, ry)
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
        else:
            text.insert(tk.END, "Неподдерживаемый формат таблицы\n")

        text.config(state=tk.DISABLED)

    def on_line_motion(self, event):
        """
        Обработчик движения мыши для предварительного отображения отрезка.
        Он удаляет предыдущий предварительный отрезок и рисует новый, соединяя
        сохранённую начальную точку (self.start_point) с текущей позицией курсора.
        Предварительный отрезок создаётся с тегом "preview_line" для более удобного удаления.
        """
        if self.start_point is None:
            return
        self.canvas.delete("preview_line")
        x0, y0 = self.start_point
        self.canvas.create_line(x0, y0, event.x, event.y, fill="gray", dash=(2, 2), tags="preview_line")

    def clear_canvas(self):
        self.canvas.delete("all")
        self.update_status("Экран очищен")

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

