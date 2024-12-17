import os
from flask import Flask, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename
import cv2
import numpy as np
import traceback


app = Flask(__name__)
app.debug = True

app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp'}

def allowed_file(filename):
    return '.' in filename and \
filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file part in the request.", 400
        file = request.files['file']
        if file.filename == '':
            return "No file selected for uploading.", 400
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            methods = request.form.getlist('methods')

            try:
                processed_image_path = process_image(filepath, methods)
            except Exception as e:
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
        elif method == 'points':
            result_img = detect_points(result_img)
   
    filename = os.path.basename(filepath)
    filename_without_ext, ext = os.path.splitext(filename)
    if not ext:
        ext = '.png'
   
    processed_filename = f'processed_{filename_without_ext}{ext}'
    processed_image_path = os.path.join(app.config['UPLOAD_FOLDER'], processed_filename)
   
    if not cv2.imwrite(processed_image_path, result_img):
        raise ValueError(f"Could not write image to {processed_image_path}. Check the path and file permissions.")
   
    return processed_image_path

def detect_brightness_changes(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    grad_mag = cv2.magnitude(grad_x, grad_y)
    grad_mag = cv2.convertScaleAbs(grad_mag)

    _, thresh = cv2.threshold(grad_mag, 50, 255, cv2.THRESH_BINARY)


    result_img = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
    return result_img


def detect_corners(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = np.float32(gray)
    dst = cv2.cornerHarris(gray, blockSize=2, ksize=3, k=0.04)
    dst = cv2.dilate(dst, None)
    img[dst > 0.01 * dst.max()] = [0, 0, 255]
    return img

def detect_lines(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLines(edges, 1, np.pi / 180, 100)
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
            cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
    return img

def detect_edges(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    edges_bgr = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    return edges_bgr

def detect_points(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    params = cv2.SimpleBlobDetector_Params()
    params.filterByArea = True
    params.minArea = 100
    params.filterByCircularity = False
    params.filterByConvexity = False
    params.filterByInertia = False
    detector = cv2.SimpleBlobDetector_create(params)
    keypoints = detector.detect(gray)
    img_final = cv2.drawKeypoints(img, keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    return img_final

def morphology_transform(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)
    kernel = np.ones((5, 5), np.uint8)
    closing = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    closing_bgr = cv2.cvtColor(closing, cv2.COLOR_GRAY2BGR)
    return closing_bgr

if __name__ == '__main__':
    app.run(debug=True)
