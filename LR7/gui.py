# gui.py
import tkinter as tk
from tkinter import messagebox
from triangulation import delaunay_triangulation
from voronoi import compute_voronoi_edges

CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Лабораторная работа 7: Триангуляция и диаграмма Вороного")

        # Режим работы: "cursor" – без добавления точек, "add" – режим добавления точек.
        self.mode = "cursor"
        self.points = []  # Список введённых пользователем точек (каждая точка: (x, y))
        self.triangles = []  # Список треугольников после триангуляции
        self.voronoi_edges = []  # Список отрезков диаграммы Вороного

        # Создаем панель инструментов.
        toolbar = tk.Frame(self, bd=1, relief=tk.RAISED)
        btn_cursor = tk.Button(toolbar, text="Курсор", command=self.set_cursor_mode)
        btn_cursor.pack(side=tk.LEFT, padx=2, pady=2)
        btn_add = tk.Button(toolbar, text="Добавить точки", command=self.set_add_mode)
        btn_add.pack(side=tk.LEFT, padx=2, pady=2)
        btn_triangulate = tk.Button(toolbar, text="Триангуляция", command=self.do_triangulation)
        btn_triangulate.pack(side=tk.LEFT, padx=2, pady=2)
        btn_voronoi = tk.Button(toolbar, text="Диаграмма Вороного", command=self.do_voronoi)
        btn_voronoi.pack(side=tk.LEFT, padx=2, pady=2)
        btn_clear = tk.Button(toolbar, text="Очистить", command=self.clear_all)
        btn_clear.pack(side=tk.LEFT, padx=2, pady=2)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        # Создаем холст для рисования.
        self.canvas = tk.Canvas(self, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="white")
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        # Ограничивающий прямоугольник для построения диаграммы Вороного (по размерам холста)
        self.bbox = (0, 0, CANVAS_WIDTH, CANVAS_HEIGHT)

    def set_cursor_mode(self):
        self.mode = "cursor"
        self.status_message("Режим: Курсор")

    def set_add_mode(self):
        self.mode = "add"
        self.status_message("Режим: Добавление точек")

    def status_message(self, msg):
        self.title(f"Лабораторная работа 7: {msg}")

    def on_canvas_click(self, event):
        """
        При щелчке по холсту в режиме "add" добавляет точку и отображает её.
        """
        if self.mode == "add":
            x, y = event.x, event.y
            self.points.append((x, y))
            r = 3
            self.canvas.create_oval(x - r, y - r, x + r, y + r, fill="black", outline="black")

    def do_triangulation(self):
        """
        Выполняет триангуляцию Делоне для набора точек и отрисовывает линии треугольников.
        """
        if len(self.points) < 3:
            messagebox.showerror("Ошибка", "Для триангуляции требуется минимум 3 точки.")
            return
        self.triangles = delaunay_triangulation(self.points)
        self.draw_triangulation()

    def draw_triangulation(self):
        self.canvas.delete("triangulation")
        for tri in self.triangles:
            pts = tri.vertices
            self.canvas.create_line(pts[0][0], pts[0][1], pts[1][0], pts[1][1],
                                    fill="blue", tags="triangulation")
            self.canvas.create_line(pts[1][0], pts[1][1], pts[2][0], pts[2][1],
                                    fill="blue", tags="triangulation")
            self.canvas.create_line(pts[2][0], pts[2][1], pts[0][0], pts[0][1],
                                    fill="blue", tags="triangulation")

    def do_voronoi(self):
        """
        Строит диаграмму Вороного по полученной триангуляции и отрисовывает её.
        """
        if not self.triangles:
            messagebox.showerror("Ошибка", "Сначала выполните триангуляцию.")
            return
        self.voronoi_edges = compute_voronoi_edges(self.triangles, self.bbox)
        self.draw_voronoi()

    def draw_voronoi(self):
        self.canvas.delete("voronoi")
        for edge in self.voronoi_edges:
            p1, p2 = edge
            self.canvas.create_line(p1[0], p1[1], p2[0], p2[1],
                                    fill="red", dash=(4, 2), tags="voronoi")

    def clear_all(self):
        """
        Очищает холст и сбрасывает списки точек, треугольников и Вороной.
        """
        self.points = []
        self.triangles = []
        self.voronoi_edges = []
        self.canvas.delete("all")
        self.status_message("Ожидание")


if __name__ == "__main__":
    app = App()
    app.mainloop()
