

document.getElementById('boutonShow').addEventListener('click', clickBoutonShow);
document.getElementById('boutonDist').addEventListener('click', clickBoutonDist);
window.country_data.style.display = 'none';
window.country_data2.style.display = 'none';
// Création d'une carte dans la balise div "map",
// et position de la vue sur un point donné et un niveau de zoom
var map = L.map('map').setView([54,13], 4);

// Ajout d'une couche de dalles OpenStreetMap
L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
     attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
     }).addTo(map);

var greenIcon = L.icon({
    iconUrl: 'images/marker-icon-green.png'
});
var normalIcon = L.icon({
    iconUrl: 'images/marker-icon.png'
});

var marker_choisi = null;
var marker_choisi2 = null;
var markers = {};
var selectCountry = document.getElementById("selectCountry");
var selectCountry2 = document.getElementById("selectCountry2");

var distance = 0;
var lat1 = 0;
var long1 = 0;

// Fonction appelée au chargement de la page
function load_data () {

  // objet pour l'envoi d'une requête Ajax
  var xhr = new XMLHttpRequest();

  // fonction appelée lorsque la réponse à la requête (liste des lieux insolites) sera arrivée
  xhr.onload = function() {

    // transformation des données renvoyées par le serveur
    // responseText est du type string, data est une liste
    var data = JSON.parse(this.responseText);

    // boucle sur les lieux
    for ( n = 0; n < data.length; n++ ) {
      addMarkers(data[n]);
      fillSelects(data[n].name);
    }
  };

  // Envoi de la requête Ajax pour la récupération de la liste des lieux insolites
  xhr.open('GET','/location',true);
  xhr.send();
}



function envoiformulaire(mode) {
   var xhr = new XMLHttpRequest();
   var ps = '';

   // on récupère le nom du pays
  if (mode === 1 || mode === 2) {
    ps = selectCountry.options[selectCountry.selectedIndex].text;
  }
  else if (mode === 3) {
    ps = selectCountry2.options[selectCountry2.selectedIndex].text;
  }

   // requête au serveur
  xhr.open('GET','/service/country/'+ps,true);

  if (mode === 1) {
    xhr.onload = function () {
      // récupération des informations au format json
      if (this.status === 200) {
        var data = JSON.parse(this.responseText);
        //window.error_msg.innerHTML = '';
        updateCountryInfo(data, 1);

        updateMap(data.wp, data.latitude.toFixed(3), data.longitude.toFixed(3), 1);
      }
      // affichage d'un message d'erreur
      else {
        window.country_data.style.display = 'none';
        window.error_msg.innerHTML = this.statusText;
      }
    };
  }
  else if (mode === 2) {
    xhr.onload = function () {
      // récupération des informations au format json
      if (this.status === 200) {
        var data = JSON.parse(this.responseText);
        //window.error_msg.innerHTML = '';
        updateCountryInfo(data, 1);

        updateMap(data.wp, data.latitude.toFixed(3), data.longitude.toFixed(3), 3);

        envoiformulaire(3);
      }
      // affichage d'un message d'erreur
      else {
        window.country_data.style.display = 'none';
        window.error_msg.innerHTML = this.statusText;
      }
    };
  }
  else if (mode === 3) {
    xhr.onload = function () {
      // récupération des informations au format json
      if (this.status === 200) {
        var data = JSON.parse(this.responseText);
        //window.error_msg.innerHTML = '';
        updateCountryInfo(data, 2);

        updateMap(data.wp, data.latitude.toFixed(3), data.longitude.toFixed(3), 2);
      }
      // affichage d'un message d'erreur
      else {
        window.country_data.style.display = 'none';
        window.error_msg.innerHTML = this.statusText;
      }
    };
  }
  // fonction callback

  xhr.send();
}



// Fonction appelée lors d'un clic sur un marqueur
function clickMarker (e) {
  selectCountry.value = e.target.name;
  envoiformulaire(1);
  window.country_data2.style.display = 'none';
}


function clickBoutonShow(e) {
  envoiformulaire(1);
  window.country_data2.style.display = 'none';
}

function clickBoutonDist(e) {
  getDistance(selectCountry.options[selectCountry.selectedIndex].text, selectCountry2.options[selectCountry2.selectedIndex].text);
  envoiformulaire(2);
}

function fillSelects(name) {
    var option1 = document.createElement("option");
    var option2 = document.createElement("option");
    option1.text = name; //le wp
    option1.value = name;
    option2.text = name; //le wp
    option2.value = name;
    selectCountry.add(option1);
    selectCountry2.add(option2);
}

function addMarkers(data) {
  var marker = L.marker([data.lat,data.lon],{title:data.name}).addTo(map);
      marker.addEventListener('click',clickMarker);
      marker.name = data.name;

      markers[data.name] = marker;
}

function getDistance(countryOne, countryTwo) {
   var xhr = new XMLHttpRequest();

   // requête au serveur
   xhr.open('GET','/service/distance/'+countryOne+'/'+countryTwo,true);

   // fonction callback
   xhr.onload = function() {

     // récupération des informations au format json
     if ( this.status === 200 ) {
       var data = JSON.parse(this.responseText);
       //window.error_msg.innerHTML = '';
       distance = data.distance_km.toFixed(0);
       window.affichageDistance.textContent = distance+"km";
     }
     // affichage d'un message d'erreur
     else {
        window.error_msg.innerHTML = this.statusText;
     }
  };
  xhr.send();
}

function updateMap(name, lat, long, mode) {
    //changer la couleur des markers, centrer la carte sur la capitale et faire un zoo
  var zoom = 6;
  if(mode === 2) {
    zoom = Math.round((-3/3943)*distance + 6.8);
    if (zoom < 3){
      zoom = 3;
    }
    lat = (parseFloat(lat) + parseFloat(lat1))/2;
    long = (parseFloat(long) + parseFloat(long1))/2;
    marker_choisi2 = markers[name];
    marker_choisi2.setIcon(greenIcon);
  }
  else if (mode === 1 || mode === 3){
    if(marker_choisi != null){
      marker_choisi.setIcon(normalIcon);
    }
    if(marker_choisi2 != null){
      marker_choisi2.setIcon(normalIcon);
    }
    marker_choisi = markers[name];
    marker_choisi.setIcon(greenIcon);
    lat1 = lat;
    long1 = long;
  }
  if (mode === 1 || mode === 2)
  {
    map.setView([lat, long], zoom);
  }
}


function updateCountryInfo(data, country_num) {
  if (country_num === 1) {
    window.country_data.style.display = 'block';
    window.country_name.textContent = data.name;
    window.continent.textContent = data.continent;
    window.capital.textContent = data.capital;
    window.latitude.textContent = data.latitude.toFixed(3);
    window.longitude.textContent = data.longitude.toFixed(3);
    window.wp.href = 'https://en.wikipedia.org/wiki/' + data.wp;
    window.drapeau.src = "flags/" + data.wp + ".png";
  }
  else if (country_num === 2) {
    window.country_data2.style.display = 'block';
    window.country_name2.textContent = data.name;
    window.continent2.textContent = data.continent;
    window.capital2.textContent = data.capital;
    window.latitude2.textContent = data.latitude.toFixed(3);
    window.longitude2.textContent = data.longitude.toFixed(3);
    window.wp2.href = 'https://en.wikipedia.org/wiki/' + data.wp;
    window.drapeau2.src = "flags/" + data.wp + ".png";
  }

}