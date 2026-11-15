#!/usr/bin/env python3
"""
blender_exportar_blocking.py - Exporta los datos reales del blocking 3D de Blender
para escribir prompts de Seedance 2.5 que coincidan con el video de referencia.

Se ejecuta DENTRO de Blender (usa bpy). Hace hasta tres cosas:

  1. EXPORTAR (siempre): recorre la linea de tiempo y escribe un JSON + un resumen
     .md con la camara real de cada fase: lente (mm), apertura, altura, trayectoria,
     velocidad, cortes, y el tamano de plano / posicion en cuadro de cada actor.
  2. PREPARAR (--preparar): deja el render como "modelo blanco" limpio (Workbench,
     sin metadatos quemados, MP4 H.264 sin audio). No toca fps ni animacion.
  3. RENDERIZAR (--render ruta.mp4): renderiza la animacion a ese archivo.

USO A - desde la interfaz de Blender:
    Pestana Scripting > Open > este archivo > Run Script.
    Ajusta el diccionario CONFIG de abajo si quieres preparar o renderizar.

USO B - linea de comandos:
    blender -b escena.blend -P blender_exportar_blocking.py -- \
        --salida blocking_data.json --preparar --aspecto 21:9 --alto 720 \
        --render blocking.mp4

Opciones (despues del "--"):
    --salida RUTA        JSON de salida (por defecto //blocking_data.json, junto al .blend)
    --objetos A,B,C      Nombres de objetos a seguir (actores, vehiculos, props clave)
    --coleccion NOMBRE   Seguir los objetos de esta coleccion (por defecto busca ACTORES)
    --principal NOMBRE   Sujeto principal (por defecto: el de mayor presencia en cuadro)
    --preparar           Aplica el look de modelo blanco limpio para el render
    --aspecto 21:9       Con --preparar: ajusta la resolucion a este aspecto de Seedance
    --alto 720           Con --aspecto: alto en pixeles (720 es suficiente)
    --render RUTA.mp4    Renderiza la animacion a este archivo

Convencion recomendada: mete personajes y vehiculos en una coleccion llamada ACTORES
y nombralos por su rol (HEROE, VILLANO, AUTO_PATRULLA). Esos nombres aparecen en el
informe y permiten mapear cada proxy gris con su imagen de referencia en el prompt.

Probado con Blender 5.3 (API bpy). Usa solo API estable; los ajustes opcionales van
protegidos para funcionar tambien en 3.6 / 4.x.
"""

import json
import math
import os
import sys

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

# ----------------------------------------------------------------------------
# CONFIG: valores usados cuando se ejecuta desde la interfaz (sin argumentos).
# ----------------------------------------------------------------------------
CONFIG = {
    "salida": "//blocking_data.json",
    "objetos": "",        # "HEROE,AUTO" o vacio para deteccion automatica
    "coleccion": "",      # vacio = busca ACTORES / BLOCKING / SUJETOS
    "principal": "",
    "preparar": False,
    "aspecto": "",        # "21:9", "16:9", "9:16", "4:3", "3:4", "1:1"
    "alto": 720,
    "render": "",         # "//blocking.mp4" para renderizar
}

ASPECTOS_SEEDANCE = {"21:9": 21 / 9, "16:9": 16 / 9, "4:3": 4 / 3, "1:1": 1.0,
                     "3:4": 3 / 4, "9:16": 9 / 16}
COLECCIONES_ACTORES = ("ACTORES", "ACTORS", "BLOCKING", "SUJETOS", "PERSONAJES")
DUR_MIN, DUR_MAX = 4.0, 30.0          # duracion de generacion de Seedance 2.5
VENTANA_S = 0.5                       # ventana de analisis de movimiento
UMBRAL_TRAS = 0.08                    # m/s minimo para contar una traslacion
UMBRAL_ROT = 2.0                      # grados/s minimo para contar una rotacion
UMBRAL_LENTE = 1.0                    # mm/s minimo para contar un zoom
TIPOS_GEOMETRIA = {"MESH", "CURVE", "SURFACE", "META", "FONT", "ARMATURE",
                   "GPENCIL", "GREASEPENCIL", "VOLUME", "POINTCLOUD", "CURVES"}


# ----------------------------------------------------------------------------
# Utilidades
# ----------------------------------------------------------------------------
def leer_argumentos():
    cfg = dict(CONFIG)
    if "--" not in sys.argv:
        return cfg
    args = sys.argv[sys.argv.index("--") + 1:]
    i = 0
    while i < len(args):
        clave = args[i].lstrip("-")
        if clave == "preparar":
            cfg["preparar"] = True
            i += 1
            continue
        if clave in cfg and i + 1 < len(args):
            valor = args[i + 1]
            cfg[clave] = int(valor) if clave == "alto" else valor
            i += 2
            continue
        print(f"[blocking] Aviso: argumento no reconocido '{args[i]}'")
        i += 1
    return cfg


def ruta_abs(ruta):
    """Resuelve rutas '//' relativas al .blend; si no hay .blend usa el directorio actual."""
    if ruta.startswith("//") and not bpy.data.filepath:
        return os.path.abspath(ruta[2:])
    return os.path.abspath(bpy.path.abspath(ruta))


def grados(rad):
    return math.degrees(rad)


def desenrollar(angulos):
    """Quita los saltos de 360 grados de una serie de angulos."""
    salida, acumulado = [], 0.0
    for i, a in enumerate(angulos):
        if i:
            d = a - angulos[i - 1]
            if d > 180:
                acumulado -= 360
            elif d < -180:
                acumulado += 360
        salida.append(a + acumulado)
    return salida


def aspecto_mas_cercano(ratio):
    nombre = min(ASPECTOS_SEEDANCE, key=lambda k: abs(math.log(ASPECTOS_SEEDANCE[k] / ratio)))
    desvio = abs(ASPECTOS_SEEDANCE[nombre] / ratio - 1.0)
    return nombre, desvio


