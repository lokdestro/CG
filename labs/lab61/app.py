import argparse

from PIL import Image, ImageDraw


def binarization(image_height, image_width, image_pixels, threshold, image, draw, file_name):
    """
    Change all pixels of image with brightness <= threshold to white, otherwise to black
    :param image_height:
    :param image_width:
    :param image_pixels: Two-dimensional array containing information about color channels of pixels
    :param threshold: Threshold at which we change pixel colors
    :param image:
    :param draw:
    :param file_name: Path in which image is saved
    :return:
    """

    for i in range(image_height):
        for j in range(image_width):
            if image_pixels[i, j][0] <= threshold:
                draw.point((i, j), (0, 0, 0))
            else:
                draw.point((i, j), (255, 255, 255))

    image.save(file_name, "JPEG")


def find_threshold(image_height, image_width, image_pixels):
    """
    Find threshold with Otsu's method
    :param image_width:
    :param image_height:
    :param image_pixels: Two-dimensional array containing information about color channels of pixels
    :return threshold: The best threshold for the white pixel class and the black pixel class to be as clear as possible
    """

    size = 256
    intensity_histogram = [0] * size  # Image intensity histogram

    for i in range(image_height):
        for j in range(image_width):
            intensity_histogram[image_pixels[i, j][0]] += 1

    pixel_count = image_width * image_height  # The number of pixels in the image
    intensity_sum = sum(index * value for index, value in enumerate(intensity_histogram))  # Image intensity
    best_threshold = 0  # Best threshold
    max_sigma = 0.0  # Max interclass variance
    first_class_pixel_count = 0  # The number of pixels in the first group
    first_class_intensity_sum = 0  # First group intensity

    for threshold in range(size - 1):
        first_class_pixel_count += intensity_histogram[threshold]
        first_class_intensity_sum += threshold * intensity_histogram[threshold]

        if pixel_count - first_class_pixel_count == 0 or first_class_pixel_count == 0:
            continue

        # The ratio of pixels in the first group to the total number of pixels
        first_class_prob = first_class_pixel_count / pixel_count

        # The ratio of pixels in the second group to the total number of pixels
        second_class_prob = 1.0 - first_class_prob

        # Average intensity in the first group
        first_class_mean = first_class_intensity_sum / first_class_pixel_count

        # Average intensity in the second group
        second_class_mean = (intensity_sum - first_class_intensity_sum) / (pixel_count - first_class_pixel_count)

        # The difference in the average brightness of the two groups
        mean_delta = first_class_mean - second_class_mean

        # Current interclass variance
        sigma = first_class_prob * second_class_prob * mean_delta * mean_delta

        if sigma > max_sigma:
            max_sigma = sigma
            best_threshold = threshold

    return best_threshold


def start_processing(file_name):
    """
    Along the image path, returns all items for image processing
    :param file_name: Path to the required image
    :returns image processing tools: image, image width, image height, image pixels, draw
    """

    image = Image.open(file_name)
    image_height, image_width, = image.size
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


def parse():
    """
    Parse command line arguments
    :return command line arguments
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('-name', help='Path to image')
    parser.add_argument('-path', help='Path to directory where everything will be saved')

    return parser.parse_args()


def main():
    args = parse()

    if args.name and args.path:
        image, image_height, image_width, image_pixels, draw = start_processing(file_name=args.name)
        threshold = find_threshold(image_height=image_height, image_width=image_width, image_pixels=image_pixels)
        binarization(image_height=image_height, image_width=image_width, image_pixels=image_pixels,
                     threshold=threshold, image=image, draw=draw, file_name=args.path + "binary.jpg")
        end_processing(draw=draw)
    else:
        raise AttributeError("Incorrect number of argument")

#python3 app.py -name "/home/dima/KG/CG/labs/lab61/grayscale_1.jpg" -path "/home/dima/KG/CG/labs/lab61"

if __name__ == '__main__':
    main()