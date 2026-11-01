# FaroNet: traslado a placa HS-03

Abrir `index.html` para el plano interactivo, o `FaroNet-HS03-plano.pdf` para las
3 hojas imprimibles. Los SVG/PNG `componentes` y `soldaduras` son las dos vistas.
`diseno.json` contiene las posiciones, los 24 cables y las redes esperadas.

Este es un nuevo reparto de agujeros. No mezclar sus coordenadas con el plano
anterior `docs/placa-perforada.html`; se conserva ese archivo como referencia.

## Qué se tomó como referencia

Las dos fotografías del usuario muestran una HS-03 de 9 × 14,5 cm, con 33 columnas
y 48 filas. El diseño usa islas independientes; no debe suponerse que las líneas
blancas de la cara de componentes conectan agujeros como en la protoboard.
Verificar esto con multímetro antes de montar. No se usan los contactos alargados
superiores/inferiores ni se necesita cortar pistas en una placa de islas.

Las coordenadas están definidas mirando el cobre: A a AG de izquierda a derecha,
fila 01 arriba. Las letras impresas se repiten después de Z: el plano denomina
AA–AG a esa segunda serie A–G. Por ejemplo, AF es la columna 32, no F (columna 6).
Marcar A01 y una flecha al borde superior antes de empezar.

Al girar la placa de izquierda a derecha, como una página, la cara de componentes
muestra AG a la izquierda y A a la derecha, manteniendo fila 01 arriba. El plano
ya incorpora esa reflexión: no volver a reflejarlo al imprimir. No girar la placa
por arriba/abajo para comparar estas vistas.

La escala del PDF, impreso al 100 %, es nominal 90 × 145 mm. Comprobar 10 pasos
entre centros, de A a K: 25,4 mm. La foto no permite verificar tolerancias físicas;
los números de agujero mandan y las piezas deben presentarse antes de soldar.

## Circuito preservado

Una Raspberry independiente por placa, con los mismos GPIO en A y B:

| J1, agujero | Función | Pin físico Raspberry | BCM |
|---|---|---:|---:|
| N43 | GND | 6 | — |
| O43 | 3,3 V | 1 | — |
| P43 | Emisor IR | 11 | 17 |
| Q43 | Receptor | 13 | 27 |
| R43 | Indicador TX | 15 | 22 |
| S43 | Indicador RX | 16 | 23 |
| T43 | Pánico | 18 | 24 |

No alimentar esta placa con 5 V, no alimentar GPIO desde otra fuente y no unir
las salidas de 3,3 V de las dos Raspberry. La Raspberry conserva su alimentación
micro-USB habitual. El conector debe enchufarse con la alimentación desconectada.

Valores definitivos: R1 330 Ω; R2 2,2 kΩ; R3 y R4 10 kΩ; R5 y R6 1 kΩ;
C1 100 nF / 0,1 µF. La resistencia de 330 Ω en la base era una prueba temporal;
no se conserva. El retorno que era C17/B20 en protoboard es una unión a GND,
no una resistencia adicional.

## Presentar las piezas, especialmente el botón

Introducir las piezas por la cara sin cobre y soldar por la cara de islas. La
Raspberry permanece externa; no se suelda a esta placa.

- J1 es una tira **hembra 1×7 de paso 2,54 mm**, para conectar los cables actuales
  hembra–macho. También se pueden soldar siete cables directamente en N43…T43,
  conservando el conector hembra en el extremo hacia la Raspberry y sujetando
  el mazo a la placa para que los tirones no recaigan en las soldaduras. J1 no es
  el socket DIP de 8 patas de la compra. Etiquetar sus siete conexiones.
- Q1 puede ir en un zócalo hembra 1×3: E en H18, B en I18, C en J18. Conservar la
  identificación de patas del 2N2222A que funcionó. La forma del encapsulado en
  el dibujo no sustituye ese patillaje. El esquema usa posiciones por función.
- IR transparente: A en H05, K en I05. PT333 negro: C en Y05, E en Z05. No inferir
  las patas de piezas nuevas por longitud. Las pruebas previas identificaron las
  piezas que se deben trasladar.
- LED TX: A en H25, K en I25; LED RX: A en Y25, K en Z25.
- SW1: patas en O33, T33, O35 y T35. Señal por O33, GND por T35. Las otras dos
  patas se sueldan solo a sus islas, sin cable externo. La huella inferida es
  **12,7 × 5,08 mm**, a partir de D30/D32/G30/G32 en la protoboard que funcionó
  (su canal central aumenta la separación horizontal). Presentar y comprobar
  encaje y contactos. Si el botón no coincide, ajustar el plano antes de soldar;
  no forzar ni usar el agujero vecino sin actualizar las conexiones.
