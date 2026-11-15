#!/usr/bin/env python3
"""
validar_prompt.py - Control de calidad del prompt de Seedance 2.5 antes de entregarlo.

Comprueba lo que mas rompe una generacion y que a ojo se escapa:
  - longitud en caracteres dentro del perfil elegido
  - bloques obligatorios de la plantilla
  - referencias @Image / @Video / @Audio coherentes con lo que se va a subir
  - bloqueo 3D declarado con su alcance (blocking, camara, timing) y su anti-fuga
  - linea de tiempo contigua de 0 s a la duracion, con los cortes del blocking
  - dialogo que cabe en su toma y solo aparece dentro de su toma
  - nombres de directores, ruido de markdown, adjetivos vacios

Uso:
    python3 validar_prompt.py prompt.txt --duracion 15 --imagenes 4 --videos 1 --blocking --cortes 6,11
    python3 validar_prompt.py prompt.txt --perfil compacto --duracion 10
    cat prompt.txt | python3 validar_prompt.py - --duracion 15

Codigo de salida: 0 si no hay errores, 1 si los hay.
"""

import argparse
import json
import re
import sys
import unicodedata

PERFILES = {
    # nombre: (minimo, maximo) en caracteres
    "completo": (5000, 10000),
    "compacto": (2500, 3000),
}

BLOQUES = {
    "completo": [
        ("SECUENCIA CINEMATOGRAFICA", True),
        ("ATRIBUTOS DE SIMULACION CENTRAL", True),
        ("ESTETICA VISUAL AVANZADA", True),
        ("REGLAS DE CONTINUIDAD Y CONFIGURACION DE CAMARA", True),
        ("ESQUEMA DE ILUMINACION", True),
        ("DISENO DE AUDIO", True),
        ("NARRATIVA Y TONO EMOCIONAL", True),
        ("PHYSICS", True),
        ("ESCENARIO", True),
        ("FICHAS MECANICAS", True),
        ("DESGLOSE DE SECUENCIA", True),
        ("BARRERAS NEGATIVAS", True),
    ],
    "compacto": [
        ("SECUENCIA CINEMATOGRAFICA", True),
        ("CAMARA Y ESTETICA", True),
        ("LUZ Y ATMOSFERA", True),
        ("AUDIO", True),
        ("ASSETS", True),
        ("DESGLOSE", True),
        ("BARRERAS NEGATIVAS", True),
    ],
}
BLOQUE_REFERENCIAS = "MAPA DE REFERENCIAS"

# Los directores se traducen a gramatica de camara; su nombre nunca va en el prompt
# (lo pide el flujo de trabajo y ademas los filtros rechazan nombres de personas reales).
NOMBRES_VETADOS = [
    "nolan", "spielberg", "george lucas", "lucasfilm", "villeneuve", "kubrick", "tarantino",
    "scorsese", "fincher", "james cameron", "ridley scott", "michael bay", "wes anderson",
    "deakins", "lubezki", "zack snyder", "peter jackson", "del toro", "cuaron", "inarritu",
    "kurosawa", "tarkovsky", "hitchcock", "coppola", "wachowski", "miyazaki", "hoytema",
    "fraser", "kaminski",
]

ADJETIVOS_VACIOS = [
    "hermoso", "hermosa", "bello", "bella", "impresionante", "increible", "espectacular",
    "majestuoso", "majestuosa", "epico", "epica", "magico", "magica", "sublime",
    "deslumbrante", "asombroso", "asombrosa", "maravilloso", "maravillosa",
    "beautiful", "stunning", "amazing", "breathtaking", "epic", "gorgeous", "awesome",
    "magical", "mesmerizing", "masterpiece", "best quality", "award-winning",
]

PALABRAS_POR_SEGUNDO = 2.6      # ritmo de habla natural; por encima el lip-sync se descuadra

# Un titulo abre linea. Se toleran simbolos delante (#, **, un emoji) para que ese ruido
# se avise como ruido y no como "falta el bloque".
PREFIJO_TITULO = r"^[^A-Za-z\n]{0,8}"

