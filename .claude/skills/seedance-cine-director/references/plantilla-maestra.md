# Plantilla maestra del prompt

Arquitectura obligatoria. El orden de los bloques y sus títulos no cambian: el usuario los
definió y `scripts/validar_prompt.py` los comprueba. Lo que va entre `<...>` se sustituye; lo
demás se copia tal cual. El prompt final es texto plano, sin markdown ni emojis. Los títulos
van en MAYÚSCULAS y las etiquetas de línea como aparecen aquí, sin tildes (DISEÑO conserva su
letra); lo que tú escribes detrás de cada etiqueta va en español correcto, con tildes y eñes.

Contenido:
1. Plantilla COMPLETA (perfil por defecto, 5.000-10.000 caracteres)
2. Bloque de referencias: las tres variantes
3. Cómo rellenar cada bloque
4. Cómo escribir cada toma del desglose
5. Presupuesto de caracteres
6. Plantilla COMPACTA (2.500-3.000 caracteres)
7. Repaso final

---

## 1. Plantilla COMPLETA

```text
SECUENCIA CINEMATOGRAFICA CONTINUA ESTILO: <GENERO>
cinematic shot, 2.39:1 anamorphic widescreen framing, <N> seconds, <one unbroken take | N shots joined by hard cuts>

MAPA DE REFERENCIAS Y BLOQUEO 3D
<bloque de referencias, sección 2>

ATRIBUTOS DE SIMULACION CENTRAL: Realismo, coherencia visual y peso real de la masa.
Z-depth: <primer término / plano medio / fondo, y qué elemento atmosférico queda DETRÁS del sujeto sin atravesarlo>. Mass inertia: <el cuerpo más pesado y cómo transfiere su energía>. Dynamic reflections: <superficie + fuente de luz en movimiento>. Temporal memory: <3-4 anclas de continuidad> idénticas del segundo 0 al <N>.

ESTETICA VISUAL AVANZADA ESTILO HOLLYWOOD BLOCKBUSTER
ultra-cinematic visuals, low saturation, soft film grain. Shot on anamorphic lens, depth of field, <mm>mm lens for textures, color grading, HDR, high quality 4K.

REGLAS DE CONTINUIDAD Y CONFIGURACION DE CAMARA
Los planos son absolutamente continuos durante los <N> segundos en el espacio y el tiempo: <eje, hora, clima, vestuario y daño acumulado que no cambian>.
Configuracion de camara: texturas de película IMAX MSM 9802 original de 15/70 mm combinada con ARRI Alexa 35 y lente panorámica anamórfica Panavision <serie> personalizada para rodaje en directo. Preservar la delicada textura granulada del celuloide de 35 mm.

ESQUEMA DE ILUMINACION, ATMOSFERA Y PALETA
Paleta de color cinematografica: <tono general y corrección de color>
COLOR GRADE: <solo si el etalonaje es fuerte o estilizado: paleta como material + luz + rol>
Iluminacion: <fuente, dirección, exposición, Kelvin, prácticas, de dónde entra la luz>
Tipo de luz: <difusa, direccional, dura, low key, high key, practical, volumetric fog...>
Matriz de luz y sombra: <ratio de contraste, dónde cae la sombra, qué queda en negro>
Atmosphere and clima: <niebla, lluvia, vapor, humo, ceniza, partículas, polvo, rayos>

DISEÑO DE AUDIO VISCERAL
Efectos de sonido tactiles: <motores, impactos, cristales: sonidos que sugieren peso>
Resonancia de alta/baja frecuencia: <graves que justifican micro-vibración de la óptica>
Contraste emocional: <respiración, jadeo, ladrido frente al caos industrial>
Musica: <ninguna, solo sonido diegético | tipo de partitura y cuándo entra>

NARRATIVA Y TONO EMOCIONAL
Tono: <melancolía, suspenso, euforia contenida...>
Inspiracion de epoca y lenguaje visual: <época + rasgos visibles de ese cine>
Expresion y tension corporal: <arco físico de la emoción: zonas del rostro, grupos musculares, trayecto de la mirada, respiración>

VFX DE TRANSFORMACIONES
<qué se transforma, partes, orden de ensamblaje o mutación, duración, toma en la que ocurre>

PHYSICS
<mass, inertia, contact, fluids, particles: las leyes que gobiernan esta escena>

ESCENARIO
Texturas industriales de primera categoria: <asfalto, titanio, concreto, vegetación...>
Sensacion tactil: <interacciones físicas con el entorno y resistencia de materiales>
Elementos visuales: <objetos concretos presentes + imperfección humana>

FICHAS MECANICAS DE PERSONAJES Y OBJETOS (ASSET SPECS)
Sujeto principal: <NOMBRE (@Image1): edad, procedencia, apariencia, piel con microporos y sudor>
Texturas de vestuario: <materiales, peso, pliegues, comportamiento bajo lluvia o viento>
Automoviles / Vehiculos: <modelo, escala, masa, luces, presencia física>
Personajes extras: <tipo, piel, temperamento y acción de los secundarios>
Dialogos, estilo de voz, acento y emocion: <reglas de ejecución vocal; las líneas van en su toma>
Bloqueo de personaje: <NOMBRE = @Image1; ESCENARIO = @Image2; VEHICULO = @Image3>

DESGLOSE DE SECUENCIA CONTINUA DE <N> SEGUNDOS

0s-3s | TOMA 1: <SUB-FASE O DINAMICA FISICA> | CONTINUO
Blocking: sigue @Video1 0s-3s: <qué muestra ese tramo del blocking>
Direccion: <forma de dirigir esta toma, sin nombres>
Toma y composicion: <tamaño de plano, ángulo, tercios, primer término, flares o bokeh>
Lentes, optica y apertura: <serie anamórfica, mm, número f, profundidad de campo>
Camara: <técnica, trayectoria, velocidad, sensación>
Accion: <cadena física acción -> reacción del sujeto con suelo, aire y objetos>
Comportamiento humano: <parpadeo, jadeo, manos, forma de caminar, reacciones>
Expresion y tono: <músculos del rostro y cambio de tensión en esta toma>
Dialogo: <PERSONAJE (tipo de voz, emoción): "línea exacta" | ninguno>

<siguiente toma...>

BARRERAS NEGATIVAS
Sin CGI evidente, sin física caricaturesca de videojuego, sin movimientos flotantes sin gravedad, sin glitches visuales, sin transiciones de desvanecimiento, sin cambios espontáneos de ropa o fisonomía, <riesgos propios de esta escena>, sin subtítulos, sin texto en pantalla, sin marcas de agua.
```

