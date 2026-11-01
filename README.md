# Redes
VIVA CRISTO REY 

## FaroNet: primera prueba óptica

Empezar por [la guía de montaje y ejecución](docs/PRIMERA_PRUEBA.md).
Abrir [el montaje interactivo en protoboard](docs/protoboard.html) en un navegador
para seleccionar Faro A/B y seguir las conexiones por pasos, sin Internet.
El [alcance](docs/ALCANCE.md) distingue esta prueba del proyecto completo.

Código: `DispositivoLuzAdaptador.py` y `faro.py`. Pruebas sin hardware:

```sh
python3 -m unittest discover -s tests -v
```

La electrónica y el controlador pigpio requieren validación en Raspberry Pi 2.

### Prueba de un Faro en una sola protoboard

El montaje que ya funcionó está en [docs/MONTAJE_CONFIRMADO.md](docs/MONTAJE_CONFIRMADO.md).
Con el LED IR apuntando al PT333 del mismo Faro:

```sh
python3 prueba_proto.py --count 5        # espera: PRUEBA OPTICA LOCAL CORRECTA
python3 prueba_proto.py --count 2 --tapado  # espera: PRUEBA CON HAZ TAPADO CORRECTA
```

Para probar el proyecto de JuankGO con este mismo circuito: [parches/LEEME.md](parches/LEEME.md).

## Plano detallado de soldadura HS-03

Abrir el [plano interactivo](docs/placa/index.html) descargado en el navegador,
o imprimir el [PDF de tres hojas](docs/placa/FaroNet-HS03-plano.pdf) al 100 %.
La [guía de soldadura](docs/placa/MONTAJE.md) explica las dos caras, las
coordenadas de cada pieza, las barras, los 24 cables y las comprobaciones físicas.
La distribución sirve para ambas Raspberry con los mismos GPIO.
Este plano tiene coordenadas propias: no mezclar sus agujeros con los de
`docs/placa-perforada.html`, que conserva la distribución anterior.

```sh
python3 tools/verificar_placa.py
```

Para usar los scripts `emisor.py` y `receptor.py` en dos Raspberry independientes,
consultar [PRUEBAS_PROTO](docs/PRUEBAS_PROTO.md).