RE_REF = re.compile(r"@\s?(image|video|audio|imagen|img|vid)\s?(\d+)", re.IGNORECASE)
RE_TOMA = re.compile(
    r"^\W{0,3}(?:TOMA\s*\d+\s*[:|\-]?\s*)?\[?\s*(\d+(?:[.,]\d+)?)\s*s?\s*[-–—]\s*"
    r"(\d+(?:[.,]\d+)?)\s*s\b", re.IGNORECASE)
RE_COMILLAS = re.compile(r"[\"“«]([^\"”»\n]{2,})[\"”»]")


def normalizar(txt):
    """Mayusculas sin acentos (la enie pasa a N) para comparar titulos."""
    sin = unicodedata.normalize("NFD", txt)
    return "".join(c for c in sin if unicodedata.category(c) != "Mn").upper()


class Informe:
    def __init__(self):
        self.items = []

    def ok(self, m):
        self.items.append(("OK", m))

    def aviso(self, m):
        self.items.append(("AVISO", m))

    def error(self, m):
        self.items.append(("ERROR", m))

    @property
    def errores(self):
        return [m for n, m in self.items if n == "ERROR"]


def revisar_longitud(texto, perfil, inf, minimo, maximo):
    n = len(texto)
    if n > maximo:
        inf.error(f"Longitud {n} caracteres: supera el maximo del perfil {perfil} ({maximo}). "
                  f"Sobran {n - maximo}. Recorta adjetivos y repeticiones, no datos de camara.")
    elif n < minimo:
        inf.aviso(f"Longitud {n} caracteres: por debajo del minimo del perfil {perfil} ({minimo}). "
                  "Faltan datos fisicos o tecnicos en algun bloque.")
    else:
        inf.ok(f"Longitud {n} caracteres (perfil {perfil}: {minimo}-{maximo}).")
    return n


def revisar_bloques(norm, perfil, hay_referencias, inf):
    faltan, pos_anterior, desorden = [], -1, False
    for titulo, obligatorio in BLOQUES[perfil]:
        # Un titulo de bloque abre linea; la misma palabra dentro de una frase no cuenta.
        m = re.search(PREFIJO_TITULO + re.escape(titulo), norm, re.MULTILINE)
        if m is None:
            if obligatorio:
                faltan.append(titulo)
            continue
        if m.start() < pos_anterior:
            desorden = True
        pos_anterior = m.start()
    if faltan:
        inf.error("Faltan bloques obligatorios: " + "; ".join(faltan) + ".")
    else:
        inf.ok(f"Estan los {len(BLOQUES[perfil])} bloques obligatorios del perfil {perfil}.")
    if desorden:
        inf.aviso("Los bloques no siguen el orden de la plantilla.")
    if hay_referencias and not re.search(PREFIJO_TITULO + BLOQUE_REFERENCIAS, norm, re.MULTILINE):
        inf.error(f"Hay referencias pero falta el bloque '{BLOQUE_REFERENCIAS}': sin un rol "
                  "explicito cada archivo filtra su encuadre, su fondo o su look al resultado.")
    for linea in norm.splitlines():
        if linea.strip().startswith("VFX DE TRANSFORMACIONES") and re.search(
                r"NO APLICA|N/A|NINGUN", linea):
            inf.aviso("El bloque VFX dice 'no aplica': eliminalo entero y ahorra caracteres.")