def velocidad_txt(v):
    if v < 0.5:
        return "slow"
    if v < 2.0:
        return "medium speed"
    if v < 6.0:
        return "fast"
    return "very fast"


def rotacion_txt(v):
    if v < 10:
        return "slow"
    if v < 40:
        return "medium speed"
    if v < 90:
        return "fast"
    return "whip"


def tercio_h(x):
    return "left third" if x < 1 / 3 else ("center" if x <= 2 / 3 else "right third")


def tercio_v(y):
    return "lower third" if y < 1 / 3 else ("middle" if y <= 2 / 3 else "upper third")


def tamano_plano(ratio):
    """ratio = altura del sujeto / altura del cuadro a su distancia.

    Para una persona de 1.8 m: ratio 2.25 significa que el cuadro abarca 0.8 m (cabeza y
    pecho), ratio 0.6 que abarca 3 m (cuerpo entero con mucho aire).
    """
    if ratio < 0.25:
        return "EWS (extreme wide)"
    if ratio < 0.6:
        return "WS (wide)"
    if ratio < 1.1:
        return "FS (full shot)"
    if ratio < 1.5:
        return "MFS (cowboy)"
    if ratio < 2.25:
        return "MS (medium)"
    if ratio < 3.6:
        return "MCU (medium close-up)"
    if ratio < 7.0:
        return "CU (close-up)"
    return "ECU (extreme close-up)"


# ----------------------------------------------------------------------------
# Preparacion del render de modelo blanco
# ----------------------------------------------------------------------------
def preparar_render(escena, cfg, avisos):
    r = escena.render
    hecho = []
    for motor in ("BLENDER_WORKBENCH", "BLENDER_WORKBENCH_NEXT"):
        try:
            r.engine = motor
            hecho.append(f"motor {motor}")
            break
        except TypeError:
            continue
    sh = escena.display.shading
    for attr, valor in (("light", "STUDIO"), ("color_type", "OBJECT"),
                        ("show_shadows", True), ("show_cavity", True),
                        ("show_object_outline", True), ("show_specular_highlight", False)):
        try:
            setattr(sh, attr, valor)
        except (AttributeError, TypeError):
            pass
    hecho.append("sombreado studio + sombras + cavidad + contorno")
    r.use_stamp = False
    r.film_transparent = False
    hecho.append("metadatos quemados OFF")
    if escena.world is not None:
        try:
            escena.world.color = (0.62, 0.62, 0.62)
            hecho.append("fondo gris claro")
        except AttributeError:
            pass
    if cfg["aspecto"]:
        if cfg["aspecto"] in ASPECTOS_SEEDANCE:
            alto = int(cfg["alto"])
            ancho = int(round(alto * ASPECTOS_SEEDANCE[cfg["aspecto"]] / 2) * 2)
            r.resolution_x, r.resolution_y, r.resolution_percentage = ancho, alto, 100
            hecho.append(f"resolucion {ancho}x{alto} ({cfg['aspecto']})")
        else:
            avisos.append(f"Aspecto '{cfg['aspecto']}' no es nativo de Seedance 2.5; "
                          f"usa uno de {', '.join(ASPECTOS_SEEDANCE)}.")
    print("[blocking] Render preparado: " + "; ".join(hecho))
    return hecho


def configurar_video(escena, ruta):
    r = escena.render
    im = r.image_settings
    if hasattr(im, "media_type"):
        im.media_type = "VIDEO"
    im.file_format = "FFMPEG"
    r.ffmpeg.format = "MPEG4"
    r.ffmpeg.codec = "H264"
    try:
        r.ffmpeg.constant_rate_factor = "MEDIUM"
        r.ffmpeg.audio_codec = "NONE"
    except (AttributeError, TypeError):
        pass
    r.filepath = ruta


# ----------------------------------------------------------------------------
# Seleccion de sujetos
# ----------------------------------------------------------------------------
def descendientes(obj):
    try:
        return list(obj.children_recursive)
    except AttributeError:
        salida, cola = [], list(obj.children)
        while cola:
            o = cola.pop()
            salida.append(o)
            cola.extend(o.children)
        return salida


def raices(objetos):
    """Deja solo los objetos cuyo ancestro no esta tambien en la lista."""
    nombres = {o.name for o in objetos}
    salida = []
    for o in objetos:
        p, tiene = o.parent, False
        while p is not None:
            if p.name in nombres:
                tiene = True
                break
            p = p.parent
        if not tiene:
            salida.append(o)
    return salida


def elegir_sujetos(escena, cfg, avisos):
    excluidos = {"CAMERA", "LIGHT", "LIGHT_PROBE", "SPEAKER"}
    if cfg["objetos"]:
        lista = []
        for nombre in [n.strip() for n in cfg["objetos"].split(",") if n.strip()]:
            if nombre in bpy.data.objects:
                lista.append(bpy.data.objects[nombre])
            else:
                avisos.append(f"Objeto '{nombre}' no existe en la escena.")
        return raices(lista), "lista --objetos"
    nombres_col = [cfg["coleccion"]] if cfg["coleccion"] else list(COLECCIONES_ACTORES)
    for nombre in nombres_col:
        col = next((c for c in bpy.data.collections if c.name.upper() == nombre.upper()), None)
        if col is not None:
            lista = [o for o in col.all_objects if o.type not in excluidos]
            if lista:
                return raices(lista), f"coleccion {col.name}"
    # Deteccion automatica: lo que se mueve (o es un rig) cuenta como actor.
    f0, f1 = escena.frame_start, escena.frame_end
    muestras = sorted({int(round(f0 + (f1 - f0) * k / 8)) for k in range(9)})
    candidatos = [o for o in escena.objects if o.type not in excluidos]
    inicio, mov = {}, {}
    for f in muestras:
        escena.frame_set(f)
        dg = bpy.context.evaluated_depsgraph_get()
        for o in candidatos:
            p = o.evaluated_get(dg).matrix_world.translation.copy()
            if o.name not in inicio:
                inicio[o.name] = p
                mov[o.name] = 0.0
            else:
                mov[o.name] = max(mov[o.name], (p - inicio[o.name]).length)
    escala = escena.unit_settings.scale_length or 1.0
    lista = [o for o in candidatos if mov[o.name] * escala > 0.05 or o.type == "ARMATURE"]
    return raices(lista), "deteccion automatica (objetos animados)"


