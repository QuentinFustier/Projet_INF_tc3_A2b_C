//connecter boutons aux fonctions onklick
document.getElementById('boutonShow').addEventListener('click', clickBoutonShow);
document.getElementById('boutonDist').addEventListener('click', clickBoutonDist);

// Création d'une carte dans la balise div "map",
// et position de la vue sur un point donné et un niveau de zoom
var map = L.map('map').setView([54,13], 4);

// Ajoute d'une couche de dalles OpenStreetMap
L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
     attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
     }).addTo(map);
//rajouter l'échelle
L.control.scale().addTo(map);

//creer le icon vert et bleu
var greenIcon = L.icon({
    iconUrl: 'images/marker-icon-green.png'
});
var normalIcon = L.icon({
    iconUrl: 'images/marker-icon.png'
});

//variables pour gérer les icons des markers
var marker_choisi = null;
var marker_choisi2 = null;
var markers = {};

//les deux listes pour afficher tous les pays
var selectCountry = document.getElementById("selectCountry");
var selectCountry2 = document.getElementById("selectCountry2");

//variables pour enregistrer la distance et les coordonnées lors d'une requete distance pour pouvoir adapter le positionnement et zoom de la carte
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
  //mode 1: appui sur le bouton show ou un marker
  //mode 2: appui sur le bouton distance
  //mode 3: deuxième pour distance => on fait deux requetes, une pour le premier pays, la deuxième pour le deuxième
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

   // fonction callback onload ; dépendant du mode
  if (mode === 1) {
    xhr.onload = callbackMode1;
  }
  else if (mode === 2) {
    xhr.onload = callbackMode2;
  }
  else if (mode === 3) {
    xhr.onload = callBackMode3;
  }

  xhr.send();
}


//fonctions callback de la fonction envoieFormulaire
function callbackMode1() {
  // récupération des informations au format json
      if (this.status === 200) {
        var data = JSON.parse(this.responseText);
        //window.error_msg.innerHTML = '';
        window.affichageDistance.textContent = "";
        updateCountryInfo(data, 1);
        updateMap(data.wp, data.latitude.toFixed(3), data.longitude.toFixed(3), 1);
      }
      // affichage d'un message d'erreur
      else {
        window.country_data.style.display = 'none';
        window.error_msg.innerHTML = this.statusText;
      }
}

function callbackMode2() {
      // récupération des informations au format json
      if (this.status === 200) {
        var data = JSON.parse(this.responseText);
        //window.error_msg.innerHTML = '';
        updateCountryInfo(data, 1);
        updateMap(data.wp, data.latitude.toFixed(3), data.longitude.toFixed(3), 2);
        envoiformulaire(3);
      }
      // affichage d'un message d'erreur
      else {
        window.country_data.style.display = 'none';
        window.error_msg.innerHTML = this.statusText;
      }
}

function callBackMode3() {
      // récupération des informations au format json
      if (this.status === 200) {
        var data = JSON.parse(this.responseText);
        //window.error_msg.innerHTML = '';
        updateCountryInfo(data, 2);
        updateMap(data.wp, data.latitude.toFixed(3), data.longitude.toFixed(3), 3);
      }
      // affichage d'un message d'erreur
      else {
        window.country_data.style.display = 'none';
        window.error_msg.innerHTML = this.statusText;
      }
}


// Fonction appelée lors d'un clic sur un marqueur
function clickMarker (e) {
  selectCountry.value = e.target.name;
  envoiformulaire(1);
}

//fonction onclick du bouton show
function clickBoutonShow(e) {
  envoiformulaire(1);
  //cacher l'affichage du pays deux, au cas où elle est visible
}

//fonction onlick du bouton distance
function clickBoutonDist(e) {
  //fonction pour faire une requete de distance au serveur et afficher le resultat sur l'élement "affichageDistance"
  getDistance(selectCountry.options[selectCountry.selectedIndex].text, selectCountry2.options[selectCountry2.selectedIndex].text);
  //envoiformulaire avec mode 2
  envoiformulaire(2);
}

function fillSelects(name) {
  //fonction pour remplir les listes de pays au lancement du programme
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
  //fonction pour rajouter les markers au lancement du programme
  var marker = L.marker([data.lat,data.lon],{title:data.name}).addTo(map);
      marker.addEventListener('click',clickMarker);
      marker.name = data.name;
      //rajouter les markers à la liste markers pour les retrouver pour changer l'icon
      markers[data.name] = marker;
}


function getDistance(countryOne, countryTwo) {
  //fonction pour faire une requete de distance au serveur et afficher le resultat sur l'élement "affichageDistance"
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
      distance_miles = data.distance_miles.toFixed(0);
      window.affichageDistance.textContent = distance+"km ("+distance_miles+"mi)";
    }
    // affichage d'un message d'erreur
    else {
      window.error_msg.innerHTML = this.statusText;
    }
  };
  xhr.send();
}

