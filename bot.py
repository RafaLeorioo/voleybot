
import json
import re
from datetime import datetime
from pathlib import Path

# ============================================================
# CONFIGURACIÓN
# ============================================================

ARCHIVO_SALIDA = Path(__file__).resolve().parent / "partidos.json"

# Introduce aquí TODAS las jornadas del calendario oficial.
#
# Campos necesarios:
# jornada, fecha, hora, local, visitante, ubicacion,
# resultado y parciales.
#
# Los campos condicion, jugado y estado se calculan automáticamente.
#
# Partido pendiente:
# "resultado": "VS"
# "parciales": ""
#
# Partido disputado:
# "resultado": "3 - 1"
# "parciales": "25-20 • 22-25 • 25-18 • 25-16"

PARTIDOS = [
    # EJEMPLO DE PARTIDO PENDIENTE (sustituye los datos por los reales):
    # {
    #     "jornada": 1,
    #     "fecha": "25/10/2026",
    #     "hora": "18:00",
    #     "local": "CD BIARENSE",
    #     "visitante": "Equipo rival",
    #     "ubicacion": "Pabellón municipal",
    #     "resultado": "VS",
    #     "parciales": "",
    # },
    #
    # EJEMPLO DE PARTIDO DISPUTADO:
    # {
    #     "jornada": 2,
    #     "fecha": "01/11/2026",
    #     "hora": "12:00",
    #     "local": "CD BIARENSE",
    #     "visitante": "Equipo rival",
    #     "ubicacion": "Pabellón municipal",
    #     "resultado": "3 - 1",
    #     "parciales": "25-20 • 22-25 • 25-18 • 25-16",
    # },
]


# ============================================================
# CONSTANTES Y VALIDACIONES
# ============================================================

CLAVES_SALIDA = [
    "jornada",
    "fecha",
    "hora",
    "condicion",
    "local",
    "visitante",
    "ubicacion",
    "resultado",
    "parciales",
    "jugado",
    "estado",
]

PATRON_HORA = re.compile(r"^(?:[01]\d|2[0-3]):[0-5]\d$")
PATRON_RESULTADO = re.compile(r"^([0-3])\s*-\s*([0-3])$")
PATRON_PARCIAL = re.compile(r"^\d{1,2}\s*-\s*\d{1,2}$")


def validar_texto(valor, campo, jornada):
    """Comprueba que un campo de texto sea válido."""
    if not isinstance(valor, str) or not valor.strip():
        raise ValueError(
            f"Jornada {jornada}: el campo '{campo}' está vacío o no es texto."
        )

    valor = valor.strip()

    if any(ord(c) < 32 for c in valor):
        raise ValueError(
            f"Jornada {jornada}: el campo '{campo}' contiene caracteres inválidos."
        )

    return valor


def validar_fecha(fecha, jornada):
    """Valida una fecha estrictamente en formato DD/MM/AAAA."""
    if not re.fullmatch(r"\d{2}/\d{2}/\d{4}", fecha):
        raise ValueError(
            f"Jornada {jornada}: fecha incorrecta '{fecha}'. "
            "Usa DD/MM/AAAA."
        )

    try:
        datetime.strptime(fecha, "%d/%m/%Y")
    except ValueError as error:
        raise ValueError(
            f"Jornada {jornada}: la fecha '{fecha}' no es válida."
        ) from error


def validar_hora(hora, jornada):
    """Valida la hora en formato HH:MM de 24 horas."""
    if not PATRON_HORA.fullmatch(hora):
        raise ValueError(
            f"Jornada {jornada}: hora incorrecta '{hora}'. Usa HH:MM."
        )


def validar_nombre_equipo(nombre, campo, jornada):
    """Evita incluir accidentalmente fechas u horas en los nombres."""
    nombre = validar_texto(nombre, campo, jornada)

    contiene_fecha = re.search(
        r"(?<!\d)\d{2}/\d{2}/\d{4}(?!\d)", nombre
    )
    contiene_hora = re.search(
        r"(?<!\d)(?:[01]\d|2[0-3]):[0-5]\d(?!\d)", nombre
    )

    if contiene_fecha or contiene_hora:
        raise ValueError(
            f"Jornada {jornada}: el equipo '{nombre}' parece contener "
            "una fecha u hora. Corrige el nombre del equipo."
        )

    return nombre


