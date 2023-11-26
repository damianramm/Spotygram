import json
import spotipy
import time
from spotipy.oauth2 import SpotifyOAuth
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import random
#version--- 1.0.0
#El programa funciona bien, pero cuando termina una cancion se para

# Cargar credenciales desde el archivo credenciales.json
with open('credenciales.json') as f:
    credenciales = json.load(f)

# Configurar autenticación de Spotify
sp_auth = SpotifyOAuth(
    client_id=credenciales['SPOTIPY_CLIENT_ID'],
    client_secret=credenciales['SPOTIPY_CLIENT_SECRET'],
    redirect_uri="https://20b0-2800-a4-28b9-7c00-9439-3809-e33d-2346.ngrok-free.app/callback",
    scope='user-modify-playback-state user-read-playback-state user-library-modify user-library-read user-read-recently-played'
)
auth_url = sp_auth.get_authorize_url()
# Crear una instancia de Spotipy para realizar búsquedas
sp = spotipy.Spotify(auth_manager=sp_auth)

# Configurar token del bot de Telegram
TELEGRAM_BOT_TOKEN = credenciales['TELEGRAM_BOT_TOKEN']

# Variable global para almacenar el estado de pausa
manual_pause = False

# Función para manejar el comando /start
def start(update, context):
    update.message.reply_text("¡Hola! Soy tu asistente de música. ¿Cuál es el nombre de la canción que quieres reproducir?")


def handle_text(update, context):
    global manual_pause

    # Obtener el nombre de la canción desde el mensaje del usuario
    nombre_cancion = update.message.text

    # Realizar la búsqueda de la canción en Spotify
    results = sp.search(q=nombre_cancion, type='track', limit=1)

    # Verificar si se encontraron resultados
    if results['tracks']['items']:
        # Obtener la URI de la primera canción encontrada
        track_uri = results['tracks']['items'][0]['uri']

        # Obtener información sobre los dispositivos activos
        devices = sp.devices()

        if devices['devices']:
            # Obtener el ID del primer dispositivo activo
            device_id = devices['devices'][0]['id']

            # Verificar si la reproducción está en pausa
            if manual_pause:
                # Reanudar la reproducción
                sp.start_playback(device_id=device_id)
                manual_pause = False

            # Función para verificar la pausa reflejada
            def check_pause_reflected(context):
                playback_info = sp.current_playback()
                return not playback_info or not playback_info['is_playing']

            # Reproducir la canción en el dispositivo específico
            sp.start_playback(uris=[track_uri], device_id=device_id)

            # Obtener la URL de la imagen de portada de la canción original
            original_track_image_url = results['tracks']['items'][0]['album']['images'][0]['url']

            # Enviar mensaje de confirmación al usuario con la imagen de portada
            update.message.reply_text(
                f"🎶 {results['tracks']['items'][0]['name']} - {results['tracks']['items'][0]['artists'][0]['name']}\n🔊 Dispositivo: {devices['devices'][0]['name']}")
            update.message.reply_photo(original_track_image_url)

            # Obtener canciones relacionadas
            related_tracks = sp.recommendations(seed_tracks=[results['tracks']['items'][0]['id']], limit=5)
        else:
            update.message.reply_text("No se encontraron dispositivos activos en tu cuenta de Spotify.")

    else:
        update.message.reply_text("No se encontraron resultados para la canción proporcionada.")

def search_and_play(nombre_cancion, update):
    # Realizar la búsqueda de la canción en Spotify
    results = sp.search(q=nombre_cancion, type='track', limit=1)

    # Resto del código para reproducir la canción y enviar mensajes de confirmación
    if results['tracks']['items']:
        # Obtener la URI de la primera canción encontrada
        track_uri = results['tracks']['items'][0]['uri']

        # Obtener información sobre los dispositivos activos
        devices = sp.devices()

        if devices['devices']:
            # Obtener el ID del primer dispositivo activo
            device_id = devices['devices'][0]['id']

            # Verificar si la reproducción está en pausa
            if manual_pause:
                # Reanudar la reproducción
                sp.start_playback(device_id=device_id)
                manual_pause = False

            # Obtener el estado actual de reproducción
            playback_info = sp.current_playback()

            # Verificar si ya hay una reproducción en curso
            if playback_info and playback_info['is_playing']:
                # Pausar la reproducción actual
                sp.pause_playback(device_id=device_id)

                # Esperar hasta que la pausa se refleje en el estado de reproducción
                while sp.current_playback()['is_playing']:
                    time.sleep(1)

            # Reproducir la canción en el dispositivo específico
            sp.start_playback(uris=[track_uri], device_id=device_id)
            # Obtener la URL de la imagen de portada de la canción original
            original_track_image_url = results['tracks']['items'][0]['album']['images'][0]['url']

            # Enviar mensaje de confirmación al usuario con la imagen de portada
            update.message.reply_text(f"🎶{results['tracks']['items'][0]['name']} - {results['tracks']['items'][0]['artists'][0]['name']}\n🔊 Dispositivo: {devices['devices'][0]['name']}")
            update.message.reply_photo(original_track_image_url)
        else:
            update.message.reply_text("No se encontraron dispositivos activos en tu cuenta de Spotify.")
    else:
        update.message.reply_text("No se encontraron resultados para la canción proporcionada.")

