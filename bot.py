import json
import re
from pathlib import Path
import requests
import pdfplumber

DIRECTORIO_ACTUAL = Path(__file__).resolve().parent

CONFIGURACIONES = [
    {
        "nombre": "Senior Masculino",
        "url_pdf": "https://fvbcv.com/exportar_competiciones.php?idens=1825",
        "equipo_objetivo": "CD BIARENSE",
        "archivo_salida": DIRECTORIO_ACTUAL / "partidos.json"
    },
    {
        "nombre": "Juvenil Femenino",
        "url_pdf": "https://fvbcv.com/exportar_competiciones.php?idens=1812",
        "equipo_objetivo": "BIARENSE",
        "archivo_salida": DIRECTORIO_ACTUAL / "partidos_femenino.json"
    },
    {
        "nombre": "Infantil Femenino",
        "url_pdf": "https://fvbcv.com/exportar_competiciones.php?idens=1850",
        "equipo_objetivo": "BIARENSE",
        "archivo_salida": DIRECTORIO_ACTUAL / "partidos_infantil.json"
    },
    {
        "nombre": "Cadete Femenino",
        "url_pdf": "https://fvbcv.com/exportar_competiciones.php?idens=1801",
        "equipo_objetivo": "BIARENSE",
        "archivo_salida": DIRECTORIO_ACTUAL / "partidos_cadete.json"
    }
]

def descargar_y_procesar():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    for config in CONFIGURACIONES:
        print(f"\n📥 Procesando categoría: {config['nombre']}...")
        archivo_pdf = DIRECTORIO_ACTUAL / f"calendario_{config['nombre'].lower().replace(' ', '_')}.pdf"
        
        try:
            response = requests.get(config["url_pdf"], headers=headers)
            if response.status_code == 200:
                with open(archivo_pdf, "wb") as f:
                    f.write(response.content)
                print(f"✅ PDF de {config['nombre']} descargado.")
            else:
                print(f"❌ Error HTTP {response.status_code} al descargar {config['nombre']}.")
                continue
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            continue

        partidos_lista = []
        current_jornada = "Jornada 1"
        
        with pdfplumber.open(archivo_pdf) as pdf:
            for pagina in pdf.pages:
                tables = pagina.extract_tables()
                for table in tables:
                    for row in table:
                        celdas = [c.replace("\n", " ").strip() if c else "" for c in row]
                        if len(celdas) < 6:
                            continue

                        col_jornada = celdas[0]
                        col_fecha_hora = celdas[1]
                        col_local = celdas[2]
                        col_res = celdas[3]
                        col_visitante = celdas[4]
                        col_pabellon = celdas[5]

                        if col_jornada.isdigit() and int(col_jornada) <= 26:
                            current_jornada = f"Jornada {col_jornada}"

                        if config["equipo_objetivo"] in col_local.upper() or config["equipo_objetivo"] in col_visitante.upper():
                            if "DESCANSA" in col_local.upper() or "DESCANSA" in col_visitante.upper():
                                continue

                            m_fecha = re.search(r'\b\d{2}/\d{2}/\d{4}\b', col_fecha_hora)
                            m_hora = re.search(r'\b\d{2}:\d{2}\b', col_fecha_hora)
                            fecha = m_fecha.group(0) if m_fecha else "Por definir"
                            hora = m_hora.group(0) if m_hora else "Por definir"

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

                            if config["equipo_objetivo"] in col_local.upper():
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

                            if not any(p["jornada"] == current_jornada and p["local"] == local and p["visitante"] == visitante for p in partidos_lista):
                                partidos_lista.append(partido_dict)

        # Guardar partidos limpios y ordenados
        if partidos_lista:
            partidos_lista.sort(key=lambda x: int(re.search(r'\d+', x["jornada"]).group()))
            with open(config["archivo_salida"], "w", encoding="utf-8") as f:
                json.dump(partidos_lista, f, ensure_ascii=False, indent=4)
            print(f"✅ Guardados {len(partidos_lista)} partidos correctamente para {config['nombre']}.")

if __name__ == "__main__":
    descargar_y_procesar()