console.log("Fichier moods_chart.js chargé !");

document.addEventListener("DOMContentLoaded", () => {
    fetch('/moods/user/') // Récupération des données JSON depuis Django
        .then(response => response.json())
        .then(data => {
            console.log("Données récupérées :", data);

            // Mapping des niveaux d'humeur, couleurs, emojis
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
                                label: function(context) {
                                    const moodName = Object.keys(moodMapping).find(key => moodMapping[key] === context.raw);
                                    return `${moodEmojis[moodName]} ${moodName}`; // Correction ici
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

            // Génération du compteur d'humeurs
            const moodCounts = data.reduce((acc, entry) => {
                acc[entry.mood__name] = (acc[entry.mood__name] || 0) + 1;
                return acc;
            }, {});

            const totalMoods = Object.values(moodCounts).reduce((a, b) => a + b, 0);

            const moodCounterContainer = document.getElementById('moodCounter');
            if (moodCounterContainer) {
                moodCounterContainer.innerHTML = '';
                Object.keys(moodCounts).forEach(mood => {
                    const countElement = document.createElement('div');
                    countElement.innerHTML = `
                        <div class="text-center mx-3" style="color: ${moodColors[mood]}">
                            <span style="font-size: 2rem;">${moodEmojis[mood]}</span><br>
                            <strong>${moodCounts[mood]}</strong>
                        </div>
                    `;
                    moodCounterContainer.appendChild(countElement);
                });
            }

            // Préparation des données pour le cercle entier
            const moodArcLabels = Object.keys(moodCounts);
            const moodArcData = Object.values(moodCounts);
            const moodArcColors = moodArcLabels.map(label => moodColors[label]);

            // Création du plugin pour afficher le texte au centre
            const centerTextPlugin = {
                id: 'centerText',
                beforeDraw(chart) {
                    const { ctx, width } = chart;
                    ctx.save();
                    ctx.font = 'bold 20px Arial';
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillStyle = '#333';
                    ctx.fillText(`${totalMoods}`, width / 2, chart.chartArea.height / 2 + chart.chartArea.top); // Correction ici
                    ctx.restore();
                }
            };

            // Création du graphique en cercle entier
            const arcCtx = document.getElementById('moodArcChart');
            if (arcCtx) {
                new Chart(arcCtx.getContext('2d'), {
                    type: 'doughnut',
                    data: {
                        labels: moodArcLabels.map(label => `${moodEmojis[label]} ${label}`), // Correction ici
                        datasets: [{
                            label: 'Répartition des Humeurs',
                            data: moodArcData,
                            backgroundColor: moodArcColors,
                            hoverOffset: 10
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: {
                                display: true,
                                position: 'top',
                                labels: {
                                    usePointStyle: true,
                                    font: {
                                        size: 14
                                    }
                                }
                            },
                            tooltip: {
                                callbacks: {
                                    label: function(context) {
                                        const moodName = context.label.split(' ')[1];
                                        return `${moodEmojis[moodName]} ${moodName}: ${context.raw}`; // Correction ici
                                    }
                                }
                            }
                        },
                        layout: {
                            padding: 10
                        },
                        cutout: '50%', // Centre ouvert
                        aspectRatio: 1
                    },
                    plugins: [centerTextPlugin]
                });
            }
        })
        .catch(error => console.error("Erreur lors de la récupération des données :", error));
});