def calcular_estado(local, visitante, resultado, parciales, jornada):
    """
    Calcula condicion, jugado y estado.
    Devuelve los valores derivados a partir del resultado.
    """

    # La condición depende exclusivamente del equipo local.
    condicion = (
        "Casa"
        if "BIARENSE" in local.upper()
        else "Fuera"
    )

    # Partido pendiente.
    if resultado.upper() == "VS":
        if parciales:
            raise ValueError(
                f"Jornada {jornada}: un partido pendiente debe tener "
                "los parciales vacíos."
            )

        return condicion, False, "Pendiente", "VS", ""

    # Validar el marcador de sets.
    coincidencia = PATRON_RESULTADO.fullmatch(resultado)

    if not coincidencia:
        raise ValueError(
            f"Jornada {jornada}: resultado incorrecto '{resultado}'. "
            "Usa, por ejemplo, '3 - 0' o '3 - 2', o 'VS' si está pendiente."
        )

    sets_local = int(coincidencia.group(1))
    sets_visitante = int(coincidencia.group(2))

    # En voleibol, el partido debe terminar al alcanzar tres sets.
    if (
        sets_local == sets_visitante
        or max(sets_local, sets_visitante) != 3
        or min(sets_local, sets_visitante) > 2
    ):
        raise ValueError(
            f"Jornada {jornada}: marcador de sets imposible "
            f"o incompleto '{resultado}'."
        )

    # Validar parciales.
    if not parciales:
        raise ValueError(
            f"Jornada {jornada}: un partido disputado debe tener parciales."
        )

    parciales_lista = [
        parcial.strip()
        for parcial in parciales.split("•")
    ]

    numero_sets = sets_local + sets_visitante

    if len(parciales_lista) != numero_sets:
        raise ValueError(
            f"Jornada {jornada}: el marcador '{resultado}' requiere "
            f"{numero_sets} parciales, pero se han indicado "
            f"{len(parciales_lista)}."
        )

    sets_ganados_local = 0
    sets_ganados_visitante = 0

    for parcial in parciales_lista:
        if not PATRON_PARCIAL.fullmatch(parcial):
            raise ValueError(
                f"Jornada {jornada}: parcial incorrecto '{parcial}'. "
                "Usa el formato 25-20."
            )

        puntos = re.fullmatch(
            r"(\d{1,2})\s*-\s*(\d{1,2})", parcial
        )
        puntos_local = int(puntos.group(1))
        puntos_visitante = int(puntos.group(2))

        if puntos_local == puntos_visitante:
            raise ValueError(
                f"Jornada {jornada}: un set no puede acabar empatado."
            )

        # Sets normales a 25 y quinto set a 15:
        # se necesitan al menos dos puntos de diferencia.
        es_ultimo_set = len(parciales_lista) == 5 and (
            parcial == parciales_lista[-1]
        )
        objetivo = 15 if es_ultimo_set else 25

        ganador_puntos = (
            puntos_local if puntos_local > puntos_visitante
            else puntos_visitante
        )
        perdedor_puntos = min(puntos_local, puntos_visitante)

        if ganador_puntos < objetivo or ganador_puntos - perdedor_puntos < 2:
            raise ValueError(
                f"Jornada {jornada}: parcial inválido '{parcial}'."
            )

        if puntos_local > puntos_visitante:
            sets_ganados_local += 1
        else:
            sets_ganados_visitante += 1

    if (
        sets_ganados_local != sets_local
        or sets_ganados_visitante != sets_visitante
    ):
        raise ValueError(
            f"Jornada {jornada}: los parciales no coinciden "
            f"con el resultado '{resultado}'."
        )

    # Determinar si gana el CD BIARENSE según la condición.
    gana_biarense = (
        sets_local > sets_visitante
        if condicion == "Casa"
        else sets_visitante > sets_local
    )

    estado = "Victoria" if gana_biarense else "Derrota"

    resultado_limpio = f"{sets_local} - {sets_visitante}"
    parciales_limpios = " • ".join(
        re.sub(r"\s*-\s*", "-", parcial)
        for parcial in parciales_lista
    )

    return condicion, True, estado, resultado_limpio, parciales_limpios


