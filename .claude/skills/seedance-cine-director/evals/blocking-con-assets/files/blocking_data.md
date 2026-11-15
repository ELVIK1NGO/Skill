# Blocking 3D - datos reales de Blender

- Archivo: escena_plaza.blend  |  Escena: Scene
- Duracion: 15.0 s (360 cuadros a 24 fps)
- Resolucion: 840x360  |  Aspecto Seedance mas cercano: 21:9 (desvio 0.0 %)
- Duracion de generacion sugerida: 15 s
- Sujetos seguidos (coleccion ACTORES): HEROE, AUTO_PATRULLA, PERSEGUIDOR  |  Principal: HEROE

## Cortes
- 6.00 s: cambio de camara (CAM_A_grua -> CAM_B_lateral)
- 11.00 s: cambio de camara (CAM_B_lateral -> CAM_C_primer_plano)

## Fases de camara (fuente de verdad para el desglose de tomas)

### Fase 1
- 0.0-3.5 s | CAM_A_grua | 28 mm | dolly in (push-in), crane down [fast, avance +6.8 m, lateral -0.9 m, vertical -3.6 m, pan -3 deg, tilt +3 deg] | altura 7.5->3.88 m
  - HEROE: EWS (extreme wide) | center, middle | a 26.82->14.49 m de camara | moves 5.0 m at 1.4 m/s, approaching camera
  - AUTO_PATRULLA: ocluido por el decorado
  - PERSEGUIDOR: EWS (extreme wide) | center, upper third -> center, middle | a 54.06->24.81 m de camara | moves 22.9 m at 6.5 m/s, approaching camera

### Fase 2
- 3.5-6.0 s | CAM_A_grua | 28 mm | dolly in (push-in), crane down, pan right, tilt up [medium speed, avance +4.0 m, lateral -0.9 m, vertical -2.2 m, pan -8 deg, tilt +7 deg] | altura 3.88->1.7 m
  - HEROE: EWS (extreme wide) -> WS (wide) | center, middle | a 14.49->7.2 m de camara | moves 3.0 m at 1.2 m/s, approaching camera
  - AUTO_PATRULLA: ocluido por el decorado
  - PERSEGUIDOR: EWS (extreme wide) -> WS (wide) | center, middle -> right third, middle | a 24.81->8.69 m de camara | moves 13.8 m at 5.6 m/s, approaching camera, crossing frame left-to-right | en cuadro solo el 82 % de la fase

### Fase 3  (entra por CORTE)
- 6.0-11.0 s | CAM_B_lateral | 40 mm | truck right, lateral tracking shot (camera travels beside HEROE) [fast, lateral +20.0 m] | altura 0.9 m
  - HEROE: FS (full shot) | center, middle | a 7->7 m de camara | moves 20.0 m at 4.0 m/s
  - AUTO_PATRULLA: fuera de cuadro
  - PERSEGUIDOR: fuera de cuadro

### Fase 4  (entra por CORTE)
- 11.0-15.0 s | CAM_C_primer_plano | 85 mm | dolly in (push-in) [slow, avance +1.6 m] | altura 1.6 m
  - HEROE: MCU (medium close-up) -> CU (close-up) | head at center, middle | a 4.23->2.62 m de camara | stays in place
  - AUTO_PATRULLA: EWS (extreme wide) -> FS (full shot) | left third, middle -> left third, lower third | a 54.92->12.6 m de camara | moves 41.0 m at 10.4 m/s, approaching camera
  - PERSEGUIDOR: fuera de cuadro

Notas: los tamanos de plano son estimaciones validas para sujetos de escala humana
(para vehiculos o edificios usa la distancia). Los tercios indican el centro del
sujeto, o su cabeza en planos cerrados. Signos: pan + = izquierda, tilt + = arriba,
avance + = hacia delante, lateral + = derecha, vertical + = sube.
