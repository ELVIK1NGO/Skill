# Blocking 3D: del render de Blender al video final

El blocking es un render gris y tosco de la escena con la cámara ya animada. Seedance 2.5 lo
recibe como video de referencia (lo que ByteDance llama *white model*) y copia de él la puesta
en escena y la cámara, mientras las imágenes de assets aportan la identidad y el texto la luz,
la física y el sonido. Un clip de referencia transmite un movimiento de cámara mucho mejor
que cualquier descripción: el modelo imita lo que ve, y una misma frase de cámara puede dar
ángulos distintos en cada intento.

Contenido:
1. Preparar el render en Blender (lo que el usuario debe hacer)
2. Exportar los datos reales de la cámara
3. Leer el blocking y montar la bitácora de planos
4. Enlazar el blocking en el prompt
5. Planos secuencia, cortes y secuencias largas
6. Tabla de diagnóstico: síntoma -> causa -> corrección

---

## 1. Preparar el render en Blender

Lista para darle al usuario cuando pregunte cómo exportar, o cuando el análisis encuentre un
problema. Cada punto existe porque el modelo copia lo que ve.

| Ajuste | Valor | Por que |
|---|---|---|
| Duración | Igual a la del video final, en segundos enteros, entre 4 y 30 | El modelo reparte el blocking sobre la duración pedida; si no coinciden, el ritmo se estira o se comprime |
| Cadencia | 24 fps | Es la cadencia del resultado; el timing queda 1:1 |
| Aspecto | El mismo que se va a generar (21:9 -> 1680x720 o 2520x1080; 16:9 -> 1280x720) | Si difiere, el modelo recompone el encuadre |
| Resolución | 720p basta; mínimo 480p | La referencia solo tiene que leerse, no lucir |
| Motor | Workbench (o Viewport Render con overlays apagados) | Rápido y neutro |
| Materiales | Blanco o gris neutro, sin texturas | Para que el modelo no copie un look |
| Luz | Estudio suave con sombras y cavidad activadas | La sombra de contacto y la oclusión le dicen al modelo la profundidad y dónde pisa cada cosa |
| Overlays | Todo fuera: ejes, rejilla, gizmos, conos de cámara, líneas de trayectoria, huesos, nombres | Cualquier línea de guía puede aparecer en el video final |
| Metadatos | Render > Metadata > Burn Into Image apagado | El texto quemado se copia |
| Barras | Sin letterbox quemado; cuadro completo | El modelo pintaría las barras |
| Profundidad de campo | Apagada | El blocking debe leerse nítido; el desenfoque se pide en el texto |
| Audio | Sin pista de audio | Puede contaminar el audio generado |
| Formato | MP4 H.264 (o MOV), menos de 200 MB | Límites de Seedance 2.5 |

Sobre la geometría:

- **Personajes: maniquíes con cabeza, torso y extremidades**, no cubos. La pose y el gesto se
  leen mucho mejor. Si la actuación corporal importa (correr, caer, girar), anima el
  maniquí aunque sea tosco: un proxy que se desliza rígido produce un personaje que patina.
- **Escala real en metros.** Un proxy de 1.80 m junto a un vehículo de 4.5 m: la relación de
  tamaños es parte de lo que se copia.
- **Entorno: cajas y planos** bastan para edificios, paredes y suelo. Un suelo siempre, para
  que haya sombra de contacto.
- **Cámara: la definitiva**, con su distancia focal real y curvas suaves. El modelo copia
  también los errores: una cámara que tiembla en el blocking tiembla en el resultado, y una
  que atraviesa una pared produce un fogonazo que se lee como corte.
- **Distinguir proxies.** Darles tonos de gris distintos ayuda a quien lee el blocking, pero
  Seedance no interpreta códigos de color de forma fiable: en el prompt cada proxy se
  identifica siempre por posición, tamaño y acción.

## 2. Exportar los datos reales de la cámara

`scripts/blender_exportar_blocking.py` se ejecuta dentro de Blender y escribe
`blocking_data.json` y `blocking_data.md`: por cada fase de cámara, el lente en mm, la altura,
los metros recorridos en cada eje, la velocidad, los cortes, y para cada actor su tamaño de
plano, su posición en tercios, su distancia a cámara y su recorrido. Detecta también si un
actor está oculto tras el decorado.

Dos formas de usarlo:

- **Interfaz:** pestaña Scripting -> Open -> el archivo -> Run Script. Los archivos aparecen
  junto al `.blend`.