function updateMap(name, lat, long, mode) {
  //changer la couleur des markers, centrer la carte sur la capitale et faire un zoom
  var zoom = 6;
  if(mode === 3) {
    //dans le mode 3, le marker du deuxième pays est mis en vert
    //Aussi le zoom est determiné dépendant de la distance
    if (distance < 100) {
      zoom = 8;
    }
    else if (distance < 500) {
      zoom = 7;
    }
    else if (distance < 1400) {
      zoom = 6;
    }
    else if (distance < 2500) {
      zoom = 5;
    }
    else {
      zoom = 4;
    }
    lat = (parseFloat(lat) + parseFloat(lat1))/2;
    long = (parseFloat(long) + parseFloat(long1))/2;
    marker_choisi2 = markers[name];
    marker_choisi2.setIcon(greenIcon);
  }
  else if (mode === 1 || mode === 2){
    //mettre le marker du pays 1 en vert ; la seule différence entre le mode 1 et 2 est que dans le mode 2 la carte n'est pas centrée sur le premier pays
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
  if (mode === 1 || mode === 3)
  {
    map.setView([lat, long], zoom);
  }
}

function updateCountryInfo(data, country_num) {
  //mettre à jour les affichages d'infos du pays 1 ou 2
  if (country_num === 1) {
    window.country_data.style.display = 'block';
    show_hide_country2('hide');
    window.country_name.textContent = data.name;
    window.continent.textContent = data.continent;
    window.capital.textContent = data.capital;
    window.latitude.textContent = data.latitude.toFixed(3);
    window.longitude.textContent = data.longitude.toFixed(3);
    //window.population.textContent = data.population_estimate;
    window.leader_title.textContent = data.leader_title;
    window.leader_name.textContent = data.leader_name;
    window.area.textContent = data.area_km2;
    window.percent_water.textContent = data.percent_water;
    //window.GPD_PPP.textContent = data.GDP_PPP_per_capita;
    //window.currency.textContent = data.currency;
    window.wp.href = 'https://en.wikipedia.org/wiki/' + data.wp;
    window.drapeau.src = "flags/" + data.wp + ".png";
    var src = "leaders/" + data.wp + ".jpg";
    if (data.wp == "Netherlands") {
      src = "leaders/" + data.wp + ".jpeg";
    }
    window.leader.src = src;
    //mettre à jour le audio
    window.hymne1_src.src = data.anthem;
    window.hymne1.load();

  }
  else if (country_num === 2) {
    show_hide_country2('show');
    window.country_data.style.display = 'block';
    window.country_name2.textContent = data.name;
    window.continent2.textContent = data.continent;
    window.capital2.textContent = data.capital;
    window.latitude2.textContent = data.latitude.toFixed(3);
    window.longitude2.textContent = data.longitude.toFixed(3);
    //window.population2.textContent = data.population_estimate;
    window.leader_title2.textContent = data.leader_title;
    window.leader_name2.textContent = data.leader_name;
    window.area2.textContent = data.area_km2;
    window.percent_water2.textContent = data.percent_water;
    //window.GPD_PPP2.textContent = data.GDP_PPP_per_capita;
    //window.currency2.textContent = data.currency;
    window.wp2.href = 'https://en.wikipedia.org/wiki/' + data.wp;
    window.drapeau2.src = "flags/" + data.wp + ".png";
    window.leader2.src = "leaders/" + data.wp + ".jpg";
    //mettre à jour le audio
    var audio = document.getElementById('hymne2');
    //var audio_src = document.getElementById('hymne1_src');
    window.hymne2_src.src = data.anthem;
    audio.load();
  }
}


function show_hide_country2(do_show_or_hide) {
  var opt = '';
  if (do_show_or_hide === 'hide'){
    opt = 'none';
  }
  else if (do_show_or_hide === 'show'){
    opt = 'block';
  }
  window.country_name2.style.display = opt;
    window.continent2.style.display = opt;
    window.capital2.style.display = opt;
    window.latitude2.style.display = opt;
    window.longitude2.style.display = opt;
    window.population2.style.display = opt;
    window.leader_title2.style.display = opt;
    window.leader_name2.style.display = opt;
    window.area2.style.display = opt;
    window.percent_water2.style.display = opt;
    window.GDP_PPP2.style.display = opt;
    window.currency2.style.display = opt;
    window.wp2.style.display = opt;
    window.drapeau2.style.display = opt;
    window.hymne2.style.display = opt;
    window.leader2.style.display = opt;
    window.hymne2.pause();
}
