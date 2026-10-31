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