# Función para manejar el comando /play
def play(update, context):
    global manual_pause
    manual_pause = False

    # Obtener el estado actual de reproducción
    playback_info = sp.current_playback()

    # Verificar si la reproducción está en pausa
    if playback_info and not playback_info['is_playing']:
        # Reanudar la reproducción
        sp.start_playback(device_id=playback_info['device']['id'])
        update.message.reply_text("Reanudando la reproducción.")
    else:
        update.message.reply_text("La reproducción no está en pausa.")

# Función para manejar el comando /pause
def pause(update, context):
    global manual_pause

    # Obtener el estado actual de reproducción
    playback_info = sp.current_playback()

    # Verificar si la reproducción está en pausa
    if playback_info and not playback_info['is_playing']:
        update.message.reply_text("La reproducción ya está en pausa.")
    else:
        manual_pause = True
        # Pausar la reproducción
        sp.pause_playback()
        update.message.reply_text("Reproducción en pausa.")

def next_track(update, context):
    # Obtener información sobre la reproducción actual
    playback_info_before = sp.current_playback()

    # Saltar a la siguiente canción
    sp.next_track()

    # Esperar un breve momento para que la información esté disponible
    time.sleep(1)

    # Obtener información sobre la reproducción después de saltar a la siguiente canción
    playback_info_after = sp.current_playback()

    # Obtener recomendaciones basadas en la última canción reproducida
    if playback_info_before and playback_info_before['item']:
        current_track_uri = playback_info_after['item']['uri']
        recommendations = sp.recommendations(seed_tracks=[current_track_uri], limit=5)

        if recommendations['tracks']:
            # Seleccionar aleatoriamente una canción recomendada
            recommended_track = random.choice(recommendations['tracks'])
            recommended_track_uri = recommended_track['uri']

            # Reproducir la canción recomendada
            sp.start_playback(uris=[recommended_track_uri])

            # Obtener la información de la canción recomendada
            recommended_track_name = recommended_track['name']
            recommended_track_artist = recommended_track['artists'][0]['name']
            recommended_device_name = playback_info_before['device']['name']
            recommended_track_image_url = recommended_track['album']['images'][0]['url']

            # Enviar mensaje de confirmación personalizado al usuario con la imagen de portada
            update.message.reply_text(f"¡Prepárate para la siguiente experiencia musical!\n\nReproduciendo una recomendación especial para ti:\n\n🎶 {recommended_track_name} - {recommended_track_artist}\n🔊 Dispositivo: {recommended_device_name}")
            update.message.reply_photo(recommended_track_image_url)
        else:
            update.message.reply_text("No se encontraron recomendaciones para la canción actual.")
    elif playback_info_after and playback_info_after['is_playing'] and playback_info_after['item']:
        # Si no se pudo obtener información después de saltar a la siguiente canción,
        # intentar reiniciar la reproducción desde la posición actual
        sp.start_playback(uris=[playback_info_after['item']['uri']], device_id=playback_info_after['device']['id'])
        update.message.reply_text("No se pudo obtener información sobre la siguiente canción. Reiniciando desde la posición actual.")
    else:
        update.message.reply_text("No hay información disponible sobre la siguiente canción.")

