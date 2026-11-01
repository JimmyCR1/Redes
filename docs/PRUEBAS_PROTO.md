# Pruebas de protoboard antes de pasar a placa perforada

## Diferencia con los archivos enviados

Los originales `emisor.py` y `receptor.py` usaban `/dev/serial0` mediante pyserial:
TX en GPIO14 (fisico 8) y RX en GPIO15 (fisico 10). El original del emisor usaba
GPIO17 como indicador. Eso no coincide con el montaje probado (GPIO17 emisor IR,
GPIO27 receptor, GPIO22/23 indicadores). Ademas, no compensaban explicitamente la
inversion del fototransistor ni verificaban CRC; el receptor delimitaba mensajes
con un segundo de silencio y acumulaba un buffer sin limite.

Se adaptaron los nombres de programa para reutilizar DispositivoLuzAdaptador,
las tramas de 128 bytes, el CRC y los GPIO actuales. Se mantienen **300 baudios**,
que ya dieron una recepcion local correcta; no se usa el valor 1200 de los originales.
No habilitar UART ni mover el cableado a GPIO14/15. No instalar pyserial/gpiozero
para estos programas. Los archivos adjuntos originales no se modificaron.

## Preparar la Raspberry A

Actualizar desde la carpeta del repositorio que contiene `faro.py`:

```sh
git pull --ff-only
sudo systemctl start pigpiod
python3 -m unittest discover -s tests -v
```

Las 16 pruebas se ejecutan sin hardware: verifican el protocolo, la prueba local
con transporte simulado y la conectividad lógica del plano. No acreditan temporizacion
GPIO, sensibilidad, soldadura ni intercambio fisico entre dos Raspberry.

Cerrar antes cualquier sesion Python que tenga un adaptador abierto usando
`faro.close()` y `exit()`. No ejecutar dos programas que posean los mismos GPIO
o usen las ondas de pigpio a la vez. Ejecutar unicamente la prueba indicada.

## Una Raspberry: emisor A apuntando al receptor A

Conservar el circuito que recibio `Hola Faro`. Usar LED IR transparente y PT333 negro,
330 ohm para el LED IR, 2,2 kohm hacia la base, 10 kohm de base a GND y 10 kohm en
el receptor. **C17/B20 es un jumper**. Las dos resistencias de 1 kohm de indicadores
permanecen. No dejar los puentes de diagnostico ni la resistencia temporal de
330 ohm en la posicion de la de 2,2 kohm. Ver MONTAJE_CONFIRMADO.md.

```sh
python3 prueba_proto.py --count 5
```

Esperado: cinco resultados `OK`, `5/5 correctas`
y `PRUEBA OPTICA LOCAL CORRECTA`. Tarda unos 22 segundos en condiciones
correctas; las perdidas agregan hasta 3 segundos de espera por trama. El programa
termina con codigo 1 si no recibe exactamente todas las tramas enviadas.

Tapar el camino de luz con una tarjeta opaca, sin mover cables. Ejecutar:

```sh
python3 prueba_proto.py --count 2 --tapado
```

Esperado: `0/2 correctas` y `PRUEBA CON HAZ TAPADO CORRECTA`. Este resultado por si solo
no prueba nada: un circuito apagado tambien lo produciria. Destapar y repetir la
prueba normal; debe pasar nuevamente.

Para comprobar la parada fisica, iniciar la prueba normal y presionar el boton
durante un envio. Debe interrumpirse por panico; no cuenta como prueba aprobada.
Al cerrar el programa se apagan los indicadores. Soltar el boton y reiniciar la
prueba para continuar. Esta parada no es todavia el zeroize criptografico completo.

Guardar resultados reales de distancia, iluminacion, correctas, ausentes y errores
CRC. Estos errores NO son BER. Las mediciones de BER del proyecto siguen pendientes.

## Dos Raspberry: emisor.py y receptor.py

Ambas usan los mismos GPIO en equipos independientes. No ejecutar ambos programas
en la misma Raspberry: abririan el mismo receptor y controlarian las mismas salidas.
No requieren Internet durante la comunicacion optica. A apunta su emisor a B y B
apunta su emisor a A. Aislar los caminos con carton opaco para reducir reflejos locales.

Obtener las direcciones una sola vez por dispositivo:

```sh
# En Raspberry A
python3 faro.py address --node A
# En Raspberry B
python3 faro.py address --node B
```

En B, sustituir DIRECCION_A por los 12 caracteres hexadecimales impresos en A:

```sh
python3 receptor.py --peer DIRECCION_A
```

En A, sustituir DIRECCION_B por los impresos en B:

```sh
python3 emisor.py 'Hola Faro' --peer DIRECCION_B --count 5
```

Esperado: cinco consultas `OK` y `5/5` (unos 45 segundos). Cada consulta incluye ida
optica y respuesta optica. El programa solo acepta la respuesta del peer esperado,
la misma secuencia y el mismo contenido con CRC valido. El receptor devuelve los
bytes sin guardarlos en disco. Ctrl+C cierra el respondedor. No es una aplicacion
de chat ni cifrado; es una prueba del enlace.

## Antes de soldar

- Prueba local repetida y control tapado/destapado satisfactorios en cada circuito.
- Verificar A/B antes de considerar demostrada la comunicacion entre nodos.
- Mantener un esquema anotado con componentes y conexiones realmente utilizados,
  incluyendo el boton en D30/D32/G30/G32, señal en C30 y GND C32/I2 del Faro A.
- Conseguir un multimetro para continuidad, ausencia de cortos y voltajes, como
  exige el enunciado. Resolver cualquier aviso de bajo voltaje de la Raspberry.
- Tras soldar, comprobar las conexiones con la alimentacion desconectada antes de
  energizar. Las islas o tiras de la placa no equivalen a las filas de la protoboard.
- Repetir las pruebas despues de soldar. Un montaje correcto en protoboard no
  garantiza que no haya errores de soldadura.

Falta completar el resto de FaroNet: mesh, privacidad, aplicacion y Worker. Esta
prueba solo valida la parte del enlace que efectivamente se ejecute y pase.
