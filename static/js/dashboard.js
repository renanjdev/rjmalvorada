// Cria o Gráfico Mensal
const ctxMensal = document.getElementById('chartMensal').getContext('2d');
new Chart(ctxMensal, {
    type: 'bar',
    data: {
        labels: dadosMensais.map(item => item[0]), // Mês
        datasets: [{
            label: 'Presenças',
            data: dadosMensais.map(item => item[1]), // Presenças
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 1
        }]
    },
    options: {
        responsive: true,
        plugins: {
            legend: {
                position: 'top',
            },
            title: {
                display: true,
                text: 'Frequência Mensal'
            }
        },
        scales: {
            x: {
                title: {
                    display: true,
                    text: 'Mês'
                }
            },
            y: {
                title: {
                    display: true,
                    text: 'Presenças'
                }
            }
        }
    }
});

// Cria o Gráfico Anual
const ctxAnual = document.getElementById('chartAnual').getContext('2d');
new Chart(ctxAnual, {
    type: 'line',
    data: {
        labels: dadosAnuais.map(item => item[0]), // Ano
        datasets: [{
            label: 'Presenças',
            data: dadosAnuais.map(item => item[1]), // Presenças
            backgroundColor: 'rgba(153, 102, 255, 0.2)',
            borderColor: 'rgba(153, 102, 255, 1)',
            borderWidth: 1,
            fill: false
        }]
    },
    options: {
        responsive: true,
        plugins: {
            legend: {
                position: 'top',
            },
            title: {
                display: true,
                text: 'Frequência Anual'
            }
        },
        scales: {
            x: {
                title: {
                    display: true,
                    text: 'Ano'
                }
            },
            y: {
                title: {
                    display: true,
                    text: 'Presenças'
                }
            }
        }
    }
});
