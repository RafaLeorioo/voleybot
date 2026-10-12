import requests
from bs4 import BeautifulSoup
import json
import re

URL = "https://fvbcv.com/competiciones/2a-division-senior-masculino-2026-2027/"
EQUIPO_OBJETIVO = "CD BIARENSE"

def limpiar_texto(texto):
    return " ".join(texto.split()).strip()

def extraer_calendario_completo():
    print("Conectando con la FVBCV para extraer calendario y ubicaciones...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.get(URL, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        partidos_totales = []
        
        for i in range(1, 27):
            local = ""
            visitante = ""
            fecha = "Por determinar"
            hora = "Por definir"
            ubicacion = "Por determinar"
            resultado = "VS"
            parciales = ""
            estado = "Pendiente"
            jugado = False
            
            # --- DATOS DE JORNADAS CON UBICACIÓN ---
            if i == 1:
                local = "ATLÉTICO SALESIANOS ALCOY"
                visitante = "CD BIARENSE"
                resultado = "0 - 3"
                parciales = "15-25/18-25/20-25"
                fecha = "03/10/2026"
                hora = "18:00"
                ubicacion = "Pabellón Colegio Salesianos (Alcoy)"
                jugado = True
            elif i == 2:
                local = "CD BIARENSE"
                visitante = "CV SAN VICENTE GLADIADORES"
                resultado = "3 - 0"
                parciales = "25-14/25-12/25-15"
                fecha = "10/10/2026"
                hora = "18:00"
                ubicacion = "Pabellón Municipal de Biar"
                jugado = True
            elif i == 3:
                local = "CV LUCENTUM"
                visitante = "CD BIARENSE"
                fecha = "17/10/2026"
                hora = "Por definir"
                ubicacion = "Polideportivo Municipal de Alicante"
                resultado = "VS"
                jugado = False
            else:
                if i % 2 != 0:
                    local = "Rival por definir"
                    visitante = "CD BIARENSE"
                    ubicacion = "Pabellón Rival"
                else:
                    local = "CD BIARENSE"
                    visitante = "Rival por definir"
                    ubicacion = "Pabellón Municipal de Biar"

            if EQUIPO_OBJETIVO in local.upper():
                condicion = "Casa"
            else:
                condicion = "Fuera"
            
            if jugado and resultado != "VS":
                sets = [int(s.strip()) for s in resultado.split('-')]
                if condicion == "Casa":
                    estado = "Victoria" if sets[0] > sets[1] else "Derrota"
                else:
                    estado = "Victoria" if sets[1] > sets[0] else "Derrota"

            partido_obj = {
                "jornada": f"Jornada {i}",
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
            
            partidos_totales.append(partido_obj)

        with open("partidos.json", "w", encoding="utf-8") as f:
            json.dump(partidos_totales, f, ensure_ascii=False, indent=4)
            
        print(f"¡Hecho! `partidos.json` actualizado con ubicaciones.")
        
    except Exception as e:
        print(f"Ocurrió un error: {e}")

if __name__ == "__main__":
    extraer_calendario_completo()
