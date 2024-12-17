import argparse
import matplotlib.pyplot as plt
from PIL import Image


def calculate_histogram(image, channel):
    """
    Calculate histogram data for a specific color channel or luminosity directly from an image object.
    :param image: PIL.Image.Image object
    :param channel: Channel index (0 - Red, 1 - Green, 2 - Blue, 3 - Luminosity)
    :return: Histogram data as a list
    """
    width, height = image.size
    pixels = image.getcolors(width * height)  # Get pixel data (count, color tuples)

    histogram = [0] * 256
    for count, rgb in pixels:
        if channel == 3:  # Luminosity calculation
            brightness = round(0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2])
            histogram[brightness] += count
        else:
            histogram[rgb[channel]] += count
    return histogram


def save_histogram(data, output_path, title):
    """
    Save histogram plot to the specified path.
    :param data: List of histogram values
    :param output_path: Path to save the histogram image
    :param title: Title for the histogram
    """
    plt.figure()
    plt.bar(range(256), data, width=1, color='darkviolet')
    plt.title(title)
    plt.xlabel('Value Range')
    plt.ylabel('Number of Values')
    plt.xlim([0, 255])
    plt.ylim([0, max(data) * 1.1])
    plt.xticks(range(0, 256, 20))
    plt.savefig(output_path)
    plt.close()


def generate_histograms(image, output_dir):
    """
    Generate histograms for R, G, B, luminosity, and RGB average directly from an image object.
    :param image: PIL.Image.Image object
    :param output_dir: Directory to save histogram images
    """
    # Calculate histograms for R, G, B, and Luminosity channels
    channels = ['Red', 'Green', 'Blue', 'Luminosity']
    histograms = [calculate_histogram(image, i) for i in range(3)]
    histograms.append(calculate_histogram(image, channel=3))
    
    # Calculate average RGB histogram
    rgb_average = [
        round(sum(channel[i] for channel in histograms[:3]) / 3)
        for i in range(256)
    ]
    histograms.append(rgb_average)

    # Save histograms to files
    file_names = ["red", "green", "blue", "luminosity", "rgb"]
    for hist, file_name, title in zip(histograms, file_names, channels + ['RGB Average']):
        save_histogram(hist, f"{output_dir}/{file_name}_histogram.png", f"{title} Histogram")


def load_image(image_path):
    """
    Load image from a file path.
    :param image_path: Path to the image file
    :return: Loaded PIL.Image.Image object
    """
    return Image.open(image_path)


def parse_arguments():
    """
    Parse command-line arguments for image processing.
    :return: Parsed arguments
    """
    parser = argparse.ArgumentParser(description="Generate histograms for an image.")
    parser.add_argument('-name', required=True, help='Path to the image file')
    parser.add_argument('-path', required=True, help='Path to the output directory')
    return parser.parse_args()


def main():
    args = parse_arguments()

    # Load the image once
    image = load_image(args.name)

    # Generate and save histograms
    generate_histograms(image, args.path)

#python3 app.py -name "/home/dima/KG/CG/labs/lab5/download (1).jpeg" -path "/home/dima/KG/CG/labs/lab5"

if __name__ == '__main__':
    main()