---

## 2. Bloque de referencias: las tres variantes

Va arriba porque es lo que el modelo más necesita obedecer, y en inglés porque estas fórmulas
son las documentadas y probadas. Adapta los nombres; conserva los verbos de control.

### A. Con blocking 3D e imágenes (el caso principal)

```text
MAPA DE REFERENCIAS Y BLOQUEO 3D
Use @Video1 as blocking, camera path and timing only: copy its framing, shot sizes, camera height, camera trajectory and speed, subject positions, screen direction, movement paths and the exact timing of every beat and cut. @Video1 is an untextured grey 3D previz made of placeholder geometry: never render grey clay, flat shading, mannequins, primitive shapes, guide lines or its lighting. Replace every proxy with the photoreal asset mapped here.
Proxy map: <the tall mannequin walking toward camera at frame centre> = <NOMBRE>, the person in @Image1. <the darker mannequin running behind> = <NOMBRE 2>, the person in @Image2. <the box vehicle arriving in the background> = the vehicle in @Image4. <the grey street and plaza> = the location in @Image3.
@Image1: identity lock for <NOMBRE> (face, hair, build, wardrobe). Appearance only, not pose or framing.
@Image2: identity lock for <NOMBRE 2>. Appearance only.
@Image3: location look (architecture, materials, palette). Appearance only; composition comes from @Video1.
@Image4: vehicle design (body, livery, lights). Appearance only.
Priority: @Video1 decides where everything is and how the camera moves; the images decide what everything looks like; this text decides light, materials, physics, performance and sound.
```

Cuatro piezas, ninguna sobra:

- **Alcance** (`blocking, camera path and timing only` + la lista de lo que se copia). Un
  "use @Video1 as reference" a secas es demasiado vago y el modelo decide por su cuenta que
  tomar.
