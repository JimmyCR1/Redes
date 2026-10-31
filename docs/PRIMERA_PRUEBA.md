# Primera prueba: dos Faros, lo más sencillo posible

Abrir [la guía interactiva de protoboard](protoboard.html) para ver agujeros,
componentes y pines. Funciona sin Internet. Permite una MB102 compartida
(A: filas 1–30; B: 34–63) o dos protoboards independientes.

## Alcance real

Esta entrega inicia el proyecto con un enlace de prueba consulta/respuesta.
No es todavía FaroNet completo ni se ha probado en hardware real.
El códec y su recuperación de errores se prueban en el entorno de desarrollo.
GPIO, tiempos ópticos, polaridad y sensibilidad deben validarse en tu Raspberry.

El usuario confirmó dos Raspberry Pi 2 B iguales: usar una para A y otra para B.
Cada Raspberry controla su propio emisor y receptor. La prueba es
A -> luz -> B -> luz -> A, sin conexión eléctrica entre los circuitos de ambas Pi.
El código está dirigido a Raspberry Pi 2 con Raspberry Pi OS, no a Pico/ESP32.

Se usa OOK, UART 8N1 a 300 baudios generada por pigpio, evitando temporización
bit a bit con sleep de Python. Una trama ocupa aproximadamente 4,27 segundos.
El emisor queda encendido en reposo: es intencional para este receptor invertido.
Cada sentido necesita su propio emisor y receptor, alineados y separados con
tubitos opacos para reducir luz ambiente y reflejos del emisor local.

## Circuito preliminar de 3,3 V por Faro

La ficha aportada del kit SEN-00241 confirma un emisor IR de 940 nm y un detector
fototransistor NPN de visión lateral. Este diseño usa ese par, no el otro detector
PT333 del recibo. La captura no identifica las patillas del par óptico: se muestran
por función A/K y C/E, sin inventar su posición física por apariencia.
No conectar el LM311 en este primer montaje: no asumimos que opere correctamente
con alimentación total de 3,3 V; exige revisar su hoja de datos y rango de entrada.

La Raspberry se alimenta con su adaptador micro-USB normal de 5 V. La restricción
de 3,3 V aplica a la electrónica externa y a GPIO: nunca aplicar 5 V a GPIO.
MB102 puede designar la protoboard o un módulo de alimentación: aquí se usa
solo la protoboard, alimentada desde 3V3 y GND de la Pi. No unir otra fuente al riel.

```text
EMISOR (duplicar para A y B)
Pi 3V3 --- 330 ohm --- anodo LED IR catodo --- colector Q1 NPN
GPIO TX --- 2,2 kohm --- base Q1
base Q1 --- 100 kohm --- GND
emisor Q1 ---------------- GND

RECEPTOR (SOLO fototransistor NPN confirmado)
Pi 3V3 --- 10 kohm ---+--- GPIO RX
                     |
                colector detector
                emisor detector --- GND

INDICADORES (dos por Faro)
GPIO TX_LED --- 1 kohm --- anodo LED visible catodo --- GND
GPIO RX_LED --- 1 kohm --- anodo LED visible catodo --- GND

PANICO
GPIO PANIC --- pulsador normalmente abierto --- GND
(pull-up interno activado por software)

DESACOPLO
3V3 --- condensador ceramico 100 nF --- GND
```

Para el 2N2222A comprado, por instrucción del usuario se toma como referencia
su imagen: **pata 1 = emisor, 2 = base, 3 = colector**. Es una suposición de diseño,
no una verificación del fabricante de la pieza. La guía ubica cada pata en una
fila separada. No girar el transistor por ensayo y error; apagar y desconectar
la alimentación antes de mover cualquier conexión. También confirmar
ánodo/cátodo y C/E del detector. El LED IR con 330 ohm limita la corriente a menos
de 10 mA incluso antes de considerar las caídas de tensión; con IR típico rondará
5–6 mA. Confirmar que está dentro de los límites del LED adquirido.
No sustituirlo por una lámpara o un faro de potencia.

La resistencia de 10 kohm es un punto inicial, no garantiza sensibilidad. El
usuario no dispone de multímetro por ahora; la guía visual no sustituye esa
verificación y el software por sí solo no verifica voltajes ni ausencia de cortos. Antes
de conectar RX, medir el nodo del detector: con el emisor apagado debería estar
cerca de 3,3 V y con luz alineada cerca de 0 V (objetivo <0,5 V y >2,8 V).
Si no conmuta claramente, hay que ajustar acondicionamiento; no soldar aún.
No se promete inmunidad a luz ambiente con un divisor sin comparador.

### Pines: BCM en el programa, físicos en el conector de 40 pines

| Señal | Faro A BCM / físico | Faro B BCM / físico |
|---|---|---|
| TX | 17 / 11 | 5 / 29 |
| RX | 27 / 13 | 6 / 31 |
| indicador TX | 22 / 15 | 13 / 33 |
| indicador RX | 23 / 16 | 19 / 35 |
| botón | 24 / 18 | 26 / 37 |
| 3V3 | físico 1 | físico 17 |
| GND | físico 6 | físico 39 |

Cada circuito se alimenta de su propia Pi; solo la luz cruza entre ellos.
No unir las salidas de 3V3 de las Raspberry. Incluso si los circuitos comparten
una MB102, quedan en grupos de filas separados y no usan rieles laterales comunes.

