import requests
from bs4 import BeautifulSoup
import json
import re

URL = "https://fvbcv.com/competiciones/2a-division-senior-masculino-2026-2027/"
EQUIPO_OBJETIVO = "BIARENSE"

def limpiar_texto(texto):
    if not texto:
        return ""
    return " ".join(texto.split()).strip()

def extraer_calendario_real():
    print("Conectando con la FVBCV para extraer las jornadas exactas...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    partidos_totales = []

    try:
        response = requests.get(URL, headers=headers, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        # Buscar todos los bloques que contengan las jornadas en la web
        # En la FVBCV las jornadas vienen agrupadas en contenedores con cabecera JOR. X
        bloques = soup.find_all(["div", "section", "table"])

        jornadas_procesadas = set()

        for bloque in bloques:
            texto_bloque = limpiar_texto(bloque.get_text())

            # Detectar el número de jornada dentro del bloque
            match_jor = re.search(r'\b(JOR\.|JORNADA)\s*(\d+)\b', texto_bloque, re.IGNORECASE)
            if not match_jor:
                continue

            num_jornada = int(match_jor.group(2))

            # Evitar duplicar bloques procesados de la misma jornada
            if EQUIPO_OBJETIVO not in texto_bloque.upper():
                continue

            # Buscar filas de partidos dentro de este bloque de jornada
            filas = bloque.find_all("tr")
            for fila in filas:
                texto_fila = limpiar_texto(fila.get_text())

                if EQUIPO_OBJETIVO in texto_fila.upper():
                    cols = [limpiar_texto(c.get_text()) for c in fila.find_all(["td", "th"])]

                    if len(cols) >= 3:
                        local = cols[0]
                        resultado_raw = cols[1]
                        visitante = cols[2]

                        # Extraer fecha y hora usando expresiones regulares
                        match_fecha = re.search(r'\b\d{2}/\d{2}/\d{4}\b', texto_fila)
                        match_hora = re.search(r'\b\d{2}:\d{2}\b', texto_fila)

                        fecha = match_fecha.group(0) if match_fecha else "Por definir"
                        hora = match_hora.group(0) if match_hora else "Por definir"

                        condicion = "Casa" if EQUIPO_OBJETIVO in local.upper() else "Fuera"
                        ubicacion = "Pabellón Municipal de Biar" if condicion == "Casa" else f"Campo de {local}"

                        # Determinar estado del partido
                        jugado = False
                        estado = "Pendiente"
                        resultado = "VS"

                        if "-" in resultado_raw and not resultado_raw.strip().startswith("-"):
                            partes = resultado_raw.replace(" ", "").split("-")
                            if len(partes) == 2 and partes[0].isdigit() and partes[1].isdigit():
                                s_loc, s_vis = int(partes[0]), int(partes[1])
                                resultado = f"{s_loc} - {s_vis}"
                                jugado = True
                                if condicion == "Casa":
                                    estado = "Victoria" if s_loc > s_vis else "Derrota"
                                else:
                                    estado = "Victoria" if s_vis > s_loc else "Derrota"

                        clave_jornada = f"Jornada {num_jornada}"

                        if clave_jornada not in jornadas_procesadas:
                            jornadas_procesadas.add(clave_jornada)
                            partidos_totales.append({
                                "jornada": clave_jornada,
                                "num_jornada": num_jornada,
                                "fecha": fecha,
                                "hora": hora,
                                "condicion": condicion,
                                "local": local,
                                "visitante": visitante,
                                "ubicacion": ubicacion,
                                "resultado": resultado,
                                "parciales": "",
                                "jugado": jugado,
                                "estado": estado
                            })

    except Exception as e:
        print(f"Error al conectar o extraer de la FVBCV: {e}")

    # Ordenar estrictamente por el número de jornada (Jornada 1, Jornada 2, ..., Jornada 26)
    partidos_totales.sort(key=lambda x: x["num_jornada"])

    # Limpiar campo auxiliar de ordenación antes de guardar
    for p in partidos_totales:
        p.pop("num_jornada", None)

    # Guardar los datos en partidos.json
    if partidos_totales:
        with open("partidos.json", "w", encoding="utf-8") as f:
            json.dump(partidos_totales, f, ensure_ascii=False, indent=4)
        print(f"¡Éxito! `partidos.json` generado con {len(partidos_totales)} jornadas en orden exacto.")
    else:
        print("No se pudieron extraer partidos en vivo. Verifica la URL de la FVBCV.")

if __name__ == "__main__":
    extraer_calendario_real()