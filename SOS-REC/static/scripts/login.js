 console.log("login.js carregado!");

 

        document.addEventListener('DOMContentLoaded', function () {
            const ctx = document.getElementById('distanciaChart').getContext('2d');
            const distanciaChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Distância (cm)',
                        data: [],
                        backgroundColor: 'rgba(54, 162, 235, 0.2)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 2,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Distância (cm)'
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: 'Horário'
                            }
                        }
                    }
                }
            });

            async function atualizarGrafico() {
                try {
                    const response = await fetch('/distancias');
                    const data = await response.json();

                    distanciaChart.data.labels = data.map(d => new Date(d.timestamp).toLocaleTimeString());
                    distanciaChart.data.datasets[0].data = data.map(d => d.valor);
                    distanciaChart.update();
                } catch (error) {
                    console.error('Erro ao atualizar o gráfico:', error);
                }
            }

            setInterval(atualizarGrafico, 2000);
            atualizarGrafico();
        });





