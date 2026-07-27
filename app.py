import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS 
import google.generativeai as genai
import openai

app = Flask(__name__, static_folder='.') # Configura static_folder para servir archivos estáticos desde el directorio actual
CORS(app) # Habilita CORS para todas las rutas (útil para desarrollo local)

# Carga las claves API de las variables de entorno
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# Configura la API de Google Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("Advertencia: GEMINI_API_KEY no está configurada. Las solicitudes a Gemini fallarán.")

# Configura la API de OpenAI
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY
else:
    print("Advertencia: OPENAI_API_KEY no está configurada. Las solicitudes a OpenAI fallarán.")

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
        return jsonify({'error': 'El prompt es requerido.'}), 400

    full_prompt = (
        f"Eres un arquitecto de software senior y maestro de codificación. Genera un código completo, funcional, "
        f"optimizado para RAM y sin errores, basado en la siguiente descripción. Incluye comentarios claros y "
        f"ejemplos de uso si es necesario. Ajusta el lenguaje y tipo de archivo según la solicitud del usuario. "
        f"Si se solicita una conexión entre archivos, diseña el código para que sea coherente.\n\n"
        f"Descripción: {prompt}"
    )
    
    try:
        if model_choice == 'gemini' and GEMINI_API_KEY:
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(full_prompt)
            result = response.text
        elif model_choice == 'openai' and OPENAI_API_KEY:
            chat_completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", # Puedes usar "gpt-4" o "gpt-4o" si tienes acceso y necesitas mayor calidad
                messages=[
                    {"role": "system", "content": "Eres un arquitecto de software senior. Generas código impecable, funcional, optimizado y con explicaciones detalladas para cualquier lenguaje."},
                    {"role": "user", "content": full_prompt}
                ]
            )
            result = chat_completion.choices[0].message.content
        else:
            return jsonify({'error': f'Modelo "{model_choice}" no disponible o su API Key no está configurada.'}), 500

        return jsonify({'result': result})

    except Exception as e:
        print(f"Error al generar código: {e}")
        return jsonify({'error': f'Error interno del servidor al generar código: {str(e)}'}), 500

@app.route('/get_solution', methods=['POST'])
def get_solution():
    data = request.get_json()
    prompt = data.get('prompt')
    model_choice = data.get('model', 'gemini') # Por defecto a gemini

    if not prompt:
        return jsonify({'error': 'El prompt es requerido.'}), 400

    full_prompt = (
        f"Proporciona una solución detallada, precisa, optimizada y sin errores para el siguiente problema o pregunta "
        f"de programación/tecnología. No inventes nada; usa solo información real y confiable. "
        f"Mantén la realidad de las cosas. Si la respuesta es muy larga, divídela en partes lógicas "
        f"para una mejor comprensión.\n\n"
        f"Pregunta/Problema: {prompt}"
    )

    try:
        if model_choice == 'gemini' and GEMINI_API_KEY:
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(full_prompt)
            result = response.text
        elif model_choice == 'openai' and OPENAI_API_KEY:
            chat_completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", # Puedes usar "gpt-4" o "gpt-4o" si tienes acceso y necesitas mayor calidad
                messages=[
                    {"role": "system", "content": "Eres un experto en tecnología y programación. Proporcionas soluciones precisas, detalladas y sin inventar nada, basándote en conocimientos reales y comprobables. Siempre la realidad de las cosas. Divide las respuestas largas en secciones claras."},
                    {"role": "user", "content": full_prompt}
                ]
            )
            result = chat_completion.choices[0].message.content
        else:
            return jsonify({'error': f'Modelo "{model_choice}" no disponible o su API Key no está configurada.'}), 500

        return jsonify({'result': result})

    except Exception as e:
        print(f"Error al obtener solución: {e}")
        return jsonify({'error': f'Error interno del servidor al obtener solución: {str(e)}'}), 500

if __name__ == '__main__':
    # Para desarrollo local: Ejecuta `python app.py`
    # Para despliegue en producción (e.g., Render), se recomienda usar Gunicorn u otro servidor WSGI.
    app.run(debug=True, port=os.environ.get('PORT', 5000)
