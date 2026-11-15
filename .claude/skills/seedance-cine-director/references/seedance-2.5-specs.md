# Seedance 2.5: límites, modos, etiquetas y generación

Datos comprobados en noviembre de 2026. Los marcados como **catálogo** salen del esquema del
modelo `seedance_2_5` que expone el conector de Higgsfield (fuente primaria). Los marcados
como **guías** salen de documentación de terceros (fal, Dreamina y otras) y pueden variar por
plataforma. Estos productos cambian deprisa: si un dato es decisivo y hay un conector
disponible, consulta el esquema vigente antes de afirmarlo.

Contenido:
1. Parámetros de generación
2. Referencias: cuántas, de qué tipo y con qué límites
3. Etiquetas `@` según la plataforma
4. Longitud del prompt
5. Modos distintos de generar desde cero
6. Diferencias con Seedance 2.0
7. Generar desde un conector (Higgsfield)
8. Fuentes

---

## 1. Parámetros de generación

| Parámetro | Valores | Origen |
|---|---|---|
| Duración | 4 a 30 s, número entero | catálogo |
| Aspect ratio | auto, 21:9, 16:9, 4:3, 1:1, 3:4, 9:16 | catálogo |
| Resolución | 480p, 720p, 1080p, 4k (por defecto 720p) | catálogo |
| Audio | Generación nativa, activada por defecto | catálogo |
| Borrador | 480p, finalizable después a más resolución | catálogo |
| Modos | text-to-video, omni reference, video edit, video extension | catálogo |

Consecuencias prácticas:

- **No existe 2.39:1 nativo.** El formato más cercano es 21:9 (2.33:1). El prompt dice
  `2.39:1 anamorphic widescreen framing` como carácter de imagen y la generación se lanza en
  21:9. Para un 2.39:1 exacto se recorta después un 2 % arriba y abajo.
- **Con referencias, el modo es omni reference.** Text-to-video no las admite.
- **Borrador primero.** Una iteración a 480p o 720p revela si la cámara y la identidad
  funcionan por una fracción del coste; el 1080p o 4K se reserva para la toma buena.

## 2. Referencias

| Tipo | Máximo | Límites por archivo | Origen |
|---|---|---|---|
| Imágenes | 30 (incluidos primer y último fotograma) | hasta 4K | catálogo / guías |
| Videos | 10 | 1.8 a 30.2 s cada uno, hasta 200 MB, MP4 o MOV, 480p a 4K; unos 30 s en total sumando todos | catálogo / guías |
| Audios | 10 | unos 30 s en total; exige al menos una imagen o un video | catálogo / guías |
| Total | 50 archivos | | guías |

- El video de blocking cuenta como una de las diez referencias de video y consume del total
  de ~30 s: un blocking de 30 s no deja sitio para otra referencia de video.
- Que el límite sea 30 imágenes no significa que convenga usarlas. La estabilidad baja con
  cada referencia. Para una toma con blocking: 1 video + 3 a 6 imágenes es el rango sano.
- Una hoja de personaje (varias vistas en una sola imagen) fija mejor la identidad que
  varias fotos sueltas.
- Algunas plataformas rechazan fotos de rostros de personas reales o imágenes con marcas
  registradas. Si una subida falla sin explicación, esa es la primera sospecha.

## 3. Etiquetas `@` según la plataforma

Las referencias se nombran por posición: el número es el orden de subida dentro de su tipo.

| Plataforma | Forma | Cómo se inserta |
|---|---|---|
| API, fal, Higgsfield y la mayoría de integraciones | `@Image1`, `@Video1`, `@Audio1` | Se escribe en el texto; la numeración sigue el orden de la lista enviada |
| Dreamina / Jimeng (interfaz web) | `@Image 1`, `@Video 1` | Se escribe `@` y se elige el archivo en el desplegable |

La sintaxis no está estandarizada entre proveedores. Si el usuario dice qué plataforma usa,
adopta su forma; si no, usa `@Image1` y avísale en las notas de que compruebe cómo aparecen
las etiquetas en su interfaz. Por eso el mapa de referencias describe además cada archivo con
palabras ("the person in @Image1"): si la etiqueta fallara, la descripción sigue orientando
al modelo.

## 4. Longitud del prompt

El tope no es del modelo: lo pone cada plataforma, y las cifras publicadas no coinciden.

| Fuente | Tope que declara |
|---|---|
| Runway (centro de ayuda) y Venice | 15.000 caracteres |
| Varias guías de terceros | 30.000 caracteres |
| Otras guías de terceros | 10.000, 5.000 y hasta 2.000 caracteres |
| Seedance 2.0 | unos 2.500 caracteres |