def revisar_referencias(texto, a, inf):
    usados = {"image": set(), "video": set(), "audio": set()}
    formas = set()
    for m in RE_REF.finditer(texto):
        tipo, num = m.group(1).lower(), int(m.group(2))
        if tipo in ("imagen", "img"):
            inf.error(f"Etiqueta '{m.group(0)}' no valida: usa @Image{num}.")
            tipo = "image"
        elif tipo == "vid":
            inf.error(f"Etiqueta '{m.group(0)}' no valida: usa @Video{num}.")
            tipo = "video"
        usados[tipo].add(num)
        formas.add("espacio" if re.search(r"[a-z] \d", m.group(0), re.IGNORECASE) else "junto")
    if len(formas) > 1:
        inf.aviso("Mezclas '@Image1' y '@Image 1'. Usa una sola forma: la que muestra tu plataforma "
                  "(API e integraciones: @Image1; selector @ de Dreamina/Jimeng: @Image 1).")
    declarados = {"image": a.imagenes, "video": a.videos, "audio": a.audios}
    nombres = {"image": "Image", "video": "Video", "audio": "Audio"}
    sin_manifiesto = all(v is None for v in declarados.values())
    total = sum(len(v) for v in usados.values())
    if sin_manifiesto:
        if total:
            inf.aviso("El prompt cita referencias (" + ", ".join(
                f"@{nombres[t]}{n}" for t in usados for n in sorted(usados[t])) +
                ") pero no indicaste cuantas se suben (--imagenes/--videos/--audios).")
        return total > 0
    for tipo, cantidad in declarados.items():
        cantidad = cantidad or 0
        fuera = sorted(n for n in usados[tipo] if n > cantidad or n < 1)
        if fuera:
            inf.error("El prompt cita " + ", ".join(f"@{nombres[tipo]}{n}" for n in fuera) +
                      f" pero solo se suben {cantidad} archivo(s) de ese tipo.")
        huerfanos = [n for n in range(1, cantidad + 1) if n not in usados[tipo]]
        if huerfanos:
            inf.error("Se suben " + ", ".join(f"@{nombres[tipo]}{n}" for n in huerfanos) +
                      " sin rol en el prompt. Una referencia sin rol contamina el resultado: "
                      "asignale un papel o no la subas.")
    if not [m for n, m in inf.items if n == "ERROR" and "@" in m] and total:
        inf.ok(f"Referencias coherentes con el manifiesto ({total} etiquetas distintas usadas).")
    if (a.imagenes or 0) > 30 or (a.videos or 0) > 10 or (a.audios or 0) > 10:
        inf.error("Seedance 2.5 admite como maximo 30 imagenes, 10 videos y 10 audios.")
    return total > 0 or any((v or 0) > 0 for v in declarados.values())


def revisar_blocking(texto, inf):
    bajo = texto.lower()
    lineas = [l for l in bajo.splitlines() if re.search(r"@\s?video\s?1\b", l)]
    if not lineas:
        inf.error("Indicaste --blocking pero el prompt no menciona @Video1.")
        return
    zona = " ".join(lineas)
    alcance = [p for p in ("blocking", "camera", "timing") if p not in zona]
    if alcance:
        inf.error("La linea de @Video1 no declara todo su alcance (falta: " + ", ".join(alcance) +
                  "). Formula probada: 'Use @Video1 as blocking, camera path and timing only'.")
    if not re.search(r"\bonly\b|\bsolo\b|unicamente", zona):
        inf.aviso("Anade 'only' al rol de @Video1 para limitarlo a camara, puesta en escena y ritmo.")
    # No basta con que aparezca la palabra "grey": tiene que haber una orden de no
    # renderizar la maqueta, o de sustituir los proxies.
    material = r"(grey|gray|gris|clay|mannequin|maniqu|primitive|flat shading|untextured|placeholder)"
    prohibe = re.search(r"(never|do not|don't|must not|nunca|no renderi)[^.\n]{0,90}" + material, bajo)
    sustituye = re.search(r"(replace|sustitu)\w*[^.\n]{0,40}(prox|placeholder|mannequin|maniqu)", bajo)
    if not (prohibe or sustituye):
        inf.error("Falta la clausula anti-fuga del blocking: di que el previz es geometria gris "
                  "sin textura que debe sustituirse (si no, el video hereda el look de maqueta).")
    else:
        inf.ok("Bloqueo 3D declarado con alcance y clausula anti-fuga.")
    tomas_sin = []
    for cab, cuerpo in separar_tomas(texto):
        if not re.search(r"@\s?video\s?1", cuerpo, re.IGNORECASE):
            tomas_sin.append(cab)
    if tomas_sin:
        inf.aviso("Tomas sin linea 'Blocking: @Video1 ...': " + ", ".join(tomas_sin) +
                  ". Anclar cada toma a su tramo del blocking evita que el modelo improvise.")


