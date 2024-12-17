from PIL import Image, ImageDraw
import base64
from io import BytesIO

def execute_algorithm(algorithm, params):
    if algorithm == 'step_by_step':
        return step_by_step_algorithm(params)
    elif algorithm == 'dda':
        return dda_algorithm(params)
    elif algorithm == 'bresenham_line':
        return bresenham_line_algorithm(params)
    elif algorithm == 'bresenham_circle':
        return bresenham_circle_algorithm(params)
    elif algorithm == 'bresenham_ellipse':
        return bresenham_ellipse_algorithm(params)
    else:
        return 'Неизвестный алгоритм'

def create_image():
    # Создаем пустое изображение 50x50 с белым фоном
    img = Image.new('RGB', (50, 50), 'white')
    
    return img


def get_image_data(img):
    # Коэффициент масштабирования
    scale_factor = 10  # 50x10 = 500 пикселей

    # Увеличиваем изображение с использованием NEAREST (ближайшего соседа) для сохранения резкости
    img = img.resize((img.width * scale_factor, img.height * scale_factor), Image.NEAREST)
    
    # Добавляем координатную сетку
    draw = ImageDraw.Draw(img)

    # Рисуем вертикальные линии на каждой границе пикселей
    for x in range(1, img.width, scale_factor):
        draw.line([(x, 0), (x, img.height)], fill='lightgray')
    draw.line([(0, 0), (0, img.height)], fill='black')
    draw.line([(0, 0), (img.width, 0)], fill='black')

    # Рисуем горизонтальные линии на каждой границе пикселей
    for y in range(1, img.height, scale_factor):
        draw.line([(0, y), (img.width, y)], fill='lightgray')

    # Преобразуем изображение в base64 для отображения на веб-странице
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str


def step_by_step_algorithm(params):
    x1 = int(params.get('x1', 0))
    y1 = int(params.get('y1', 0))
    x2 = int(params.get('x2', 0))
    y2 = int(params.get('y2', 0))

    img = create_image()
    draw = ImageDraw.Draw(img)

    dx = x2 - x1
    dy = y2 - y1

    steps = max(abs(dx), abs(dy))

    if steps == 0:
        draw.point((x1, y1), fill='black')
    else:
        x_inc = dx / steps
        y_inc = dy / steps

        x = x1
        y = y1

        for _ in range(steps + 1):
            draw.point((round(x), round(y)), fill='black')
            x += x_inc
            y += y_inc

    img_str = get_image_data(img)
    return img_str

def dda_algorithm(params):
    x1 = int(params.get('x1', 5))
    y1 = int(params.get('y1', 5))
    x2 = int(params.get('x2', 45))
    y2 = int(params.get('y2', 45))

    img = create_image()
    draw = ImageDraw.Draw(img)

    dx = x2 - x1

    dy = y2 - y1

    steps = max(abs(dx), abs(dy))

    if steps == 0:
        draw.point((x1, y1), fill='red')
    else:
        x_inc = dx / steps
        y_inc = dy / steps

        x = x1
        y = y1

        for _ in range(steps + 1):
            draw.point((round(x), round(y)), fill='red')
            x += x_inc
            y += y_inc

    img_str = get_image_data(img)
    return img_str

def bresenham_line_algorithm(params):
    x1 = int(params.get('x1', 5))
    y1 = int(params.get('y1', 5))
    x2 = int(params.get('x2', 45))
    y2 = int(params.get('y2', 45))

    img = create_image()
    draw = ImageDraw.Draw(img)

    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    x, y = x1, y1

    sx = -1 if x1 > x2 else 1
    sy = -1 if y1 > y2 else 1

    if dy <= dx:
        err = dx / 2.0
        while x != x2:
            draw.point((x, y), fill='purple')
            err -= dy
            if err < 0:
                y += sy
                err += dx
            x += sx
    else:
        err = dy / 2.0
        while y != y2:
            draw.point((x, y), fill='purple')
            err -= dx
            if err < 0:
                x += sx
                err += dy
            y += sy
    draw.point((x, y), fill='purple')

    img_str = get_image_data(img)
    return img_str

def bresenham_circle_algorithm(params):
    xc = int(params.get('xc', 25))
    yc = int(params.get('yc', 25))
    r = int(params.get('radius', 20))
    
    img = create_image()
    draw = ImageDraw.Draw(img)
    
    x = 0
    y = r
    d = 3 - 2 * r

    def draw_circle(xc, yc, x, y):
        points = [
            (xc + x, yc + y),
            (xc - x, yc + y),
            (xc + x, yc - y),
            (xc - x, yc - y),
            (xc + y, yc + x),
            (xc - y, yc + x),
            (xc + y, yc - x),
            (xc - y, yc - x),
        ]
        for point in points:
            if 0 <= point[0] < 50 and 0 <= point[1] < 50:
                draw.point(point, fill='blue')
    
    while y >= x:
        draw_circle(xc, yc, x, y)
        x += 1
        if d > 0:
            y -= 1
            d = d + 4 * (x - y) + 10
        else:
            d = d + 4 * x + 6

    img_str = get_image_data(img)
    return img_str

def bresenham_ellipse_algorithm(params):
    xc = int(params.get('xc', 25))
    yc = int(params.get('yc', 25))
    rx = int(params.get('rx', 15))  # Большая полуось
    ry = int(params.get('ry', 10))  # Малая полуось

    img = create_image()
    draw = ImageDraw.Draw(img)

    x = 0
    y = ry
    rx2 = rx * rx
    ry2 = ry * ry
    two_rx2 = 2 * rx2
    two_ry2 = 2 * ry2
    px = 0
    py = two_rx2 * y

    def draw_ellipse(xc, yc, x, y):
        points = [
            (xc + x, yc + y),
            (xc - x, yc + y),
            (xc + x, yc - y),
            (xc - x, yc - y)
        ]
        for point in points:
            if 0 <= point[0] < 50 and 0 <= point[1] < 50:
                draw.point(point, fill='green')

    # Первая часть
    p = round(ry2 - (rx2 * ry) + (0.25 * rx2))
    while px < py:
        draw_ellipse(xc, yc, x, y)
        x += 1
        px += two_ry2
        if p < 0:
            p += ry2 + px
        else:
            y -= 1
            py -= two_rx2
            p += ry2 + px - py

    # Вторая часть
    p = round(ry2 * (x + 0.5) * (x + 0.5) + rx2 * (y - 1) * (y - 1) - rx2 * ry2)
    while y >= 0:
        draw_ellipse(xc, yc, x, y)
        y -= 1
        py -= two_rx2
        if p > 0:
            p += rx2 - py
        else:
            x += 1
            px += two_ry2
            p += rx2 - py + px

    img_str = get_image_data(img)
    return img_str