- Las resistencias usan separación de cuatro pasos (10,16 mm) entre terminales.
  C1 usa O40/Q40, dos pasos (5,08 mm). Adaptar suavemente la forma de las patas,
  sin tirar del encapsulado. Si el tamaño real no permite el montaje, detener esa
  pieza y ajustar su huella; no cambiar conexiones de forma improvisada.

Los dos componentes ópticos están separados y son simétricos respecto al centro
horizontal de la placa. Sus cuerpos se montan verticales, apuntando hacia fuera
de la cara de componentes. Para comunicar dos placas iguales, enfrentar esas
caras y alinear el transparente de una con el negro de la otra. Colocar pantallas
opacas si hace falta reducir reflejos. No se promete una distancia nueva.

## Soldar barras y cables

Son **dos barras y 24 cables**, detallados en el HTML/PDF y en `cables.csv`.

- BG: alambre de cobre estañado continuo sobre la columna B, de B03 a B45, GND.
- BV: alambre de cobre estañado continuo sobre la columna AF, de AF03 a AF45, 3,3 V.
- Soldar cada barra en los extremos y en sus puntos de derivación. No hace falta
  soldar las 43 islas, pero cualquier isla que toque la barra pertenece a esa red.
- Reservar esas columnas. No colocar otras piezas o redes sobre ellas. No usar
  una hilera de gotas de estaño como reemplazo del alambre.
- Alternativa: unir sucesivamente los mismos puntos de derivación con cable
  aislado, pelando solamente los extremos. Debe quedar la misma red continua.
- W01…W24 son cables aislados. Los codos dibujados son rutas sugeridas, no puntos
  de soldadura. Solo se sueldan los dos extremos de cada cable a las islas que
  indica su fila en la tabla. Cualquier cruce intermedio conserva aislamiento.
- Cuando una isla ya tiene una pata, soldar el extremo del cable a esa isla/pata
  por debajo. No forzar dos o tres conductores dentro de un agujero. Recortar y
  aislar para que el conductor desnudo no alcance la isla vecina.
- No reutilizar agujeros de la protoboard como si conservaran conectividad: este
  plano tiene coordenadas nuevas y reproduce la red mediante cables explícitos.

Presentar primero todo sin soldar. Soldar después resistencias, condensador,
headers, piezas restantes y finalmente las barras/cables. Inspeccionar cada unión;
una isla suelta o despegada requiere reparar y verificar su conexión.

## Antes y después de alimentar

1. Sin Raspberry conectada ni alimentación, comprobar continuidad de cada W y
   de cada barra. No deben existir cortos permanentes entre 3,3 V y GND. C1 puede
   provocar una lectura transitoria de carga; no confundirla con un corto permanente.
2. Verificar que ningún cable cruzado esté pelado, que no haya puentes accidentales
   de estaño y que J1 esté rotulado. Verificar el botón suelto/presionado.
3. Usar un multímetro real. El plano, una fotografía y las pruebas de Python no
   miden continuidad ni voltajes; el enunciado exige registrar esas mediciones.
4. Conectar a la Raspberry apagada. Al alimentar, comprobar 3,3 V en la barra BV
   respecto de BG. Detenerse ante calentamiento o una conexión inesperada.
5. Repetir los indicadores, el botón (1 suelto/0 presionado) y la prueba óptica
   estática. Después repetir las tramas de prueba y el intercambio A/B.
6. Repetir las pruebas a las distancias de trabajo y documentar resultados reales.
   No presentar la verificación del plano como validación de la placa fabricada.

## Evidencia y límites

El usuario informa que su protoboard pasó las pruebas utilizando el LED IR redondo
transparente y el PT333 negro. No se inventan aquí cantidades o mediciones no
aportadas. El diseño conserva el circuito y los GPIO; la distribución física es
nueva. La huella del botón debe validarse en seco y los patillajes se transfieren
de las piezas probadas. No se ha fabricado ni medido esta placa desde el entorno
cloud. El proyecto completo aún requiere sus otros entregables.

`python3 tools/verificar_placa.py` comprueba que las 12 redes eléctricas previstas
son distintas, que todas sus conexiones están completas, que no hay piezas en el
mismo agujero, y que los GPIO coinciden con `faro.py`. No modela las propiedades
analógicas, los contactos internos reales del pulsador ni la calidad de soldadura.
