let chartsInstancias = {};

async function cargarVistaMetricas() {
    const contenedor = document.getElementById('metrics-container');
    contenedor.style.display = 'flex';
    contenedor.innerHTML = '<p style="text-align:center; color:var(--text-muted); padding: 20px;">Cargando datos métricos...</p>';

    try {
        const respuesta = await fetch(`${categoriaActual.archivoClasificacion}?t=${new Date().getTime()}`);
        if (!respuesta.ok) throw new Error("No hay datos disponibles para las métricas.");
        const equipos = await respuesta.json();

        const colorHex = obtenerColorHex(categoriaActual.tipo);

        let indexA = equipos.findIndex(eq => eq.equipo.toUpperCase().includes('BIARENSE'));
        if (indexA === -1) indexA = 0;
        
        // Por defecto dejamos el Equipo B sin seleccionar (-1)
        let indexB = -1;

        let html = `
            <div class="metrics-wrapper" style="display: flex; flex-direction: column; gap: 20px; width: 100%;">
                
                <!-- Tarjeta de Selección Dual Cara a Cara Mejorada -->
                <div class="metrics-selector-card">
                    <div style="font-size: 0.85rem; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 12px; text-align: center;">
                        ⚔️ Enfrentamiento Cara a Cara
                    </div>
                    <div class="matchup-container">
                        <div class="team-select-wrapper">
                            <span class="team-role-label" style="color: ${colorHex};">Local / Principal</span>
                            <select id="team-selector-a" class="team-select-dropdown" onchange="actualizarDashboardMetricas()">
        `;

        equipos.forEach((eq, index) => {
            const selected = (index === indexA) ? 'selected' : '';
            html += `<option value="${index}" ${selected}>${eq.posicion}º - ${eq.equipo}</option>`;
        });

        html += `
                            </select>
                        </div>

                        <div class="vs-badge-container">
                            <span class="vs-badge" style="background-color: ${colorHex};">VS</span>
                        </div>

                        <div class="team-select-wrapper">
                            <span class="team-role-label" style="color: #94a3b8;">Rival / Visitante</span>
                            <select id="team-selector-b" class="team-select-dropdown" onchange="actualizarDashboardMetricas()">
                                <option value="-1" selected disabled>Selecciona rival...</option>
        `;

        equipos.forEach((eq, index) => {
            html += `<option value="${index}">${eq.posicion}º - ${eq.equipo}</option>`;
        });

        html += `
                            </select>
                        </div>
                    </div>
                </div>

                <!-- Tarjeta 1: Puntuación General -->
                <div class="metric-card" style="width: 100%;">
                    <div class="metric-title-wrapper">
                        <span class="metric-card-title" style="color: ${colorHex};">Puntuación General</span>
                    </div>
                    <div class="chart-container" style="position: relative; height: 160px; width: 100%;">
                        <canvas id="chartPuntuacion"></canvas>
                    </div>
                </div>

                <!-- Tarjeta 2: Desglose de Partidos -->
                <div class="metric-card" style="width: 100%;">
                    <div class="metric-title-wrapper">
                        <span class="metric-card-title" style="color: ${colorHex};">Desglose de Partidos (Ganados / Perdidos)</span>
                    </div>
                    <div class="chart-container" style="position: relative; height: 220px; width: 100%;">
                        <canvas id="chartPartidos"></canvas>
                    </div>
                </div>

                <!-- Tarjeta 3: Sets y Sanciones -->
                <div class="metric-card" style="width: 100%;">
                    <div class="metric-title-wrapper">
                        <span class="metric-card-title" style="color: ${colorHex};">Rendimiento en Sets y Sanciones</span>
                    </div>
                    <div class="chart-container" style="position: relative; height: 190px; width: 100%;">
                        <canvas id="chartSets"></canvas>
                    </div>
                </div>

                <!-- Tarjeta 4: Volumen de Puntos de Juego -->
                <div class="metric-card" style="width: 100%;">
                    <div class="metric-title-wrapper">
                        <span class="metric-card-title" style="color: ${colorHex};">Volumen de Puntos de Juego (Tantos)</span>
                    </div>
                    <div class="chart-container" style="position: relative; height: 160px; width: 100%;">
                        <canvas id="chartPuntosJuego"></canvas>
                    </div>
                </div>

            </div>
        `;

        contenedor.innerHTML = html;
        window.equiposCacheMetricas = equipos;
        actualizarDashboardMetricas();

    } catch (error) {
        console.error('Error cargando métricas:', error);
        contenedor.innerHTML = `
            <div class="card" style="text-align:center; padding: 30px;">
                <h3 style="font-size: 1rem; margin-bottom: 6px;">Métricas no disponibles</h3>
                <p style="font-size: 0.8rem; color: var(--text-muted);">Se requiere un archivo de clasificación con datos completos para generar las estadísticas.</p>
            </div>
        `;
    }
}

