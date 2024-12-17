from PIL import Image, ImageDraw


def compute_matrix_value(first_matrix, second_matrix, size):
    value = 0

    for i in range(size):
        for j in range(size):
            value += first_matrix[i][j] * second_matrix[i][j]

    return value


def create_expand_matrix(image_matrix, matrix_height, matrix_width, shift):
    new_matrix_height, new_matrix_width = matrix_height + 2 * shift, matrix_width + 2 * shift
    expand_matrix = [[0] * new_matrix_width for _ in range(new_matrix_height)]

    for i in range(new_matrix_height):
        for j in range(new_matrix_width):
            pos_i, pos_j = i, j

            if pos_i >= shift:
                pos_i -= shift

            if pos_j >= shift:
                pos_j -= shift

            if pos_i >= matrix_height:
                pos_i -= shift

            if pos_j >= matrix_width:
                pos_j -= shift

            expand_matrix[i][j] = image_matrix[pos_i][pos_j]

    return expand_matrix, new_matrix_height, new_matrix_width


def draw_image(image_matrix, image_height, image_width, image, draw, file_name):
    """
    Draw image from a given matrix of pixel colors
    :param image_matrix: Two-dimensional array containing information about color channels of pixels
    :param image_height:
    :param image_width:
    :param image:
    :param draw:
    :param file_name: Path in which image is saved
    :return None
    """

    for i in range(image_height):
        for j in range(image_width):
            draw.point((i, j), (image_matrix[i][j], image_matrix[i][j], image_matrix[i][j]))

    image.save(file_name, "JPEG")


def start_processing(file_name):
    """
    Along the image path, returns all items for image processing
    :param file_name: Path to the required image
    :returns image processing tools: image, image width, image height, image pixels, draw
    """

    image = Image.open(file_name)
    image_height, image_width = image.size
    image_pixels = image.load()
    draw = ImageDraw.Draw(image)

    return image, image_height, image_width, image_pixels, draw


def end_processing(draw):
    """
    Close image processing tools
    :param draw:
    :return:
    """

    del draw


def create_image_matrix(image_pixels, image_height, image_width):
    """
    The input array contains a tuple of 3 identical elements, the output is only 1
    :param image_pixels: Two-dimensional array containing information about color channels of pixels
    :param image_height:
    :param image_width:
    :return image_matrix: Two-dimensional array containing information about brightness of pixels
    """

    image_matrix = [[0] * image_width for _ in range(image_height)]

    for i in range(image_height):
        for j in range(image_width):
            image_matrix[i][j] = image_pixels[i, j][0]

    return image_matrix