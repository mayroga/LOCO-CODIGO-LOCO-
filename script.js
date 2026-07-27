document.addEventListener('DOMContentLoaded', () => {
    const promptInput = document.getElementById('promptInput');
    const generateCodeBtn = document.getElementById('generateCodeBtn');
    const getSolutionBtn = document.getElementById('getSolutionBtn');
    const aiModelSelect = document.getElementById('aiModel');
    const outputArea = document.getElementById('outputArea'); // Ahora es un <code> dentro de <pre>
    const loadingDiv = document.getElementById('loading');
    const errorDiv = document.getElementById('error');
    const continuationControls = document.getElementById('continuationControls');
    const continueBtn = document.getElementById('continueBtn');
    const copyBtn = document.getElementById('copyBtn');

    const CHUNK_SIZE_LINES = 15; // Mostrar aproximadamente 15 líneas por fragmento
    const CHUNK_SIZE_CHARS = 1000; // Fallback: 1000 caracteres si no hay saltos de línea
    let fullResponse = '';
    let currentPosition = 0;
    let displayedContent = ''; // Contenido que se ha mostrado hasta ahora

    // Función para mostrar el estado de carga
    function showLoading(show) {
        loadingDiv.style.display = show ? 'block' : 'none';
        errorDiv.style.display = 'none';
        generateCodeBtn.disabled = show;
        getSolutionBtn.disabled = show;
        promptInput.disabled = show;
        aiModelSelect.disabled = show;
        copyBtn.style.display = 'none'; // Ocultar copiar al cargar
    }

    // Función para mostrar un error
    function showError(message) {
        errorDiv.textContent = `Error: ${message}`;
        errorDiv.style.display = 'block';
        outputArea.textContent = ''; // Limpiar salida previa
        displayedContent = '';
        continuationControls.style.display = 'none';
        copyBtn.style.display = 'none';
    }

    // Función para aplicar resaltado de sintaxis
    function applySyntaxHighlighting() {
        // Asegúrate de que Highlight.js esté disponible
        if (typeof hljs !== 'undefined') {
            outputArea.innerHTML = hljs.highlightAuto(displayedContent).value;
        } else {
            outputArea.textContent = displayedContent; // Fallback si hljs no carga
        }
        outputArea.parentElement.scrollTop = outputArea.parentElement.scrollHeight; // Auto-scroll
    }

    // Función para añadir un fragmento de la respuesta al área de salida
    function displayNextChunk() {
        if (currentPosition >= fullResponse.length) {
            continuationControls.style.display = 'none';
            copyBtn.style.display = 'block'; // Mostrar copiar solo al final
            return;
        }

        let nextChunk = '';
        const remainingResponse = fullResponse.substring(currentPosition);
        const lines = remainingResponse.split('\n');

        // Intentar chunking por líneas
        if (lines.length > 1) {
            let chunkLines = 0;
            let currentChunkLength = 0;
            for (let i = 0; i < lines.length; i++) {
                if (chunkLines < CHUNK_SIZE_LINES || currentChunkLength < CHUNK_SIZE_CHARS) {
                    nextChunk += lines[i] + '\n';
                    chunkLines++;
                    currentChunkLength += lines[i].length + 1; // +1 por el salto de línea
                } else {
                    break;
                }
            }
            // Asegurarse de no cortar una línea si la última línea del chunk excede CHUNK_SIZE_CHARS
            // Esta lógica simple puede mejorarse para ser más robusta con código
            currentPosition += nextChunk.length;
        } else {
            // Si no hay saltos de línea (una línea muy larga), chunk por caracteres
            nextChunk = remainingResponse.substring(0, CHUNK_SIZE_CHARS);
            currentPosition += nextChunk.length;
        }
        
        displayedContent += nextChunk;
        applySyntaxHighlighting(); // Aplicar resaltado al contenido acumulado

        if (currentPosition < fullResponse.length) {
            continuationControls.style.display = 'block';
            copyBtn.style.display = 'none'; // Ocultar copiar si hay más contenido
        } else {
            continuationControls.style.display = 'none';
            copyBtn.style.display = 'block'; // Mostrar copiar al final
        }
    }

    // Función para restablecer el estado de la salida
    function resetOutputState() {
        fullResponse = '';
        currentPosition = 0;
        displayedContent = '';
        outputArea.textContent = ''; // Limpiar el texto sin resaltado
        continuationControls.style.display = 'none';
        errorDiv.style.display = 'none';
        copyBtn.style.display = 'none';
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
            if (data.result) {
                fullResponse = data.result;
                displayNextChunk();
            } else {
                showError('La respuesta del servidor no contiene un resultado válido.');
            }

        } catch (error) {
            console.error('Error al comunicarse con el servidor:', error);
            showError(`No se pudo obtener la respuesta. (${error.message})`);
        } finally {
            showLoading(false);
        }
    }

    // Event listener para el botón de copiar
    copyBtn.addEventListener('click', () => {
        const textToCopy = fullResponse; // Copiar el contenido completo, no solo lo mostrado
        navigator.clipboard.writeText(textToCopy).then(() => {
            // Animación de feedback
            copyBtn.textContent = '¡Copiado!';
            setTimeout(() => {
                copyBtn.textContent = 'Copiar al Portapapeles';
            }, 1500);
        }).catch(err => {
            console.error('Error al copiar:', err);
            alert('Error al copiar el texto.');
        });
    });

    generateCodeBtn.addEventListener('click', () => sendRequest('generate_code'));
    getSolutionBtn.addEventListener('click', () => sendRequest('get_solution'));
    continueBtn.addEventListener('click', displayNextChunk);
});
