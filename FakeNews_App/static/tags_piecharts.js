// tags_piecharts.js - Génère les camemberts Chart.js pour l'analyse des tags

document.addEventListener('DOMContentLoaded', function() {
    // Les variables suivantes doivent être injectées dans le template avant ce script !
    if (typeof emotionsLabels === 'undefined') return;

    // Couleurs cohérentes
    const emotionColors = ['#2563eb','#10b981','#f59e42','#ef4444','#a21caf','#64748b'];
    const objectivityColors = ['#2563eb','#f59e42'];
    const toneColors = ['#10b981','#64748b','#ef4444'];

    // Chart.js - Emotions
    new Chart(document.getElementById('emotionsPie'), {
        type: 'pie',
        data: {
            labels: emotionsLabels.map((l,i)=>l+` : ${emotionsData[i]} (${emotionsPercent[i]}%)`),
            datasets: [{
                data: emotionsData,
                backgroundColor: emotionColors,
                borderWidth: 1
            }]
        },
        options: {plugins:{legend:{position:'bottom'}}}
    });
    // Chart.js - Objectivité
    new Chart(document.getElementById('objectivityPie'), {
        type: 'pie',
        data: {
            labels: objectivityLabels.map((l,i)=>l+` : ${objectivityData[i]} (${objectivityPercent[i]}%)`),
            datasets: [{
                data: objectivityData,
                backgroundColor: objectivityColors,
                borderWidth: 1
            }]
        },
        options: {plugins:{legend:{position:'bottom'}}}
    });
    // Chart.js - Ton
    new Chart(document.getElementById('tonePie'), {
        type: 'pie',
        data: {
            labels: toneLabels.map((l,i)=>l+` : ${toneData[i]} (${tonePercent[i]}%)`),
            datasets: [{
                data: toneData,
                backgroundColor: toneColors,
                borderWidth: 1
            }]
        },
        options: {plugins:{legend:{position:'bottom'}}}
    });
});
