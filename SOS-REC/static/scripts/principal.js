

        // Configura o gráfico de distância
        const ctxDistancia = document.getElementById('distanciaChart').getContext('2d');
        const distanciaChart = new Chart(ctxDistancia, {
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

        // Função para atualizar gráfico puxando dados da rota /distancias
        async function atualizarGraficoDistancia() {
            try {
                const response = await fetch('/distancias');
                if (!response.ok) {
                    console.error('Erro na resposta do /distancias:', response.status);
                    return;
                }
                const data = await response.json();

                if (!Array.isArray(data) || data.length === 0) {
                    console.warn('Dados vazios ou formato inesperado do /distancias');
                    return;
                }

                distanciaChart.data.labels = data.map(d => new Date(d.timestamp).toLocaleTimeString());
                distanciaChart.data.datasets[0].data = data.map(d => d.valor);

                distanciaChart.update();
            } catch (error) {
                console.error('Erro ao atualizar gráfico de distância:', error);
            }
        }

        // Atualiza previsão do tempo
        async function atualizarPrevisaoTempo() {
            try {
                const response = await fetch('/previsao_tempo');
                if (!response.ok) {
                    console.error('Erro na resposta do /previsao_tempo:', response.status);
                    return;
                }
                const data = await response.json();

                document.getElementById('temperatura').textContent = data.temperatura || '--';
                document.getElementById('condicao').textContent = data.condicao || '--';
                document.getElementById('humidade').textContent = data.humidade || '--';
            } catch (error) {
                console.error('Erro ao atualizar previsão do tempo:', error);
            }
        }

        // Atualiza nível da maré
        
       async function atualizarNivelMare() {
    try {
        const response = await fetch('/nivel_mare');
        if (!response.ok) {
            console.error('Erro na resposta do /nivel_mare:', response.status);
            return;
        }
        const data = await response.json();
       document.getElementById('nivel_mare').textContent = data.status ?? '--';
    } catch (error) {
        console.error('Erro ao atualizar nível da maré:', error);
    }
}

// Atualiza tudo a cada 2 segundos
setInterval(() => {
    atualizarGraficoDistancia();
    atualizarPrevisaoTempo();
    atualizarNivelMare();
}, 2000);

// Atualização inicial
atualizarGraficoDistancia();
atualizarPrevisaoTempo();
atualizarNivelMare();

document.addEventListener('DOMContentLoaded', function () {
    var map = L.map('map').setView([-8.05, -34.9], 12);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    // Lista de áreas de risco (nome e coordenadas aproximadas)
    const areasRisco = [
        { nome: "Linha do Tiro", coords: [-8.0095, -34.9115] },
        { nome: "Passarinho", coords: [-7.9908, -34.9308] },
        { nome: "Nova Descoberta", coords: [-8.0117, -34.9182] },
        { nome: "Vasco da Gama", coords: [-8.0227, -34.9187] },
        { nome: "Brejo da Guabiraba", coords: [-8.0085, -34.9445] },
        { nome: "Guabiraba", coords: [-7.9955, -34.9565] },
        { nome: "Dois Unidos", coords: [-8.0080, -34.9000] },
        { nome: "Alto José do Pinho", coords: [-8.0275, -34.9175] },
        { nome: "Alto José Bonifácio", coords: [-8.0220, -34.9250] },
        { nome: "Ibura", coords: [-8.1230, -34.9360] },
        { nome: "Cohab", coords: [-8.1330, -34.9400] },
        { nome: "Areias", coords: [-8.0850, -34.9500] },
        { nome: "Mustardinha", coords: [-8.0700, -34.9250] },
        { nome: "Torrões", coords: [-8.0700, -34.9450] },
        { nome: "Afogados", coords: [-8.0800, -34.9200] },
        { nome: "Imbiribeira", coords: [-8.1120, -34.9170] },
        { nome: "Jardim São Paulo", coords: [-8.0900, -34.9500] },
        { nome: "Cordeiro", coords: [-8.0500, -34.9300] },
        { nome: "Casa Amarela", coords: [-8.0220, -34.9110] },
        { nome: "Água Fria", coords: [-8.0080, -34.9000] }
    ];

    areasRisco.forEach(area => {
        L.marker(area.coords, {icon: L.icon({iconUrl: 'https://cdn-icons-png.flaticon.com/512/684/684908.png', iconSize: [32, 32]})})
            .addTo(map)
            .bindPopup(`<b>${area.nome}</b><br>Área de risco de alagamento/deslizamento`);
    });

    // Exemplo de marcador do sensor
    L.marker([-8.063149, -34.871139])
        .addTo(map)
        .bindPopup('Sensor SOS-REC<br>Marco Zero');
});