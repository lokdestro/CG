import argparse
from PIL import Image, ImageDraw


def convert_to_grayscale(image_name, output_path, coefficients):
    """
    Преобразует цветное изображение в градации серого и сохраняет несколько вариантов.
    :param image_name: Путь к исходному изображению
    :param output_path: Каталог для сохранения преобразованных изображений
    :param coefficients: Список коэффициентов для преобразования
    :return: None
    """
    try:
        image = Image.open(image_name)
        image_width, image_height = image.size
        image_pixels = image.load()
        draw = ImageDraw.Draw(image)

        for idx, (coef_r, coef_g, coef_b) in enumerate(coefficients, start=1):
            new_image = image.copy()
            new_draw = ImageDraw.Draw(new_image)
            for x in range(image_width):
                for y in range(image_height):
                    red, green, blue = image_pixels[x, y]
                    gray = round(coef_r * red + coef_g * green + coef_b * blue)
                    new_draw.point((x, y), (gray, gray, gray))

            new_image.save(f"{output_path}/grayscale_{idx}.jpg", "JPEG")
        print(f"Все изображения успешно сохранены в {output_path}")
    except FileNotFoundError:
        print(f"Файл {image_name} не найден.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")


def parse_arguments():
    """
    Парсинг аргументов командной строки.
    :return: Обработанные аргументы
    """
    parser = argparse.ArgumentParser(description="Программа для преобразования изображения в градации серого.")
    parser.add_argument('-name', required=True, help='Путь к исходному изображению')
    parser.add_argument('-path', required=True, help='Каталог для сохранения преобразованных изображений')

    return parser.parse_args()


def main():
    """
    Основная функция для обработки изображения.
    """
    args = parse_arguments()
    coefficients = [
        (0.299, 0.587, 0.114),     # Первый вариант
        (0.2126, 0.7152, 0.0722),  # Второй вариант
        (0.2627, 0.6780, 0.0593)   # Третий вариант
    ]

    convert_to_grayscale(image_name=args.name, output_path=args.path, coefficients=coefficients)


if __name__ == '__main__':
    main()