function extraerDatosBloques(eq) {
    return {
        puntuacion: [
            parseInt(eq.ptos ?? eq.Ptos) || 0,
            parseInt(eq.pj ?? eq.Pj) || 0
        ],
        partidos: [
            parseInt(eq.pg3 ?? eq.PG3) || 0,
            parseInt(eq.pg2 ?? eq.PG2) || 0,
            parseInt(eq.pp1 ?? eq.PP1) || 0,
            parseInt(eq.pp0 ?? eq.PP0) || 0
        ],
        sets: [
            parseInt(eq.sf ?? eq.SF) || 0,
            parseInt(eq.sc ?? eq.SC) || 0,
            parseInt(eq.sa ?? eq.SA) || 0
        ],
        puntosJuego: [
            parseInt(eq.pf ?? eq.PF) || 0,
            parseInt(eq.pc ?? eq.PC) || 0
        ]
    };
}

function crearGraficaBloque(canvasId, labels, dataA, dataB, teamAName, teamBName, colorHex, colorRival) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    if (chartsInstancias[canvasId]) {
        chartsInstancias[canvasId].destroy();
    }

    // Si no hay rival seleccionado (dataB es null), solo mostramos el dataset del equipo A
    let datasets = [
        {
            label: teamAName,
            data: dataA,
            backgroundColor: colorHex,
            borderColor: colorHex,
            borderWidth: 1,
            borderRadius: 4
        }
    ];

    if (dataB) {
        datasets.push({
            label: teamBName,
            data: dataB,
            backgroundColor: colorRival,
            borderColor: colorRival,
            borderWidth: 1,
            borderRadius: 4
        });
    }

    chartsInstancias[canvasId] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: datasets
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: { color: '#fff', font: { size: 11, family: "'Plus Jakarta Sans', sans-serif" } }
                },
                tooltip: { mode: 'index', intersect: false }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: { color: '#94a3b8', font: { size: 10 } },
                    grid: { color: 'rgba(255, 255, 255, 0.05)' }
                },
                y: {
                    ticks: { color: '#ffffff', font: { weight: '600', size: 11 } },
                    grid: { display: false }
                }
            }
        }
    });
}

function actualizarDashboardMetricas() {
    const selectA = document.getElementById('team-selector-a');
    const selectB = document.getElementById('team-selector-b');
    if (!selectA || !selectB || !window.equiposCacheMetricas) return;

    const indexA = parseInt(selectA.value);
    const indexB = parseInt(selectB.value);
    const eqA = window.equiposCacheMetricas[indexA];
    const eqB = indexB >= 0 ? window.equiposCacheMetricas[indexB] : null;
    
    if (!eqA) return;

    const datosA = extraerDatosBloques(eqA);
    const datosB = eqB ? extraerDatosBloques(eqB) : null;

    const colorHex = obtenerColorHex(categoriaActual.tipo);
    const colorRival = 'rgba(148, 163, 184, 0.7)';

    // Renderizar las 4 gráficas independientes (con o sin rival)
    crearGraficaBloque(
        'chartPuntuacion',
        ['Ptos (Puntos Totales)', 'PJ (Partidos Jugados)'],
        datosA.puntuacion, datosB ? datosB.puntuacion : null,
        eqA.equipo, eqB ? eqB.equipo : null, colorHex, colorRival
    );

    crearGraficaBloque(
        'chartPartidos',
        ['PG3 (Ganados 3-0/3-1)', 'PG2 (Ganados 3-2)', 'PP1 (Perdidos 2-3)', 'PP0 (Perdidos 0-3/1-3)'],
        datosA.partidos, datosB ? datosB.partidos : null,
        eqA.equipo, eqB ? eqB.equipo : null, colorHex, colorRival
    );

    crearGraficaBloque(
        'chartSets',
        ['SF (Sets a Favor)', 'SC (Sets en Contra)', 'SA (Sanciones)'],
        datosA.sets, datosB ? datosB.sets : null,
        eqA.equipo, eqB ? eqB.equipo : null, colorHex, colorRival
    );

    crearGraficaBloque(
        'chartPuntosJuego',
        ['PF (Puntos a Favor)', 'PC (Puntos en Contra)'],
        datosA.puntosJuego, datosB ? datosB.puntosJuego : null,
        eqA.equipo, eqB ? eqB.equipo : null, colorHex, colorRival
    );
}