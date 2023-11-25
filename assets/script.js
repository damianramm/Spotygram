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

let ChatbotURL = localStorage.getItem("ChatbotURL");

function redirigir(){
  window.location.href = `https://web.telegram.org/k/#@$${ChatbotURL}`;
};
const formulario = document.getElementById('formulario')

const procesarForm = (event) =>
{
  event.preventDefault();
 
let ChatbotName = document.getElementById('TELEGRAM_BOT_NAME').value;
//let URLChatbot = `https://web.telegram.org/k/#@$${ChatbotURL.value}`;

  const datos = new FormData(event.target);
  const datosCompletos = Object.fromEntries(datos.entries());
  console.log(JSON.stringify(datosCompletos));
  console.log(ChatbotName);
 
  localStorage.setItem("ChatbotURL", `https://web.telegram.org/k/#@${ChatbotName}`);
  
}

formulario.addEventListener('submit', procesarForm);

//--------------------------------------

//  ElBrujaATodaCumbiabot
