# Cine-Director 2.5 · skill de prompts para Seedance 2.5

Skill para Claude que convierte una idea en un prompt de producción para **Seedance 2.5**, con
soporte para **blocking 3D de Blender** como referencia de cámara, puesta en escena y timing,
combinado con imágenes de personajes, escenarios, vehículos y objetos.

## Qué hace

1. **Lee tu blocking.** Valida el video contra los límites de Seedance 2.5, detecta los
   cortes y genera hojas de contacto con el segundo de cada cuadro para leer qué hace la
   cámara. Si exportas los datos desde Blender, usa las cifras exactas: lente, altura, metros,
   velocidad, tamaño de plano.
2. **Reparte el control.** El blocking decide dónde y cuándo; las imágenes, quién y qué; el
   texto, cómo. Cada archivo recibe un rol único y un orden de subida.
3. **Escribe el prompt** con tu plantilla de bloques: referencias, simulación, estética,
   cámara, iluminación, audio, narrativa, física, escenario, fichas de assets, desglose de
   tomas por segundos y barreras negativas. Sin nombres de directores: su forma de dirigir se
   traduce a lenguaje de cámara.
4. **Lo valida** antes de entregarlo: longitud, bloques, etiquetas, cortes, diálogo.

## Cómo usarla

**En Claude Code** (incluida la versión web): abre una sesión en este repositorio. La skill
se carga sola desde `.claude/skills/`. Escribe `/seedance-cine-director` o describe tu escena.

**En claude.ai o la app de escritorio:** instala `dist/seedance-cine-director.skill` desde
Ajustes > Capacidades > Skills.

Ejemplo de encargo:

> Tengo el blocking de 15 segundos en `blocking.mp4` y cuatro imágenes: la protagonista, el
> villano, la ciudad y la patrulla. Es una persecución nocturna con lluvia. Hazme el prompt.

Recibes la ficha de generación, el orden de subida, la lectura del blocking para que la
confirmes, el prompt listo para pegar y unas notas de dirección.

## Preparar el blocking en Blender

Reglas cortas (la tabla completa está en `references/blocking-3d.md`):

- Misma duración y mismo aspecto que el video final. 24 fps. Entre 4 y 30 segundos enteros.
- Modelo blanco: sin texturas, sin ejes, sin rejilla, sin texto quemado, sin barras negras.
- Maniquíes para los personajes, cajas para el entorno, escala real en metros.
- MP4 H.264 a 720p, sin audio.

El script `scripts/blender_exportar_blocking.py` exporta los datos reales de la cámara y
puede dejar el render listo:

```bash
blender -b escena.blend -P blender_exportar_blocking.py -- \
    --salida blocking_data.json --preparar --aspecto 21:9 --alto 720 --render blocking.mp4
```

También funciona desde la pestaña Scripting de Blender (Open > Run Script). Pon personajes y
vehículos en una colección llamada `ACTORES` y nómbralos por su rol.

## Requisitos

- `ffmpeg` y `ffprobe` para analizar el video.
- Python 3 con `pillow` y `numpy` para las hojas de contacto y la detección de cortes.
- Blender 3.6 o superior para el exportador (probado en 5.3).

## Contenido

```
.claude/skills/seedance-cine-director/
├── SKILL.md                              flujo de trabajo
├── references/
│   ├── plantilla-maestra.md              arquitectura obligatoria del prompt
│   ├── blocking-3d.md                    preparar, leer y enlazar el blocking; diagnóstico
│   ├── direccion-optica-fisica.md        formas de dirigir, lentes, física, micro-expresión
│   ├── seedance-2.5-specs.md             límites, modos, etiquetas, generación por conector
│   └── ejemplo-completo.md               una entrega terminada
├── scripts/
│   ├── analizar_blocking.py              valida el video y genera hojas de contacto
│   ├── blender_exportar_blocking.py      exporta datos de cámara desde Blender
│   └── validar_prompt.py                 control de calidad del prompt
└── evals/                                tres casos de prueba
dist/seedance-cine-director.skill         paquete instalable
```

Para regenerar el paquete después de editar la skill, pídele a Claude que la vuelva a
empaquetar con skill-creator.
