let categoriaActual = {
    archivoPartidos: '',
    archivoClasificacion: '',
    subtitulo: '',
    urlFvbcv: '',
    tipo: 'senior'
};
let vistaActual = 'partidos'; // 'partidos' o 'clasificacion'

window.addEventListener('DOMContentLoaded', () => {
    cargarProximosPartidosGlobales();
});

function parsearFecha(strFecha) {
    if (!strFecha || !strFecha.includes('/')) return null;
    const partes = strFecha.split('/');
    if (partes.length !== 3) return null;
    return new Date(`${partes[2]}-${partes[1]}-${partes[0]}`);
}

function obtenerClaseCategoria(archivo) {
    if (archivo.includes('femenino')) return 'categoria-femenino';
    if (archivo.includes('infantil')) return 'categoria-infantil';
    if (archivo.includes('cadete')) return 'categoria-cadete';
    return 'categoria-senior';
}

function obtenerColorHex(tipo) {
    switch (tipo) {
        case 'femenino': return '#ec4899'; // Rosa Juvenil
        case 'infantil': return '#8b5cf6'; // Morado Infantil
        case 'cadete': return '#f59e0b';   // Amarillo Cadete
        case 'senior': default: return '#10b981'; // Verde Senior
    }
}

async function cargarProximosPartidosGlobales() {
    const equipos = [
        { nombre: 'Senior Masculino', archivo: 'partidos.json', archivoClasif: 'clasificacion.json', subtitulo: 'Voleibol Senior Masculino', urlFvbcv: 'https://fvbcv.com/exportar_competiciones.php?idens=1825', tipo: 'senior' },
        { nombre: 'Juvenil Femenino', archivo: 'partidos_femenino.json', archivoClasif: 'clasificacion_femenino.json', subtitulo: 'Voleibol Juvenil Femenino', urlFvbcv: 'https://fvbcv.com/exportar_competiciones.php?idens=1812', tipo: 'femenino' },
        { nombre: 'Infantil Femenino', archivo: 'partidos_infantil.json', archivoClasif: 'clasificacion_infantil.json', subtitulo: 'Voleibol Infantil Femenino', urlFvbcv: 'https://fvbcv.com/exportar_competiciones.php?idens=1850', tipo: 'infantil' },
        { nombre: 'Cadete Femenino', archivo: 'partidos_cadete.json', archivoClasif: 'clasificacion_cadete.json', subtitulo: 'Voleibol Cadete Femenino', urlFvbcv: 'https://fvbcv.com/exportar_competiciones.php?idens=1801', tipo: 'cadete' }
    ];

    const contenedorPreviews = document.getElementById('global-previews-container');
    contenedorPreviews.innerHTML = '';
    const ahora = new Date().getTime();

    for (const eq of equipos) {
        try {
            const res = await fetch(`${eq.archivo}?t=${new Date().getTime()}`);
            if (!res.ok) continue;
            const partidos = await res.json();

            let proximoPartido = null;
            let menorDif = Infinity;

            partidos.forEach(p => {
                const estadoLimpio = p.estado ? p.estado.toLowerCase().trim() : '';
                if (estadoLimpio === 'pendiente' || estadoLimpio === 'programado') {
                    const f = parsearFecha(p.fecha);
                    if (f) {
                        const dif = Math.abs(f.getTime() - ahora);
                        if (dif < menorDif) {
                            menorDif = dif;
                            proximoPartido = p;
                        }
                    } else if (!proximoPartido) {
                        proximoPartido = p;
                    }
                }
            });

            if (!proximoPartido) {
                proximoPartido = partidos.find(p => p.estado && p.estado.toLowerCase().trim() === 'pendiente');
            }

            if (proximoPartido) {
                const esCasa = proximoPartido.condicion === 'Casa';
                const rival = esCasa ? proximoPartido.visitante : proximoPartido.local;
                const iconoCond = esCasa ? '🏠' : '🚗';

                let claseColorCard = '';
                if (eq.tipo === 'femenino') claseColorCard = 'femenino';
                else if (eq.tipo === 'infantil') claseColorCard = 'infantil';
                else if (eq.tipo === 'cadete') claseColorCard = 'cadete';

                const cardMini = document.createElement('div');
                cardMini.className = `global-preview-card ${claseColorCard}`;
                cardMini.onclick = () => cargarCategoria(eq.archivo, eq.archivoClasif, eq.subtitulo, eq.urlFvbcv, eq.tipo);
                cardMini.innerHTML = `
                    <div class="gp-info">
                        <span class="gp-team-name">${eq.nombre}</span>
                        <span class="gp-matchup">${iconoCond} vs ${rival}</span>
                    </div>
                    <div class="gp-meta" style="text-align:right;">
                        <span style="font-weight:700; color:#93c5fd; display:block;">${proximoPartido.fecha}</span>
                        <span style="font-size:0.75rem; color:var(--text-muted);">⏰ ${proximoPartido.hora || 'Por definir'}</span>
                    </div>
                `;
                contenedorPreviews.appendChild(cardMini);
            }
        } catch (e) {
            console.error(`Error cargando resumen para ${eq.nombre}:`, e);
        }
    }

    if (contenedorPreviews.children.length === 0) {
        contenedorPreviews.innerHTML = '<p style="text-align:center; color:var(--text-muted); font-size: 0.8rem;">No hay partidos pendientes próximamente.</p>';
    }
}

