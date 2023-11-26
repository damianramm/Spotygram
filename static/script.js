// Get the modal
var modal = document.getElementById("modal");

// Get the button that opens the modal
var btn = document.getElementById("openModal");

// Get the <span> element that closes the modal
var span = document.getElementsByClassName("close")[0];

// When the user clicks on the button, open the modal
btn.onclick = function() {
  modal.style.display = "block";
}

// When the user clicks on <span> (x), close the modal
span.onclick = function() {
  modal.style.display = "none";
}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
  if (event.target == modal) {
    modal.style.display = "none";
  }
}

function redirigir() {
  // Realiza una solicitud AJAX para obtener el JSON
  fetch('/telegram')
    .then(response => response.json())
    .then(data => {
      // Utiliza el nombre del bot en la URL de redirección
      window.location.href = `https://web.telegram.org/k/#@${data.ChatbotURL}`;
    })
    .catch(error => console.error('Error:', error));
}

const formulario = document.getElementById('formulario');

const procesarForm = (event) => {
  event.preventDefault();

  let ChatbotName = document.getElementById('TELEGRAM_BOT_NAME').value;

  const datos = new FormData(event.target);
  const datosCompletos = Object.fromEntries(datos.entries());
  
  // Asegúrate de que los nombres de las claves coincidan exactamente con las claves que esperas en el servidor
  const datosFormateados = {
    SPOTIPY_CLIENT_ID: datosCompletos.SPOTIFY_CLIENT_ID,
    SPOTIPY_CLIENT_SECRET: datosCompletos.SPOTIFY_CLIENT_SECRET,
    TELEGRAM_BOT_TOKEN: datosCompletos.TELEGRAM_BOT_TOKEN,
    TELEGRAM_BOT_NAME: datosCompletos.TELEGRAM_BOT_NAME,
  };
  
  fetch('/enviar_credenciales', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: new URLSearchParams(datosFormateados).toString()
  })
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error('Error:', error));  
}

formulario.addEventListener('submit', procesarForm);

//--------------------------------------
