import os
import logging
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import google.generativeai as genai
import openai

# Configuración básica de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__, static_folder='.') # Configura static_folder para servir archivos estáticos desde el directorio actual

# Configuración de CORS: ESENCIAL para producción, especifica tus dominios.
# Para desarrollo puedes usar un asterisco, pero ¡NUNCA EN PRODUCCIÓN!
# Ejemplo para producción: CORS(app, resources={r"/*": {"origins": ["https://tu-dominio.onrender.com", "http://localhost:3000"]}})
# Para este despliegue, asumiremos el mismo origen o un entorno controlado, pero se advierte.
# Para Render, si el frontend y backend se sirven desde la misma aplicación Flask,
# es posible que no necesites CORS explícito para las rutas API si el navegador las considera "same-origin".
# Sin embargo, lo mantendremos con una nota para la configuración de producción si se separan los servicios.
CORS(app) # Permisivo para facilitar el desarrollo, ajustar para producción.

# Carga las claves API de las variables de entorno
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# Configura la API de Google Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    logging.info("Google Gemini API configurada.")
else:
    logging.warning("Advertencia: GEMINI_API_KEY no está configurada. Las solicitudes a Gemini fallarán.")

# Configura la API de OpenAI
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY
    logging.info("OpenAI API configurada.")
else:
    logging.warning("Advertencia: OPENAI_API_KEY no está configurada. Las solicitudes a OpenAI fallarán.")

