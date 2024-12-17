import tkinter as tk
import time

# Функция для отрисовки звезды
def draw_star(canvas):
    coordinates = [
        (200, 100), (230, 160), (300, 160), (250, 200), (270, 260),
        (200, 220), (135, 260), (150, 200), (100, 160), (170, 160)
    ]
    canvas.create_polygon(coordinates, fill="#FF6400", outline="#FF6400")

# Функция для отрисовки результирующих фигур
def draw_intersection(canvas):
    figure = [(50, 250), (130, 120), (250, 50), (350, 200), (240, 300), (90, 345)]
    window = [(100, 100), (300, 100), (300, 300), (100, 300)]
    
    # Применяем алгоритм отсечения
    clipped = clip_algorithm_sutherland_hodgman(figure, window)

    # Отрисовка исходного многоугольника
    draw_polygon(canvas, figure, "#009900", "#009900")
    canvas.update()
    time.sleep(1)

    # Отрисовка окна
    draw_polygon(canvas, window, "#990000", "#990000")
    canvas.update()
    time.sleep(1)

    # Отрисовка отсеченного многоугольника
    draw_polygon(canvas, clipped, "#000099", "#000099")
    canvas.update()

# Реализация алгоритма отсечения Сазерленда–Ходжмана
def clip_algorithm_sutherland_hodgman(figure, window):
    def is_inside(point, point_from, point_to):
        return (point_to[0] - point_from[0]) * (point[1] - point_from[1]) > (point_to[1] - point_from[1]) * (point[0] - point_from[0])

    def intersection(window_point_from, window_point_to, figure_point_from, figure_point_to):
        windows_diff = (window_point_from[0] - window_point_to[0], window_point_from[1] - window_point_to[1])
        figure_diff = (figure_point_from[0] - figure_point_to[0], figure_point_from[1] - figure_point_to[1])
        n1 = (window_point_from[0] * window_point_to[1]) - (window_point_from[1] * window_point_to[0])
        n2 = (figure_point_from[0] * figure_point_to[1]) - (figure_point_from[1] * figure_point_to[0])
        n3 = (windows_diff[0] * figure_diff[1]) - (windows_diff[1] * figure_diff[0])
        return (
            (n1 * figure_diff[0] - n2 * windows_diff[0]) / n3,
            (n1 * figure_diff[1] - n2 * windows_diff[1]) / n3
        )

    output_list = figure
    window_point_from = window[-1]
    for window_point_to in window:
        input_list = output_list
        output_list = []
        figure_point_from = input_list[-1]
        for figure_point_to in input_list:
            if is_inside(figure_point_to, window_point_from, window_point_to):
                if not is_inside(figure_point_from, window_point_from, window_point_to):
                    output_list.append(intersection(window_point_from, window_point_to, figure_point_from, figure_point_to))
                output_list.append(figure_point_to)
            elif is_inside(figure_point_from, window_point_from, window_point_to):
                output_list.append(intersection(window_point_from, window_point_to, figure_point_from, figure_point_to))
            figure_point_from = figure_point_to
        window_point_from = window_point_to
    return output_list

# Функция для отрисовки многоугольника
def draw_polygon(canvas, polygon, stroke_style, fill_style):
    canvas.create_polygon(polygon, outline=stroke_style, fill=fill_style, width=2)

# Основная программа
def main():
    root = tk.Tk()
    root.title("Иллюстрация растровых алгоритмов")

    # Создаем холсты для отрисовки
    line_canvas = tk.Canvas(root, width=500, height=400, bg='white')
    line_canvas.pack(side=tk.LEFT, padx=10, pady=10)

    clip_canvas = tk.Canvas(root, width=400, height=400, bg='white')
    clip_canvas.pack(side=tk.RIGHT, padx=10, pady=10)

    # Отрисовка
    draw_star(line_canvas)
    draw_intersection(clip_canvas)

    root.mainloop()

if __name__ == "__main__":
    main()
