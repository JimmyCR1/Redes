# Montaje confirmado del Faro A (protoboard MB102)

Este es el montaje real que funcionó en la protoboard: indicadores, botón,
transistor y una trama "Hola Faro" recibida por luz con CRC correcto.
**Reemplaza** a la guía preliminar donde no coincidan (resistencia de 100 kΩ,
par SEN-00241, pines distintos para B y posición del botón).

El Faro B se arma igual, en su propia Raspberry y con los mismos pines.

## Pines de la Raspberry (iguales en A y B)

| Señal | BCM (programa) | Pin físico | Agujero |
|---|---|---|---|
| 3,3 V | — | 1 | b1 |
| GND | — | 6 | a2 |
| TX, emisor IR | 17 | 11 | a10 |
| RX, receptor PT333 | 27 | 13 | a22 |
| Indicador TX | 22 | 15 | f4 |
| Indicador RX | 23 | 16 | f10 |
| Botón | 24 | 18 | c30 |

No usar los pines físicos 2 ni 4: son 5 V.

## Componentes

| Componente | Posición | Nota |
|---|---|---|
| LED IR transparente redondo | ánodo e6, cátodo e8 | emite |
| PT333 negro redondo | pata larga (E) e20, pata corta (C) e22 | recibe |
| 2N2222A | 1/E e12, 2/B e13, 3/C e14 | patillaje según la imagen de referencia |
| 330 Ω | a1 → a6 | limita corriente del LED IR |
| 2,2 kΩ | c10 → c13 | resistencia de base |
| **10 kΩ** | d13 → d17 | base a GND (sustituye a la de 100 kΩ) |
| 10 kΩ | c22 → c26 | pull-up del receptor |
| 1 kΩ | h4 → h6 | indicador TX |
| 1 kΩ | h10 → h12 | indicador RX |
| LED visible TX | ánodo j6, cátodo j8 | |
| LED visible RX | ánodo j12, cátodo j14 | |
| Condensador cerámico 100 nF (104) | d1 → d2 | sin polaridad |
| Pulsador de 4 patas | d30, d32, g30, g32 | atraviesa el canal central |

## Puentes (jumpers macho–macho)

| Puente | Función |
|---|---|
| e2 → f2 | GND al lado derecho de la fila 2 |
| a20 → c2 | GND a la fila del PT333 |
| a26 → e1 | 3,3 V a la resistencia del receptor |
| a8 → a14 | cátodo del LED IR al colector del transistor |
| b12 → b2 | emisor del transistor a GND |
| c17 → b20 | GND a la resistencia de base (**cable, no resistencia**) |
| f8 → g2 | cátodo del indicador TX a GND |
| f14 → h2 | cátodo del indicador RX a GND |
| c32 → i2 | botón a GND |

## Alineación

Las puntas del LED IR y del PT333 deben mirarse entre sí, a unos 5–10 mm, sin
tocarse. Si ambos apuntan hacia arriba, el receptor lee siempre 1.

Para dos Faros: emisor A → receptor B y emisor B → receptor A. Separar los dos
caminos con cartón o un tubito opaco para que cada receptor no vea a su propio emisor.

## Pruebas en la Raspberry

```sh
cd ~/faronet-github
git pull --ff-only
python3 -m unittest discover -s tests -v
python3 prueba_proto.py --count 5
```

Esperado: `5/5 correctas` y `PRUEBA OPTICA LOCAL CORRECTA`.

Luego tapa el camino de luz con cartón y ejecuta:

```sh
python3 prueba_proto.py --count 2 --tapado
```

Esperado: `0/2 correctas` y `PRUEBA CON HAZ TAPADO CORRECTA`.

Con el botón presionado durante la prueba debe aparecer `Detenido: Pánico activado`
y encenderse los dos indicadores.

## Al pasar a placa perforada

- En una placa de islas los agujeros no están unidos como en la protoboard:
  cada "fila" se vuelve un puente de estaño o alambre. Replicar las uniones, no
  las posiciones.
- Usar headers hembra hacia la Raspberry para poder desconectarla.
- Dejar el LED IR y el PT333 en el borde de la placa para poder enfrentarlos.
- Antes de energizar: revisar que no haya cortos entre 3,3 V y GND, idealmente
  con un multímetro prestado. Después repetir las pruebas de arriba.
