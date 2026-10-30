let chartInstanciaSets = null;
let chartInstanciaPuntos = null;

async function cargarVistaMetricas() {
    const contenedor = document.getElementById('metrics-container');
    contenedor.style.display = 'flex';
    contenedor.innerHTML = '<p style="text-align:center; color:var(--text-muted); padding: 20px;">Cargando datos métricos...</p>';

    try {
        const respuesta = await fetch(`${categoriaActual.archivoClasificacion}?t=${new Date().getTime()}`);
        if (!respuesta.ok) throw new Error("No hay datos disponibles para las métricas.");
        const equipos = await respuesta.json();

        const colorHex = obtenerColorHex(categoriaActual.tipo);

        let html = `
            <div class="metrics-wrapper">
                <div class="metrics-selector-card">
                    <span class="metrics-label">Seleccionar Equipo para Análisis</span>
                    <select id="team-selector" class="team-select-dropdown" onchange="actualizarDashboardMetricas()">
                `;

        equipos.forEach((eq, index) => {
            const esBiarense = eq.equipo.toUpperCase().includes('BIARENSE');
            const selected = (esBiarense || index === 0) ? 'selected' : '';
            html += `<option value="${index}" ${selected}>${eq.posicion}º - ${eq.equipo}</option>`;
        });

        html += `
                    </select>
                </div>

                <div class="metrics-grid">
                    <!-- Tarjeta Gráfica de Sets con Botón (i) -->
                    <div class="metric-card">
                        <div class="metric-title-wrapper">
                            <span class="metric-card-title" style="color: ${colorHex};">📊 Desglose de Sets</span>
                            <button class="info-icon-btn" onclick="toggleExplicacion('sets-desc')" title="Explicación">i</button>
                        </div>
                        <div id="sets-desc" class="metric-explanation" style="border-left-color: ${colorHex};">
                            Muestra la proporción de <strong>sets ganados</strong> (en color) frente a los <strong>sets perdidos</strong> (translúcido) acumulados durante toda la temporada.
                        </div>
                        <div class="chart-container">
                            <canvas id="setsChart"></canvas>
                        </div>
                    </div>

                    <!-- Tarjeta Gráfica de Puntos con Botón (i) -->
                    <div class="metric-card">
                        <div class="metric-title-wrapper">
                            <span class="metric-card-title" style="color: ${colorHex};">🏐 Puntos de Juego</span>
                            <button class="info-icon-btn" onclick="toggleExplicacion('puntos-desc')" title="Explicación">i</button>
                        </div>
                        <div id="puntos-desc" class="metric-explanation" style="border-left-color: ${colorHex};">
                            Compara el volumen total de <strong>puntos anotados</strong> a favor con los <strong>puntos recibidos</strong> por parte de los rivales en los partidos disputados.
                        </div>
                        <div class="chart-container">
                            <canvas id="puntosChart"></canvas>
                        </div>
                    </div>

                    <div class="kpi-row">
                        <div class="kpi-box">
                            <span id="kpi-efectividad" class="kpi-value" style="color: ${colorHex};">-</span>
                            <span class="kpi-title">% Éxito en Sets</span>
                        </div>
                        <div class="kpi-box">
                            <span id="kpi-coef" class="kpi-value" style="color: ${colorHex};">-</span>
                            <span class="kpi-title">Balance de Puntos</span>
                        </div>
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
                <i class="fa-solid fa-triangle-exclamation" style="font-size: 2rem; color: #f59e0b; margin-bottom: 10px;"></i>
                <h3 style="font-size: 1rem; margin-bottom: 6px;">Métricas no disponibles</h3>
                <p style="font-size: 0.8rem; color: var(--text-muted);">Se requiere un archivo de clasificación con datos completos para generar las estadísticas.</p>
            </div>
        `;
    }
}

function toggleExplicacion(id) {
    const el = document.getElementById(id);
    if (el) {
        el.style.display = (el.style.display === 'block') ? 'none' : 'block';
    }
}

function actualizarDashboardMetricas() {
    const select = document.getElementById('team-selector');
    if (!select || !window.equiposCacheMetricas) return;

    const index = parseInt(select.value);
    const eq = window.equiposCacheMetricas[index];
    if (!eq) return;

    const sf = parseInt(eq.sf) || 0;
    const sc = parseInt(eq.sc) || 0;
    const pf = parseInt(eq.pf) || 0;
    const pc = parseInt(eq.pc) || 0;

    // KPIs Intuitivos
    const totalSets = sf + sc;
    const porcentajeSets = totalSets > 0 ? Math.round((sf / totalSets) * 100) : 0;
    
    const balancePuntos = pf - pc;
    const balancePuntosStr = balancePuntos > 0 ? `+${balancePuntos}` : `${balancePuntos}`;

    document.getElementById('kpi-efectividad').innerText = `${porcentajeSets}%`;
    document.getElementById('kpi-coef').innerText = balancePuntosStr;
    
    const kpiCoefEl = document.getElementById('kpi-coef');
    if (balancePuntos > 0) {
        kpiCoefEl.style.color = '#10b981';
    } else if (balancePuntos < 0) {
        kpiCoefEl.style.color = '#ef4444';
    } else {
        kpiCoefEl.style.color = '#fff';
    }

    const colorHex = obtenerColorHex(categoriaActual.tipo);

    // Gráfica de Sets
    const ctxSets = document.getElementById('setsChart').getContext('2d');
    if (chartInstanciaSets) chartInstanciaSets.destroy();
    chartInstanciaSets = new Chart(ctxSets, {
        type: 'doughnut',
        data: {
            labels: ['Sets a Favor', 'Sets en Contra'],
            datasets: [{
                data: [sf, sc],
                backgroundColor: [colorHex, 'rgba(255, 255, 255, 0.1)']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: 'bottom', labels: { color: '#fff', font: { size: 11 } } } }
        }
    });

    // Gráfica de Puntos
    const ctxPuntos = document.getElementById('puntosChart').getContext('2d');
    if (chartInstanciaPuntos) chartInstanciaPuntos.destroy();
    chartInstanciaPuntos = new Chart(ctxPuntos, {
        type: 'bar',
        data: {
            labels: ['Anotados (PF)', 'Recibidos (PC)'],
            datasets: [{
                data: [pf, pc],
                backgroundColor: [colorHex, 'rgba(148, 163, 184, 0.3)']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255, 255, 255, 0.05)' } },
                x: { ticks: { color: '#94a3b8' }, grid: { display: false } }
            }
        }
    });
}