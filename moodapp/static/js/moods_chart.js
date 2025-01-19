console.log("Fichier moods_chart.js chargé !");


fetch('/moods/user/')
    .then(response => response.json())
    .then(data => {
        console.log("Données récupérées :", data);  // Vérifie que les données sont bien récupérées

        // Assurez-vous que les notes sont présentes dans les données
        data.forEach((entry, index) => {
            console.log(`Note pour l'élément ${index} : ${entry.note}`);  // Vérifie que la note est bien extraite
        });

        // Mapping des niveaux d'humeur et couleurs
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

        // Extraction des notes
        const notes = data.map(entry => entry.note || "Pas de note");  // Vérifie que la note est bien présente
        console.log("Notes extraites :", notes);  // Vérification des notes

        // Création du graphique linéaire avec Chart.js
        const ctx = document.getElementById('moodChart');
        if (!ctx) {
            console.error("Impossible de trouver l'élément 'moodChart' !");
            return;
        }

        new Chart(ctx.getContext('2d'), {
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
                    segment: {
                        borderColor: (ctx) => {
                            const nextIndex = ctx.p1DataIndex;
                            return moodColorsList[nextIndex] || '#4CAF50';
                        }
                    },
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
                            title: function(tooltipItem) {
                                const index = tooltipItem[0].dataIndex;
                                return `Date : ${labels[index]}`;
                            },
                            label: function(tooltipItem) {
                                const index = tooltipItem.dataIndex;
                                const moodName = Object.keys(moodMapping).find(key => moodMapping[key] === moodValues[index]);
                                const note = notes[index];  // Récupère la note
                                return `${moodEmojis[moodName]} ${moodName} | Note : ${note}`;
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
                            callback: function(value) {
                                return Object.keys(moodMapping).find(key => moodMapping[key] === value) || "";
                            }
                        },
                        min: 1,
                        max: 5
                    }
                }
            }
        });
    })
    .catch(error => console.error("Erreur lors de la récupération des données :", error));