No hay cifra publicada para Dreamina, Jimeng, Higgsfield ni fal. De ahí los perfiles:

- **COMPLETO, 5.000-10.000.** Cabe en todas las plataformas que declaran 10.000 o más y deja
  margen para que la atención del modelo no se disperse.
- **COMPACTO, 2.500-3.000.** Para Seedance 2.0 y plataformas de tope corto.
- **Tope a medida.** Si la interfaz corta el texto o devuelve un error de longitud, el
  usuario dice la cifra y se valida con `--max`. Un texto truncado pierde el final: las
  últimas tomas y las barreras negativas.

## 5. Modos distintos de generar desde cero

| Modo | Para qué | Qué cambia en el prompt |
|---|---|---|
| Video edit | Corregir una parte de un video ya generado (relight, cambiar un objeto, un tramo de tiempo) | Se describe solo el cambio y se pide conservar todo lo demás; duración y aspecto los fija el video |
| Video extension | Alargar un video hacia delante o hacia atrás | Se describe lo que ocurre en el tramo nuevo, con las mismas anclas de continuidad |

Sirven para rescatar una toma casi buena sin regenerarla entera, y para secuencias de más de
30 s.

## 6. Diferencias con Seedance 2.0

| | Seedance 2.0 | Seedance 2.5 |
|---|---|---|
| Duración | 4-15 s | 4-30 s |
| Referencias | 9 imágenes, 3 videos, 3 audios (12 archivos) | 30 imágenes, 10 videos, 10 audios (50) |
| Video de referencia total | ~15 s | ~30 s |
| Prompt | ~2.500 caracteres | Mucho mayor |
| Blocking 3D | Funciona como referencia de cámara | Flujo de white model documentado por ByteDance |

Para Seedance 2.0: perfil COMPACTO, duración máxima 15 s, y como mucho 9 imágenes.

## 7. Generar desde un conector (Higgsfield)

Solo si el usuario lo pide y hay herramientas `mcp__Higgsfield__*` disponibles. El esquema
puede haber cambiado: confírmalo con `models_explore` (action `get`, model_id
`seedance_2_5`) antes de llamar.

1. **Subir los medios en el orden del manifiesto.** `media_upload` devuelve una URL por
   archivo; se sube con PUT y se confirma con `media_confirm`. Cada archivo queda con un
   `media_id`.
2. **Consultar el coste sin generar.** `generate_video` con `get_cost: true` y los mismos
   parámetros que la generación real.
3. **Enseñar el coste y esperar la aprobación del usuario.** Una generación gasta créditos
   y no se puede deshacer.
4. **Generar.** Parámetros de esta skill:
   - `model`: `seedance_2_5`
   - `mode`: `omni_reference`
   - `duration`: la del blocking
   - `aspect_ratio`: el del blocking
   - `resolution`: `720p` para iterar, o `draft: true` para un borrador a 480p
   - `generate_audio`: `true`
   - `medias`: el blocking con rol `video_references`; cada imagen con rol
     `image_references`, en el orden del manifiesto. Un primer fotograma va con rol
     `start_image`.
   - `prompt`: el prompt validado.
5. **Revisar el borrador** con la tabla de diagnóstico de `blocking-3d.md` antes de pedir la
   versión final.

Si el envío da un error de tiempo de espera, no reenvíes: el trabajo puede haberse creado.
Comprueba su estado primero.

## 8. Fuentes

- Esquema del modelo `seedance_2_5` en el catálogo de Higgsfield (consultado en noviembre de
  2026): modos, duración, resolución, aspect ratios, roles y máximos de medios.
- fal.ai, guía de prompts y documentación de reference-to-video de Seedance 2.5: límites por
  archivo, numeración `@Image1` por orden de lista, necesidad de dar un rol a cada referencia.
- Dreamina (CapCut), guías de Seedance 2.5 sobre white model y 3D blockout: uso del modelo
  blanco para bloqueo espacial, trayectoria de cámara y movimiento de varios personajes.
- seeddance.io, guía de reference-to-video: fórmula `Use @video1 as blocking, camera path,
  and timing only` y aviso sobre la herencia de materiales grises.
- pixo.video, guía de blockout a film: eliminar ejes, líneas de trayectoria y conos de cámara
  antes de subir.
- cozyclay.org, control de cámara en Seedance 2.5: un clip de referencia transmite la cámara
  mejor que una descripción.
- Runway (centro de ayuda, "Creating with Seedance 2.5"), Venice, marketdragon.ph, callirra,
  ezugc, cdance: topes de caracteres del prompt, que difieren entre si.