## Instalación en la Raspberry (no en el PC ni en el entorno cloud)

Desde una copia del repositorio, con Raspberry Pi OS compatible con Pi 2:

```sh
sudo apt update
sudo apt install pigpio python3-pigpio
sudo systemctl enable --now pigpiod
/usr/bin/python3 -m unittest discover -s tests -v
/usr/bin/python3 faro.py address --node A
/usr/bin/python3 faro.py address --node B
```

Estos comandos de instalación no han sido ejecutados en tu Pi. Si la distribución
no ofrece los paquetes, registrar `cat /etc/os-release` y el error antes de cambiar
de biblioteca. No compilar ni instalar binarios de fuentes desconocidas.
No exponer pigpiod a Internet. No ejecutar otros programas que generen waves
mientras se usa esta prueba: el transmisor de waves del daemon es compartido.

Anotar las dos direcciones públicas que imprimen los últimos comandos. Se guardan
en la SD, en `~/.local/state/faronet/`. No son llaves ni contraseñas.

Terminal 1, receptor/respondedor B (reemplazar DIRECCION_A):

```sh
/usr/bin/python3 faro.py serve --node B --peer DIRECCION_A
```

Terminal 2, iniciador A (reemplazar DIRECCION_B):

```sh
/usr/bin/python3 faro.py ping --node A --peer DIRECCION_B --message 'Hola' --count 3
```

Esperar aproximadamente medio minuto para tres consultas correctas. Cada consulta
comprueba que B recibe el contenido y lo devuelve por luz. A devuelve estado de
salida 1 si alguna falla. No hay retransmisión automática en esta primera prueba.
Solo A inicia; B responde únicamente a consultas válidas dirigidas a él. Este
sondeo con un iniciador evita colisiones en el banco de dos Faros; no es todavía
un mecanismo de acceso para múltiples iniciadores.

En dos Pi, usar A en una y B en otra; cada una debe tener instalada su copia.
Para rotar dirección, detener ambos procesos y ejecutar `faro.py rotate --node A`
o `--node B`; volver a configurar `--peer`. No rotar durante una consulta.

El pulsador detiene el Faro correspondiente y enciende ambos indicadores mientras
el proceso permanece activo. Reiniciar el proceso tras soltarlo. Esta prueba no
almacena ni genera llaves. **No implementa todavía el zeroize criptográfico del
proyecto**: borrar objetos Python no garantiza borrar memoria, swap o copias en SD.
No usar esta prueba para transmitir información privada.

## Trama v1 (128 bytes totales)

| Campo | Bytes |
|---|---:|
| Sincronización A5 5A A5 5A | 4 |
| Versión = 1 | 1 |
| Tipo: consulta = 1, respuesta = 2 | 1 |
| Dirección origen | 6 |
| Dirección destino | 6 |
| Secuencia big endian | 2 |
| Longitud del contenido | 1 |
| Contenido y relleno cero | 105 |
| CRC-16/CCITT-FALSE big endian | 2 |

CRC sobre los primeros 126 bytes, polinomio 0x1021, inicial 0xFFFF, sin reflexión
ni XOR final. El padding mantiene tamaño fijo pero no aporta cifrado ni anonimato.
La biblioteca admite bytes externos hasta 105 bytes; la fragmentación de paquetes
mesh mayores queda pendiente. La dirección del Faro identifica el enlace, no debe
convertirse en identificador global del usuario en la futura mesh.

## Validación y paso a placa perforada

1. Con todo apagado, verificar continuidad y ausencia de cortos entre 3V3 y GND.
2. Alimentar sin GPIO RX conectado y medir las tensiones del detector con y sin luz.
3. Apagar, conectar RX y probar consulta/respuesta. Probar también con el haz tapado:
   deben fallar las consultas. Probar pánico en cada placa.
4. Repetir con luz normal a **tres distancias distintas**, por ejemplo 1, 3 y 5 cm.
   Registrar distancias reales, cantidad de consultas, errores y goodput.
5. La proporción de consultas fallidas y los errores CRC **no son BER**. Queda
   pendiente una prueba de patrón conocido que cuente bits erróneos y documente
   por separado pérdidas de sincronización; no inventar ese resultado.
6. Solo tras pasar la prueba, transferir los dos circuitos a placas separadas.
   El éxito en protoboard no garantiza el éxito después de soldar: las placas
   de islas no tienen las uniones internas de una protoboard. Reproducir cada
   conexión con puentes y revisar posibles cortos antes de energizar.
   Colocar emisor/receptor en el borde, con separación y pantallas opacas. Usar
   headers desmontables hacia la Pi, rieles claramente marcados y socket si se
   añade un comparador. En placas de tiras cortar pistas según el diseño definitivo.
7. Repetir mediciones y fotografiar ambas caras. Todavía falta el esquemático CAD
   final, que depende del modelo real del detector y del transistor.

### Material mínimo por placa

1 LED IR, 1 fototransistor NPN confirmado, 1 PN2222A, resistencias 330 ohm,
2,2 kohm, 100 kohm, 10 kohm y dos de 1 kohm, 2 LEDs visibles, 1 pulsador,
1 condensador 100 nF, headers, cables y placa perforada.
Verificar disponibilidad de LEDs indicadores y pulsadores: no se distinguen en
las fotografías. El BOM final debe incluir costos reales en colones; no se
convierten precios de la captura sin moneda/tipo de cambio confirmados.