- **Anti-fuga** (`untextured grey 3D previz ... never render grey clay`). Sin ella el
  resultado hereda materiales grises o formas de maqueta.
- **Mapa de proxies**. El modelo no sabe qué cápsula es qué personaje. Describe cada proxy
  por posición, tamaño y acción visibles en el video. Si dos proxies se parecen, añade por
  dónde entran o qué hacen primero.
- **Prioridad**. Resuelve de antemano cualquier choque entre video, imágenes y texto.

### B. Solo imágenes (sin blocking)

```text
MAPA DE REFERENCIAS
@Image1: identity lock for <NOMBRE> (face, hair, build, wardrobe). Appearance only, not pose or framing.
@Image2: location look (architecture, materials, palette). Appearance only.
@Image3: prop design for <OBJETO>. Appearance only.
Priority: the images decide what everything looks like; this text decides camera, light, physics, performance and sound.
```

Sin blocking, la cámara la decide el texto: aquí las líneas de cámara del desglose cargan
todo el peso y deben ser precisas (técnica, dirección, velocidad, altura).

### C. Sin referencias (text-to-video)

Se omite el bloque entero. La identidad del personaje descansa en la ficha de assets, así que
describe 4-5 rasgos fijos y repite el nombre del personaje en cada toma.

### Casos particulares

- **Primer fotograma.** Si el usuario aporta un fotograma inicial, se sube como imagen de
  inicio y debe coincidir con el encuadre del segundo 0 del blocking; si no coincide, se
  pelean. Añade: `@Image1 is the first frame.` y quítale cualquier otro rol.
- **Audio de referencia.** `@Audio1 defines <NOMBRE>'s voice` o `@Audio1 is the music bed`.
  Un rol, igual que el resto. Un audio de referencia necesita al menos una imagen o video.
- **Blocking con color o textura.** Si el previz no es gris, cambia la anti-fuga por lo que
  sí quieres conservar: `@Video1 is a rough previz: keep its layout and camera, discard its
  materials, colours and lighting.`

---

## 3. Cómo rellenar cada bloque

**Cabecera.** Género en una palabra o dos. `2.39:1 anamorphic widescreen framing` cuando se
genera en 21:9, que es el formato nativo más cercano. Escribe `letterbox` solo si el usuario
quiere barras negras dentro de un cuadro 16:9: esa palabra hace que el modelo las pinte. La
segunda línea dice si es plano secuencia o cuántos planos unidos por corte; con blocking, lo
que diga el blocking.

**Atributos de simulación central.** Son las cuatro capacidades que el flujo le exige al
motor, convertidas en algo comprobable en esta escena concreta. No copies definiciones:
nombra qué capa de profundidad contiene qué, qué cuerpo pesa, qué superficie refleja qué luz
y qué tres o cuatro detalles deben llegar intactos al último segundo.

**Estética visual.** La línea es fija; solo cambia el milimetraje del lente de texturas.

**Continuidad y cámara.** La frase de continuidad se concreta: qué no cambia. La
configuración de cámara es fija; cambia la serie Panavision (C-series para flares azules
clásicos y caída suave en los bordes, E-series más nítida, G-series compacta y moderna,
T-series limpia y de alto contraste, Primo anamorphic para nitidez neutra).

**Iluminación.** Es el bloque que más pesa en el realismo. Siempre: de dónde viene la luz
(ventana, cielo, farola, pantalla), en que dirección golpea al sujeto, y su temperatura en
Kelvin. Tabla de temperaturas en `direccion-optica-fisica.md`. `COLOR GRADE` solo cuando el
etalonaje es protagonista; en looks naturalistas se borra la línea y el color vive en
`Iluminacion`.

**Audio.** Seedance 2.5 genera audio nativo, así que este bloque produce sonido real y,
además, empuja a la imagen a reaccionar: un impacto de 40 Hz justifica la micro-vibración del
lente. Describe frecuencia, material y distancia. Decide la música: si no dices nada, el
modelo improvisa una.

**Narrativa y tono.** Nunca se cuenta la emoción: se muestra. `Expresion y tension corporal`
describe el arco completo de la secuencia (de que estado a que estado); cada toma detalla su
parte. En `Inspiracion` describe la época y sus rasgos visibles (grano, óptica, paleta,
forma de mover la cámara). Si el usuario nombra películas, tradúcelas a esos rasgos: el
modelo responde a lo visible, y los títulos de franquicias pueden activar filtros.

