document.addEventListener('DOMContentLoaded', () => {
    const promptInput = document.getElementById('promptInput');
    const generateCodeBtn = document.getElementById('generateCodeBtn');
    const getSolutionBtn = document.getElementById('getSolutionBtn');
    const aiModelSelect = document.getElementById('aiModel');
    const outputArea = document.getElementById('outputArea');
    const loadingDiv = document.getElementById('loading');
    const errorDiv = document.getElementById('error');
    const continuationControls = document.getElementById('continuationControls');
    const continueBtn = document.getElementById('continueBtn');

    const CHUNK_SIZE = 800; // Caracteres por fragmento para mostrar
    let fullResponse = '';
    let currentPosition = 0;

    // Función para mostrar el estado de carga
    function showLoading(show) {
        loadingDiv.style.display = show ? 'block' : 'none';
        errorDiv.style.display = 'none';
        generateCodeBtn.disabled = show;
        getSolutionBtn.disabled = show;
        promptInput.disabled = show;
        aiModelSelect.disabled = show;
    }

    // Función para mostrar un error
    function showError(message) {
        errorDiv.textContent = `Error: ${message}`;
        errorDiv.style.display = 'block';
        outputArea.textContent = ''; // Limpiar salida previa
        continuationControls.style.display = 'none';
    }

    // Función para añadir un fragmento de la respuesta al área de salida
    function displayNextChunk() {
        if (currentPosition >= fullResponse.length) {
            continuationControls.style.display = 'none';
            return;
        }

        const nextChunk = fullResponse.substring(currentPosition, currentPosition + CHUNK_SIZE);
        outputArea.textContent += nextChunk;
        currentPosition += CHUNK_SIZE;

        if (currentPosition < fullResponse.length) {
            continuationControls.style.display = 'block';
        } else {
            continuationControls.style.display = 'none';
        }
        outputArea.scrollTop = outputArea.scrollHeight; // Auto-scroll to bottom
    }

    // Función para restablecer el estado de la salida
    function resetOutputState() {
        fullResponse = '';
        currentPosition = 0;
        outputArea.textContent = '';
        continuationControls.style.display = 'none';
        errorDiv.style.display = 'none';
    }

    // Función genérica para enviar solicitud al backend
    async function sendRequest(endpoint) {
        resetOutputState();
        showLoading(true);

        const prompt = promptInput.value.trim();
        const aiModel = aiModelSelect.value;

        if (!prompt) {
            showError('Por favor, ingresa una descripción para el código o la solución.');
            showLoading(false);
            return;
        }

        try {
            // Asumiendo que el backend se ejecutará en el mismo host/puerto durante el desarrollo.
            // Para despliegue en Render, esta URL deberá ser la URL de tu servicio backend.
            // Por ejemplo: const backendUrl = 'https://tu-servicio-backend.onrender.com';
            // fetch(`${backendUrl}/${endpoint}`, { ... });
            
            const response = await fetch(`/${endpoint}`, { 
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ prompt, model: aiModel }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `Error HTTP: ${response.status}`);
            }

            const data = await response.json();
            fullResponse = data.result;
            displayNextChunk();

        } catch (error) {
            console.error('Error al comunicarse con el servidor:', error);
            showError(`No se pudo obtener la respuesta. (${error.message})`);
        } finally {
            showLoading(false);
        }
    }

    generateCodeBtn.addEventListener('click', () => sendRequest('generate_code'));
    getSolutionBtn.addEventListener('click', () => sendRequest('get_solution'));
    continueBtn.addEventListener('click', displayNextChunk);
});
