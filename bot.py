import json
import re
from pathlib import Path
import requests
import pdfplumber

URL_PDF_DIRECTA = "https://fvbcv.com/exportar_competiciones.php?idens=1825"
EQUIPO_OBJETIVO = "CD BIARENSE"
DIRECTORIO_ACTUAL = Path(__file__).resolve().parent
ARCHIVO_PDF = DIRECTORIO_ACTUAL / "calendario_grupo3.pdf"
ARCHIVO_SALIDA = DIRECTORIO_ACTUAL / "partidos.json"

def descargar_pdf_directo():
    print("📥 Descargando el PDF del Grupo 3 directamente desde la federación...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    response = requests.get(URL_PDF_DIRECTA, headers=headers)
    if response.status_code == 200:
        with open(ARCHIVO_PDF, "wb") as f:
            f.write(response.content)
        print("✅ PDF descargado correctamente.")
    else:
        raise Exception(f"Error HTTP {response.status_code} al descargar el PDF.")

def procesar_tablas_exactas():
    print("🔍 Procesando las columnas exactas del PDF oficial...")
    partidos_lista = []
    
    if not ARCHIVO_PDF.exists():
        print("❌ Error: No se encuentra el archivo PDF.")
        return

    current_jornada = "Jornada 1"

    with pdfplumber.open(ARCHIVO_PDF) as pdf:
        for pagina in pdf.pages:
            tables = pagina.extract_tables()
            for table in tables:
                for row in table:
                    # Limpiamos las celdas de la fila
                    celdas = [c.replace("\n", " ").strip() if c else "" for c in row]
                    
                    if len(celdas) < 6:
                        continue

                    col_jornada = celdas[0]
                    col_fecha_hora = celdas[1]
                    col_local = celdas[2]
                    col_res = celdas[3]
                    col_visitante = celdas[4]
                    col_pabellon = celdas[5]

                    # Actualizar jornada si la celda tiene un número válido
                    if col_jornada.isdigit() and int(col_jornada) <= 26:
                        current_jornada = f"Jornada {col_jornada}"

                    # Comprobar si nuestro equipo juega en esta fila (ya sea como local o visitante)
                    if EQUIPO_OBJETIVO in col_local.upper() or EQUIPO_OBJETIVO in col_visitante.upper():
                        
                        # Extraer fecha y hora de la columna 1
                        m_fecha = re.search(r'\b\d{2}/\d{2}/\d{4}\b', col_fecha_hora)
                        m_hora = re.search(r'\b\d{2}:\d{2}\b', col_fecha_hora)
                        fecha = m_fecha.group(0) if m_fecha else "Por definir"
                        hora = m_hora.group(0) if m_hora else "Por definir"

                        # Analizar resultado y parciales de la columna 3
                        jugado = False
                        resultado = "VS"
                        parciales = ""
                        estado = "Pendiente"

                        m_res = re.search(r'\b([0-3])\s*-\s*([0-3])\b', col_res)
                        m_parciales = re.search(r'\(([^)]+)\)', col_res)

                        if m_res:
                            s1, s2 = int(m_res.group(1)), int(m_res.group(2))
                            resultado = f"{s1} - {s2}"
                            jugado = True
                            if m_parciales:
                                parciales = m_parciales.group(1).replace(" ", "")

                        # Determinar condición
                        if EQUIPO_OBJETIVO in col_local.upper():
                            condicion = "Casa"
                            local = col_local
                            visitante = col_visitante
                            ubicacion = col_pabellon if col_pabellon else "Pabellón Municipal de Biar"
                        else:
                            condicion = "Fuera"
                            local = col_local
                            visitante = col_visitante
                            ubicacion = col_pabellon if col_pabellon else f"Pabellón de {local}"

                        if jugado:
                            partes = resultado.split("-")
                            s_loc, s_vis = int(partes[0]), int(partes[1])
                            if condicion == "Casa":
                                estado = "Victoria" if s_loc > s_vis else "Derrota"
                            else:
                                estado = "Victoria" if s_vis > s_loc else "Derrota"

                        partido_dict = {
                            "jornada": current_jornada,
                            "fecha": fecha,
                            "hora": hora,
                            "condicion": condicion,
                            "local": local,
                            "visitante": visitante,
                            "ubicacion": ubicacion,
                            "resultado": resultado,
                            "parciales": parciales,
                            "jugado": jugado,
                            "estado": estado
                        }

                        # Evitar duplicados de la misma jornada para el Biarense
                        if not any(p["jornada"] == current_jornada for p in partidos_lista):
                            partidos_lista.append(partido_dict)

    if partidos_lista:
        # Ordenar cronológicamente por número de jornada
        partidos_lista.sort(key=lambda x: int(re.search(r'\d+', x["jornada"]).group()))
        with open(ARCHIVO_SALIDA, "w", encoding="utf-8") as f:
            json.dump(partidos_lista, f, ensure_ascii=False, indent=4)
        print(f"✅ ¡Éxito absoluto! Se han guardado {len(partidos_lista)} partidos exactos y limpios en `partidos.json`.")
    else:
        print("⚠️ No se pudieron extraer los partidos.")

if __name__ == "__main__":
    try:
        descargar_pdf_directo()
    except Exception as e:
        print(f"⚠️ Aviso al descargar: {e}. Usando PDF local...")
    
    procesar_tablas_exactas()