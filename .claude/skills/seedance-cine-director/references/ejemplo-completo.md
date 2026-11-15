# Ejemplo completo: de un blocking de tres planos a la entrega

Un caso real resuelto con esta skill, de principio a fin. El blocking se construyó y se
renderizó en Blender con `blender_exportar_blocking.py --preparar`, y el prompt pasó el
validador. Sirve para ver el nivel de detalle esperado y el formato exacto de la entrega.
Al final hay un segundo ejemplo en perfil COMPACTO.

---

## El encargo

> Tengo el blocking en Blender de una escena de 15 segundos (`blocking_plaza.mp4`) y quiero
> usarlo como referencia de cámara en Seedance 2.5. Es una persecución nocturna con lluvia en
> una ciudad futurista: Mara, una mensajera de unos 30 años, camina por un callejón hacia la
> plaza, la descubren y echa a correr; al final se detiene sin aliento y una patrulla
> blindada frena detrás de ella. Voy a subir además 4 imágenes: `mara_ref.png` (ella,
> chaqueta roja impermeable, cicatriz en la ceja), `cazador_ref.png` (el que la persigue,
> armadura negra mate), `ciudad_ref.png` (el escenario, neones y hormigón mojado) y
> `patrulla_ref.png` (el vehículo). Al final ella susurra "Ya no corro más".

## Lo que se hizo antes de escribir

1. `python3 scripts/analizar_blocking.py blocking_plaza.mp4` -> 15.0 s, 24 fps, 1260x540,
   aspecto 21:9, sin errores, cortes en 6.00 s y 11.00 s, tres hojas de contacto.
2. Se abrieron las tres hojas. Sin ejes, sin texto, sin barras: blocking limpio.
3. El usuario aportó además `blocking_data.md`, exportado desde Blender, con las cifras
   exactas: 28 mm, 40 mm y 85 mm; alturas de cámara; metros recorridos; velocidades.
4. Decisiones de dirección: la amenaza crece en el fondo durante el primer plano, así que
   f/8 y f/5.6 para mantenerla legible; el cierre aísla el rostro a f/2.8. Realismo físico
   de gran formato para la persecución y asombro coreografiado para el cierre.
5. `python3 scripts/validar_prompt.py prompt.txt --duracion 15 --aspecto 21:9 --imagenes 4
   --videos 1 --blocking --cortes 6,11` -> `RESULTADO: APTO | 9976 caracteres`.

---

## La entrega

### FICHA DE GENERACIÓN

| Parámetro | Valor |
|---|---|
| Modelo | Seedance 2.5 |
| Modo | Omni reference |
| Duración | 15 s (la del blocking) |
| Aspect ratio | 21:9 (el del blocking) |
| Resolución | Borrador a 480p o 720p; toma final a 1080p |
| Audio | Activado |

### ORDEN DE SUBIDA

El número de cada etiqueta lo fija el orden de subida. Respeta este orden.

| Etiqueta | Archivo | Rol único |
|---|---|---|
| @Video1 | blocking_plaza.mp4 | Blocking: cámara, puesta en escena y timing |
| @Image1 | mara_ref.png | Identidad de MARA |
| @Image2 | cazador_ref.png | Identidad de EL CAZADOR |
| @Image3 | ciudad_ref.png | Look del escenario |
| @Image4 | patrulla_ref.png | Diseño del vehículo |

### ASÍ LEÍ TU BLOCKING

| Tramo | Corte | Plano | Cámara | Sujetos |
|---|---|---|---|---|
| 0-3 s | - | Extreme wide, picado | 28 mm. Grúa que baja de 7.5 m a 4.5 m mientras avanza a 2 m/s | Maniquí gris medio en el centro, camina hacia cámara. Maniquí oscuro muy al fondo, se acerca corriendo |
| 3-6 s | - | Extreme wide -> wide | 28 mm. La grúa acaba a 1.7 m con leve tilt up y pan a la derecha | Maniquí gris en el centro. El oscuro entra por el tercio derecho, a 9 m |
| 6-11 s | Corte en 6 s | Full shot, contrapicado | 40 mm. Travelling lateral a 0.9 m de altura, 20 m a la derecha a 4 m/s | Maniquí gris centrado, corre de izquierda a derecha. Bolardos cruzando en primer término |
| 11-15 s | Corte en 11 s | Medium close-up -> close-up | 85 mm. Push-in lento de 1.6 m, a 1.6 m de altura | Maniquí gris quieto, cabeza en el centro. Caja-vehículo que llega por el fondo izquierdo y frena |