def caja_mundo(obj, dg):
    """Esquinas de la caja envolvente (objeto + descendientes) en coordenadas de mundo."""
    esquinas = []
    for o in [obj] + descendientes(obj):
        if o.type not in TIPOS_GEOMETRIA:
            continue
        oe = o.evaluated_get(dg)
        try:
            esquinas.extend(oe.matrix_world @ Vector(c) for c in oe.bound_box)
        except Exception:
            pass
    if not esquinas:
        esquinas = [obj.evaluated_get(dg).matrix_world.translation.copy()]
    return esquinas


def tan_medio_vertical(dato, escena):
    """Tangente del semi-angulo vertical REAL del cuadro (respeta sensor fit y aspecto)."""
    if dato.type == "ORTHO":
        return None
    try:
        marco = dato.view_frame(scene=escena)
        ys = [v.y for v in marco]
        z = abs(marco[0].z)
        if z > 1e-9:
            return (max(ys) - min(ys)) / 2.0 / z
    except Exception:
        pass
    return math.tan(dato.angle_y / 2.0)


def esta_ocluido(escena, dg, origen, puntos, propios):
    """True si todos los rayos camara->sujeto chocan antes con otro objeto."""
    try:
        for p in puntos:
            d = p - origen
            largo = d.length
            if largo < 1e-4:
                return False
            ok, _, _, _, objeto, _ = escena.ray_cast(dg, origen, d.normalized(), distance=largo - 0.02)
            if not ok or objeto is None or objeto.name in propios:
                return False
        return True
    except Exception:
        return False


# ----------------------------------------------------------------------------
# Muestreo de la linea de tiempo
# ----------------------------------------------------------------------------
def muestrear(escena, sujetos):
    fps = escena.render.fps / (escena.render.fps_base or 1.0)
    escala = escena.unit_settings.scale_length or 1.0
    cuadros = []
    for f in range(escena.frame_start, escena.frame_end + 1):
        escena.frame_set(f)               # aplica tambien los marcadores de camara
        dg = bpy.context.evaluated_depsgraph_get()
        cam = escena.camera
        reg = {"f": f, "t": (f - escena.frame_start) / fps, "cam": None, "suj": {}}
        if cam is not None:
            ce = cam.evaluated_get(dg)
            m = ce.matrix_world
            rot = m.to_3x3()
            adelante = (rot @ Vector((0, 0, -1))).normalized()
            derecha = (rot @ Vector((1, 0, 0))).normalized()
            arriba = (rot @ Vector((0, 1, 0))).normalized()
            dato = ce.data
            horizontal = Vector((adelante.x, adelante.y, 0.0))
            if horizontal.length < 1e-4:              # camara cenital o nadir
                horizontal = Vector((arriba.x, arriba.y, 0.0))
            horizontal.normalize()
            der_h = Vector((derecha.x, derecha.y, 0.0))
            der_h = der_h.normalized() if der_h.length > 1e-4 else Vector((1, 0, 0))
            foco, foco_obj = None, None
            if getattr(dato, "dof", None) is not None and dato.dof.use_dof:
                if dato.dof.focus_object is not None:
                    foco_obj = dato.dof.focus_object.name
                    objetivo = dato.dof.focus_object.evaluated_get(dg).matrix_world.translation
                    foco = (objetivo - m.translation).length * escala
                else:
                    foco = dato.dof.focus_distance * escala
            reg["cam"] = {
                "nombre": cam.name,
                "pos": m.translation.copy() * escala,
                "adelante": adelante, "adelante_h": horizontal, "derecha_h": der_h,
                "yaw": grados(math.atan2(horizontal.y, horizontal.x)),
                "pitch": grados(math.asin(max(-1.0, min(1.0, adelante.z)))),
                "roll": grados(math.asin(max(-1.0, min(1.0, derecha.z)))),
                "lente": float(dato.lens) if dato.type != "ORTHO" else None,
                "sensor": float(dato.sensor_width),
                "tan_v": tan_medio_vertical(dato, escena),
                "tipo": dato.type,
                "dof": bool(getattr(dato, "dof", None) and dato.dof.use_dof),
                "fstop": float(dato.dof.aperture_fstop) if getattr(dato, "dof", None) else None,
                "foco": foco, "foco_obj": foco_obj,
            }
            for s in sujetos:
                esquinas = caja_mundo(s, dg)
                centro = sum(esquinas, Vector()) / len(esquinas)
                alto_real = (max(e.z for e in esquinas) - min(e.z for e in esquinas)) * escala
                proy = [world_to_camera_view(escena, cam, e) for e in esquinas]
                c = world_to_camera_view(escena, cam, centro)
                z_max = max(e.z for e in esquinas)
                z_min = min(e.z for e in esquinas)
                cabeza = Vector((centro.x, centro.y, z_max - 0.08 * (z_max - z_min)))
                k = world_to_camera_view(escena, cam, cabeza)
                delante = [p for p in proy if p.z > 0]
                xs = [p.x for p in delante] or [c.x]
                ys = [p.y for p in delante] or [c.y]
                x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
                visible = bool(delante) and x1 > 0 and x0 < 1 and y1 > 0 and y0 < 1
                ocluido = False
                if visible:
                    propios = {s.name} | {d.name for d in descendientes(s)}
                    ocluido = esta_ocluido(escena, dg, m.translation, [centro, cabeza], propios)
                    visible = not ocluido
                area = max(0.0, min(x1, 1) - max(x0, 0)) * max(0.0, min(y1, 1) - max(y0, 0))
                dist = c.z * escala
                ratio = None
                if reg["cam"]["tan_v"] and dist > 1e-3 and alto_real > 1e-3:
                    alto_cuadro = 2.0 * dist * reg["cam"]["tan_v"]
                    ratio = alto_real / alto_cuadro
                reg["suj"][s.name] = {
                    "pos": centro * escala, "x": c.x, "y": c.y, "dist": dist,
                    "kx": k.x, "ky": k.y, "ocluido": ocluido,
                    "visible": visible, "area": area if visible else 0.0,
                    "alto": alto_real, "ratio": ratio,
                }
        cuadros.append(reg)
    return cuadros, fps


