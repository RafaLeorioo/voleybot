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

def extraer_calendario_vivo():
    print("Conectando con la web oficial de la FVBCV para extraer datos en vivo...")
    partidos_totales = []
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(URL, headers=headers, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Buscar todas las filas de partidos en la web oficial
        filas = soup.find_all("tr")
        jornada_count = 1

        for fila in filas:
            columnas = fila.find_all(["td", "th"])
            texto_fila = " ".join([limpiar_texto(c.get_text()) for c in columnas])
            
            # Filtrar únicamente las filas donde juega el CD BIARENSE
            if EQUIPO_OBJETIVO in texto_fila.upper() and len(columnas) >= 3:
                textos = [limpiar_texto(c.get_text()) for c in columnas]
                
                # Extraer local, visitante y resultado según las columnas
                local = textos[0] if len(textos) > 0 else ""
                resultado_raw = textos[1] if len(textos) > 1 else "VS"
                visitante = textos[2] if len(textos) > 2 else ""
                
                # Extraer fecha y hora del texto de toda la fila
                match_fecha = re.search(r'\b\d{2}/\d{2}/\d{4}\b', texto_fila)
                match_hora = re.search(r'\b\d{2}:\d{2}\b', texto_fila)

                fecha = match_fecha.group(0) if match_fecha else "Por definir"
                hora = match_hora.group(0) if match_hora else "Por definir"

                # Condición de Casa / Fuera dinámica
                condicion = "Casa" if EQUIPO_OBJETIVO in local.upper() else "Fuera"
                ubicacion = "Pabellón Municipal de Biar" if condicion == "Casa" else f"Campo de {local}"

                # Analizar resultado y estado
                jugado = False
                estado = "Pendiente"
                resultado = "VS"
                
                # Comprobar si hay marcador en vivo (ejemplo: "3 - 0" o "0-3")
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

                partido_obj = {
                    "jornada": f"Jornada {jornada_count}",
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
                }
                partidos_totales.append(partido_obj)
                jornada_count += 1

        print(f"Se han extraído {len(partidos_totales)} partidos en tiempo real de la FVBCV.")

    except Exception as e:
        print(f"Error extrayendo datos de la FVBCV: {e}")

    # Guardar la extracción en partidos.json
    if partidos_totales:
        with open("partidos.json", "w", encoding="utf-8") as f:
            json.dump(partidos_totales, f, ensure_ascii=False, indent=4)
        print("¡`partidos.json` actualizado correctamente con datos en vivo!")

if __name__ == "__main__":
    extraer_calendario_vivo()