- **Terminal**, que además puede dejar el render listo y lanzarlo:
  ```bash
  blender -b escena.blend -P blender_exportar_blocking.py -- \
      --salida blocking_data.json --preparar --aspecto 21:9 --alto 720 --render blocking.mp4
  ```
  `--preparar` aplica la tabla de la sección 1 (motor, sombreado, metadatos, resolución) sin
  tocar los fps ni la animación.

Convención que conviene pedir al usuario: una colección llamada `ACTORES` con personajes y
vehículos, nombrados por su rol (`HEROE`, `VILLANO`, `AUTO_PATRULLA`). Esos nombres salen en
el informe y hacen trivial el mapa de proxies. Sin esa colección, el script sigue lo que se
mueve.

Cuando existen estos datos, mandan sobre cualquier estimación visual: el milimetraje del
prompt es el de Blender y los metros y velocidades se pueden citar tal cual.

## 3. Leer el blocking y montar la bitácora de planos

`scripts/analizar_blocking.py video.mp4` entrega un informe y hojas de contacto. Cada
miniatura lleva su segundo exacto; las líneas amarillas son la cuadrícula de tercios que añade
el script; la barra roja marca el primer cuadro tras un corte.

Recorre las hojas en orden y rellena una fila por tramo:

| Tramo | Corte | Tamaño de plano | Cámara: altura, ángulo, movimiento, velocidad | Sujetos: proxy -> tercio -> recorrido |
|---|---|---|---|---|

Cómo deducir el movimiento comparando miniaturas consecutivas:

| Lo que ves | Lo que hace la cámara |
|---|---|
| Todo el cuadro se desplaza a la vez, cerca y lejos por igual | Paneo (pan) o inclinación (tilt): la cámara gira sin moverse |
| El primer término se desplaza mucho más que el fondo | Travelling lateral (truck) o grúa: la cámara se traslada. Ese paralaje es la señal |
| El centro crece y los bordes se van hacia fuera, con cambio de paralaje | Dolly in (push-in). Al revés, dolly out |
| El encuadre se cierra sin que cambie la relación entre primer término y fondo | Zoom óptico, no dolly |
| El sujeto mantiene tamaño y posición mientras el fondo corre | Tracking: la cámara viaja con el sujeto |
| El fondo gira alrededor de un sujeto que queda centrado | Orbita (arc) |
| El horizonte sube en cuadro | La cámara baja o se inclina hacia abajo. Si baja, el suelo cercano se aplana |
| El sujeto crece y el fondo se ensancha a la vez | Dolly zoom |
| Saltos pequeños e irregulares entre cuadros | Cámara en mano |

Altura y ángulo de cámara: mira dónde queda la línea del horizonte respecto al sujeto. Si
corta al personaje por los ojos, cámara a la altura de los ojos (~1.6 m); por la cintura o
más abajo, contrapicado (low angle); por encima de la cabeza, picado (high angle).

El script no intenta adivinar el movimiento de cámara: en un render gris y plano las
estimaciones automáticas fallan más de lo que ayudan. Lo que decide es lo que ves en las
hojas. Si un movimiento es sutil y dudas, pide más miniaturas con
`--cuadros-por-segundo 4`, o los datos de Blender.

Si no puedes ver el video ni ejecutar scripts, pide los datos de Blender o esta misma tabla
rellenada por el usuario. No inventes la cámara.

## 4. Enlazar el blocking en el prompt

Tres lugares, los tres necesarios:

1. **Mapa de referencias** (arriba del prompt): alcance, anti-fuga, mapa de proxies y
   prioridad. Las fórmulas están en `plantilla-maestra.md`, sección 2.
2. **Cada toma del desglose**: línea `Blocking: sigue @Video1 <tramo>: <lo que muestra>`. Con
   los tiempos idénticos a los del video.
3. **Barreras negativas**: `sin maniquies, sin geometria gris, sin sombreado plano`.

Y dos ajustes fuera del prompt, en la ficha de generación: duración igual a la del blocking y
el mismo aspect ratio.

Lo que el texto añade encima del blocking, porque un render gris no puede llevarlo:

- Carácter óptico: flares anamórficos, respiración del foco, distorsión de barril, bokeh oval.
- Profundidad de campo y cambios de foco (`rack focus from the hand to the face at 7s`).
- Textura del movimiento: peso de cámara en mano, micro-vibración por un impacto.
- Todo lo físico y vivo: pelo, tela, polvo, agua, respiración, micro-expresión.

Lo que el texto no debe hacer: nombrar un movimiento, un tamaño de plano o un corte distinto
al del video. Ante la duda sobre lo que hace el blocking en un tramo, escribe menos cámara y
deja que mande la referencia (`Camara: sigue exactamente la trayectoria de @Video1`).