@app.route('/')
def serve_index():
    """Sirve el archivo index.html como la página principal."""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Sirve archivos estáticos como CSS y JS."""
    return send_from_directory(app.static_folder, filename)

@app.route('/generate_code', methods=['POST'])
def generate_code():
    data = request.get_json()
    prompt = data.get('prompt')
    model_choice = data.get('model', 'gemini') # Por defecto a gemini

    if not prompt:
        logging.error("Solicitud de generación de código sin prompt.")
        return jsonify({'error': 'El prompt es requerido para generar código.'}), 400

    full_prompt = (
        f"Eres un ARQUITECTO DE SOFTWARE SENIOR Y MAESTRO DE CODIFICACIÓN, el experto número 1 del mundo. "
        f"Tu misión es generar CÓDIGOS COMPLETOS, FUNCIONALES, OPTIMIZADOS para RAM y rendimiento, y ABSOLUTAMENTE SIN ERRORES. "
        f"BASA TU RESPUESTA EXCLUSIVAMENTE EN HECHOS Y SOLUCIONES REALES Y COMPROBABLES; NO INVENTES NADA NI PROPORCIONES INFORMACIÓN FALSA. "
        f"Siempre proporciona la realidad de las cosas. "
        f"Incluye comentarios CLAROS Y CONCISOS, y EJEMPLOS DE USO si son necesarios. "
        f"AJUSTA el lenguaje de programación y el tipo de archivo según la solicitud del usuario. "
        f"Si la solicitud implica múltiples archivos o componentes, DISEÑA EL CÓDIGO para que estén SIEMPRE CONECTADOS entre sí, "
        f"manteniendo una coherencia y arquitectura impecables. "
        f"No añadas frases de continuación como '¿Deseas continuar?' ya que la aplicación gestiona la paginación de la respuesta completa."
        f"\n\nDESCRIPCIÓN DE LA SOLICITUD DE CÓDIGO:\n{prompt}"
    )
    
    try:
        if model_choice == 'gemini' and GEMINI_API_KEY:
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(full_prompt)
            result = response.text
            logging.info(f"Código generado con Gemini para prompt: {prompt[:50]}...")
        elif model_choice == 'openai' and OPENAI_API_KEY:
            chat_completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", # Considera usar "gpt-4" o "gpt-4o" para mayor calidad y adherencia estricta.
                messages=[
                    {"role": "system", "content": "Eres un arquitecto de software senior y experto global. Generas código impecable, funcional, optimizado y con explicaciones detalladas para cualquier lenguaje, basándote SOLO en la realidad y hechos. Nunca inventas."},
                    {"role": "user", "content": full_prompt}
                ]
            )
            result = chat_completion.choices[0].message.content
            logging.info(f"Código generado con OpenAI para prompt: {prompt[:50]}...")
        else:
            error_msg = f'Modelo "{model_choice}" no disponible o su API Key no está configurada.'
            logging.error(error_msg)
            return jsonify({'error': error_msg}), 500

        return jsonify({'result': result}) # Envuelve el resultado para consistencia

    except Exception as e:
        logging.exception(f"Error al generar código para prompt: {prompt[:50]}...")
        return jsonify({'error': f'Error interno del servidor al generar código: {str(e)}. Por favor, inténtalo de nuevo o revisa tu prompt.'}), 500

@app.route('/get_solution', methods=['POST'])
def get_solution():
    data = request.get_json()
    prompt = data.get('prompt')
    model_choice = data.get('model', 'gemini') # Por defecto a gemini

    if not prompt:
        logging.error("Solicitud de solución sin prompt.")
        return jsonify({'error': 'El prompt es requerido para obtener una solución.'}), 400

    full_prompt = (
        f"Eres un EXPERTO EN TECNOLOGÍA Y PROGRAMACIÓN, el número 1 del mundo en dar soluciones. "
        f"Proporciona una SOLUCIÓN DETALLADA, PRECISA, OPTIMIZADA y ABSOLUTAMENTE SIN ERRORES para el siguiente problema o pregunta "
        f"de programación/tecnología. "
        f"BASA TU RESPUESTA EXCLUSIVAMENTE EN INFORMACIÓN REAL, VERIFICABLE Y CONFIABLE; NO INVENTES NADA, NO DIGAS MENTIRAS. "
        f"Siempre proporciona la realidad de las cosas y las fuentes correctas cuando sea aplicable. "
        f"Si la respuesta es muy larga, ESTRUCTÚRALA y divídela en PARTES LÓGICAS CLARAS para una mejor comprensión, "
        f"como si estuvieras redactando un manual. La aplicación gestionará la paginación, así que no incluyas preguntas de continuación."
        f"\n\nPREGUNTA/PROBLEMA A RESOLVER:\n{prompt}"
    )

    try:
        if model_choice == 'gemini' and GEMINI_API_KEY:
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(full_prompt)
            result = response.text
            logging.info(f"Solución generada con Gemini para prompt: {prompt[:50]}...")
        elif model_choice == 'openai' and OPENAI_API_KEY:
            chat_completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", # Considera usar "gpt-4" o "gpt-4o" para mayor calidad y adherencia estricta.
                messages=[
                    {"role": "system", "content": "Eres un experto en tecnología y programación. Proporcionas soluciones precisas, detalladas y sin inventar nada, basándote en conocimientos reales y comprobables. Siempre la realidad de las cosas. Divide las respuestas largas en secciones claras. Nunca inventes."},
                    {"role": "user", "content": full_prompt}
                ]
            )
            result = chat_completion.choices[0].message.content
            logging.info(f"Solución generada con OpenAI para prompt: {prompt[:50]}...")
        else:
            error_msg = f'Modelo "{model_choice}" no disponible o su API Key no está configurada.'
            logging.error(error_msg)
            return jsonify({'error': error_msg}), 500

        return jsonify({'result': result})

    except Exception as e:
        logging.exception(f"Error al obtener solución para prompt: {prompt[:50]}...")
        return jsonify({'error': f'Error interno del servidor al obtener solución: {str(e)}. Por favor, inténtalo de nuevo o revisa tu prompt.'}), 500

if __name__ == '__main__':
    # Para desarrollo local: Ejecuta `python app.py`
    # Para despliegue en producción (e.g., Render), se recomienda usar Gunicorn u otro servidor WSGI.
    # Usamos os.environ.get('PORT', 5000) para que Render pueda inyectar el puerto si es necesario.
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