Si algo de esta tabla no coincide con tu blocking, dímelo antes de generar.

### PROMPT

```text
SECUENCIA CINEMATOGRAFICA CONTINUA ESTILO: SCI-FI, ACCION, SUSPENSO
cinematic shot, 2.39:1 anamorphic widescreen framing, 15 seconds, 3 shots joined by hard cuts at 6s and 11s

MAPA DE REFERENCIAS Y BLOQUEO 3D
Use @Video1 as blocking, camera path and timing only: copy its framing, shot sizes, camera height, camera trajectory and speed, subject positions, screen direction, movement paths and the exact timing of every beat and cut. @Video1 is an untextured grey 3D previz made of placeholder geometry: never render grey clay, flat shading, mannequins, primitive shapes, guide lines or its lighting. Replace every proxy with the photoreal asset mapped here.
Proxy map: the mid-grey mannequin at frame centre that walks toward camera, then runs left-to-right, then stands in close-up = MARA, the woman in @Image1. The taller, darker mannequin that runs in from the far background and enters on the right = EL CAZADOR, the armoured figure in @Image2. The box vehicle that arrives behind her in the last shot and brakes = the armoured patrol in @Image4. The grey boxes, posts and plaza = the city in @Image3.
@Image1: identity lock for MARA (face, hair, build, wardrobe). Appearance only, not pose or framing.
@Image2: identity lock for EL CAZADOR (armour, helmet, proportions). Appearance only.
@Image3: location look (architecture, materials, neon, palette). Appearance only; composition comes from @Video1.
@Image4: vehicle design (body, plating, lights). Appearance only.
Priority: @Video1 decides where everything is and how the camera moves; the images decide what everything looks like; this text decides light, materials, physics, performance and sound.

ATRIBUTOS DE SIMULACION CENTRAL: Realismo, coherencia visual y peso real de la masa.
Z-depth: lluvia y bolardos en primer término, MARA en plano medio, EL CAZADOR y la patrulla al fondo; el vapor queda siempre DETRÁS de MARA, sin atravesarla. Mass inertia: la patrulla de 9 toneladas hunde el morro al frenar y empuja una ola de agua. Dynamic reflections: sus reflectores barren el hormigón mojado. Temporal memory: chaqueta roja, cicatriz en la ceja izquierda, pelo empapado y bolsa cruzada, idénticos del segundo 0 al 15.

ESTETICA VISUAL AVANZADA ESTILO HOLLYWOOD BLOCKBUSTER
ultra-cinematic visuals, low saturation, soft film grain. Shot on anamorphic lens, depth of field, 100mm lens for textures, color grading, HDR, high quality 4K.

REGLAS DE CONTINUIDAD Y CONFIGURACION DE CAMARA
Los planos son absolutamente continuos durante los 15 segundos en el espacio y el tiempo: misma noche, misma lluvia, misma dirección de huida (izquierda a derecha de pantalla), mismo vestuario empapado.
Configuracion de camara: texturas de película IMAX MSM 9802 original de 15/70 mm combinada con ARRI Alexa 35 y lente panorámica anamórfica Panavision C-series personalizada para rodaje en directo. Preservar la delicada textura granulada del celuloide de 35 mm.

ESQUEMA DE ILUMINACION, ATMOSFERA Y PALETA
Paleta de color cinematografica: negros azulados, hormigón gris frío y un único acento rojo en la chaqueta.
COLOR GRADE: teal en sombras, ámbar de sodio en altas luces, rojo sin desaturar.
Iluminacion: low key nocturno. Farolas de sodio a 2200 K en contraluz desde el fondo; neón cian a 9000 K lateral desde la izquierda; reflectores de la patrulla a 5600 K desde el fondo en la última toma.
Tipo de luz: practical, hard directional backlight, volumetric fog.
Matriz de luz y sombra: contraste 8:1, media cara de MARA en sombra, EL CAZADOR en silueta con borde de luz.
Atmosphere and clima: lluvia densa vertical, vapor de rejillas, bruma que dibuja los haces de luz.

DISEÑO DE AUDIO VISCERAL
Efectos de sonido tactiles: lluvia sobre chapa, botas que rompen charcos, neumáticos sobre asfalto mojado, siseo hidráulico de frenos.
Resonancia de alta/baja frecuencia: turbina de la patrulla como sub-bass de 40 Hz que crece desde el segundo 11 y hace vibrar la óptica.
Contraste emocional: respiración de MARA, nasal al inicio y jadeo roto al final, contra el zumbido eléctrico del neón.
Musica: ninguna, solo sonido diegético.

NARRATIVA Y TONO EMOCIONAL
Tono: suspenso que rompe en huida y termina en agotamiento desafiante.
Inspiracion de epoca y lenguaje visual: neo-noir de ciencia ficción de los años 80: calles mojadas, neón reflejado, humo a contraluz.
Expresion y tension corporal: de control (mandíbula suelta, mirada baja) a alarma (ojos que saltan a un reflejo, hombros que suben), a esfuerzo máximo (cuello en cuerdas) y a rendición activa (exhalación larga, barbilla que sube).

PHYSICS
Cada pisada desplaza agua en corona. La tela mojada pesa y llega tarde. La lluvia rebota en lo duro y resbala por lo vertical. La patrulla frena con transferencia de masa al eje delantero y frenada larga sobre mojado.

ESCENARIO
Texturas industriales de primera categoria: hormigón mojado con manchas de óxido, chapa galvanizada, bolardos de acero desconchado.
Sensacion tactil: charcos de 2 cm que se abren al pisar, rejillas que escupen vapor.
Elementos visuales: rótulo de neón con un tubo fundido, una bolsa de plástico atrapada en un bolardo.

FICHAS MECANICAS DE PERSONAJES Y OBJETOS (ASSET SPECS)
Sujeto principal: MARA (@Image1), mensajera de 30 años, atlética, piel con microporos y gotas que resbalan, cicatriz en la ceja izquierda, pelo oscuro empapado.
Texturas de vestuario: chaqueta roja impermeable de pliegues pesados, botas de suela gruesa, bolsa de lona que golpea la cadera.
Automoviles / Vehiculos: patrulla blindada (@Image4), 9 toneladas, blindaje mate, barra de reflectores frontal.
Personajes extras: EL CAZADOR (@Image2), 1.95 m, armadura negra mate, casco cerrado, carrera pesada y constante.
Dialogos, estilo de voz, acento y emocion: solo habla MARA, una vez, en español neutro, voz grave y sin aire.
Bloqueo de personaje: MARA = @Image1; EL CAZADOR = @Image2; ESCENARIO = @Image3; PATRULLA = @Image4.

DESGLOSE DE SECUENCIA CONTINUA DE 15 SEGUNDOS

0s-3s | TOMA 1: DESCENSO SOBRE EL CALLEJON | CONTINUO
Blocking: sigue @Video1 0s-3s: extreme wide high angle; la cámara baja de 7.5 m a 4.5 m y avanza a 2 m/s; MARA en el centro camina hacia cámara.
Direccion: practical large-format realism: crane with physical weight, deep staging, a threat far in the background.
Toma y composicion: EWS picado, líneas de fuga del callejón, lluvia en primer término.
Lentes, optica y apertura: field of view of the 28 mm in @Video1, anamorphic character, f/8, deep focus.
Camara: crane down con dolly in, continuo y pesado.
Accion: MARA camina a 1.4 m/s, talón y punta; cada paso abre un charco. Al fondo EL CAZADOR corre a 6 m/s.
Comportamiento humano: manos en los bolsillos, hombros encogidos.
Expresion y tono: mandíbula suelta, parpadeo lento, respiración nasal.
Dialogo: ninguno.

3s-6s | TOMA 2: AMENAZA EN PROFUNDIDAD | CONTINUO
Blocking: sigue @Video1 3s-6s: la grúa termina a 1.7 m, altura de ojos, con leve tilt up; MARA llega a wide shot en el centro; EL CAZADOR entra por el tercio derecho a 9 m.
Direccion: practical large-format realism: wide lens close to the subject, both planes sharp.
Toma y composicion: WS a la altura de los ojos, vapor entre los dos.
Lentes, optica y apertura: 28 mm field of view, f/5.6, MARA y EL CAZADOR nítidos a la vez.
Camara: la grúa se asienta con una micro-vibración; ligero pan right.
Accion: sin detenerse, MARA ve el reflejo en un charco -> acorta el paso -> el torso gira 20 grados -> la bolsa se adelanta por inercia.
Comportamiento humano: saca las manos y los dedos se cierran sobre la correa.
Expresion y tono: los ojos saltan al charco y vuelven, el masetero se marca.
Dialogo: ninguno.

6s-11s | TOMA 3: FUGA LATERAL | HARD CUT
Blocking: sigue @Video1 6s-11s: low-angle lateral tracking a 0.9 m; la cámara viaja a la derecha a 4 m/s junto a MARA; full shot, MARA centrada corre de izquierda a derecha.
Direccion: practical large-format realism: camera low on a tracking vehicle, the take holds.
Toma y composicion: FS contrapicado, bolardos y lluvia cruzando en primer término, neón en oval bokeh.
Lentes, optica y apertura: field of view of the 40 mm in @Video1, f/4, motion blur en primer término.
Camara: lateral tracking a velocidad constante, vibración leve de rodadura.
Accion: el talón empuja y levanta agua -> el torso se inclina 20 grados -> la zancada se alarga tres pasos -> la chaqueta llega tarde; desde el segundo 9 la zancada se acorta y el agua salpica más alto.
Comportamiento humano: brazos que bombean, un resbalón corregido, un vistazo por encima del hombro.
Expresion y tono: aletas de la nariz dilatadas, cuello en cuerdas, cejas juntas.
Dialogo: ninguno; solo jadeo.

11s-15s | TOMA 4: FRENADA Y RENDICION | HARD CUT
Blocking: sigue @Video1 11s-15s: medium close-up frontal de MARA a 1.6 m con push-in lento hasta close-up; la patrulla llega por el fondo, tercio izquierdo, y frena detrás.
Direccion: choreographed reveal: slow push-in on a face while the threat arrives behind in soft focus.
Toma y composicion: MCU a CU, reflectores que florecen en horizontal blue flares.
Lentes, optica y apertura: field of view of the 85 mm in @Video1, f/2.8, foco en los ojos.
Camara: dolly in de 1.6 m en 4 segundos; micro-vibración cuando la turbina se acerca.
Accion: MARA quieta, el pecho sube y baja. Detrás, la patrulla frena: el morro se hunde -> las ruedas se deforman -> una ola de agua avanza -> la suspensión rebota.
Comportamiento humano: el agua le cae por la cara, traga saliva, no se gira.
Expresion y tono: exhalación larga, los párpados inferiores se tensan, la barbilla sube dos centímetros.
Dialogo: MARA (voz grave, sin aire, susurro firme): "Ya no corro más."

BARRERAS NEGATIVAS
Sin CGI evidente, sin física caricaturesca de videojuego, sin movimientos flotantes sin gravedad, sin glitches visuales, sin transiciones de desvanecimiento, sin cambios espontáneos de ropa o fisonomía, sin maniquíes ni geometría gris, sin cortes fuera de los segundos 6 y 11, sin subtítulos, sin texto en pantalla, sin marcas de agua.
```

