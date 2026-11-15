#!/usr/bin/env python3
"""
analizar_blocking.py - Analiza el video de blocking 3D (render de Blender u otro previz)
antes de escribir el prompt de Seedance 2.5.

Que hace:
  1. Lee la ficha tecnica (duracion, fps, resolucion, aspecto, peso, audio).
  2. La valida contra los limites de video de referencia de Seedance 2.5.
  3. Detecta los cortes y avisa de barras negras quemadas o color en el previz.
  4. Genera hojas de contacto con marca de tiempo y cuadricula de tercios para que
     el director (Claude o una persona) vea que hace la camara en cada tramo.
     El movimiento de camara se lee en esas hojas (o, mejor, en los datos de Blender):
     en un render gris y plano ninguna estimacion automatica es fiable.
  5. Escribe blocking_report.md y blocking_report.json con tramos sugeridos.

Uso:
    python3 analizar_blocking.py blocking.mp4
    python3 analizar_blocking.py blocking.mp4 --salida ./analisis --cuadros-por-segundo 3

Requisitos: ffmpeg y ffprobe en el PATH. Pillow para las hojas de contacto y numpy
para los cortes (si faltan, el script entrega lo que pueda y lo avisa).
"""

import argparse
import json
import math
import os
import shutil
import subprocess
import sys

try:
    import numpy as np
except ImportError:  # el analisis de movimiento es opcional
    np = None
try:
    from PIL import Image, ImageDraw, ImageFont, ImageStat
except ImportError:  # las hojas de contacto son opcionales
    Image = None

ASPECTOS_SEEDANCE = {"21:9": 21 / 9, "16:9": 16 / 9, "4:3": 4 / 3, "1:1": 1.0,
                     "3:4": 3 / 4, "9:16": 9 / 16}
REF_DUR_MIN, REF_DUR_MAX = 1.8, 30.2     # video de referencia
GEN_DUR_MIN, GEN_DUR_MAX = 4, 30         # duracion de generacion
REF_PESO_MAX_MB = 200
MAX_CUADROS_HOJA = 48
COLUMNAS, FILAS, ANCHO_MINIATURA = 3, 4, 640


def salir(mensaje):
    print(f"ERROR: {mensaje}", file=sys.stderr)
    sys.exit(2)


def ejecutar(cmd, binario=False):
    r = subprocess.run(cmd, capture_output=True)
    if binario:
        return r.returncode, r.stdout, r.stderr.decode("utf-8", "replace")
    return r.returncode, r.stdout.decode("utf-8", "replace"), r.stderr.decode("utf-8", "replace")


def fraccion(txt):
    try:
        if "/" in txt:
            a, b = txt.split("/")
            return float(a) / float(b) if float(b) else 0.0
        return float(txt)
    except (ValueError, TypeError):
        return 0.0


# ----------------------------------------------------------------------------
# 1. Ficha tecnica
# ----------------------------------------------------------------------------
def leer_ficha(video):
    codigo, out, err = ejecutar(["ffprobe", "-v", "error", "-print_format", "json",
                                 "-show_format", "-show_streams", video])
    if codigo != 0:
        salir(f"ffprobe no pudo leer el archivo: {err.strip()[:300]}")
    info = json.loads(out)
    v = next((s for s in info.get("streams", []) if s.get("codec_type") == "video"), None)
    if v is None:
        salir("El archivo no contiene una pista de video.")
    audio = any(s.get("codec_type") == "audio" for s in info.get("streams", []))
    fmt = info.get("format", {})
    fps = fraccion(v.get("avg_frame_rate", "")) or fraccion(v.get("r_frame_rate", ""))
    dur = float(fmt.get("duration") or v.get("duration") or 0.0)
    cuadros = int(v.get("nb_frames") or 0) or int(round(dur * fps))
    ancho, alto = int(v["width"]), int(v["height"])
    # Respeta la rotacion declarada (videos verticales grabados con movil)
    rot = 0
    for sd in v.get("side_data_list", []) or []:
        if "rotation" in sd:
            rot = int(sd["rotation"])
    if abs(rot) in (90, 270):
        ancho, alto = alto, ancho
    return {
        "archivo": os.path.abspath(video),
        "contenedor": fmt.get("format_name", ""),
        "extension": os.path.splitext(video)[1].lower().lstrip("."),
        "codec": v.get("codec_name", ""),
        "duracion_s": round(dur, 3), "fps": round(fps, 3), "cuadros": cuadros,
        "ancho": ancho, "alto": alto, "relacion": round(ancho / alto, 4),
        "peso_mb": round(os.path.getsize(video) / 1e6, 2),
        "audio": audio,
    }


