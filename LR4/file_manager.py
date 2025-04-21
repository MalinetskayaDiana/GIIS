def read_object(filename):
    """
    Читает 3D объект из текстового файла и возвращает данные в виде словаря.

    Ожидаемый формат файла:
      - Первая непустая строка: число вершин (N).
      - Следующие N строк: координаты вершин (x, y, z) разделённые пробелами.
      - Следующая строка: число граней (M).
      - Следующие M строк: индексы вершин для каждой грани (индексы разделены пробелами).

    Комментарии и пустые строки пропускаются.
    Пример файла:

      8
      0 0 0
      100 0 0
      100 100 0
      0 100 0
      0 0 100
      100 0 100
      100 100 100
      0 100 100
      6
      0 1 2 3
      4 5 6 7
      0 1 5 4
      2 3 7 6
      1 2 6 5
      0 3 7 4

    Возвращает:
        dict: {"vertices": list, "faces": list}
    """
    vertices = []
    faces = []

    try:
        with open(filename, "r", encoding="utf-8") as f:
            # Читаем все строки, фильтруя пустые строки и комментарии
            lines = [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]

        if not lines:
            raise ValueError("Файл пуст или не содержит данных.")

        # Первая строка: число вершин
        num_vertices = int(lines[0])
        current_line = 1

        # Читаем координаты вершин
        for i in range(num_vertices):
            if current_line >= len(lines):
                raise ValueError("Недостаточно строк для указания всех вершин.")
            parts = lines[current_line].split()
            if len(parts) < 3:
                raise ValueError(f"Неверный формат координат в строке {current_line + 1}.")
            vertex = [float(parts[0]), float(parts[1]), float(parts[2])]
            vertices.append(vertex)
            current_line += 1

        if current_line >= len(lines):
            raise ValueError("Отсутствуют данные о гранях.")

        # Следующая строка: число граней
        num_faces = int(lines[current_line])
        current_line += 1

        # Читаем описание граней
        for i in range(num_faces):
            if current_line >= len(lines):
                raise ValueError("Недостаточно строк для указания всех граней.")
            parts = lines[current_line].split()
            # Преобразуем номера вершин в целые числа.
            face = [int(idx) for idx in parts]
            faces.append(face)
            current_line += 1

        return {"vertices": vertices, "faces": faces}

    except Exception as e:
        raise Exception(f"Ошибка при чтении файла '{filename}': {e}")
