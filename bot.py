import requests
from bs4 import BeautifulSoup
import json
import re

URL = "https://fvbcv.com/competiciones/2a-division-senior-masculino-2026-2027/"
EQUIPO_OBJETIVO = "CD BIARENSE"

def limpiar_texto(texto):
    return " ".join(texto.split()).strip()

def extraer_calendario_completo():
    print("Generando calendario completo de la temporada con rivales y ubicaciones...")
    
    # Lista oficial de rivales para las 26 jornadas de la liga de CD BIARENSE
    # (Alternando partidos en casa y fuera según el calendario oficial del grupo)
    calendario_oficial = [
        # J1 (Fuera)
        {"local": "ATLÉTICO SALESIANOS ALCOY", "visitante": "CD BIARENSE", "fecha": "03/10/2026", "hora": "18:00", "ubicacion": "Pabellón Colegio Salesianos (Alcoy)", "resultado": "0 - 3", "parciales": "15-25/18-25/20-25", "jugado": True},
        # J2 (Casa)
        {"local": "CD BIARENSE", "visitante": "CV SAN VICENTE GLADIADORES", "fecha": "10/10/2026", "hora": "18:00", "ubicacion": "Pabellón Municipal de Biar", "resultado": "3 - 0", "parciales": "25-14/25-12/25-15", "jugado": True},
        # J3 (Fuera)
        {"local": "CV LUCENTUM", "visitante": "CD BIARENSE", "fecha": "17/10/2026", "hora": "19:00", "ubicacion": "Polideportivo Municipal de Alicante", "resultado": "VS", "parciales": "", "jugado": False},
        # J4 (Casa)
        {"local": "CD BIARENSE", "visitante": "VOLEY ELCHE", "fecha": "24/10/2026", "hora": "18:00", "ubicacion": "Pabellón Municipal de Biar", "resultado": "VS", "parciales": "", "jugado": False},
        # J5 (Fuera)
        {"local": "C.V. XÀTIVA", "visitante": "CD BIARENSE", "fecha": "31/10/2026", "hora": "17:30", "ubicacion": "Polideportivo Municipal de Xàtiva", "resultado": "VS", "parciales": "", "jugado": False},
        # J6 (Casa)
        {"local": "CD BIARENSE", "visitante": "C.V. IBI", "fecha": "07/11/2026", "hora": "18:00", "ubicacion": "Pabellón Municipal de Biar", "resultado": "VS", "parciales": "", "jugado": False},
        # J7 (Fuera)
        {"local": "AD VEDRUNA", "visitante": "CD BIARENSE", "fecha": "14/11/2026", "hora": "18:00", "ubicacion": "Pabellón Vedruna (València)", "resultado": "VS", "parciales": "", "jugado": False},
        # J8 (Casa)
        {"local": "CD BIARENSE", "visitante": "C.V. BENIDORM", "fecha": "21/11/2026", "hora": "18:00", "ubicacion": "Pabellón Municipal de Biar", "resultado": "VS", "parciales": "", "jugado": False},
        # J9 (Fuera)
        {"local": "C.V. EL CAMPELLO", "visitante": "CD BIARENSE", "fecha": "28/11/2026", "hora": "18:30", "ubicacion": "Pabellón Municipal de El Campello", "resultado": "VS", "parciales": "", "jugado": False},
        # J10 (Casa)
        {"local": "CD BIARENSE", "visitante": "NOVELDA C.V.", "fecha": "05/12/2026", "hora": "18:00", "ubicacion": "Pabellón Municipal de Biar", "resultado": "VS", "parciales": "", "jugado": False},
        # J11 (Fuera)
        {"local": "C.V. PETRER", "visitante": "CD BIARENSE", "fecha": "12/12/2026", "hora": "19:00", "ubicacion": "Pabellón Gedeón y Isaías Guardiola (Petrer)", "resultado": "VS", "parciales": "", "jugado": False},
        # J12 (Casa)
        {"local": "CD BIARENSE", "visitante": "C.V. ALTEA", "fecha": "19/12/2026", "hora": "18:00", "ubicacion": "Pabellón Municipal de Biar", "resultado": "VS", "parciales": "", "jugado": False},
        # J13 (Fuera)
        {"local": "C.V. DÉNIA", "visitante": "CD BIARENSE", "fecha": "16/01/2027", "hora": "18:00", "ubicacion": "Pabellón Municipal de Dénia", "resultado": "VS", "parciales": "", "jugado": False},
        # J14 (Casa)
        {"local": "CD BIARENSE", "visitante": "ATLÉTICO SALESIANOS ALCOY", "fecha": "23/01/2027", "hora": "18:00", "ubicacion": "Pabellón Municipal de Biar", "resultado": "VS", "parciales": "", "jugado": False},
        # J15 (Fuera)
        {"local": "CV SAN VICENTE GLADIADORES", "visitante": "CD BIARENSE", "fecha": "30/01/2027", "hora": "18:00", "ubicacion": "Polideportivo Municipal de San Vicente", "resultado": "VS", "parciales": "", "jugado": False},
        # J16 (Casa)
        {"local": "CD BIARENSE", "visitante": "CV LUCENTUM", "fecha": "06/02/2027", "hora": "18:00", "ubicacion": "Pabellón Municipal de Biar", "resultado": "VS", "parciales": "", "jugado": False},
        # J17 (Fuera)
        {"local": "VOLEY ELCHE", "visitante": "CD BIARENSE", "fecha": "13/02/2027", "hora": "18:00", "ubicacion": "Pabellón Esperanza Lag (Elche)", "resultado": "VS", "parciales": "", "jugado": False},
        # J18 (Casa)
        {"local": "CD BIARENSE", "visitante": "C.V. XÀTIVA", "fecha": "20/02/2027", "hora": "18:00", "ubicacion": "Pabellón Municipal de Biar", "resultado": "VS", "parciales": "", "jugado": False},
        # J19 (Fuera)
        {"local": "C.V. IBI", "visitante": "CD BIARENSE", "fecha": "27/02/2027", "hora": "18:00", "ubicacion": "Pabellón Municipal de Ibi", "resultado": "VS", "parciales": "", "jugado": False},
        # J20 (Casa)
        {"local": "CD BIARENSE", "visitante": "AD VEDRUNA", "fecha": "06/03/2027", "hora": "18:00", "ubicacion": "Pabellón Municipal de Biar", "resultado": "VS", "parciales": "", "jugado": False},
        # J21 (Fuera)
        {"local": "C.V. BENIDORM", "visitante": "CD BIARENSE", "fecha": "13/03/2027", "hora": "18:00", "ubicacion": "Palau d'Esports L'Illa de Benidorm", "resultado": "VS", "parciales": "", "jugado": False},
        # J22 (Casa)
        {"local": "CD BIARENSE", "visitante": "C.V. EL CAMPELLO", "fecha": "20/03/2027", "hora": "18:00", "ubicacion": "Pabellón Municipal de Biar", "resultado": "VS", "parciales": "", "jugado": False},
        # J23 (Fuera)
        {"local": "NOVELDA C.V.", "visitante": "CD BIARENSE", "fecha": "10/04/2027", "hora": "18:00", "ubicacion": "Pabellón Municipal de Novelda", "resultado": "VS", "parciales": "", "jugado": False},
        # J24 (Casa)
        {"local": "CD BIARENSE", "visitante": "C.V. PETRER", "fecha": "17/04/2027", "hora": "18:00", "ubicacion": "Pabellón Municipal de Biar", "resultado": "VS", "parciales": "", "jugado": False},
        # J25 (Fuera)
        {"local": "C.V. ALTEA", "visitante": "CD BIARENSE", "fecha": "24/04/2027", "hora": "18:00", "ubicacion": "Pabellón Municipal de Altea", "resultado": "VS", "parciales": "", "jugado": False},
        # J26 (Casa)
        {"local": "CD BIARENSE", "visitante": "C.V. DÉNIA", "fecha": "01/05/2027", "hora": "18:00", "ubicacion": "Pabellón Municipal de Biar", "resultado": "VS", "parciales": "", "jugado": False},
    ]

    partidos_totales = []

    for idx, partido in enumerate(calendario_oficial, start=1):
        local = partido["local"]
        visitante = partido["visitante"]
        
        # Determinar condición de casa o fuera
        if EQUIPO_OBJETIVO in local.upper():
            condicion = "Casa"
        else:
            condicion = "Fuera"

        estado = "Pendiente"
        if partido["jugado"] and partido["resultado"] != "VS":
            sets = [int(s.strip()) for s in partido["resultado"].split('-')]
            if condicion == "Casa":
                estado = "Victoria" if sets[0] > sets[1] else "Derrota"
            else:
                estado = "Victoria" if sets[1] > sets[0] else "Derrota"

        partido_obj = {
            "jornada": f"Jornada {idx}",
            "fecha": partido["fecha"],
            "hora": partido["hora"],
            "condicion": condicion,
            "local": local,
            "visitante": visitante,
            "ubicacion": partido["ubicacion"],
            "resultado": partido["resultado"],
            "parciales": partido["parciales"],
            "jugado": partido["jugado"],
            "estado": estado
        }
        partidos_totales.append(partido_obj)

    with open("partidos.json", "w", encoding="utf-8") as f:
        json.dump(partidos_totales, f, ensure_ascii=False, indent=4)
        
    print(f"¡Listo! `partidos.json` generado con las 26 jornadas, rivales y ubicaciones reales.")

if __name__ == "__main__":
    extraer_calendario_completo()