def aspecto_mas_cercano(relacion):
    nombre = min(ASPECTOS_SEEDANCE, key=lambda k: abs(math.log(ASPECTOS_SEEDANCE[k] / relacion)))
    return nombre, abs(ASPECTOS_SEEDANCE[nombre] / relacion - 1.0)


# ----------------------------------------------------------------------------
# 2. Validacion contra Seedance 2.5
# ----------------------------------------------------------------------------
def validar(f):
    v = []  # (nivel, mensaje) con nivel en OK / AVISO / ERROR

    d = f["duracion_s"]
    if d < REF_DUR_MIN or d > REF_DUR_MAX:
        v.append(("ERROR", f"Duracion {d:.2f} s fuera del rango de video de referencia "
                           f"({REF_DUR_MIN}-{REF_DUR_MAX} s). Recorta o divide el blocking."))
    elif d < GEN_DUR_MIN:
        v.append(("AVISO", f"Duracion {d:.2f} s: menor que la generacion minima ({GEN_DUR_MIN} s); "
                           "el modelo tendra que estirar el blocking."))
    else:
        v.append(("OK", f"Duracion {d:.2f} s dentro del rango de referencia."))
    gen = int(min(GEN_DUR_MAX, max(GEN_DUR_MIN, round(d))))
    if abs(d - gen) > 0.12:
        v.append(("AVISO", f"La generacion usa segundos enteros: {d:.2f} s se generaria como {gen} s "
                           "y el ritmo se desplazaria. Renderiza el blocking con la duracion exacta."))

    if f["peso_mb"] > REF_PESO_MAX_MB:
        v.append(("ERROR", f"Pesa {f['peso_mb']} MB (maximo {REF_PESO_MAX_MB} MB). Re-exporta en "
                           "H.264 a 720p."))
    else:
        v.append(("OK", f"Peso {f['peso_mb']} MB (maximo {REF_PESO_MAX_MB} MB)."))

    if f["extension"] not in ("mp4", "mov"):
        v.append(("ERROR", f"Extension .{f['extension']}: sube el blocking como MP4 o MOV."))
    if f["codec"] not in ("h264", "hevc"):
        v.append(("AVISO", f"Codec {f['codec']}: H.264 es el mas compatible entre plataformas."))

    nombre, desvio = aspecto_mas_cercano(f["relacion"])
    if desvio > 0.02:
        v.append(("AVISO", f"Aspecto {f['ancho']}x{f['alto']} ({f['relacion']:.3f}:1) no es nativo; "
                           f"el mas cercano es {nombre}. Renderiza el blocking en el aspecto que vas "
                           "a generar o el encuadre se recompone."))
    else:
        v.append(("OK", f"Aspecto {nombre} nativo de Seedance 2.5."))

    lado = min(f["ancho"], f["alto"])
    if lado < 480:
        v.append(("AVISO", f"Resolucion {f['ancho']}x{f['alto']}: por debajo de 480p la puesta en "
                           "escena se lee peor. 720p es suficiente."))
    elif max(f["ancho"], f["alto"]) > 4096:
        v.append(("AVISO", "Resolucion superior a 4K: no aporta nada a una referencia; baja a 720p/1080p."))

    if f["fps"] < 23 or f["fps"] > 61:
        v.append(("AVISO", f"{f['fps']:g} fps: usa 24 fps para que el timing coincida con el resultado."))
    elif abs(f["fps"] - 24) > 0.1:
        v.append(("AVISO", f"{f['fps']:g} fps: funciona, pero 24 fps es la cadencia de cine recomendada."))

    if f["audio"]:
        v.append(("AVISO", "El blocking lleva pista de audio. Si no es una referencia de sonido "
                           "intencional, exportalo sin audio para que no contamine el audio generado."))
    return v, gen, nombre