# ============================================================
# GENERACIÓN DEL JSON
# ============================================================

def generar_partidos():
    partidos_finales = []
    jornadas_vistas = set()

    for partido in PARTIDOS:
        if not isinstance(partido, dict):
            raise ValueError("Cada partido debe ser un diccionario.")

        jornada_original = partido.get("jornada")

        if isinstance(jornada_original, bool):
            raise ValueError("El número de jornada debe ser un entero.")

        try:
            jornada_numero = int(jornada_original)
        except (TypeError, ValueError) as error:
            raise ValueError(
                f"Jornada inválida: {jornada_original!r}."
            ) from error

        if (
            jornada_numero < 1
            or str(jornada_numero) != str(jornada_original).strip()
        ):
            raise ValueError(
                f"Número de jornada incorrecto: {jornada_original!r}."
            )

        if jornada_numero in jornadas_vistas:
            raise ValueError(
                f"La jornada {jornada_numero} aparece más de una vez."
            )

        jornadas_vistas.add(jornada_numero)

        fecha = validar_texto(
            partido.get("fecha"), "fecha", jornada_numero
        )
        hora = validar_texto(
            partido.get("hora"), "hora", jornada_numero
        )
        local = validar_nombre_equipo(
            partido.get("local"), "local", jornada_numero
        )
        visitante = validar_nombre_equipo(
            partido.get("visitante"), "visitante", jornada_numero
        )
        ubicacion = validar_texto(
            partido.get("ubicacion"), "ubicacion", jornada_numero
        )
        resultado = validar_texto(
            partido.get("resultado"), "resultado", jornada_numero
        )
        parciales = partido.get("parciales")

        if not isinstance(parciales, str):
            raise ValueError(
                f"Jornada {jornada_numero}: 'parciales' debe ser texto."
            )

        parciales = parciales.strip()

        validar_fecha(fecha, jornada_numero)
        validar_hora(hora, jornada_numero)

        if local.casefold() == visitante.casefold():
            raise ValueError(
                f"Jornada {jornada_numero}: el equipo local y el "
                "visitante no pueden ser el mismo."
            )

        (
            condicion,
            jugado,
            estado,
            resultado,
            parciales,
        ) = calcular_estado(
            local,
            visitante,
            resultado,
            parciales,
            jornada_numero,
        )

        # Se construye explícitamente para garantizar las claves exactas.
        partido_final = {
            "jornada": f"Jornada {jornada_numero}",
            "fecha": fecha,
            "hora": hora,
            "condicion": condicion,
            "local": local,
            "visitante": visitante,
            "ubicacion": ubicacion,
            "resultado": resultado,
            "parciales": parciales,
            "jugado": jugado,
            "estado": estado,
        }

        assert list(partido_final.keys()) == CLAVES_SALIDA
        partidos_finales.append((jornada_numero, partido_final))

    # Orden numérico real: Jornada 2 antes que Jornada 10.
    partidos_finales.sort(key=lambda elemento: elemento[0])

    return [partido for _, partido in partidos_finales]


def main():
    try:
        partidos = generar_partidos()

        with ARCHIVO_SALIDA.open("w", encoding="utf-8") as archivo:
            json.dump(
                partidos,
                archivo,
                ensure_ascii=False,
                indent=4,
            )
            archivo.write("\n")

        print(f"JSON generado correctamente: {ARCHIVO_SALIDA}")
        print(f"Total de partidos: {len(partidos)}")
        print("Jornadas ordenadas numéricamente.")
        print("Estructura y datos validados.")

        if not partidos:
            print(
                "AVISO: no hay partidos cargados. "
                "Añade el calendario real a PARTIDOS."
            )

    except (ValueError, OSError) as error:
        print(f"ERROR: {error}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