def separar_tomas(texto):
    """Devuelve [(cabecera 'a-b', cuerpo)] de cada toma del desglose."""
    tomas, actual = [], None
    for linea in texto.splitlines():
        m = RE_TOMA.match(linea.strip())
        if m:
            actual = [f"{m.group(1)}s-{m.group(2)}s", linea + "\n", float(m.group(1).replace(",", ".")),
                      float(m.group(2).replace(",", "."))]
            tomas.append(actual)
        elif actual is not None:
            if normalizar(linea).strip().startswith("BARRERAS NEGATIVAS"):
                actual = None
            else:
                actual[1] += linea + "\n"
    return [(t[0], t[1]) for t in tomas]


def leer_tiempos(texto):
    tiempos = []
    for linea in texto.splitlines():
        m = RE_TOMA.match(linea.strip())
        if m:
            tiempos.append((float(m.group(1).replace(",", ".")), float(m.group(2).replace(",", ".")),
                            linea.strip()))
    return tiempos


def revisar_linea_de_tiempo(texto, a, inf):
    tiempos = leer_tiempos(texto)
    if not tiempos:
        inf.error("No hay tomas con marca de tiempo (formato '0s-3s | TOMA 1 ...' al inicio de linea).")
        return
    problemas = []
    if abs(tiempos[0][0]) > 0.01:
        problemas.append(f"la primera toma empieza en {tiempos[0][0]:g} s y no en 0 s")
    for (a0, a1, _), (b0, b1, _) in zip(tiempos, tiempos[1:]):
        if abs(b0 - a1) > 0.01:
            problemas.append(f"hueco o solape entre {a0:g}s-{a1:g}s y {b0:g}s-{b1:g}s")
    for t0, t1, _ in tiempos:
        if t1 - t0 < 1.0:
            problemas.append(f"la toma {t0:g}s-{t1:g}s dura menos de 1 s (el modelo no la resuelve)")
    if a.duracion is not None and abs(tiempos[-1][1] - a.duracion) > 0.01:
        problemas.append(f"la ultima toma acaba en {tiempos[-1][1]:g} s y la duracion es {a.duracion:g} s")
    if problemas:
        inf.error("Linea de tiempo incoherente: " + "; ".join(problemas) + ".")
    else:
        inf.ok(f"Linea de tiempo contigua: {len(tiempos)} tomas de 0 s a {tiempos[-1][1]:g} s.")

    if a.duracion is not None:
        m = re.search(r"DESGLOSE DE SECUENCIA[^\n]*?(\d+)\s*SEGUNDOS", normalizar(texto))
        if m and int(m.group(1)) != int(a.duracion):
            inf.error(f"El titulo del desglose dice {m.group(1)} segundos y la duracion es "
                      f"{a.duracion:g} s.")
        if a.duracion < 4 or a.duracion > 30 or abs(a.duracion - round(a.duracion)) > 1e-6:
            inf.error("Seedance 2.5 genera de 4 a 30 segundos enteros.")

    if a.cortes is not None:
        cortes = [float(c) for c in a.cortes.split(",") if c.strip()] if a.cortes.strip().lower() \
            not in ("", "ninguno", "none", "0") else []
        inicios = {round(t0, 2): cab for t0, _, cab in tiempos}
        for c in cortes:
            cerca = [t for t in inicios if abs(t - c) <= 0.25]
            if not cerca:
                inf.error(f"El blocking corta en {c:g} s pero ninguna toma empieza ahi. Las fronteras "
                          "de las tomas deben coincidir con los cortes del blocking.")
            elif not re.search(r"\bCUT\b|CORTE", normalizar(inicios[cerca[0]])):
                inf.error(f"La toma que empieza en {cerca[0]:g} s no marca el corte en su cabecera "
                          "(escribe 'HARD CUT').")
        for t0, _, cab in tiempos:
            if re.search(r"\bHARD CUT\b|ENTRA POR CORTE", normalizar(cab)) and \
                    not any(abs(t0 - c) <= 0.25 for c in cortes):
                inf.error(f"La toma de {t0:g} s declara un corte que no existe en el blocking. "
                          "El texto no puede contradecir al video de referencia.")
        if not [m for n, m in inf.items if n == "ERROR" and ("corte" in m.lower())]:
            inf.ok("Cortes del prompt alineados con el blocking (" +
                   (", ".join(f"{c:g} s" for c in cortes) if cortes else "plano secuencia") + ").")


