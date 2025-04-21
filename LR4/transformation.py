import numpy as np
import math

def create_translation_matrix(dx, dy, dz):
    """
    Возвращает 4x4 матрицу перемещения с заданными смещениями по осям dx, dy, dz.
    """
    T = np.array([
        [1, 0, 0, dx],
        [0, 1, 0, dy],
        [0, 0, 1, dz],
        [0, 0, 0, 1]
    ])
    return T

def create_scaling_matrix(sx, sy, sz):
    """
    Возвращает 4x4 матрицу масштабирования с коэффициентами sx, sy, sz.
    """
    S = np.array([
        [sx, 0,  0,  0],
        [0,  sy, 0,  0],
        [0,  0,  sz, 0],
        [0,  0,  0,  1]
    ])
    return S

def create_rotation_matrix_x(rx_deg):
    """
    Возвращает 4x4 матрицу поворота вокруг оси X на угол rx_deg (в градусах).
    """
    rx = math.radians(rx_deg)
    Rx = np.array([
        [1, 0,           0,          0],
        [0, math.cos(rx), -math.sin(rx), 0],
        [0, math.sin(rx), math.cos(rx),  0],
        [0, 0,           0,          1]
    ])
    return Rx

def create_rotation_matrix_y(ry_deg):
    """
    Возвращает 4x4 матрицу поворота вокруг оси Y на угол ry_deg (в градусах).
    """
    ry = math.radians(ry_deg)
    Ry = np.array([
        [math.cos(ry),  0, math.sin(ry), 0],
        [0,             1, 0,            0],
        [-math.sin(ry), 0, math.cos(ry), 0],
        [0,             0, 0,            1]
    ])
    return Ry

def create_rotation_matrix_z(rz_deg):
    """
    Возвращает 4x4 матрицу поворота вокруг оси Z на угол rz_deg (в градусах).
    """
    rz = math.radians(rz_deg)
    Rz = np.array([
        [math.cos(rz), -math.sin(rz), 0, 0],
        [math.sin(rz), math.cos(rz),  0, 0],
        [0,            0,             1, 0],
        [0,            0,             0, 1]
    ])
    return Rz

def create_rotation_matrix(rx_deg, ry_deg, rz_deg):
    """
    Возвращает составную матрицу поворота, полученную умножением матриц поворота вокруг осей Z, Y, X.
    Порядок применения: сначала Rx, затем Ry, затем Rz (т.е. R = Rz * Ry * Rx).
    """
    Rz = create_rotation_matrix_z(rz_deg)
    Ry = create_rotation_matrix_y(ry_deg)
    Rx = create_rotation_matrix_x(rx_deg)
    return Rz @ Ry @ Rx

def create_perspective_projection_matrix(d):
    """
    Возвращает 4x4 матрицу перспективной проекции с параметром d (расстояние до экрана).
    Для применения в однородных координатах.
    Примечание: перспективная проекция часто применяется не как матрица преобразования
    в моделировании, а при отрисовке (после умножения на матрицу модели). Здесь приведён пример.
    """
    P = np.array([
        [1, 0,     0,      0],
        [0, 1,     0,      0],
        [0, 0,     1,      0],
        [0, 0, 1/d,      0]
    ])
    return P
