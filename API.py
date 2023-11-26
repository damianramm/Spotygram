import json
import os
from flask import Flask, request, jsonify, render_template, redirect, session
from spotipy.oauth2 import SpotifyOAuth

template_folder = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'templates')
static_folder = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static')

app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)

# Obtener la ruta del directorio actual del script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Obtener la ruta completa al archivo 'credenciales.json'
credentials_path = os.path.join(script_dir, 'credenciales.json')

# Generar una clave secreta aleatoria (puedes cambiar esto en un entorno de producción)
app.secret_key = os.urandom(24)

# Ruta al archivo donde se guardarán las credenciales
ARCHIVO_CREDENCIALES = 'credenciales.json'

@app.route('/index')
def index():
    # Servir el archivo index.html desde el directorio actual
    return render_template('index.html')

@app.route('/callback')
def callback():
    # Obtener el código de autorización de la URL de retorno
    code = request.args.get('code')

    with open('credenciales.json') as f:
        credenciales = json.load(f)

    # Configurar el auth_manager con la clave secreta
    sp_oauth = SpotifyOAuth(
        client_id=credenciales['SPOTIPY_CLIENT_ID'],
        client_secret=credenciales['SPOTIPY_CLIENT_SECRET'],
        redirect_uri="https://261a-2800-a4-29ec-8700-9439-3809-e33d-2346.ngrok-free.app/callback",
        scope='user-modify-playback-state user-read-playback-state user-library-modify user-library-read user-read-recently-played'
    )
    try:
        token_info = sp_oauth.get_access_token(code)
        access_token = token_info['access_token']
        refresh_token = token_info['refresh_token']

        # Almacenar los tokens en la sesión del usuario
        session['access_token'] = access_token
        session['refresh_token'] = refresh_token

    except Exception as e:
        print(f"Error durante el proceso de autorización: {str(e)}")

    # Redirigir al usuario a la página principal o a donde sea necesario
    return redirect('/index')

@app.route('/credenciales')
def credenciales():
    return render_template('credentials.html')

@app.route('/enviar_credenciales', methods=['POST'])
def recibir_credenciales():
    # Obtener los datos del formulario
    datos_credenciales = request.form

    # Validar que se proporcionaron todas las credenciales necesarias
    print(datos_credenciales)  # Imprime los datos del formulario para depuración
    if 'SPOTIPY_CLIENT_ID' in datos_credenciales and 'SPOTIPY_CLIENT_SECRET' in datos_credenciales and 'TELEGRAM_BOT_TOKEN' in datos_credenciales \
        and 'TELEGRAM_BOT_NAME' in datos_credenciales:

        # Guardar los datos del formulario en un archivo
        with open(ARCHIVO_CREDENCIALES, 'w') as f:
            json.dump(datos_credenciales, f, indent=2)

        return jsonify({'mensaje': 'Credenciales recibidas y guardadas correctamente'})
    else:
        return jsonify({'error': 'No se proporcionaron todas las credenciales necesarias'})

@app.route('/telegram', methods=['GET'])
def obtener_chatbot_url():
    with open(ARCHIVO_CREDENCIALES) as f:
        credenciales = json.load(f)
        return jsonify({'ChatbotURL': credenciales.get('TELEGRAM_BOT_NAME', '')})

if __name__ == '__main__':
    app.run(debug=True)