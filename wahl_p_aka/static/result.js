var ctx = document.getElementById('result-chart').getContext('2d');

labels = []
colors = []
data = []

results.forEach((party) => {
    labels.push(party['short_name'])
    colors.push(party['color'])
    data.push(party['percent'])
})

var myChart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: labels,
        datasets: [{
            label: 'Prozent Übereinstimmung',
            data: data,
            backgroundColor: colors,
            borderWidth: 1
        }]
    },
    options: {
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
});