# ----------------------------------------------------------------------------
# Analisis: cortes, fases de movimiento y sujetos
# ----------------------------------------------------------------------------
def detectar_cortes(cuadros):
    pasos = []
    for a, b in zip(cuadros, cuadros[1:]):
        if a["cam"] and b["cam"] and a["cam"]["nombre"] == b["cam"]["nombre"]:
            pasos.append((b["cam"]["pos"] - a["cam"]["pos"]).length)
    mediana = sorted(pasos)[len(pasos) // 2] if pasos else 0.0
    cortes = []
    for i in range(1, len(cuadros)):
        a, b = cuadros[i - 1]["cam"], cuadros[i]["cam"]
        if not a or not b:
            continue
        if a["nombre"] != b["nombre"]:
            cortes.append({"i": i, "t": cuadros[i]["t"], "tipo": "cambio de camara",
                           "de": a["nombre"], "a": b["nombre"]})
            continue
        salto = (b["pos"] - a["pos"]).length
        giro = grados(a["adelante"].angle(b["adelante"], 0.0))
        if (salto > 1.0 and salto > 10 * max(mediana, 1e-4)) or giro > 15.0:
            cortes.append({"i": i, "t": cuadros[i]["t"], "tipo": "salto de camara",
                           "de": a["nombre"], "a": b["nombre"]})
    return cortes


def descomponer(cs):
    """Desplazamiento de camara sumado cuadro a cuadro en sus ejes de cada instante.

    Sumar por cuadro (y no medir de extremo a extremo) es lo que permite leer bien las
    trayectorias curvas: en una orbita el recorrido es lateral, aunque el punto final
    quede "delante" del inicial.
    """
    empuje = lateral = sube = recorrido = 0.0
    for x, y in zip(cs, cs[1:]):
        d = y["cam"]["pos"] - x["cam"]["pos"]
        d_h = Vector((d.x, d.y, 0.0))
        empuje += d_h.dot(x["cam"]["adelante_h"])
        lateral += d_h.dot(x["cam"]["derecha_h"])
        sube += d.z
        recorrido += d.length
    return empuje, lateral, sube, recorrido


def buscar_orbita(cs, dt):
    """Detecta si la camara gira alrededor de un punto fijo al que mira.

    Cruza (minimos cuadrados, en planta) los ejes de mirada de varios cuadros. Si convergen
    en un punto P a distancia constante y la camara barre un angulo alrededor de P, es una
    orbita. Devuelve (centro, radio, barrido_grados) o None.
    """
    n = len(cs)
    idx = sorted({int(round(k * (n - 1) / 8)) for k in range(9)})
    a11 = a12 = a22 = b1 = b2 = 0.0
    for i in idx:
        c = cs[i]["cam"]
        u = c["adelante_h"]
        nx, ny = -u.y, u.x                     # normal a la linea de mirada
        k = nx * c["pos"].x + ny * c["pos"].y
        a11 += nx * nx
        a12 += nx * ny
        a22 += ny * ny
        b1 += nx * k
        b2 += ny * k
    det = a11 * a22 - a12 * a12
    if abs(det) < 1e-4:                        # miradas paralelas: no hay punto de cruce
        return None
    centro = Vector(((b1 * a22 - b2 * a12) / det, (a11 * b2 - a12 * b1) / det, 0.0))
    radios, angulos = [], []
    for i in idx:
        c = cs[i]["cam"]
        r = Vector((c["pos"].x - centro.x, c["pos"].y - centro.y, 0.0))
        if r.length < 0.3 or (-r.normalized()).dot(c["adelante_h"]) < 0.9:
            return None                        # la camara no esta mirando a ese punto
        radios.append(r.length)
        angulos.append(grados(math.atan2(r.y, r.x)))
    if max(radios) > 1.25 * min(radios) or max(radios) > 300:
        return None
    angulos = desenrollar(angulos)
    barrido = angulos[-1] - angulos[0]
    if abs(barrido) / dt < 5.0 or abs(barrido) < 4.0:
        return None
    return centro, sum(radios) / len(radios), barrido


def analizar_ventana(cs, principal):
    """Clasifica el movimiento de camara entre el primer y el ultimo cuadro de 'cs'."""
    a, b = cs[0]["cam"], cs[-1]["cam"]
    dt = max(cs[-1]["t"] - cs[0]["t"], 1e-6)
    empuje, lateral, sube, recorrido = descomponer(cs)
    yaws = desenrollar([c["cam"]["yaw"] for c in cs])
    d_yaw = yaws[-1] - yaws[0]
    d_pitch = b["pitch"] - a["pitch"]
    d_roll = b["roll"] - a["roll"]
    d_lente = (b["lente"] - a["lente"]) if (a["lente"] and b["lente"]) else 0.0
    etiquetas = []
    # Una componente solo cuenta si supera el umbral y pesa >= 25 % de la dominante:
    # asi una grua con 10 cm de deriva lateral no se describe como "truck".
    t_max = max(abs(empuje), abs(lateral), abs(sube))
    r_max = max(abs(d_yaw), abs(d_pitch), abs(d_roll))

    def cuenta_t(v):
        return abs(v) / dt > UMBRAL_TRAS and abs(v) >= 0.25 * t_max

    def cuenta_r(v):
        return abs(v) / dt > UMBRAL_ROT and abs(v) >= 0.25 * r_max

    sp = cs[0]["suj"].get(principal) if principal else None
    sq = cs[-1]["suj"].get(principal) if principal else None
    orbita = buscar_orbita(cs, dt) if cuenta_t(lateral) else None
    if orbita:
        centro, radio, barrido = orbita
        alrededor = ""
        if sp and (Vector((sp["pos"].x, sp["pos"].y, 0.0)) - centro).length < max(0.5, 0.3 * radio):
            alrededor = f" around {principal}"
        etiquetas.append("orbit " + ("right (counter-clockwise)" if barrido > 0 else "left (clockwise)")
                         + alrededor + f", {abs(barrido):.0f} deg at {radio:.1f} m radius")
    if cuenta_t(empuje):
        etiquetas.append("dolly in (push-in)" if empuje > 0 else "dolly out (pull-back)")
    if cuenta_t(lateral) and not orbita:       # en una orbita, truck y pan ya estan dichos
        etiquetas.append("truck right" if lateral > 0 else "truck left")
    if cuenta_t(sube):
        etiquetas.append("crane up" if sube > 0 else "crane down")
    if cuenta_r(d_yaw) and not orbita:
        etiquetas.append("pan left" if d_yaw > 0 else "pan right")
    if cuenta_r(d_pitch):
        etiquetas.append("tilt up" if d_pitch > 0 else "tilt down")
    if cuenta_r(d_roll):
        etiquetas.append("roll (dutch)")
    if abs(d_lente) / dt > UMBRAL_LENTE:
        etiquetas.append("zoom in" if d_lente > 0 else "zoom out")
    # Movimientos compuestos que tienen nombre propio
    if abs(d_lente) / dt > UMBRAL_LENTE and cuenta_t(empuje) and (d_lente > 0) != (empuje > 0):
        etiquetas.append("dolly zoom (vertigo)")
    if sp and sq and not orbita:
        v_suj = (sq["pos"] - sp["pos"]) / dt
        v_cam = (b["pos"] - a["pos"]) / dt
        if v_suj.length > 0.3 and (v_cam - v_suj).length < 0.35 * v_suj.length:
            hacia = (a["pos"] - sp["pos"]).normalized().dot(v_suj.normalized())
            if hacia > 0.6:
                etiquetas.append(f"leading tracking shot (camera retreats ahead of {principal})")
            elif hacia < -0.6:
                etiquetas.append(f"follow shot (camera travels behind {principal})")
            else:
                etiquetas.append(f"lateral tracking shot (camera travels beside {principal})")
    if not etiquetas:
        etiquetas.append("static (locked-off)")
    return {
        "etiquetas": etiquetas, "dt": dt, "empuje": empuje, "lateral": lateral,
        "sube": sube, "d_yaw": d_yaw, "d_pitch": d_pitch, "d_roll": d_roll,
        "d_lente": d_lente, "dist": recorrido,
        "orbita": ({"grados": round(orbita[2], 1), "radio_m": round(orbita[1], 2)} if orbita else None),
    }


def temblor(cs, fps):
    """Mide el temblor de camara en mano: (rms en grados, es_temblor).

    Usa la segunda diferencia de la rotacion. En un movimiento animado con curvas suaves
    esa aceleracion mantiene el signo durante muchos cuadros; en una camara en mano cambia
    de signo casi en cada cuadro. Se exige amplitud Y alternancia de signo.
    """
    if len(cs) < 8:
        return 0.0, False
    yaws = desenrollar([c["cam"]["yaw"] for c in cs])
    pitches = [c["cam"]["pitch"] for c in cs]
    total, cambios, cuenta = 0.0, 0, 0
    for serie in (yaws, pitches):
        d2 = [serie[i - 1] - 2 * serie[i] + serie[i + 1] for i in range(1, len(serie) - 1)]
        total += sum(v * v for v in d2)
        cuenta += len(d2)
        cambios += sum(1 for x, y in zip(d2, d2[1:]) if x * y < 0)
    rms = math.sqrt(total / cuenta) if cuenta else 0.0
    alternancia = cambios / max(1, cuenta - 2)
    return rms, bool(rms > 0.03 and alternancia > 0.5)


def resumen_sujeto(cs, nombre):
    a, b = cs[0]["suj"].get(nombre), cs[-1]["suj"].get(nombre)
    if not a or not b:
        return None
    visibles = [c["suj"][nombre] for c in cs if c["suj"].get(nombre, {}).get("visible")]
    if not visibles:
        tapado = any(c["suj"].get(nombre, {}).get("ocluido") for c in cs)
        return {"nombre": nombre, "visible": False,
                "motivo": "ocluido por el decorado" if tapado else "fuera de cuadro"}
    ini, fin = visibles[0], visibles[-1]

    def en_cuadro(v):
        # En planos cerrados (el cuerpo no cabe) importa donde cae la cabeza.
        if v["ratio"] and v["ratio"] >= 1.0:
            return f"head at {tercio_h(v['kx'])}, {tercio_v(v['ky'])}"
        return f"{tercio_h(v['x'])}, {tercio_v(v['y'])}"
    dt = max(cs[-1]["t"] - cs[0]["t"], 1e-6)
    recorrido = sum((y["suj"][nombre]["pos"] - x["suj"][nombre]["pos"]).length
                    for x, y in zip(cs, cs[1:]))
    vel = recorrido / dt
    d_dist = b["dist"] - a["dist"]
    if vel < 0.1:
        accion = "stays in place"
    else:
        accion = f"moves {recorrido:.1f} m at {vel:.1f} m/s"
    if vel >= 0.1 and abs(d_dist) > 0.3:
        accion += ", approaching camera" if d_dist < 0 else ", receding from camera"
    if vel >= 0.1 and abs(fin["x"] - ini["x"]) > 0.12:
        accion += ", crossing frame " + ("left-to-right" if fin["x"] > ini["x"] else "right-to-left")
    return {
        "nombre": nombre, "visible": True,
        "plano_inicio": tamano_plano(ini["ratio"]) if ini["ratio"] else None,
        "plano_fin": tamano_plano(fin["ratio"]) if fin["ratio"] else None,
        "cuadro_inicio": en_cuadro(ini), "cuadro_fin": en_cuadro(fin),
        "diminuto": bool(max(v["area"] for v in visibles) < 0.001),
        "visible_pct": int(round(100.0 * len(visibles) / len(cs))),
        "x_inicio": round(ini["x"], 2), "x_fin": round(fin["x"], 2),
        "dist_inicio_m": round(ini["dist"], 2), "dist_fin_m": round(fin["dist"], 2),
        "altura_m": round(ini["alto"], 2), "velocidad_ms": round(vel, 2),
        "accion": accion,
    }


def construir_fases(cuadros, fps, cortes, sujetos, principal):
    limites = [0] + [c["i"] for c in cortes] + [len(cuadros)]
    paso = max(2, int(round(VENTANA_S * fps)))
    fases = []
    for s in range(len(limites) - 1):
        seg = [c for c in cuadros[limites[s]:limites[s + 1]] if c["cam"]]
        if len(seg) < 2:
            continue
        # 1) ventanas de medio segundo con su conjunto de etiquetas
        ventanas, i = [], 0
        while i < len(seg) - 1:
            j = min(i + paso, len(seg) - 1)
            if len(seg) - 1 - j < paso // 2:
                j = len(seg) - 1
            ventanas.append((i, j, tuple(sorted(analizar_ventana(seg[i:j + 1], principal)["etiquetas"]))))
            i = j
        # 2) fusiona ventanas consecutivas con el mismo movimiento
        grupos = []
        for i, j, et in ventanas:
            if grupos and grupos[-1][2] == et:
                grupos[-1] = (grupos[-1][0], j, et)
            else:
                grupos.append((i, j, et))
        # 3) absorbe fases muy cortas (< 0.75 s) en su vecina mas larga
        cambio = True
        while cambio and len(grupos) > 1:
            cambio = False
            for k, (i, j, et) in enumerate(grupos):
                if seg[j]["t"] - seg[i]["t"] < 0.75:
                    izq = grupos[k - 1] if k > 0 else None
                    der = grupos[k + 1] if k + 1 < len(grupos) else None
                    dur_izq = seg[izq[1]]["t"] - seg[izq[0]]["t"] if izq else -1
                    dur_der = seg[der[1]]["t"] - seg[der[0]]["t"] if der else -1
                    if dur_izq >= dur_der:
                        grupos[k - 1] = (izq[0], j, izq[2])
                    else:
                        grupos[k + 1] = (i, der[1], der[2])
                    del grupos[k]
                    cambio = True
                    break
        # 4) une fases vecinas que, medidas enteras, resultan ser el mismo movimiento
        cambio = True
        while cambio and len(grupos) > 1:
            cambio = False
            for k in range(len(grupos) - 1):
                (i0, j0, _), (i1, j1, _) = grupos[k], grupos[k + 1]
                e0 = sorted(analizar_ventana(seg[i0:j0 + 1], principal)["etiquetas"])
                e1 = sorted(analizar_ventana(seg[i1:j1 + 1], principal)["etiquetas"])
                quitar_cifras = lambda et: [x.split(",")[0] for x in et]
                if quitar_cifras(e0) == quitar_cifras(e1):
                    grupos[k] = (i0, j1, tuple(e0))
                    del grupos[k + 1]
                    cambio = True
                    break
        # 5) describe cada fase con totales reales
        for k, (i, j, _) in enumerate(grupos):
            cs = seg[i:j + 1]
            mov = analizar_ventana(cs, principal)
            a, b = cs[0]["cam"], cs[-1]["cam"]
            vel = mov["dist"] / mov["dt"]
            vel_rot = (abs(mov["d_yaw"]) + abs(mov["d_pitch"])) / mov["dt"]
            rms, en_mano = temblor(cs, fps)
            fin_t = cs[-1]["t"] + (1.0 / fps if (j == len(seg) - 1) else 0.0)
            fase = {
                "inicio_s": round(cs[0]["t"], 2), "fin_s": round(fin_t, 2),
                "camara": a["nombre"],
                "entra_por_corte": bool(k == 0 and s > 0),
                "movimiento": mov["etiquetas"],
                "velocidad_camara_ms": round(vel, 2),
                "ritmo": (velocidad_txt(vel) if vel > UMBRAL_TRAS else
                          (rotacion_txt(vel_rot) + " rotation" if vel_rot > UMBRAL_ROT else "still")),
                "recorrido_m": round(mov["dist"], 2),
                "empuje_m": round(mov["empuje"], 2), "lateral_m": round(mov["lateral"], 2),
                "vertical_m": round(mov["sube"], 2),
                "pan_grados": round(mov["d_yaw"], 1), "tilt_grados": round(mov["d_pitch"], 1),
                "roll_grados": round(mov["d_roll"], 1),
                "lente_mm": [round(a["lente"], 1) if a["lente"] else None,
                             round(b["lente"], 1) if b["lente"] else None],
                "altura_camara_m": [round(a["pos"].z, 2), round(b["pos"].z, 2)],
                "inclinacion_grados": [round(a["pitch"], 1), round(b["pitch"], 1)],
                "orbita": mov["orbita"],
                "camara_en_mano": en_mano, "temblor_rms_grados": round(rms, 3),
                "dof": ({"fstop": round(a["fstop"], 1), "foco_m": round(a["foco"], 2) if a["foco"] else None,
                         "foco_objeto": a["foco_obj"]} if a["dof"] else None),
                "sujetos": [r for r in (resumen_sujeto(cs, o.name) for o in sujetos) if r],
            }
            fases.append(fase)
    return fases


# ----------------------------------------------------------------------------
# Salida
# ----------------------------------------------------------------------------
def linea_fase(f):
    partes = [f"{f['inicio_s']:.1f}-{f['fin_s']:.1f} s", f["camara"]]
    l0, l1 = f["lente_mm"]
    if l0:
        partes.append(f"{l0:g} mm" if l0 == l1 else f"{l0:g}->{l1:g} mm")
    mov = ", ".join(f["movimiento"])
    detalle = []
    if abs(f["empuje_m"]) >= 0.1:
        detalle.append(f"avance {f['empuje_m']:+.1f} m")
    if abs(f["lateral_m"]) >= 0.1:
        detalle.append(f"lateral {f['lateral_m']:+.1f} m")
    if abs(f["vertical_m"]) >= 0.1:
        detalle.append(f"vertical {f['vertical_m']:+.1f} m")
    if abs(f["pan_grados"]) >= 2:
        detalle.append(f"pan {f['pan_grados']:+.0f} deg")
    if abs(f["tilt_grados"]) >= 2:
        detalle.append(f"tilt {f['tilt_grados']:+.0f} deg")
    partes.append(f"{mov} [{f['ritmo']}" + (", " + ", ".join(detalle) if detalle else "") + "]")
    h0, h1 = f["altura_camara_m"]
    partes.append(f"altura {h0:g} m" if abs(h0 - h1) < 0.05 else f"altura {h0:g}->{h1:g} m")
    if f["camara_en_mano"]:
        partes.append("handheld shake")
    if f["dof"]:
        partes.append(f"f/{f['dof']['fstop']:g}")
    return " | ".join(partes)


def escribir_md(ruta, datos):
    m = datos["escena"]
    L = ["# Blocking 3D - datos reales de Blender", "",
         f"- Archivo: {m['archivo'] or '(sin guardar)'}  |  Escena: {m['nombre']}",
         f"- Duracion: {m['duracion_s']} s ({m['cuadros']} cuadros a {m['fps']:g} fps)",
         f"- Resolucion: {m['resolucion'][0]}x{m['resolucion'][1]}  |  Aspecto Seedance mas cercano: "
         f"{m['aspecto_seedance']} (desvio {m['aspecto_desvio_pct']} %)",
         f"- Duracion de generacion sugerida: {m['duracion_generacion_s']} s",
         f"- Sujetos seguidos ({datos['sujetos_origen']}): "
         f"{', '.join(datos['sujetos']) or 'ninguno'}  |  Principal: {datos['principal'] or '-'}", ""]
    if datos["avisos"]:
        L.append("## Avisos")
        L += [f"- {a}" for a in datos["avisos"]]
        L.append("")
    L.append("## Cortes")
    if datos["cortes"]:
        L += [f"- {c['t_s']:.2f} s: {c['tipo']} ({c['de']} -> {c['a']})" for c in datos["cortes"]]
    else:
        L.append("- Ninguno: plano secuencia continuo (one unbroken take).")
    L += ["", "## Fases de camara (fuente de verdad para el desglose de tomas)", ""]
    for n, f in enumerate(datos["fases"], 1):
        L.append(f"### Fase {n}{'  (entra por CORTE)' if f['entra_por_corte'] else ''}")
        L.append("- " + linea_fase(f))
        for s in f["sujetos"]:
            if not s.get("visible"):
                L.append(f"  - {s['nombre']}: {s.get('motivo', 'fuera de cuadro')}")
                continue
            plano = s["plano_inicio"] if s["plano_inicio"] == s["plano_fin"] else \
                f"{s['plano_inicio']} -> {s['plano_fin']}"
            cuadro = s["cuadro_inicio"] if s["cuadro_inicio"] == s["cuadro_fin"] else \
                f"{s['cuadro_inicio']} -> {s['cuadro_fin']}"
            extra = ""
            if s.get("diminuto"):
                extra += " | apenas un punto en cuadro"
            if s.get("visible_pct", 100) < 90:
                extra += f" | en cuadro solo el {s['visible_pct']} % de la fase"
            L.append(f"  - {s['nombre']}: {plano} | {cuadro} | a {s['dist_inicio_m']:g}->"
                     f"{s['dist_fin_m']:g} m de camara | {s['accion']}{extra}")
        L.append("")
    L += ["Notas: los tamanos de plano son estimaciones validas para sujetos de escala humana",
          "(para vehiculos o edificios usa la distancia). Los tercios indican el centro del",
          "sujeto, o su cabeza en planos cerrados. Signos: pan + = izquierda, tilt + = arriba,",
          "avance + = hacia delante, lateral + = derecha, vertical + = sube.", ""]
    with open(ruta, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))


