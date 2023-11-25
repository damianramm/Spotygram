import json

from flask import Flask, request, jsonify

app = Flask(__name__)

# Ruta al archivo donde se guardarán las credenciales
ARCHIVO_CREDENCIALES = 'credenciales.json'

@app.route('/enviar_credenciales', methods=['POST'])
def recibir_credenciales():
    datos_credenciales = request.get_json()

    # Validar que se proporcionaron todas las credenciales necesarias
    if 'spotify' in datos_credenciales and 'telegram' in datos_credenciales:
        # Guardar el JSON de credenciales en un archivo
        with open(ARCHIVO_CREDENCIALES, 'w') as f:
            json.dump(datos_credenciales, f, indent=2)
        return jsonify({'mensaje': 'Credenciales recibidas y guardadas correctamente'})
    else:
        return jsonify({'error': 'No se proporcionaron todas las credenciales necesarias'})

if __name__ == '__main__':
    app.run(debug=True)