# ----------------------------------------------------------------------------
# 3. Cortes (numpy)
# ----------------------------------------------------------------------------
def leer_cuadros_gris(video, ancho, alto):
    """Decodifica todo el video en gris a baja resolucion: array (N, alto, ancho)."""
    codigo, datos, err = ejecutar(["ffmpeg", "-v", "error", "-i", video, "-an",
                                   "-vf", f"scale={ancho}:{alto}:flags=area,format=gray",
                                   "-f", "rawvideo", "-pix_fmt", "gray", "-"], binario=True)
    if codigo != 0 or not datos:
        return None
    n = len(datos) // (ancho * alto)
    return np.frombuffer(datos[:n * ancho * alto], dtype=np.uint8).reshape(n, alto, ancho)


def detectar_cortes(cuadros, fps):
    """Un corte es un pico aislado de diferencia entre cuadros consecutivos."""
    c = cuadros.astype(np.float32) / 255.0
    dif = np.abs(c[1:] - c[:-1]).mean(axis=(1, 2))
    cortes = []
    for i, d in enumerate(dif):
        vecinos = np.concatenate([dif[max(0, i - 6):i], dif[i + 1:i + 7]])
        base = float(np.median(vecinos)) if len(vecinos) else 0.0
        if d > 0.045 and d > 4.0 * max(base, 0.004):
            cortes.append({"cuadro": i + 1, "t_s": round((i + 1) / fps, 3), "fuerza": round(float(d), 3)})
    # Descarta cortes pegados (flashes de 1-2 cuadros)
    limpios = []
    for k in cortes:
        if not limpios or k["cuadro"] - limpios[-1]["cuadro"] > max(2, fps * 0.2):
            limpios.append(k)
    return limpios