def main():
    cfg = leer_argumentos()
    escena = bpy.context.scene
    avisos = []
    cuadro_original = escena.frame_current

    preparado = preparar_render(escena, cfg, avisos) if cfg["preparar"] else []

    sujetos, origen = elegir_sujetos(escena, cfg, avisos)
    cuadros, fps = muestrear(escena, sujetos)
    con_camara = [c for c in cuadros if c["cam"]]
    if not con_camara:
        raise SystemExit("[blocking] ERROR: la escena no tiene camara activa. "
                         "Asigna una camara (Scene > Camera) o marcadores con camara.")

    # Sujeto principal: el indicado, o el de mayor presencia acumulada en cuadro.
    presencia = {o.name: sum(c["suj"].get(o.name, {}).get("area", 0.0) for c in con_camara)
                 for o in sujetos}
    sujetos = sorted(sujetos, key=lambda o: -presencia[o.name])[:12]
    principal = cfg["principal"] if cfg["principal"] in presencia else \
        (sujetos[0].name if sujetos else "")
    if cfg["principal"] and cfg["principal"] not in presencia:
        avisos.append(f"--principal '{cfg['principal']}' no esta entre los sujetos seguidos.")

    cortes = detectar_cortes(cuadros)
    fases = construir_fases(cuadros, fps, cortes, sujetos, principal)

    r = escena.render
    ancho = int(r.resolution_x * r.resolution_percentage / 100)
    alto = int(r.resolution_y * r.resolution_percentage / 100)
    n = len(cuadros)
    duracion = n / fps
    aspecto, desvio = aspecto_mas_cercano(ancho / alto)
    dur_gen = int(min(DUR_MAX, max(DUR_MIN, round(duracion))))

    if duracion < 1.8 or duracion > 30.2:
        avisos.append(f"Duracion {duracion:.2f} s fuera del rango de video de referencia de "
                      "Seedance 2.5 (1.8-30.2 s). Ajusta el rango de cuadros.")
    elif duracion < DUR_MIN:
        avisos.append(f"Duracion {duracion:.2f} s menor que la generacion minima (4 s): "
                      "el modelo tendra que estirar el blocking.")
    if abs(duracion - round(duracion)) > 0.05:
        avisos.append(f"Duracion {duracion:.2f} s no es un numero entero de segundos; Seedance "
                      f"genera en segundos enteros. Ajusta a {round(duracion) * fps:g} cuadros.")
    if abs(fps - 24) > 0.01:
        avisos.append(f"La escena esta a {fps:g} fps. 24 fps es lo recomendado; si lo cambias, "
                      "remapea la animacion para no alterar la duracion.")
    if desvio > 0.02:
        avisos.append(f"El aspecto {ancho}x{alto} ({ancho / alto:.3f}:1) no coincide con ninguno "
                      f"nativo de Seedance 2.5; el mas cercano es {aspecto}. Renderiza el blocking "
                      "en el mismo aspecto que vas a generar para que el encuadre no se recomponga.")
    if r.use_stamp:
        avisos.append("Render > Metadata > Burn Into Image esta activo: el texto quemado se "
                      "filtraria al video final. Desactivalo (o usa --preparar).")
    if any(c["cam"] is None for c in cuadros):
        avisos.append("Hay cuadros sin camara activa.")
    if not sujetos:
        avisos.append("No se detectaron actores. Crea una coleccion ACTORES o usa --objetos.")
    if any(f["dof"] for f in fases):
        avisos.append("La camara tiene profundidad de campo activa. En el blocking conviene "
                      "apagarla (todo nitido) y pedir el desenfoque en el prompt.")

    paso_json = max(1, int(round(fps / 4)))
    datos = {
        "escena": {
            "archivo": bpy.data.filepath, "nombre": escena.name,
            "blender": bpy.app.version_string, "fps": round(fps, 3), "cuadros": n,
            "cuadro_inicio": escena.frame_start, "cuadro_fin": escena.frame_end,
            "duracion_s": round(duracion, 3), "duracion_generacion_s": dur_gen,
            "resolucion": [ancho, alto], "aspecto_seedance": aspecto,
            "aspecto_desvio_pct": round(desvio * 100, 1),
        },
        "preparacion_aplicada": preparado,
        "sujetos": [o.name for o in sujetos], "sujetos_origen": origen,
        "principal": principal,
        "cortes": [{"t_s": round(c["t"], 3), "tipo": c["tipo"], "de": c["de"], "a": c["a"]}
                   for c in cortes],
        "fases": fases,
        "avisos": avisos,
        "muestras": [{
            "t_s": round(c["t"], 2), "camara": c["cam"]["nombre"],
            "pos_m": [round(v, 3) for v in c["cam"]["pos"]],
            "yaw": round(c["cam"]["yaw"], 1), "pitch": round(c["cam"]["pitch"], 1),
            "roll": round(c["cam"]["roll"], 1),
            "lente_mm": round(c["cam"]["lente"], 1) if c["cam"]["lente"] else None,
            "sujetos": {k: {"x": round(v["x"], 3), "y": round(v["y"], 3),
                            "dist_m": round(v["dist"], 2), "visible": v["visible"],
                            "plano": tamano_plano(v["ratio"]) if v["ratio"] else None}
                        for k, v in c["suj"].items() if k in presencia},
        } for c in con_camara[::paso_json]],
    }

    salida = ruta_abs(cfg["salida"])
    os.makedirs(os.path.dirname(salida) or ".", exist_ok=True)
    with open(salida, "w", encoding="utf-8") as fh:
        json.dump(datos, fh, ensure_ascii=False, indent=1)
    ruta_md = os.path.splitext(salida)[0] + ".md"
    escribir_md(ruta_md, datos)
    print(f"[blocking] Datos exportados: {salida}")
    print(f"[blocking] Resumen legible:  {ruta_md}")
    print(f"[blocking] {duracion:.2f} s | {len(cortes)} corte(s) | {len(fases)} fase(s) | "
          f"{len(sujetos)} sujeto(s)")
    for a in avisos:
        print(f"[blocking] AVISO: {a}")

    escena.frame_set(cuadro_original)

    if cfg["render"]:
        destino = ruta_abs(cfg["render"])
        os.makedirs(os.path.dirname(destino) or ".", exist_ok=True)
        configurar_video(escena, destino)
        print(f"[blocking] Renderizando animacion a {destino} ...")
        bpy.ops.render.render(animation=True)
        print(f"[blocking] Render terminado: {destino}")


if __name__ == "__main__":
    main()
