# Dirección, óptica, física y actuación

Material de consulta para el paso 3 (decidir como director) y para rellenar las líneas
técnicas de la plantilla. No se copia entero al prompt: se elige lo que la escena necesita.

Contenido:
1. Formas de dirigir (sin nombres)
2. Lente y apertura según la escala de la acción
3. Temperatura de color
4. Manual de cinemática: cadenas acción -> reacción
5. Micro-expresión: zonas del rostro y grupos musculares
6. Audio táctil
7. Imperfección humana

---

## 1. Formas de dirigir

El usuario piensa en directores; el prompt habla en gramática de cámara. La columna "clave"
solo sirve para que reconozcas la petición ("como Nolan", "a lo Villeneuve"). **Ningún nombre
de esta columna, ni de ninguna otra persona real, se escribe en el prompt**: se escribe la
frase de la columna "Dirección". Un nombre propio no le da al modelo nada que renderizar y
además puede hacer que la plataforma rechace el prompt.

### A. Realismo físico de gran formato
*Clave: Nolan.*

- Cámara: gran formato IMAX 15/70 en mano o montada en el vehículo; se siente su peso. Angular
  cerca del sujeto en lugar de teleobjetivo lejos.
- Puesta en escena: efectos físicos en cámara, localización real, acción en profundidad con
  varios planos nítidos a la vez. La tensión viene de un reloj: algo en el fondo se acerca.
- Luz: fuentes prácticas y luz natural dura; paleta acero, azul frío y ámbar desaturado.
- Sonido: tono grave ascendente que nunca resuelve, tic-tac mecánico, impactos secos.
- Dirección (para pegar): `practical large-format realism: IMAX handheld with physical
  weight, wide lens close to the subject, in-camera effects, deep staging, a visible ticking
  threat in the background`

### B. Asombro coreografiado
*Clave: Spielberg.*

- Cámara: un solo movimiento fluido que reencuadra de plano general a primer plano porque el
  actor se mueve hacia la cámara. Push-in lento hacia un rostro que mira algo fuera de cuadro
  antes de revelar qué es.
- Puesta en escena: capas en profundidad, objetos en primer término que enmarcan, reflejos en
  cristal o espejo que dan dos imágenes en una.
- Luz: contraluz fuerte con haces volumétricos, siluetas, prácticas que florecen, flares.
  Tungsteno cálido frente a luna fría.
- Sonido: silencio antes de la revelación; un motivo sonoro que anuncia la presencia.
- Dirección: `choreographed long take: the blocking reframes from wide to close-up in one
  fluid move, slow push-in on a face reacting to something off-screen, strong backlight with
  volumetric shafts and silhouette`

### C. Ópera espacial clásica, universo usado
*Clave: Lucas.*

- Cámara: cuadros amplios y estables, composición geométrica, teleobjetivo observacional de
  estilo documental. La cámara casi no se mueve: se mueven los sujetos, con dirección de
  pantalla muy clara.
- Puesta en escena: tecnología gastada, con arañazos, aceite, hollín y remiendos. Fondo con
  varias capas de actividad. Vehículos que cruzan el cuadro a gran velocidad.
- Luz: sol bajo en el horizonte, contraste limpio, colores primarios puntuales sobre tierra
  y metal.
- Sonido: zumbidos mecánicos por capas, motores con carácter, golpes metálicos.
- Dirección: `classic space-opera grammar: stable wide tableau, long-lens documentary
  observation, worn used-future surfaces, fast vehicles with clean screen direction, the
  camera holds while the subjects move`

### D. Escala monumental contemplativa
*Clave: Villeneuve.*

- Cámara: lenta y deliberada; push-in casi imperceptible, planos sostenidos. Composición
  centrada y minimalista con mucho espacio negativo.
- Puesta en escena: figura humana diminuta frente a una estructura colosal; siluetas;
  quietud. La actuación es contenida: respiración y mirada.
- Luz: cenital suave o cielo cubierto, bruma, polvo o niebla que difuminan el fondo; paleta
  casi monocroma (ocre, pizarra, ámbar).
- Sonido: drones de subgrave, metal grave distorsionado, silencio antes del impacto.
- Dirección: `monumental contemplative scale: tiny human figure against a colossal structure,
  slow imperceptible push-in, centred minimal frame with negative space, haze-diffused
  monochrome light, restrained performance`

### Reparto por función dramática

Cuando el usuario pide "tomas dirigidas cada una por su director", asigna por lo que la toma
tiene que conseguir, no por turnos:

| La toma tiene que | Gramática |
|---|---|
| Establecer escala y lugar | D |
| Sostener tensión física, persecución, impacto | A |
| Revelar algo o mostrar una reacción emocional | B |
| Mostrar vehículos, combate espacial, acción cinética clara | C |

Dos gramáticas por secuencia de 15 s como máximo, salvo petición expresa: cambiar de estilo
en cada toma rompe la unidad visual. Con blocking, la gramática se elige *después* de leerlo:
la cámara ya está decidida, así que se escoge la forma de dirigir que encaja con lo que el
blocking hace, y aporta la luz, el sonido y la actuación de ese estilo.