def barras_negras(cuadros):
    """Detecta letterbox quemado: franjas superior e inferior negras en todo el video."""
    n, alto, _ = cuadros.shape
    muestra = cuadros[:: max(1, n // 24)]
    perfil = muestra.max(axis=(0, 2))                  # brillo maximo por fila
    arriba = 0
    while arriba < alto // 2 and perfil[arriba] < 18:
        arriba += 1
    abajo = 0
    while abajo < alto // 2 and perfil[alto - 1 - abajo] < 18:
        abajo += 1
    return (arriba + abajo) / alto if min(arriba, abajo) >= max(2, alto * 0.02) else 0.0


def tramos_sugeridos(duracion, cortes):
    """Divide en bloques de 2-4 s respetando los cortes como fronteras obligatorias."""
    limites = [0.0] + [k["t_s"] for k in cortes if 0.3 < k["t_s"] < duracion - 0.3] + [duracion]
    tramos = []
    for a, b in zip(limites, limites[1:]):
        largo = b - a
        partes = max(1, int(round(largo / 3.0)))
        for i in range(partes):
            ini = a + largo * i / partes
            fin = a + largo * (i + 1) / partes
            if 0 < i:
                ini = round(ini * 2) / 2
            if i < partes - 1:
                fin = round(fin * 2) / 2
            tramos.append({"desde_s": round(ini, 2), "hasta_s": round(fin, 2),
                           "entra_por_corte": bool(i == 0 and a > 0)})
    return tramos


# ----------------------------------------------------------------------------
# 4. Hojas de contacto
# ----------------------------------------------------------------------------
def fuente(tam):
    for ruta in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                 "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
                 "C:/Windows/Fonts/arialbd.ttf"):
        if os.path.exists(ruta):
            try:
                return ImageFont.truetype(ruta, tam)
            except OSError:
                pass
    try:
        return ImageFont.load_default(size=tam)
    except TypeError:
        return ImageFont.load_default()


def hojas_de_contacto(video, f, cortes, salida, cps, con_tercios):
    dur, fps, n = f["duracion_s"], f["fps"], f["cuadros"]
    if dur * cps > MAX_CUADROS_HOJA:
        cps = MAX_CUADROS_HOJA / dur
    indices = sorted({min(n - 1, int(round(t * fps)))
                      for t in [i / cps for i in range(int(dur * cps) + 1)]})
    tras_corte = {min(n - 1, k["cuadro"]) for k in cortes}
    antes_corte = {max(0, k["cuadro"] - 1) for k in cortes}
    indices = sorted(set(indices) | tras_corte | antes_corte | {n - 1})

    alto_mini = int(round(ANCHO_MINIATURA * f["alto"] / f["ancho"] / 2) * 2)
    seleccion = "+".join(f"eq(n\\,{i})" for i in indices)
    codigo, datos, err = ejecutar(
        ["ffmpeg", "-v", "error", "-i", video, "-an",
         "-vf", f"select='{seleccion}',scale={ANCHO_MINIATURA}:{alto_mini}:flags=lanczos",
         "-fps_mode", "passthrough", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], binario=True)
    if codigo != 0:  # ffmpeg antiguo: -vsync en lugar de -fps_mode
        codigo, datos, err = ejecutar(
            ["ffmpeg", "-v", "error", "-i", video, "-an",
             "-vf", f"select='{seleccion}',scale={ANCHO_MINIATURA}:{alto_mini}:flags=lanczos",
             "-vsync", "0", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], binario=True)
    tam = ANCHO_MINIATURA * alto_mini * 3
    obtenidos = len(datos) // tam
    if codigo != 0 or obtenidos == 0:
        return [], [], f"No se pudieron extraer cuadros: {err.strip()[:200]}"
    indices = indices[:obtenidos]

    barra, margen = 34, 6
    tipografia = fuente(22)
    por_hoja = COLUMNAS * FILAS
    rutas, saturaciones = [], []
    for h in range(0, len(indices), por_hoja):
        grupo = indices[h:h + por_hoja]
        filas = int(math.ceil(len(grupo) / COLUMNAS))
        hoja = Image.new("RGB", (COLUMNAS * (ANCHO_MINIATURA + margen) + margen,
                                 filas * (alto_mini + barra + margen) + margen), (24, 24, 24))
        dib = ImageDraw.Draw(hoja)
        for j, idx in enumerate(grupo):
            k = h + j
            mini = Image.frombytes("RGB", (ANCHO_MINIATURA, alto_mini), datos[k * tam:(k + 1) * tam])
            saturaciones.append(ImageStat.Stat(mini.convert("HSV").split()[1]).mean[0] / 255.0)
            x = margen + (j % COLUMNAS) * (ANCHO_MINIATURA + margen)
            y = margen + (j // COLUMNAS) * (alto_mini + barra + margen)
            es_corte = idx in tras_corte
            dib.rectangle([x, y, x + ANCHO_MINIATURA - 1, y + barra - 1],
                          fill=(170, 30, 30) if es_corte else (50, 50, 50))
            etiqueta = f"t={idx / fps:05.2f}s  #{idx}" + ("   CORTE: plano nuevo" if es_corte else "")
            dib.text((x + 8, y + 5), etiqueta, fill=(255, 255, 255), font=tipografia)
            hoja.paste(mini, (x, y + barra))
            if con_tercios:
                for p in (1 / 3, 2 / 3):
                    gx = x + int(ANCHO_MINIATURA * p)
                    gy = y + barra + int(alto_mini * p)
                    dib.line([gx, y + barra, gx, y + barra + alto_mini - 1], fill=(255, 210, 0), width=1)
                    dib.line([x, gy, x + ANCHO_MINIATURA - 1, gy], fill=(255, 210, 0), width=1)
        ruta = os.path.join(salida, f"hoja_contacto_{len(rutas) + 1:02d}.png")
        hoja.save(ruta, optimize=True)
        rutas.append(ruta)
    tiempos = [round(i / fps, 2) for i in indices]
    sat = sum(saturaciones) / len(saturaciones) if saturaciones else 0.0
    return rutas, tiempos, sat


# ----------------------------------------------------------------------------
# 5. Informe
# ----------------------------------------------------------------------------
def escribir_informe(ruta, r):
    f = r["ficha"]
    marca = {"OK": "[OK]", "AVISO": "[AVISO]", "ERROR": "[ERROR]"}
    L = ["# Informe de blocking 3D para Seedance 2.5", "",
         "## Ficha tecnica",
         f"- Archivo: {f['archivo']}",
         f"- Duracion: {f['duracion_s']} s | {f['cuadros']} cuadros | {f['fps']:g} fps",
         f"- Imagen: {f['ancho']}x{f['alto']} ({f['relacion']:.3f}:1) | codec {f['codec']} | "
         f"{f['peso_mb']} MB | audio: {'si' if f['audio'] else 'no'}", "",
         "## Validacion contra Seedance 2.5"]
    L += [f"- {marca[n]} {m}" for n, m in r["validacion"]]
    L += ["", "## Ajustes de generacion que hacen coincidir resultado y blocking",
          f"- Duracion: {r['duracion_generacion_s']} s",
          f"- Aspect ratio: {r['aspecto_seedance']}",
          "- Modo: omni reference, con este video como unica referencia de video del blocking", "",
          "## Cortes detectados"]
    if r["cortes"] is None:
        L.append("- No analizado (falta numpy).")
    elif r["cortes"]:
        L += [f"- {k['t_s']:.2f} s (cuadro {k['cuadro']}, fuerza {k['fuerza']})" for k in r["cortes"]]
        L.append("- Cada corte debe aparecer como HARD CUT en ese segundo exacto del desglose.")
        L.append("- Confirma cada uno en las hojas: un objeto que tapa todo el cuadro o una camara")
        L.append("  que atraviesa una pared tambien producen un pico, y eso es un fallo del blocking.")
    else:
        L.append("- Ninguno: plano secuencia (one unbroken take). No escribas cortes en el prompt.")
    L += ["", "## Tramos sugeridos para el desglose (ajustalos tras ver las hojas)"]
    L += [f"- {t['desde_s']:g}s-{t['hasta_s']:g}s" + ("  <- entra por corte" if t["entra_por_corte"] else "")
          for t in r["tramos"]]
    L += ["", "## Hojas de contacto"]
    if r["hojas"]:
        L += [f"- {h}" for h in r["hojas"]]
        L += ["", "Cada miniatura lleva su segundo exacto. Las lineas amarillas son la cuadricula de",
              "tercios anadida por este script (no estan en tu render). Barra roja = primer cuadro",
              "tras un corte."]
    else:
        L.append(f"- No generadas: {r.get('hojas_error', 'falta Pillow')}")
    if r["observaciones"]:
        L += ["", "## Observaciones"] + [f"- {o}" for o in r["observaciones"]]
    L += ["", "## Siguiente paso",
          "Abre cada hoja de contacto y anota por tramo: tamano de plano, altura y angulo de",
          "camara, movimiento, posicion de cada proxy en tercios y hacia donde se desplaza.",
          "Revisa tambien que no haya ejes, rejilla, gizmos, lineas de trayectoria ni texto en",
          "pantalla: todo lo que se ve en el blocking puede acabar en el video final.", ""]
    with open(ruta, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))


def main():
    ap = argparse.ArgumentParser(description="Analiza un video de blocking 3D para Seedance 2.5.")
    ap.add_argument("video")
    ap.add_argument("--salida", default="", help="Carpeta de salida (por defecto: <video>_analisis)")
    ap.add_argument("--cuadros-por-segundo", type=float, default=2.0,
                    help="Miniaturas por segundo en las hojas de contacto (por defecto 2)")
    ap.add_argument("--sin-tercios", action="store_true", help="No dibujar la cuadricula de tercios")
    a = ap.parse_args()

    if not os.path.isfile(a.video):
        salir(f"No existe el archivo: {a.video}")
    for herramienta in ("ffmpeg", "ffprobe"):
        if shutil.which(herramienta) is None:
            salir(f"Falta {herramienta}. Instalalo (apt install ffmpeg / brew install ffmpeg / "
                  "winget install ffmpeg) y vuelve a ejecutar.")

    salida = a.salida or os.path.splitext(os.path.abspath(a.video))[0] + "_analisis"
    os.makedirs(salida, exist_ok=True)

    ficha = leer_ficha(a.video)
    validacion, dur_gen, aspecto = validar(ficha)
    observaciones = []

    cortes = None
    if np is not None:
        ancho_g = 160
        alto_g = max(16, int(round(ancho_g * ficha["alto"] / ficha["ancho"] / 2) * 2))
        gris = leer_cuadros_gris(a.video, ancho_g, alto_g)
        if gris is not None and len(gris) > 2:
            ficha["cuadros"] = int(len(gris))
            cortes = detectar_cortes(gris, ficha["fps"])
            barras = barras_negras(gris)
            if barras > 0:
                observaciones.append(
                    f"Barras negras quemadas (~{barras * 100:.0f} % del alto). El modelo las copiaria: "
                    "renderiza a cuadro completo en el aspecto final, sin letterbox.")
        else:
            observaciones.append("No se pudo decodificar el video para detectar cortes.")
    else:
        observaciones.append("numpy no esta instalado: sin deteccion de cortes (pip install numpy). "
                             "Localizalos a ojo en las hojas de contacto.")

    hojas, tiempos, extra = [], [], None
    if Image is not None:
        hojas, tiempos, extra = hojas_de_contacto(a.video, ficha, cortes or [], salida,
                                                  a.cuadros_por_segundo, not a.sin_tercios)
        if hojas and isinstance(extra, float) and extra > 0.18:
            observaciones.append(
                f"El blocking tiene color apreciable (saturacion media {extra:.2f}). Un modelo blanco "
                "neutro evita que Seedance copie colores del previz; si el color es intencional, "
                "dilo en el prompt.")
    else:
        extra = "Pillow no esta instalado (pip install pillow)."

    resultado = {
        "ficha": ficha,
        "validacion": validacion,
        "duracion_generacion_s": dur_gen,
        "aspecto_seedance": aspecto,
        "cortes": cortes,
        "tramos": tramos_sugeridos(ficha["duracion_s"], cortes or []),
        "hojas": hojas,
        "tiempos_miniaturas_s": tiempos,
        "observaciones": observaciones,
    }
    if not hojas:
        resultado["hojas_error"] = extra if isinstance(extra, str) else "sin cuadros"

    ruta_json = os.path.join(salida, "blocking_report.json")
    ruta_md = os.path.join(salida, "blocking_report.md")
    with open(ruta_json, "w", encoding="utf-8") as fh:
        json.dump(resultado, fh, ensure_ascii=False, indent=1)
    escribir_informe(ruta_md, resultado)

    errores = [m for n, m in validacion if n == "ERROR"]
    avisos = [m for n, m in validacion if n == "AVISO"]
    print(f"Blocking: {ficha['duracion_s']} s | {ficha['fps']:g} fps | {ficha['ancho']}x{ficha['alto']} "
          f"| aspecto {aspecto} | {ficha['peso_mb']} MB")
    print(f"Generar con: duracion {dur_gen} s, aspect ratio {aspecto}")
    if cortes is not None:
        print("Cortes: " + (", ".join(f"{k['t_s']:.2f}s" for k in cortes) if cortes
                            else "ninguno (plano secuencia)"))
    for m in errores:
        print(f"ERROR: {m}")
    for m in avisos + observaciones:
        print(f"AVISO: {m}")
    print(f"Informe: {ruta_md}")
    for h in hojas:
        print(f"Hoja de contacto: {h}")
    sys.exit(1 if errores else 0)


if __name__ == "__main__":
    main()