function volverAlSelector() {
    document.getElementById('partidos-container').style.display = 'none';
    document.getElementById('clasificacion-container').style.display = 'none';
    document.getElementById('selector-screen').style.display = 'flex';
    document.getElementById('bottom-nav-bar').style.display = 'none';
    document.getElementById('main-subtitle').innerText = '';
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function cargarCategoria(archivoJson, archivoClasif, subtituloTexto, urlFvbcv, tipoCategoria = 'senior') {
    categoriaActual = {
        archivoPartidos: archivoJson,
        archivoClasificacion: archivoClasif,
        subtitulo: subtituloTexto,
        urlFvbcv: urlFvbcv,
        tipo: tipoCategoria
    };
    vistaActual = 'partidos';

    document.getElementById('selector-screen').style.display = 'none';
    
    // Asignar color dinámico a la barra inferior de botones
    const navBar = document.getElementById('bottom-nav-bar');
    navBar.className = `bottom-nav-bar categoria-${tipoCategoria}`;
    navBar.style.display = 'flex';

    // Aplicar color en línea a los botones flotantes según la categoría
    const colorHex = obtenerColorHex(tipoCategoria);
    document.querySelectorAll('.floating-btn').forEach(btn => {
        btn.style.borderColor = colorHex;
    });
    const accentBtn = document.querySelector('.floating-btn.accent-btn');
    if (accentBtn) {
        accentBtn.style.backgroundColor = colorHex;
        accentBtn.style.borderColor = colorHex;
    }

    document.getElementById('fvbcv-link').href = urlFvbcv;
    document.getElementById('main-subtitle').innerText = subtituloTexto;

    actualizarBotonToggle();
    renderizarVistaActual();
}

function alternarVista() {
    vistaActual = (vistaActual === 'partidos') ? 'clasificacion' : 'partidos';
    actualizarBotonToggle();
    renderizarVistaActual();
}

function actualizarBotonToggle() {
    const icono = document.getElementById('toggle-icon');
    const texto = document.getElementById('toggle-text');
    if (vistaActual === 'partidos') {
        icono.className = 'fa-solid fa-table-list';
        texto.innerText = 'Clasificación';
    } else {
        icono.className = 'fa-solid fa-calendar-days';
        texto.innerText = 'Partidos';
    }
}

function renderizarVistaActual() {
    const contenedorPartidos = document.getElementById('partidos-container');
    const contenedorClasif = document.getElementById('clasificacion-container');

    if (vistaActual === 'partidos') {
        contenedorClasif.style.display = 'none';
        contenedorPartidos.style.display = 'flex';
        cargarPartidos(categoriaActual.archivoPartidos);
    } else {
        contenedorPartidos.style.display = 'none';
        contenedorClasif.style.display = 'flex';
        contenedorClasif.innerHTML = '';
        cargarClasificacion(categoriaActual.archivoClasificacion);
    }
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

async function cargarPartidos(archivoJson) {
    const contenedor = document.getElementById('partidos-container');
    contenedor.innerHTML = '<p style="text-align:center; color:var(--text-muted); padding: 20px;">Cargando partidos...</p>';
    
    const claseCat = obtenerClaseCategoria(archivoJson);
    const colorHex = obtenerColorHex(categoriaActual.tipo);

    try {
        const respuesta = await fetch(`${archivoJson}?t=${new Date().getTime()}`);
        const partidosGuardados = await respuesta.json();
        contenedor.innerHTML = '';

        const mapaPartidos = {};
        let maxJornada = 0;

        partidosGuardados.forEach(p => {
            const numJ = parseInt(p.jornada.replace(/\D/g, ''));
            if (numJ) {
                mapaPartidos[numJ] = p;
                if (numJ > maxJornada) maxJornada = numJ;
            }
        });

        const totalJornadas = maxJornada > 0 ? maxJornada : 26;
        let mejorCardParaScroll = null;
        let menorDiferenciaTiempo = Infinity;
        const ahora = new Date().getTime();

        for (let i = 1; i <= totalJornadas; i++) {
            const card = document.createElement('div');
            card.className = `card ${claseCat}`;
            const p = mapaPartidos[i];

            if (!p) {
                card.className = `card descanso-card ${claseCat}`;
                card.innerHTML = `
                    <span class="jornada-badge">JORNADA ${i}</span>
                    <div class="descanso-title">☕ DESCANSO</div>
                    <p style="font-size: 0.82rem; color: var(--text-muted);">Sin encuentro programado.</p>
                `;
            } else {
                const estadoClass = `status-${p.estado.toLowerCase().trim()}`;
                const esCasa = p.condicion === 'Casa';
                const iconoCondicion = esCasa ? '🏠 Casa' : '🚗 Fuera';
                const mapsUrl = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(p.ubicacion)}`;

                let resLoc = '-';
                let resVis = '-';
                if (p.resultado && p.resultado.includes('-')) {
                    const partes = p.resultado.split('-');
                    resLoc = partes[0].trim();
                    resVis = partes[1].trim();
                }

                let parcialesHTML = '';
                if (p.parciales) {
                    const sets = p.parciales.split('/').map(s => s.trim()).filter(Boolean).join('  •  ');
                    parcialesHTML = `
                        <div class="parciales-container">
                            <span style="font-size: 0.7rem; text-transform: uppercase; color: var(--text-muted); font-weight: 700;">📊 Parciales por Set</span>
                            <span class="sets-text" style="color: ${colorHex}">${sets}</span>
                        </div>
                    `;
                }

                const esLocalBiarense = p.local.toUpperCase().includes('BIARENSE');
                const esVisBiarense = p.visitante.toUpperCase().includes('BIARENSE');

                card.innerHTML = `
                    <div class="card-header">
                        <span class="jornada-badge" style="color: ${colorHex}">${p.jornada}</span>
                        <span class="status-badge ${estadoClass}">${p.estado}</span>
                    </div>
                    <div class="match-info">
                        <div class="team-row">
                            <span class="team ${esLocalBiarense ? 'highlight' : ''}" style="${esLocalBiarense ? `color: ${colorHex};` : ''}">${p.local}</span>
                            <span class="score-pill">${resLoc}</span>
                        </div>
                        <div class="team-row">
                            <span class="team ${esVisBiarense ? 'highlight' : ''}" style="${esVisBiarense ? `color: ${colorHex};` : ''}">${p.visitante}</span>
                            <span class="score-pill">${resVis}</span>
                        </div>
                    </div>
                    ${parcialesHTML}
                    <div class="details">
                        <div class="details-row">
                            <div class="detail-item">📅 <span>${p.fecha}</span></div>
                            <div class="detail-item">⏰ <span>${p.hora || 'Por definir'}</span></div>
                            <div class="detail-item"><span>${iconoCondicion}</span></div>
                        </div>
                        <div class="location-box" style="background: ${colorHex}10; border: 1px solid ${colorHex}30; color: ${colorHex};">
                            <span style="font-size:0.8rem; color: #fff;">🏟️ <strong style="color: ${colorHex}">Ubicación:</strong> ${p.ubicacion}</span>
                            <a href="${mapsUrl}" target="_blank" class="maps-btn" style="background: ${colorHex}; color: #fff;">📍 Maps</a>
                        </div>
                    </div>
                `;

                const estadoLimpio = p.estado ? p.estado.toLowerCase().trim() : '';
                if (estadoLimpio === 'pendiente' || estadoLimpio === 'programado') {
                    const fechaPartido = parsearFecha(p.fecha);
                    if (fechaPartido) {
                        const diferencia = Math.abs(fechaPartido.getTime() - ahora);
                        if (diferencia < menorDiferenciaTiempo) {
                            menorDiferenciaTiempo = diferencia;
                            if (mejorCardParaScroll) mejorCardParaScroll.classList.remove('next-match');
                            mejorCardParaScroll = card;
                            card.classList.add('next-match');
                        }
                    } else if (!mejorCardParaScroll) {
                        mejorCardParaScroll = card;
                        card.classList.add('next-match');
                    }
                }
            }
            contenedor.appendChild(card);
        }

        if (!mejorCardParaScroll) {
            const cardPendiente = contenedor.querySelector('.status-pendiente');
            if (cardPendiente) {
                mejorCardParaScroll = cardPendiente.closest('.card');
                if (mejorCardParaScroll) mejorCardParaScroll.classList.add('next-match');
            }
        }

        setTimeout(() => {
            if (mejorCardParaScroll) mejorCardParaScroll.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }, 100);

    } catch (error) {
        console.error('Error al cargar partidos:', error);
        contenedor.innerHTML = '<p style="text-align:center; color:#ef4444; padding:20px;">Error cargando los partidos.</p>';
    }
}

async function cargarClasificacion(archivoJson) {
    const contenedor = document.getElementById('clasificacion-container');
    contenedor.innerHTML = '<p style="text-align:center; color:var(--text-muted); padding: 20px;">Cargando clasificación...</p>';
    
    const claseCat = obtenerClaseCategoria(archivoJson);
    const colorCat = obtenerColorHex(categoriaActual.tipo);

    try {
        const respuesta = await fetch(`${archivoJson}?t=${new Date().getTime()}`);
        if (!respuesta.ok) throw new Error("No hay datos de clasificación disponibles todavía.");
        const filas = await respuesta.json();

        let html = `
            <div class="table-responsive">
                <table class="standings-table ${claseCat}">
                    <thead>
                        <tr>
                            <th style="color: ${colorCat}; background: ${colorCat}20;">POS</th>
                            <th style="text-align: left; color: ${colorCat}; background: ${colorCat}20;">EQUIPO</th>
                            <th style="color: ${colorCat}; background: ${colorCat}20;">PJ</th>
                            <th style="color: ${colorCat}; background: ${colorCat}20;">PTOS</th>
                        </tr>
                    </thead>
                    <tbody>
        `;

        filas.forEach(f => {
            const esBiarense = f.equipo.toUpperCase().includes('BIARENSE');
            const rowClass = esBiarense ? 'biarense-row' : '';
            const estiloFila = esBiarense ? `style="background: ${colorCat}25; font-weight: 700; color: #fff;"` : '';
            html += `
                <tr class="${rowClass}" ${estiloFila}>
                    <td><strong>${f.posicion}</strong></td>
                    <td style="text-align: left;">${f.equipo}</td>
                    <td>${f.pj}</td>
                    <td><strong>${f.ptos}</strong></td>
                </tr>
            `;
        });

        html += `
                    </tbody>
                </table>
            </div>
        `;
        contenedor.innerHTML = html;

    } catch (error) {
        console.error('Error al cargar clasificación:', error);
        contenedor.innerHTML = `
            <div class="card" style="text-align:center; padding: 30px;">
                <i class="fa-solid fa-triangle-exclamation" style="font-size: 2rem; color: #f59e0b; margin-bottom: 10px;"></i>
                <h3 style="font-size: 1rem; margin-bottom: 6px;">Clasificación no disponible</h3>
                <p style="font-size: 0.8rem; color: var(--text-muted);">Próximamente se generará automáticamente el archivo de clasificación desde los PDFs de la federación.</p>
            </div>
        `;
    }
}