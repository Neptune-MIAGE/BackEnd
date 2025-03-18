document.addEventListener("DOMContentLoaded", fetchMoodStreak);

async function fetchMoodStreak() {
    const streakDiv = document.getElementById("mood-streak");

    try {
        // Récupération des humeurs de l'utilisateur
        const response = await fetch('/moods/user_moods_json/');
        const moods = await response.json();

        if (moods.length === 0) {
            streakDiv.innerHTML = "Aucune donnée enregistrée. Commencez dès aujourd'hui !";
            streakDiv.classList.remove("d-none");
            return;
        }

        // Trier les humeurs par date
        moods.sort((a, b) => new Date(b.date) - new Date(a.date));

        let streak = 0;
        let previousDate = new Date(moods[0].date);
        previousDate.setHours(0, 0, 0, 0);

        for (let i = 1; i < moods.length; i++) {
            let currentDate = new Date(moods[i].date);
            currentDate.setHours(0, 0, 0, 0);

            let diffDays = Math.floor((previousDate - currentDate) / (1000 * 60 * 60 * 24));

            if (diffDays === 1) {
                streak++;
            } else if (diffDays > 1) {
                break; // Fin de la série de jours consécutifs
            }

            previousDate = currentDate;
        }

        // Affichage du streak
        if (streak > 1) {
            streakDiv.innerHTML = `🔥 Série d'humeurs positives : <span id="streak-count">${streak}</span> jours consécutifs !`;
            streakDiv.classList.remove("d-none");
        } else {
            streakDiv.innerHTML = "Aucune série active, enregistre ton humeur chaque jour pour commencer un streak !";
            streakDiv.classList.remove("d-none");
        }

    } catch (error) {
        console.error("Erreur lors de la récupération du streak :", error);
        streakDiv.innerHTML = "Impossible de charger les données du streak.";
        streakDiv.classList.remove("d-none");
    }
}
