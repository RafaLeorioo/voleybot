import os
import json
import requests
import pdfplumber
import re

# Lista de equipos con sus URLs oficiales de la FVBCV y los nombres de sus archivos de salida
CATEGORIAS = [
    {
        "nombre": "Senior Masculino",
        "url_fvbcv": "https://fvbcv.com/exportar_competiciones.php?idens=1825",
        "json_partidos": "partidos.json",
        "json_clasif": "clasificacion.json"
    },
    {
        "nombre": "Juvenil Femenino",
        "url_fvbcv": "https://fvbcv.com/exportar_competiciones.php?idens=1812",
        "json_partidos": "partidos_femenino.json",
        "json_clasif": "clasificacion_femenino.json"
    },
    {
        "nombre": "Infantil Femenino",
        "url_fvbcv": "https://fvbcv.com/exportar_competiciones.php?idens=1850",
        "json_partidos": "partidos_infantil.json",
        "json_clasif": "clasificacion_infantil.json"
    },
    {
        "nombre": "Cadete Femenino",
        "url_fvbcv": "https://fvbcv.com/exportar_competiciones.php?idens=1801",
        "json_partidos": "partidos_cadete.json",
        "json_clasif": "clasificacion_cadete.json"
    }
]

def extraer_clasificacion(pdf_path, json_output_path):
    clasificacion = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    if not table:
                        continue
                    
                    filas_clasificacion = []
                    esperado = 1
                    
                    for row in table:
                        if not row or not row[0]:
                            continue
                        
                        val_pos = row[0].strip()
                        
                        if val_pos.isdigit() and int(val_pos) == esperado:
                            equipo_candidato = row[1].strip() if len(row) > 1 else ""
                            
                            if equipo_candidato and not "/" in equipo_candidato and ":" not in equipo_candidato:
                                if equipo_candidato.upper() != "EQUIPO" and equipo_candidato.upper() != "CLASIFICACION":
                                    filas_clasificacion.append(row)
                                    esperado += 1
                    
                    if len(filas_clasificacion) >= 3:
                        for row in filas_clasificacion:
                            item = {
                                "posicion": row[0].strip(),
                                "equipo": row[1].strip() if len(row) > 1 else "",
                                "pj": row[2].strip() if len(row) > 2 else "",
                                "pg3": row[3].strip() if len(row) > 3 else "",
                                "pg2": row[4].strip() if len(row) > 4 else "",
                                "pp1": row[5].strip() if len(row) > 5 else "",
                                "pp0": row[6].strip() if len(row) > 6 else "",
                                "sf": row[8].strip() if len(row) > 8 else "",
                                "sc": row[9].strip() if len(row) > 9 else "",
                                "pf": row[10].strip() if len(row) > 10 else "",
                                "pc": row[11].strip() if len(row) > 11 else "",
                                "ptos": row[12].strip() if len(row) > 12 else ""
                            }
                            if item not in clasificacion:
                                clasificacion.append(item)
                        break
                if clasificacion:
                    break
        
        if clasificacion:
            with open(json_output_path, 'w', encoding='utf-8') as f:
                json.dump(clasificacion, f, ensure_ascii=False, indent=4)
            print(f"✅ ¡Clasificación extraída en {json_output_path}!")
        else:
            print(f"⚠️ No se pudo extraer la clasificación en {json_output_path}")
    except Exception as e:
        print(f"❌ Error en clasificación: {e}")

def extraer_partidos(pdf_path, json_output_path):
    """
    Parsea los partidos del PDF de la FVBCV y actualiza el archivo JSON correspondiente,
    filtrando estrictamente resultados reales de voleibol (ej. 3-0, 1-3).
    """
    try:
        partidos_existentes = []
        if os.path.exists(json_output_path):
            with open(json_output_path, 'r', encoding='utf-8') as f:
                partidos_existentes = json.load(f)

        actualizados = 0
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    for row in table:
                        if not row:
                            continue
                        row_texto = [str(cell).strip() for cell in row if cell]
                        if len(row_texto) >= 3:
                            for p in partidos_existentes:
                                local = p.get("local", "").upper()
                                visitante = p.get("visitante", "").upper()
                                
                                if local and visitante and any(local in t.upper() for t in row_texto) and any(visitante in t.upper() for t in row_texto):
                                    for cell in row:
                                        if cell:
                                            cell_str = str(cell).strip()
                                            # Expresión regular estricta para resultados de vóley (ej: 3-0, 3-1, 0-3, 2-3)
                                            # Evita totalmente horas (18:00) o fechas
                                            if re.match(r'^[0-3]\s*-\s*[0-3]$', cell_str):
                                                if cell_str != p.get("resultado"):
                                                    p["resultado"] = cell_str
                                                    p["jugado"] = True
                                                    p["estado"] = "Finalizado"
                                                    actualizados += 1

        with open(json_output_path, 'w', encoding='utf-8') as f:
            json.dump(partidos_existentes, f, ensure_ascii=False, indent=4)
            
        print(f"✅ Partidos actualizados en {json_output_path} ({actualizados} cambios detectados)")
    except Exception as e:
        print(f"❌ Error en partidos: {e}")

def procesar_todo():
    for cat in CATEGORIAS:
        print(f"\n--- Procesando: {cat['nombre']} ---")
        try:
            response = requests.get(cat['url_fvbcv'])
            if response.status_code == 200:
                pdf_temp = "temp_competencia.pdf"
                with open(pdf_temp, "wb") as f:
                    f.write(response.content)
                
                # Ejecutamos ambas tareas: Partidos y Clasificación
                extraer_partidos(pdf_temp, cat['json_partidos'])
                extraer_clasificacion(pdf_temp, cat['json_clasif'])
                
                if os.path.exists(pdf_temp):
                    os.remove(pdf_temp)
            else:
                print(f"❌ Error descargando PDF. Código: {response.status_code}")
        except Exception as e:
            print(f"❌ Error procesando {cat['nombre']}: {e}")

if __name__ == "__main__":
    procesar_todo()
