from flask import Flask, request, jsonify, render_template
from algorithms import execute_algorithm

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run_algorithm', methods=['POST'])
def run_algorithm():
    data = request.json
    algorithm = data.get('algorithm')
    params = data.get('parameters')

    # Выполнение выбранного алгоритма
    result = execute_algorithm(algorithm, params)

    return jsonify({'result': result})

if __name__ == '__main__':
    app.run(debug=True)
