document.getElementById('algorithm').addEventListener('change', function() {
    const selectedAlgorithm = this.value;
    const parametersDiv = document.getElementById('parameters');
    parametersDiv.innerHTML = ''; // Очистить предыдущие параметры

    switch (selectedAlgorithm) {
        case 'step_by_step':
        case 'dda':
        case 'bresenham_line':
            // Параметры для отрисовки линии
            createParameterInput(parametersDiv, 'x1', 'X1:', 'number', '5');
            createParameterInput(parametersDiv, 'y1', 'Y1:', 'number', '5');
            createParameterInput(parametersDiv, 'x2', 'X2:', 'number', '45');
            createParameterInput(parametersDiv, 'y2', 'Y2:', 'number', '45');
            break;
        case 'bresenham_circle':
            // Параметры для отрисовки окружности
            createParameterInput(parametersDiv, 'xc', 'X центра:', 'number', '25');
            createParameterInput(parametersDiv, 'yc', 'Y центра:', 'number', '25');
            createParameterInput(parametersDiv, 'radius', 'Радиус:', 'number', '20');
            break;
        default:
            // Если алгоритм не выбран или опция сбросилась
            parametersDiv.innerHTML = '';
            break;
    }
});


document.getElementById('runButton').addEventListener('click', function() {
    const selectedAlgorithm = document.getElementById('algorithm').value;

    if (!selectedAlgorithm) {
        alert('Пожалуйста, выберите алгоритм.');
        return;
    }

    const parameters = collectParameters();

    // Отправка запроса на сервер
    fetch('/run_algorithm', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            algorithm: selectedAlgorithm,
            parameters: parameters
        })
    })
    .then(response => response.json())
    .then(data => {
        // Обработка результата
        const resultImage = document.getElementById('resultImage');
        resultImage.src = 'data:image/png;base64,' + data.result;
    })
    .catch(error => {
        console.error('Ошибка:', error);
    });
});

function createParameterInput(container, id, labelText, type, defaultValue) {
    const label = document.createElement('label');
    label.for = id;
    label.textContent = labelText;

    const input = document.createElement('input');
    input.type = type;
    input.id = id;
    input.value = defaultValue || '';

    container.appendChild(label);
    container.appendChild(input);
    container.appendChild(document.createElement('br'));
}



function collectParameters() {
    const inputs = document.querySelectorAll('#parameters input');
    const params = {};

    inputs.forEach(input => {
        params[input.id] = input.value;
    });

    return params;
}