def revisar_dialogo(texto, inf):
    norm = normalizar(texto)
    m_desglose = re.search(PREFIJO_TITULO + "DESGLOSE", norm, re.MULTILINE)
    inicio_desglose = m_desglose.start() if m_desglose else -1
    if inicio_desglose > 0:
        fuera = RE_COMILLAS.findall(texto[:inicio_desglose])
        if fuera:
            inf.aviso("Hay texto entre comillas antes del desglose (" + "; ".join(
                f'"{f[:28]}"' for f in fuera[:3]) + "). Las lineas de dialogo van solo dentro de su "
                "toma: fuera de ella generan habla duplicada o texto en pantalla.")
    for cab, cuerpo in separar_tomas(texto):
        m = re.match(r"([\d.,]+)s-([\d.,]+)s", cab)
        dur = float(m.group(2).replace(",", ".")) - float(m.group(1).replace(",", "."))
        lineas = [l for l in cuerpo.splitlines() if normalizar(l).strip().startswith("DIALOGO")]
        palabras = sum(len(q.split()) for l in lineas for q in RE_COMILLAS.findall(l))
        if palabras and palabras > PALABRAS_POR_SEGUNDO * dur:
            inf.error(f"La toma {cab} tiene {palabras} palabras de dialogo para {dur:g} s "
                      f"(maximo ~{int(PALABRAS_POR_SEGUNDO * dur)}). Acorta la linea o repartela "
                      "entre tomas: el habla que no cabe se acelera o desincroniza los labios.")


def revisar_estilo(texto, a, inf):
    bajo = normalizar(texto).lower()
    vetados = [n for n in NOMBRES_VETADOS if re.search(r"\b" + re.escape(n) + r"\b", bajo)]
    if vetados:
        inf.error("Nombres de directores o cineastas en el prompt: " + ", ".join(vetados) +
                  ". Describe su forma de dirigir (lente, movimiento, luz), nunca el nombre.")
    else:
        inf.ok("Sin nombres de directores.")
    ruido = []
    if re.search(r"^\s*#{1,6}\s", texto, re.MULTILINE):
        ruido.append("titulos con #")
    if "**" in texto or "__" in texto:
        ruido.append("negritas ** o __")
    if "```" in texto:
        ruido.append("bloques ```")
    if re.search(r"\\[a-zA-Z]+", texto):
        ruido.append("comandos tipo \\rightarrow (usa '->')")
    if re.search(r"[\U0001F000-\U0001FAFF☀-➿\U0001F1E6-\U0001F1FF]", texto):
        ruido.append("emojis")
    if ruido:
        inf.aviso("Ruido de formato que gasta caracteres o puede salir como texto en pantalla: " +
                  ", ".join(ruido) + ". El prompt va en texto plano con titulos en mayusculas.")
    if re.search(r"\[[^\]\n]{0,60}\]", texto) and re.search(
            r"\[(?:especificar|nombre|ej|genero|n|mm|serie)[^\]]*\]", bajo):
        inf.error("Quedan marcadores de plantilla sin rellenar (texto entre corchetes).")
    # La cabecera lleva el genero ("FANTASIA EPICA"): ahi la palabra es una etiqueta, no relleno.
    cuerpo = "\n".join(l for l in bajo.splitlines() if not l.strip().startswith("secuencia cinematografica"))
    vacios = sorted({p for p in ADJETIVOS_VACIOS if re.search(r"\b" + re.escape(p) + r"\b", cuerpo)})
    if vacios:
        inf.aviso("Adjetivos sin informacion fisica: " + ", ".join(vacios) +
                  ". Cambialos por un dato medible (material, velocidad, Kelvin, mm).")
    if a.aspecto and a.aspecto != "16:9" and "letterbox" in bajo:
        inf.aviso(f"Generas en {a.aspecto} y el prompt pide 'letterbox': el modelo puede quemar barras "
                  "negras dentro del cuadro. Usa 'anamorphic widescreen framing' si no las quieres.")
    if re.search(r"subtitle|subtitulo|watermark|marca de agua|on-screen text|texto en pantalla", bajo) is None:
        inf.aviso("Las barreras negativas no excluyen subtitulos, texto en pantalla ni marcas de agua.")