## 5. Planos secuencia, cortes y secuencias largas

- **Plano secuencia** (sin cortes en el blocking): cabecera `one unbroken take, no cuts`,
  todas las tomas `CONTINUO`, y en barreras negativas `sin cortes ni cambios de plano`. Las
  "tomas" del desglose son fases de tiempo dentro del mismo plano.
- **Varios planos**: cabecera `<N> shots joined by hard cuts`. La toma que entra por corte
  lleva `HARD CUT` y empieza en el segundo exacto del corte. Entre planos, lo que da
  continuidad es un ancla repetida: el mismo vestuario, la misma herida, el mismo sonido que
  atraviesa el corte.
- **Planos muy cortos**: menos de 1 s no se resuelven. Si el blocking tiene un plano de medio
  segundo, sugiere alargarlo o fundirlo con el vecino.
- **Secuencias de más de 30 s**: se parten en generaciones de 4-30 s por los cortes del
  blocking. Cada parte lleva su propio video de blocking, las mismas imágenes de assets en el
  mismo orden y los mismos bloques globales. Para empalmar, el último fotograma de una parte
  puede entrar como primer fotograma de la siguiente.

## 6. Tabla de diagnóstico

Se generan primero borradores baratos (480p o 720p) y se revisa en este orden: cámara,
identidad, look, timing, física. Se corrige una sola cosa por iteración.

| Síntoma en el video | Causa probable | Corrección |
|---|---|---|
| Sale gris, de plástico, con maniquíes o cajas | Falta o es débil la anti-fuga; no hay imagen de look | Reforzar `never render grey clay, mannequins or primitives`; añadir imagen del escenario; añadir la barrera negativa |
| La cámara no sigue al blocking | El texto describe otra cámara, o el rol de @Video1 es vago | Quitar del texto todo movimiento que no este en el video; usar la fórmula `blocking, camera path and timing only` |
| Sigue la cámara pero cambia el encuadre | Aspect ratio distinto entre blocking y generación | Igualar el aspect ratio o re-renderizar el blocking |
| El timing se adelanta o se atrasa | Duración de generación distinta a la del blocking | Igualar la duración; blocking en segundos enteros |
| Aparecen líneas, ejes, texto o iconos | Overlays o metadatos en el render | Re-renderizar limpio (sección 1) |
| Aparecen barras negras | Letterbox quemado en el blocking o la palabra `letterbox` en el prompt | Render a cuadro completo; usar `anamorphic widescreen framing` |
| El personaje no se parece a su imagen | Demasiadas referencias, o la imagen es pequeña, oscura o con varias personas | Menos referencias; imagen limpia, frontal, bien iluminada, de una sola persona; fijar 3-4 rasgos en la ficha |
| Los personajes se intercambian | Mapa de proxies ambiguo | Describir cada proxy por dónde entra y qué hace; diferenciar tamaños en el blocking |
| El personaje toma la pose o el fondo de su imagen | La imagen no tiene `Appearance only` | Añadir `Appearance only, not pose or framing`; usar una imagen sobre fondo neutro |
| El personaje patina o flota | El proxy se desliza sin animación | Animar el maniquí; reforzar contacto en `Accion` y `PHYSICS` (peso, talón, polvo) |
| Aparecen cortes que no existen | El desglose se lee como planos distintos | Cabecera `one unbroken take`; tomas `CONTINUO`; barrera `sin cortes` |
| Faltan los cortes del blocking | No están marcados en el texto | `HARD CUT` en la cabecera de la toma, en el segundo exacto |
| Un fogonazo o cambio brusco a mitad de plano | La cámara del blocking atraviesa geometría | Corregir la trayectoria en Blender |
| Ropa o rasgos cambian a mitad | Sin anclas de continuidad | Nombrar las anclas en `Temporal memory` y en la ficha |
| Labios desincronizados o habla acelerada | Demasiado diálogo para la toma | Acortar o repartir entre tomas; ~2.5 palabras por segundo |
| Sale texto o subtítulos | Comillas fuera del diálogo, o falta la barrera | Comillas solo en `Dialogo`; `sin subtitulos, sin texto en pantalla` |
| Música que nadie pidió | El bloque de audio no decide la música | `Musica: ninguna, solo sonido diegetico` |
| La plataforma rechaza una imagen | Filtro de rostros reales o de marcas | Usar un personaje generado o ilustrado; quitar logotipos |
| El modelo ignora instrucciones del texto | Prompt demasiado largo o redundante, o mezcla de idiomas mal leída | Recortar repeticiones; probar la versión íntegra en inglés |
