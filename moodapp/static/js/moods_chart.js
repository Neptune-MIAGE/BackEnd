console.log("Fichier moods_chart.js chargé !");

document.addEventListener("DOMContentLoaded", async function () {
    try {
        const response = await fetch('/moods/user/');
        const data = await response.json();
        console.log("Données récupérées :", data);

        // Mapping des niveaux d'humeur, couleurs et emojis
        const moodMapping = {
            "Awful": 1,
            "Sad": 2,
            "Neutral": 3,
            "Happy": 4,
            "Awesome": 5
        };

        const moodColors = {
            "Awful": '#E53935',     // Rouge
            "Sad": '#FF7043',       // Orange
            "Neutral": '#FFCA28',   // Jaune
            "Happy": '#4CAF50',     // Vert
            "Awesome": '#81C784'    // Vert clair
        };

        const moodEmojis = {
            "Awful": "😡",
            "Sad": "😢",
            "Neutral": "😐",
            "Happy": "😊",
            "Awesome": "😁"
        };

        // Préparation des données pour le graphique linéaire
        const labels = data.map(entry => new Date(entry.date).toLocaleDateString());
        const moodValues = data.map(entry => moodMapping[entry.mood__name]);
        const moodColorsList = data.map(entry => moodColors[entry.mood__name]);

        // Création du graphique linéaire avec Chart.js
        const ctx = document.getElementById('moodChart');
        if (!ctx) {
            console.error("Impossible de trouver l'élément 'moodChart' !");
            return;
        }

        let moodChartInstance = new Chart(ctx.getContext('2d'), {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Évolution des Humeurs',
                    data: moodValues,
                    borderColor: '#4CAF50',
                    pointBackgroundColor: moodColorsList,
                    pointBorderColor: moodColorsList,
                    pointRadius: 5,
                    pointHoverRadius: 7,
                    tension: 0.4,
                    fill: false
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                const moodName = Object.keys(moodMapping).find(key => moodMapping[key] === context.raw);
                                return `${moodEmojis[moodName]} ${moodName}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        title: { display: true, text: 'Date' }
                    },
                    y: {
                        title: { display: true, text: 'Niveau d\'Humeur' },
                        ticks: {
                            callback: function (value) {
                                return Object.keys(moodMapping).find(key => moodMapping[key] === value) || "";
                            }
                        },
                        min: 1,
                        max: 5
                    }
                }
            }
        });

        // Ajout des tendances d'humeur au graphique existant
        fetch('/moods/trends/')
            .then(response => response.json())
            .then(trendData => {
                console.log("Tendances récupérées :", trendData);

                const trendLabels = Object.keys(trendData);
                const trendDatasets = [];

                Object.keys(trendData[trendLabels[0]]).forEach(mood => {
                    trendDatasets.push({
                        label: `Tendance ${mood}`,
                        data: trendLabels.map(date => trendData[date][mood] || 0),
                        borderColor: getRandomColor(),
                        borderWidth: 2,
                        fill: false,
                        borderDash: [5, 5] // Ligne en pointillés pour différencier les tendances
                    });
                });

                if (moodChartInstance) {
                    trendDatasets.forEach(dataset => moodChartInstance.data.datasets.push(dataset));
                    moodChartInstance.update();
                }
            })
            .catch(error => console.error("Erreur lors de la récupération des tendances :", error));

        // Fonction pour générer des couleurs aléatoires
        function getRandomColor() {
            return `hsl(${Math.random() * 360}, 80%, 60%)`;
        }

    } catch (error) {
        console.error("Erreur lors du chargement des données d'humeur :", error);
    }
});