9976 caracteres · perfil COMPLETO (5.000-10.000).

### NOTAS DE DIRECCIÓN

- Supuestos: Mara mide 1.70 m y la patrulla pesa 9 toneladas; la lluvia y los neones salen de
  `ciudad_ref.png`. La línea de diálogo va en español neutro.
- En el blocking el maniquí no se detiene entre los segundos 3 y 6, así que Mara reacciona
  sin pararse: el texto no pide nada que el video no haga.
- Riesgo principal: que el maniquí oscuro y el gris se intercambien en el segundo 5, cuando
  se acercan. Si ocurre, diferenciar más sus alturas en Blender.
- Primer borrador a 480p: comprobar, por este orden, que la cámara sigue al blocking, que
  Mara se parece a su imagen y que no queda nada gris.
- El tope de caracteres depende de la plataforma. Si la tuya corta el texto, pídeme la
  versión COMPACTA.

---

## Segundo ejemplo: perfil COMPACTO

Encargo: Seedance 2.0 en una plataforma que corta a 3.000 caracteres; una imagen del
personaje (`guerrera_ref.png`) y un blocking de 8 segundos en plano secuencia donde la cámara
orbita alrededor de ella mientras desenvaina frente a un dragón que aterriza al fondo.

Validado con `--perfil compacto --duracion 8 --imagenes 1 --videos 1 --blocking --cortes
ninguno` -> `RESULTADO: APTO | 2790 caracteres`.