def main():
    ap = argparse.ArgumentParser(description="Valida un prompt de Seedance 2.5.")
    ap.add_argument("prompt", help="Archivo de texto con el prompt, o '-' para leer de stdin")
    ap.add_argument("--perfil", choices=sorted(PERFILES), default="completo")
    ap.add_argument("--min", type=int, default=None, help="Minimo de caracteres (sobrescribe el perfil)")
    ap.add_argument("--max", type=int, default=None, help="Maximo de caracteres (sobrescribe el perfil)")
    ap.add_argument("--duracion", type=float, default=None, help="Duracion de la generacion en segundos")
    ap.add_argument("--imagenes", type=int, default=None, help="Numero de imagenes que se suben")
    ap.add_argument("--videos", type=int, default=None, help="Numero de videos que se suben")
    ap.add_argument("--audios", type=int, default=None, help="Numero de audios que se suben")
    ap.add_argument("--blocking", action="store_true", help="@Video1 es un blocking 3D")
    ap.add_argument("--cortes", default=None,
                    help="Segundos de los cortes del blocking separados por coma, o 'ninguno'")
    ap.add_argument("--aspecto", default="", help="Aspect ratio de la generacion (p. ej. 21:9)")
    ap.add_argument("--json", action="store_true", help="Salida en JSON")
    a = ap.parse_args()

    texto = sys.stdin.read() if a.prompt == "-" else open(a.prompt, encoding="utf-8").read()
    texto = texto.strip()
    if not texto:
        print("ERROR: el prompt esta vacio.", file=sys.stderr)
        sys.exit(1)

    minimo, maximo = PERFILES[a.perfil]
    minimo = a.min if a.min is not None else minimo
    maximo = a.max if a.max is not None else maximo

    inf = Informe()
    n = revisar_longitud(texto, a.perfil, inf, minimo, maximo)
    hay_ref = revisar_referencias(texto, a, inf)
    revisar_bloques(normalizar(texto), a.perfil, hay_ref, inf)
    if a.blocking:
        revisar_blocking(texto, inf)
    revisar_linea_de_tiempo(texto, a, inf)
    revisar_dialogo(texto, inf)
    revisar_estilo(texto, a, inf)

    if a.json:
        print(json.dumps({"caracteres": n, "perfil": a.perfil, "valido": not inf.errores,
                          "resultados": [{"nivel": k, "mensaje": m} for k, m in inf.items]},
                         ensure_ascii=False, indent=1))
    else:
        for nivel, mensaje in inf.items:
            print(f"[{nivel}] {mensaje}")
        avisos = sum(1 for k, _ in inf.items if k == "AVISO")
        print(f"\nRESULTADO: {'APTO' if not inf.errores else 'NO APTO'} | {n} caracteres | "
              f"{len(inf.errores)} error(es), {avisos} aviso(s)")
    sys.exit(1 if inf.errores else 0)


if __name__ == "__main__":
    main()