def like(update, context):
    # Obtener el estado actual de reproducción
    playback_info = sp.current_playback()

    # Verificar si hay una canción en reproducción
    if playback_info and playback_info['is_playing'] and playback_info['item']:
        # Obtener la URI de la canción en reproducción
        track_uri = playback_info['item']['uri']

        # Verificar si la canción ya está en la lista de reproducción de "Me gusta"
        is_liked = is_song_liked(track_uri)

        track_name = playback_info['item']['name']
        track_artist = playback_info['item']['artists'][0]['name']

        if is_liked:
            # Si la canción ya está en la lista de "Me gusta", eliminarla
            sp.current_user_saved_tracks_delete(tracks=[track_uri])
            update.message.reply_text(f"Has quitado '{track_name}' de tu lista de 'Me Gusta' 😢")
        else:
            # Agregar la canción a la lista de reproducción de "Me gusta"
            sp.current_user_saved_tracks_add(tracks=[track_uri])
            update.message.reply_text(f"¡Has agregado '{track_name}' a tu lista de 'Me Gusta'! 👍")
    else:
        update.message.reply_text("No hay ninguna canción reproduciéndose en este momento.")


def is_song_liked(track_uri):
    try:
        liked_tracks = sp.current_user_saved_tracks()
    except spotipy.SpotifyException as e:
        print(f"Error al obtener pistas guardadas: {e}")

    # Verificar si la canción actual está en la lista de "Me gusta"
    return any(track['track']['uri'] == track_uri for track in liked_tracks['items'])

# Función para manejar el comando /historial
def historial(update, context):
    # Obtener el límite deseado del mensaje del usuario, si está disponible
    try:
        limite_deseado = int(context.args[0])
        
        # Verificar si el límite deseado es mayor que el límite máximo permitido (50)
        if limite_deseado > 50:
            update.message.reply_text("El límite especificado es mayor que el límite máximo permitido de 50. Se utilizará el límite máximo.")
            limite_deseado = 50
    except (IndexError, ValueError):
        # Si no se proporciona un límite válido, utilizar un valor predeterminado y enviar un mensaje informativo
        limite_deseado = 5
        update.message.reply_text("El límite especificado no es válido o no se proporcionó. Se utilizará el límite predeterminado de 5.")

    # Obtener las primeras pistas recientemente reproducidas por el usuario
    recently_played = sp.current_user_recently_played(limit=limite_deseado)

    # Verificar si hay pistas recientes disponibles
    if 'items' in recently_played:
        # Limitar la cantidad de pistas a mostrar
        pistas_mostradas = recently_played['items'][:limite_deseado]

        # Mensaje de respuesta inicial
        update.message.reply_text(f"🎵 Aquí están tus últimas {limite_deseado} canciones reproducidas:")

        # Imprimir detalles de las pistas recientes
        for track in pistas_mostradas:
            # Obtener información de la pista
            nombre_cancion = track['track']['name']
            nombre_artista = track['track']['artists'][0]['name']
            nombre_album = track['track']['album']['name']
            portada_url = track['track']['album']['images'][0]['url']

            # Crear mensaje con formato y emojis
            message = f"🎶 {nombre_cancion} - {nombre_artista}\n📀 Álbum: {nombre_album}"
            
            # Enviar mensaje con la portada de la canción
            update.message.reply_photo(portada_url, caption=message)
    else:
        update.message.reply_text("No hay pistas recientes disponibles en tu historial de reproducción.")


def help_command(update, context):
    help_message = """
    Puedes escribir cualquier canción o artista que quieras que se reproduzca.

    Estos son los comandos disponibles:
    /start - Inicia la conversación con el bot.
    /play - Reanuda la reproducción de música.
    /pause - Pausa la reproducción de música.
    /next - Cambia a la siguiente canción.
    /like - Agrega la canción a la lista de Me Gusta.
    /historial + numero - Muestra las ultimas canciones reproducidas.
    /help - Muestra esta ayuda.
    """
    update.message.reply_text(help_message)


def main():
    # Inicializar el bot de Telegram
    updater = Updater(TELEGRAM_BOT_TOKEN)

    # Obtener el despachador para registrar manejadores
    dp = updater.dispatcher

    # Registrar manejadores de comandos
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("play", play))
    dp.add_handler(CommandHandler("pause", pause))
    dp.add_handler(CommandHandler("next", next_track))
    dp.add_handler(CommandHandler("like", like))
    dp.add_handler(CommandHandler("historial", historial))
    dp.add_handler(CommandHandler("help", help_command))
    # Registrar manejador de mensajes de texto
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))

    # Iniciar el bot
    updater.start_polling()

    # Ejecutar el bot hasta que se reciba una señal para detenerlo
    updater.idle()

if __name__ == '__main__':
    main()