```text
SECUENCIA CINEMATOGRAFICA CONTINUA ESTILO: FANTASIA EPICA. cinematic shot, 2.39:1 anamorphic widescreen framing, 8 seconds, one unbroken take, no cuts.

MAPA DE REFERENCIAS
Use @Video1 as blocking, camera path and timing only: copy its framing, the orbit trajectory and speed, subject positions and timing. It is an untextured grey previz: replace every proxy, never render grey clay, mannequins or primitives. The standing mannequin at frame centre = KAIRA, the warrior in @Image1. The large winged block landing in the background = the dragon. @Image1 is appearance only, not pose or framing.

CAMARA Y ESTETICA
IMAX 15/70 mm + ARRI Alexa 35, Panavision C-series anamorphic, grano de celuloide 35 mm, low saturation, HDR. Realismo, coherencia visual y peso real de la masa. Continuidad absoluta de armadura de bronce, trenza y corte en el pómulo.

LUZ Y ATMOSFERA
Sol bajo de hora dorada a 3400 K en contraluz desde la derecha; relleno frío de cielo a 8000 K. Contraste 6:1, KAIRA con borde de luz. Ceniza en suspensión y polvo que el dragón levanta al aterrizar, siempre detrás de ella.

AUDIO
Acero que roza la vaina, cuero que cruje, aleteo como sub-bass de 30 Hz que hace vibrar la óptica, impacto sordo del aterrizaje, respiración controlada. Musica: ninguna.

ASSETS
KAIRA (@Image1): 30 años, armadura de bronce abollada, trenza negra, corte en el pómulo izquierdo, espada larga de acero mate. DRAGON: 20 m, escamas de obsidiana, alas membranosas, 12 toneladas. ESCENARIO: meseta de basalto agrietado, ceniza, estandartes rotos.

DESGLOSE
0s-3s | TOMA 1 TENSION | @Video1 0s-3s | CONTINUO: MS, 50 mm, f/4. Camara: orbit lento a la derecha a la altura del pecho. Accion: KAIRA planta los pies -> el peso baja a las caderas -> la mano derecha cierra sobre la empuñadura. Gesto: mandíbula marcada, mirada fija, respiración nasal. Dialogo: ninguno.
3s-6s | TOMA 2 ATERRIZAJE | @Video1 3s-6s | CONTINUO: MS con el dragón entrando al fondo, f/5.6, ambos nítidos. Camara: el orbit continúa; sacudida seca al impacto. Accion: el dragón frena con las alas -> las patas golpean el basalto -> la roca se agrieta -> una onda de ceniza avanza y agita la trenza con retraso. Gesto: parpadea una vez, no retrocede. Dialogo: ninguno.
6s-8s | TOMA 3 ACERO | @Video1 6s-8s | CONTINUO: MCU de tres cuartos, f/2.8, dragón en oval bokeh. Camara: el orbit se cierra en push-in. Accion: giro de cadera -> hombro -> la hoja sale de la vaina y capta el sol en un flare horizontal. Gesto: aletas de la nariz dilatadas, la barbilla baja. Dialogo: KAIRA (voz grave, baja): "Ven."

BARRERAS NEGATIVAS
Sin CGI evidente, sin física de videojuego, sin flotación, sin glitches, sin fundidos, sin cortes, sin cambios de ropa o fisonomía, sin geometría gris, sin subtítulos, sin texto en pantalla, sin marcas de agua.
```
