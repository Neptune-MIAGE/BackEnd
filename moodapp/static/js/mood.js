// Fonction pour convertir le temps en humeur
function getMoodFromWeather(weatherCode) {
    if (weatherCode === 0) return "Awesome"; // Clear
    if (weatherCode === 1) return "Happy";  // Partially clear
    if (weatherCode === 3) return "Neutral"; // Cloudy
    if (weatherCode === 61) return "Sad";   // Rain
    return "Happy"; // Valeur par défaut
}

// Fonction pour récupérer les données météo d'Open-Meteo
async function fetchWeatherAndSuggestMood() {
    const suggestedMoodDiv = document.getElementById('suggested-mood');
    const suggestedMoodText = document.getElementById('suggested-mood-text');

    try {
        console.log("Récupération des données météo...");
        // Coordonnées fictives (Paris)
        const latitude = 48.8566;
        const longitude = 2.3522;

        // Requête à Open-Meteo
        const response = await fetch(
            `https://api.open-meteo.com/v1/forecast?latitude=${latitude}&longitude=${longitude}&current_weather=true`
        );
        const data = await response.json();
        console.log("Données récupérées : ", data);

        // Extraction de la météo actuelle
        const weatherCode = data.current_weather.weathercode; // Exemple de code météo
        const mood = getMoodFromWeather(weatherCode);
        console.log("Humeur suggérée : ", mood);

        // Affichage de la suggestion d’humeur
        suggestedMoodText.textContent = `Suggestion : Basé sur la météo actuelle, nous recommandons l'humeur "${mood}" !`;
        suggestedMoodDiv.classList.remove('d-none');  // On retire 'd-none' pour afficher la suggestion
    } catch (error) {
        console.error("Erreur lors de la récupération des données météo :", error);
        suggestedMoodText.textContent = "Impossible de récupérer la météo pour le moment.";
        suggestedMoodDiv.classList.remove('d-none');  // On retire 'd-none' pour afficher l'erreur
    }
}

async function fetchTodayMood() {
    try {
        const response = await fetch('/moods/user_moods_json/');
        const moods = await response.json();
        
        if (moods.length > 0) {
            const lastMood = moods[moods.length - 1];  // Dernière humeur enregistrée
            const moodText = document.getElementById("mood-text");
            const moodMessage = document.getElementById("mood-message");
            const moodDiv = document.getElementById("today-mood");

            const moodEmojis = { "Awesome": "😁", "Happy": "😊", "Neutral": "😐", "Sad": "😢", "Awful": "😡" };
            const moodMessages = { 
                "Awesome": "Tu es au top aujourd'hui !", 
                "Happy": "Belle journée en perspective !", 
                "Neutral": "Une journée classique.", 
                "Sad": "Besoin d’un petit remontant ?", 
                "Awful": "Courage, ça ira mieux demain !"
            };

            moodText.innerHTML = `${moodEmojis[lastMood.mood__name]} ${lastMood.mood__name}`;
            moodMessage.innerText = moodMessages[lastMood.mood__name] || "";

            // Vérifie si lastMood est valide et met à jour l'affichage
            if (lastMood && lastMood.mood__name) {
                moodDiv.classList.remove("d-none");
            } else {
                moodDiv.classList.add("d-none"); // Cache si aucune humeur
            }

            // Modifier la couleur selon l'humeur
            const moodColors = { "Awesome": "success", "Happy": "primary", "Neutral": "secondary", "Sad": "warning", "Awful": "danger" };
            moodDiv.classList.add(`alert-${moodColors[lastMood.mood__name]}`);
        }
    } catch (error) {
        console.error("Erreur lors de la récupération de l'humeur du jour :", error);
    }


    
    // Exécuter la récupération du streak au chargement de la page
    document.addEventListener("DOMContentLoaded", fetchMoodStreak);
    
    
    // Charger le streak au chargement de la page
    document.addEventListener("DOMContentLoaded", fetchMoodStreak);
    
}


// Charger l'humeur du jour au chargement de la page
document.addEventListener("DOMContentLoaded", fetchTodayMood);



// Charger la suggestion d'humeur au chargement de la page
document.addEventListener('DOMContentLoaded', fetchWeatherAndSuggestMood);