Si el usuario pide un director que no está aquí, describe tú su gramática en las mismas cinco
dimensiones: cámara, puesta en escena, luz, sonido y una frase de dirección.

---

## 2. Lente y apertura según la escala de la acción

La apertura es la palanca que obliga al modelo a separar o a unir los planos de profundidad.

| Situación | Focal (anamórfico) | Apertura | Efecto |
|---|---|---|---|
| Establecer lugar, escala monumental | 24-35 mm | f/8-f/11 | Todo nítido, líneas de fuga, figura pequeña |
| Amenaza en el fondo que debe leerse | 40-50 mm | f/5.6-f/8 | Sujeto y peligro nítidos a la vez |
| Persecución con compresión de distancias | 100-180 mm | f/5.6 | El perseguidor parece pegado a la espalda |
| Acción cuerpo a cuerpo, cámara inmersa | 28-40 mm | f/4 | Cercanía física, distorsión leve en los bordes |
| Diálogo o reacción con contexto | 50-65 mm | f/2.8-f/4 | Rostro nítido, fondo reconocible pero suave |
| Aislar una emoción | 75-100 mm | f/2-f/2.8 | Fondo en bokeh oval, solo existen los ojos |
| Textura, detalle, inserción | 100 mm macro | f/4-f/5.6 | Poros, hilos, gotas |
| Vértigo, revelación psicológica | dolly zoom 35 -> 75 mm | f/4 | El fondo se expande tras un sujeto fijo |

Notas de uso:

- Un anamórfico 2x tiene el campo horizontal de un esférico de la mitad de focal. Con
  blocking, el milimetraje que mandan los datos de Blender es el de la cámara esférica del
  programa: cítalo como campo de visión y deja lo anamórfico como carácter
  (`field of view of the 28 mm in @Video1, Panavision C-series anamorphic character: oval
  bokeh, horizontal blue flares`).
- Carácter anamórfico que el modelo entiende: `oval bokeh`, `horizontal lens flares`,
  `barrel distortion at the edges`, `focus breathing`, `soft corner falloff`.
- Un cambio de foco se escribe con su segundo: `rack focus from the foreground hand to the
  face at 7s`.

---

## 3. Temperatura de color

| Fuente | Kelvin |
|---|---|
| Vela, fuego | 1800-2000 K |
| Sodio de farola antigua | 2000-2200 K |
| Tungsteno, bombilla práctica | 2700-3200 K |
| Hora dorada | 3200-3800 K |
| Fluorescente blanco frío | 4000-4500 K |
| Luz de día, flash | 5500-5600 K |
| Cielo cubierto | 6500-7500 K |
| Sombra abierta, hora azul | 8000-10000 K |
| Luz de luna estilizada | 4100 K sobre balance de tungsteno (se ve azul) |

Una fuente cálida y otra fría en el mismo cuadro dan separación de planos sin necesidad de
desenfoque. Di siempre de dónde entra cada una.

---

## 4. Manual de cinemática

El modelo simula peso cuando el texto encadena causas y efectos. Fórmula general:

`compresion -> carga de energia -> liberacion -> transferencia -> asentamiento`

Cuanto más masa: aceleración más lenta, más recorrido tras el frenado, más reacción del suelo.

| Acción | Cadena |
|---|---|
| Arrancar a correr | El peso cae sobre la pierna trasera -> el torso se inclina 20 grados -> el talón empuja y levanta grava -> los brazos compensan -> la zancada se alarga en tres pasos |
| Frenar en seco | Los talones se clavan -> las rodillas absorben -> el torso sigue 20 cm por inercia -> los brazos se abren para equilibrar -> el polvo adelanta al cuerpo |
| Saltar | Flexión profunda de cadera y rodilla -> los brazos atrás -> extensión explosiva -> el cuerpo sube sin flotar: parábola -> en el punto más alto la ropa pierde peso un instante |
| Aterrizar | Punta, talón, rodillas ceden -> la mano toca el suelo -> el impacto sube por la columna -> polvo radial -> medio segundo de asentamiento antes de levantarse |
| Golpear | Giro de cadera -> hombro -> codo -> puño; el pie contrario pivota -> al impacto el objetivo cede y la onda recorre la tela y la carne -> retroceso del brazo |
| Caer | Pérdida de apoyo -> los brazos buscan agarre -> cadera primero -> rebote corto -> el cuerpo se asienta por partes, no de golpe |
| Girar la cabeza | Los ojos van primero -> la cabeza sigue -> los hombros llegan tarde -> el pelo llega el último y se pasa |
| Vehículo que frena | El morro se hunde sobre la suspensión -> las ruedas delanteras se deforman -> humo y marcas en el asfalto -> la carga interior se desplaza hacia delante -> rebote de la suspensión al detenerse |
| Vehículo que gira | La carrocería se inclina hacia fuera -> las ruedas exteriores se cargan -> la trasera desliza -> gravilla en abanico -> contravolante |
| Impacto contra un objeto | Contacto -> deformación del más blando -> fragmentos que salen en la dirección del impulso, los pesados cerca y los ligeros lejos -> polvo que tarda en caer |
| Tela y pelo | Siempre llegan tarde: siguen al cuerpo con retraso, se pasan y vuelven. Mojados pesan y se pegan |
| Lluvia, agua, humo | La lluvia rebota en superficies duras y forma corona; resbala por las verticales. El humo se enrosca detrás del sujeto, nunca lo atraviesa |