**VFX de transformaciones.** Solo si hay transformación, ensamblaje o mutación. Si no la hay,
el bloque se elimina entero con su título.

**Physics.** Las leyes de esta escena en una o dos líneas: qué masa domina, cómo se frena,
qué hace el fluido o la partícula al contacto.

**Escenario.** Materiales con nombre, no "calle urbana". Aquí entra la imperfección humana:
suciedad, desgaste, un objeto cotidiano fuera de sitio.

**Fichas de assets.** Cada personaje u objeto con su etiqueta entre paréntesis la primera vez.
Para que la identidad no derive, fija 3-4 rasgos invariables. `Bloqueo de personaje` es el
resumen de qué imagen fija a quién; debe coincidir con el mapa de referencias. En `Dialogos`
van las reglas de voz (timbre, acento, intensidad), no las líneas.

**Barreras negativas.** Lista corta y concreta. Seedance no tiene campo de prompt negativo,
así que las restricciones viajan en el texto: funcionan mejor pocas y específicas que muchas
y genéricas. Añade las propias de la escena (por ejemplo `sin maniquies ni geometria gris`
cuando hay blocking) y cierra siempre con subtítulos, texto en pantalla y marcas de agua.

---

## 4. Cómo escribir cada toma del desglose

**Cabecera.** `<inicio>s-<fin>s | TOMA n: <NOMBRE DE LA SUB-FASE> | <CONTINUO | HARD CUT>`

- Los tiempos empiezan en 0, no dejan huecos ni se solapan y terminan en la duración exacta.
- Una toma por fase de acción, de 2 a 5 segundos: 4 o 5 tomas en 15 s, 6 a 8 en 30 s. Menos
  de 1 s el modelo no lo resuelve. Si un mismo plano de cámara dura 5 s y la acción evoluciona
  dentro, se queda en una toma y la evolución se escribe con su segundo
  (`desde el segundo 9 la zancada se acorta`).
- `HARD CUT` solo donde el blocking corta, en ese segundo. Dentro de un mismo plano de cámara,
  `CONTINUO`. En un plano secuencia todas son `CONTINUO`.
- El nombre de la sub-fase es la dinámica física: COMPRESION, PERSECUCION, FRENADA, REVELACION.

**Blocking.** Solo con blocking. Ancla la toma a su tramo del video y resume lo que ese tramo
muestra, con los datos de la bitácora: `sigue @Video1 6s-11s: low-angle lateral tracking,
camera 0.9 m high travelling right at 4 m/s, subject full shot at frame centre`.

**Dirección.** La forma de dirigir de esta toma en una línea, sin nombres propios. Sale de
`direccion-optica-fisica.md`. Dos gramáticas por secuencia como mucho, salvo que el usuario
pida más: cambiar de estilo en cada toma rompe la unidad.

**Toma y composición.** Tamaño de plano, ángulo, dónde cae el sujeto en los tercios, qué hay
en primer término, flares o bokeh. Con blocking, tamaño y posición salen de la bitácora.

**Lentes, óptica y apertura.** Serie, milimetraje, número f y lo que eso deja nítido. La
apertura es la herramienta para obligar al modelo a separar planos: f/5.6-f/8 mantiene
legible el peligro del fondo, f/2-f/2.8 aisla al personaje.

**Cámara.** Técnica, trayectoria, velocidad y sensación. Con blocking esta línea confirma lo
que hace el video y añade lo que el gris no lleva: peso de cámara en mano, respiración del
operador, vibración por impacto, cambio de foco. Sin blocking es la única fuente y debe ser
completa.

**Acción.** Cadena acción -> reacción con masa: `compresión -> carga -> liberación ->
transferencia -> asentamiento`. Qué toca qué, qué cede, qué sale despedido.

**Comportamiento humano y Expresión.** Lo pequeño y concreto: parpadeo, jadeo, dedos, forma
de pisar. En `Expresion`, las zonas del rostro y los músculos que cambian *en esta toma*
respecto a la anterior.

