// mengambil data yang dikirim dari HTML
const labels = adminData.chartLabels;
const data = adminData.chartValues;

const ctx = document.getElementById('salesChart').getContext('2d');
new Chart(ctx, {
    type: 'doughnut',
    data: {
        labels: labels,
        datasets: [{
            data: data,
            backgroundColor: ['#e50914', '#00d2d3', '#2ecc71', '#3498db', '#9b59b6'],
            borderWidth: 0
        }]
    },
    options: { 
        responsive: true, 
        maintainAspectRatio: false, 
        plugins: { legend: { display: false } } 
    }
});