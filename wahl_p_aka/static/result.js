var ctx = document.getElementById('result-chart').getContext('2d');

labels = []
data = []

results.forEach((party) => {
    labels.push(party['short_name'])
    data.push(party['percent'])
})

var myChart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: labels,
        datasets: [{
            label: 'Prozent Übereinstimmung',
            data: data,
            backgroundColor: [
                '#219fd1',
            ],
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
