import json

EQUIPO_OBJETIVO = "CD BIARENSE"

def extraer_calendario_completo():
    print("Generando calendario oficial completo para CD BIARENSE...")

    # Calendario Oficial Estructurado de la Temporada
    calendario_oficial = [
        {"jornada": 1, "local": "ATLÉTICO SALESIANOS ALCOY", "visitante": "CD BIARENSE", "fecha": "03/10/2026", "hora": "12:00", "ubicacion": "Pabellón Colegio Salesianos (Alcoy)", "resultado": "0 - 3", "parciales": "15-25 • 18-25 • 20-25", "jugado": True},
        {"jornada": 2, "local": "CD BIARENSE", "visitante": "CV SAN VICENTE GLADIADORES", "fecha": "10/10/2026", "hora": "18:00", "ubicacion": "Pabellón Municipal de Biar", "resultado": "3 - 0", "parciales": "25-14 • 25-12 • 25-15", "jugado": True},
        {"jornada": 3, "local": "CV LUCENTUM", "visitante": "CD BIARENSE", "fecha": "17/10/2026", "hora": "19:00", "ubicacion": "Polideportivo Municipal de Alicante", "resultado": "VS", "parciales": "", "jugado": False},
        {"jornada": 4, "local": "CD BIARENSE", "visitante": "CV ELCHE", "fecha": "24/10/2026", "hora": "18:00", "ubicacion": "Pabellón Municipal de Biar", "resultado": "VS", "parciales": "", "jugado": False},
        {"jornada": 5, "local": "FABRAQUER VB CAMPELLO", "visitante": "CD BIARENSE", "fecha": "31/10/2026", "hora": "17:30", "ubicacion": "Pabellón Municipal El Campello", "resultado": "VS", "parciales": "", "jugado": False},
        {"jornada": 6, "local": "CD BIARENSE", "visitante": "GRUPO NEXUS GUARDAMAR", "fecha": "07/11/2026", "hora": "18:00", "ubicacion": "Pabellón Municipal de Biar", "resultado": "VS", "parciales": "", "jugado": False},
        {"jornada": 7, "local": "CD BIARENSE", "visitante": "VOLEIBOL VINALOPÓ AZUL", "fecha": "14/11/2026", "hora": "18:00", "ubicacion": "Pabellón Municipal de Biar", "resultado": "VS", "parciales": "", "jugado": False},
        {"jornada": 8, "local": "POLANENS SANTA POLA", "visitante": "CD BIARENSE", "fecha": "21/11/2026", "hora": "18:00", "ubicacion": "Pabellón Municipal Santa Pola", "resultado": "VS", "parciales": "", "jugado": False},
        {"jornada": 9, "local": "CD BIARENSE", "visitante": "CV CREVILLENT", "fecha": "28/11/2026", "hora": "18:00", "ubicacion": "Pabellón Municipal de Biar", "resultado": "VS", "parciales": "", "jugado": False},
        {"jornada": 10, "local": "CV SAN VICENTE ESPARTANOS", "visitante": "CD BIARENSE", "fecha": "05/12/2026", "hora": "18:00", "ubicacion": "Polideportivo Municipal San Vicente", "resultado": "VS", "parciales": "", "jugado": False},
        {"jornada": 11, "local": "CD BIARENSE", "visitante": "CV LUCENTUM - B", "fecha": "12/12/2026", "hora": "18:00", "ubicacion": "Pabellón Municipal de Biar", "resultado": "VS", "parciales": "", "jugado": False},
        {"jornada": 12, "local": "CV SAN VICENTE GLADIADORES", "visitante": "CD BIARENSE", "fecha": "19/12/2026", "hora": "18:00", "ubicacion": "Polideportivo Municipal San Vicente", "resultado": "VS", "parciales": "", "jugado": False},
        {"jornada": 13, "local": "CD BIARENSE", "visitante": "ATLÉTICO SALESIANOS ALCOY", "fecha": "16/01/2027", "hora": "18:00", "ubicacion": "Pabellón Municipal de Biar", "resultado": "VS", "parciales": "", "jugado": False},
    ]

    partidos_totales = []

    for p in calendario_oficial:
        local = p["local"]
        visitante = p["visitante"]
        
        # Determinar si jugamos en Casa o Fuera
        condicion = "Casa" if EQUIPO_OBJETIVO in local.upper() else "Fuera"

        # Calcular Victoria, Derrota o Pendiente
        estado = "Pendiente"
        if p["jugado"] and p["resultado"] != "VS":
            try:
                sets = [int(s.strip()) for s in p["resultado"].split('-')]
                if condicion == "Casa":
                    estado = "Victoria" if sets[0] > sets[1] else "Derrota"
                else:
                    estado = "Victoria" if sets[1] > sets[0] else "Derrota"
            except Exception:
                estado = "Finalizado"

        partido_obj = {
            "jornada": f"Jornada {p['jornada']}",
            "fecha": p["fecha"],
            "hora": p["hora"],
            "condicion": condicion,
            "local": local,
            "visitante": visitante,
            "ubicacion": p["ubicacion"],
            "resultado": p["resultado"],
            "parciales": p["parciales"],
            "jugado": p["jugado"],
            "estado": estado
        }
        partidos_totales.append(partido_obj)

    # Guardar partidos.json
    with open("partidos.json", "w", encoding="utf-8") as f:
        json.dump(partidos_totales, f, ensure_ascii=False, indent=4)
        
    print(f"¡Éxito! `partidos.json` generado correctamente con {len(partidos_totales)} jornadas completas.")

if __name__ == "__main__":
    extraer_calendario_completo()