Datos que anclan la escala: velocidad en m/s o km/h, masa aproximada, distancia de frenado,
altura de la caída. Una cifra por acción basta.

---

## 5. Micro-expresión

La emoción no se nombra: se describe qué músculo cambia y hacia dónde va la mirada. En una
secuencia de 15 s la expresión tiene que evolucionar: estímulo -> micro-reacción -> cambio de
tensión -> nuevo estado.

| Zona | Músculo o gesto | Lo que comunica |
|---|---|---|
| Frente | El frontal sube las cejas | Sorpresa, alerta |
| Entrecejo | El corrugador junta las cejas | Concentración, dolor, ira contenida |
| Ojos | El orbicular los entorna; el párpado inferior se tensa | Evaluación, desconfianza |
| Parpadeo | Se detiene, o se acelera | Fijación, o estrés |
| Mirada | Salta entre dos puntos, o baja y a un lado | Cálculo, o vergüenza y recuerdo |
| Nariz | Aletas dilatadas; el elevador del labio la arruga | Esfuerzo, asco |
| Mandíbula | El masetero se marca bajo la piel | Rabia contenida, decisión |
| Labios | El orbicular los aprieta; una comisura tiembla | Contención, llanto que llega |
| Mejillas | El cigomático tira hacia arriba, con o sin ojos | Alegría real, o sonrisa falsa |
| Cuello | El platisma se tensa en cuerdas; la nuez sube al tragar | Miedo, esfuerzo |
| Hombros | El trapecio los sube hacia las orejas, o caen | Amenaza, o rendición |
| Manos | Los dedos se cierran en la tela; los nudillos palidecen | Ansiedad, control |
| Respiración | Alta y corta en el pecho; o larga, por la nariz, con el diafragma | Pánico, o dominio |

Ejemplo de arco en tres tomas, sin nombrar ninguna emoción:

- 0s-4s: mirada fija al frente, parpadeo lento, respiración nasal larga, mandíbula suelta.
- 4s-9s: los ojos saltan a la derecha y vuelven, el masetero se marca dos veces, el pecho
  empieza a subir alto y corto, los dedos se cierran sobre la correa.
- 9s-15s: los párpados inferiores se tensan, las aletas de la nariz se dilatan, una
  exhalación lenta por la boca entreabierta, los hombros bajan dos centímetros.

Detalles de piel que venden el realismo: microporos, sudor que perla en la sien y cae,
vello erizado, enrojecimiento por esfuerzo, vaho en el aire frío.

---

## 6. Audio táctil

Seedance 2.5 genera el sonido, y el sonido que describes empuja además a la imagen: un grave
profundo justifica la vibración del lente y del polvo.

| Capa | Vocabulario |
|---|---|
| Peso e impacto | `40 Hz sub-bass thud`, golpe seco de metal contra hormigón, crujido de suspensión, neumático que muerde grava |
| Mecánica | Siseo hidráulico, turbina que sube de tono, servo con zumbido, relé que chasquea, cadena que tensa |
| Fricción y material | Cuero que cruje, tela mojada que se despega, cristal que se astilla en granos, arena contra metal |
| Resonancia | Reverberación larga de hangar, eco corto de callejón, grave que hace vibrar el suelo, agudo metálico que queda sonando |
| Orgánico | Respiración corta por la nariz, jadeo, trago de saliva, latido sordo, ladrido lejano, pasos que cambian de superficie |
| Ambiente | Viento que silba en una rendija, lluvia sobre chapa, ciudad lejana amortiguada, silencio con zumbido eléctrico |

Tres decisiones por escena: qué suena pesado, qué frecuencia domina y qué sonido humano
contrasta con el entorno. Y la música: ninguna, o cuál y desde qué segundo.

---

## 7. Imperfección humana

La IA tiende a la simetría y a lo limpio. Dos o tres de estos detalles por escena la rompen:

- Suciedad y desgaste: chicle en el asfalto, pintura descascarillada, una pegatina medio
  arrancada, óxido en un tornillo, barro seco en una bota.
- Objetos cotidianos fuera de sitio: un vaso de cartón rodando, una bolsa atrapada en una
  valla, un cable suelto, una colilla, un carrito abandonado.
- Asimetrías del cuerpo y la ropa: un cordón desatado, una manga más subida que la otra, una
  cicatriz vieja, pelo pegado a la frente por el sudor.
- Extras que reaccionan mal: alguien que tarda en apartarse, uno que mira al lado
  equivocado, un perro que ladra a destiempo, un conductor que se queda con el intermitente
  puesto.
- Fallos de la óptica: una mota de polvo en el lente, un reflejo que cruza, una gota en el
  filtro, un leve desenfoque que se corrige.