**Diálogo.** `NOMBRE (voz grave, susurro tenso): "linea"`. Líneas cortas: unas 2.5 palabras
por segundo de toma. Si hay dos personajes en cuadro, di quién habla y quién mantiene la boca
cerrada. Sin diálogo: `ninguno` y, si procede, qué sonido humano hay.

---

## 5. Presupuesto de caracteres

La plantilla completa desborda los 10.000 caracteres si cada línea se escribe a gusto. Este
reparto cabe con cuatro imágenes y cuatro tomas; con cinco tomas, cada una baja a unos 720.

| Bloque | Caracteres |
|---|---|
| Cabecera | 180 |
| Mapa de referencias y bloqueo 3D | 1.500 |
| Atributos de simulación central | 500 |
| Estética + continuidad y cámara | 700 |
| Iluminación, atmósfera y paleta | 750 |
| Audio | 450 |
| Narrativa y tono | 450 |
| Physics + escenario | 650 |
| Fichas de assets | 800 |
| Desglose: 4 tomas x 900 | 3.600 |
| Barreras negativas | 350 |

Dónde se recorta cuando sobra, por este orden: adjetivos; datos repetidos entre la línea
`Blocking` y las de composición y cámara (lo que ya dice el blocking no se repite); terceros
ejemplos de una lista; detalles de escenario que no salen en cuadro. Lo que no se recorta: el
mapa de referencias, las cifras de cámara y las cadenas de acción.

---

## 6. Plantilla COMPACTA

Para Seedance 2.0, plataformas con tope de ~3.000 caracteres o cuando el usuario la pida.
Mismos contenidos, fusionados. Una línea por toma.

```text
SECUENCIA CINEMATOGRAFICA CONTINUA ESTILO: <GENERO>. cinematic shot, 2.39:1 anamorphic widescreen framing, <N> seconds, <take>.

MAPA DE REFERENCIAS
Use @Video1 as blocking, camera path and timing only: copy framing, camera trajectory, subject positions and the timing of every cut. It is an untextured grey previz: replace every proxy, never render grey clay or primitives. <proxy> = @Image1 <NOMBRE>; <proxy> = @Image2. Images are appearance only.

CAMARA Y ESTETICA
IMAX 15/70 mm + ARRI Alexa 35, Panavision <serie> anamorphic, grano de celuloide 35 mm, low saturation, HDR. Realismo, coherencia visual y peso real de la masa. Continuidad absoluta de <anclas>.

LUZ Y ATMOSFERA
<fuente + dirección + Kelvin. Contraste. Volumétricos. Paleta.>

AUDIO
<táctiles + graves + contraste orgánico. Música si/no.>

ASSETS
<NOMBRE (@Image1): 3-4 rasgos fijos, vestuario. VEHICULO (@Image3): masa, luces. ESCENARIO (@Image2): materiales.>

DESGLOSE
0s-3s | TOMA 1 <FASE> | @Video1 0s-3s | CONTINUO: <plano, mm, f/>. Cámara: <...>. Acción: <cadena física>. Gesto: <micro-expresión>. Diálogo: <...>.
3s-6s | TOMA 2 <FASE> | @Video1 3s-6s | HARD CUT: <...>

BARRERAS NEGATIVAS
Sin CGI evidente, sin física de videojuego, sin flotación, sin glitches, sin fundidos, sin cambios de ropa o fisonomía, sin geometría gris, sin subtítulos, sin texto en pantalla, sin marcas de agua.
```

Para caber: una sola gramática de dirección, 4-5 tomas como máximo, y los bloques globales
reducidos a datos. Lo último que se recorta es el mapa de referencias y la línea de cámara.

---

## 7. Repaso final

Antes de pasar el validador, relee como si fueras el modelo:

- ¿Cada archivo que se sube tiene su rol en el mapa? ¿Y cada etiqueta citada existe?
- Con blocking: ¿alguna línea de cámara pide algo que el video no hace?
- ¿Las fronteras de las tomas caen en los cortes del blocking?
- ¿Hay alguna emoción nombrada en vez de mostrada?
- ¿Queda algún `<...>` sin rellenar, algún nombre de director o algún adjetivo vacío?
- ¿El diálogo cabe en su toma y solo aparece ahí?
