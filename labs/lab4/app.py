import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import CubicSpline

# Исходные точки графика
graphic_points = [
    {"x": 0, "y": 200},
    {"x": 50, "y": 300},
    {"x": 100, "y": 100},
    {"x": 150, "y": 170},
    {"x": 200, "y": 120},
    {"x": 250, "y": 250},
    {"x": 300, "y": 300},
    {"x": 350, "y": 50},
    {"x": 400, "y": 100},
    {"x": 450, "y": 200},
    {"x": 500, "y": 150},
    {"x": 550, "y": 300},
    {"x": 600, "y": 120},
    {"x": 650, "y": 200},
    {"x": 700, "y": 230},
    {"x": 750, "y": 200}
]

# Функция для построения осей
def draw_axis(ax):
    ax.axhline(200, color='black', linewidth=2, label='Ось X')  # Главная горизонтальная ось
    ax.axvline(0, color='black', linewidth=2)                  # Вертикальная ось
    for point in graphic_points:
        ax.axvline(point['x'], color='gray', linewidth=0.5, linestyle='--')  # Вертикальные линии

# Функция отрисовки прямой линии
def draw_init_chart(ax):
    x_points = [point["x"] for point in graphic_points]
    y_points = [point["y"] for point in graphic_points]
    ax.plot(x_points, y_points, color='blue', label='Исходная линия')

# Функция отрисовки аппроксимации с помощью Кубического Сплайна
def draw_approximation(ax):
    x_points = [point["x"] for point in graphic_points]
    y_points = [point["y"] for point in graphic_points]

    # Создаем интерполяцию CubicSpline
    spline = CubicSpline(x_points, y_points)
    
    # Создаем новые значения для гладкости кривой
    x_new = np.linspace(min(x_points), max(x_points), 300)
    y_new = spline(x_new)

    # Рисуем аппроксимирующую кривую
    ax.plot(x_new, y_new, color='red', linewidth=2, label='Аппроксимация (Spline)')

# Основная функция визуализации
def visualize():
    fig, ax = plt.subplots(figsize=(12, 6))
    draw_axis(ax)                    # Оси
    draw_init_chart(ax)              # Ломаная линия
    draw_approximation(ax)           # Аппроксимирующая кривая

    ax.set_xlim(-50, 800)            # Лимиты оси X
    ax.set_ylim(0, 400)              # Лимиты оси Y
    ax.legend()                      # Легенда
    ax.set_title("График с аппроксимацией кубическим сплайном")
    plt.show()

# Запуск программы
visualize()
