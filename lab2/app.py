import os
from flask import Flask, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename
import cv2
import numpy as np
import traceback


app = Flask(__name__)
app.debug = True

# Configure upload folder
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Allowed extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp'}

def allowed_file(filename):
    return '.' in filename and \
filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        # Check if file part is present
        if 'file' not in request.files:
            return "No file part in the request.", 400
        file = request.files['file']
        if file.filename == '':
            return "No file selected for uploading.", 400
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)  # Prevent directory traversal
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Get selected processing methods
            methods = request.form.getlist('methods')

            # Process the image
            try:
                processed_image_path = process_image(filepath, methods)
            except Exception as e:
                # Log the full traceback
                app.logger.error(f"Error processing image: {e}\n{traceback.format_exc()}")
                return f"An error occurred while processing the image: {e}", 500

            return render_template('result.html', original_image=filepath, processed_image=processed_image_path)
        else:
            return "Invalid file type. Only PNG, JPG, JPEG, and BMP files are allowed.", 400
    return render_template('upload.html')

def process_image(filepath, methods):
    img = cv2.imread(filepath)
    if img is None:
       raise ValueError(f"Could not load image at {filepath}. Ensure the file is an image and in a supported format.")
    result_img = img.copy()
   
    for method in methods:
        if method == 'corners':
            result_img = detect_corners(result_img)
        elif method == 'lines':
            result_img = detect_lines(result_img)
        elif method == 'edges':
            result_img = detect_edges(result_img)
        elif method == 'morphology':
            result_img = morphology_transform(result_img)
        elif method == 'brightness':
            result_img = detect_brightness_changes(result_img)
   
    # Получаем имя файла и расширение
    filename = os.path.basename(filepath)
    filename_without_ext, ext = os.path.splitext(filename)
    if not ext:
        # Если расширение отсутствует, используем по умолчанию .png
        ext = '.png'
   
    # Формируем имя обработанного изображения с расширением
    processed_filename = f'processed_{filename_without_ext}{ext}'
    processed_image_path = os.path.join(app.config['UPLOAD_FOLDER'], processed_filename)
   
    # Сохраняем изображение с корректным расширением
    if not cv2.imwrite(processed_image_path, result_img):
        raise ValueError(f"Could not write image to {processed_image_path}. Check the path and file permissions.")
   
    return processed_image_path

def detect_brightness_changes(img):
    # Преобразуем изображение в оттенки серого, если оно цветное
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img

    # Вычисляем градиент яркости с помощью оператора Sobel
    grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    grad_mag = cv2.magnitude(grad_x, grad_y)
    grad_mag = cv2.convertScaleAbs(grad_mag)

    # Применяем пороговую обработку для выделения значительных перепадов яркости
    _, thresh = cv2.threshold(grad_mag, 50, 255, cv2.THRESH_BINARY)

    # Преобразуем обратно в цветное изображение
    result_img = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
    return result_img


def detect_corners(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = np.float32(gray)
    # Параметры детектора Харриса
    dst = cv2.cornerHarris(gray, blockSize=2, ksize=3, k=0.04)
    dst = cv2.dilate(dst, None)
    # Пороговое значение для определения сильных углов
    img[dst > 0.01 * dst.max()] = [0, 0, 255]
    return img

def detect_lines(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)
    if lines is not None:
        for rho_theta in lines:
            rho, theta = rho_theta[0]
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a * rho
            y0 = b * rho
            x1 = int(x0 + 1000 * (-b))
            y1 = int(y0 + 1000 * (a))
            x2 = int(x0 - 1000 * (-b))

            y2 = int(y0 - 1000 * (a))
            cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
    return img

def detect_edges(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    # Конвертируем обратно в BGR, чтобы объединить с оригиналом
    edges_bgr = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    return edges_bgr

def morphology_transform(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Бинаризация изображения
    _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    # Определение структурного элемента
    kernel = np.ones((5, 5), np.uint8)
    # Применение морфологических операций
    closing = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    # Конвертируем обратно в BGR
    closing_bgr = cv2.cvtColor(closing, cv2.COLOR_GRAY2BGR)
    return closing_bgr

if __name__ == '__main__':
    app.run(debug=True)
