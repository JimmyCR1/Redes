# Probar el proyecto de JuankGO con nuestro Faro (GPIO 17/27)

Repositorio original: https://github.com/JuankGO/redes-proyecto1-faronet
(probado sobre su commit `c7a3b9b`).

Su código usa la UART de hardware (`/dev/ttyAMA0`, GPIO 14/15) y un receptor
que da 1 con luz. Nuestro circuito usa GPIO 17/27 y el receptor da 0 con luz.
`juank-pigpio.patch` le agrega `--uart pigpio`, sin cambiar el resto:

| Cambio | Archivo |
|---|---|
| Puerto serie por pigpio en GPIO17 (TX) y GPIO27 (RX invertido) | `faro/serie_pigpio.py` (nuevo) |
| `--uart pigpio` usa ese puerto en todas sus herramientas | `faro/medio.py` |
| LEDs en GPIO 22/23 y botón en GPIO 24 | `faro/gpio.py` |
| Pruebas sin hardware del puerto pigpio | `tests/test_serie_pigpio.py` (nuevo) |

También agrega un byte de relleno al final de cada envío, por el mismo
problema del último byte que encontramos con `prueba_proto.py`.

No hace falta activar la UART con `raspi-config`: pigpio no la usa.

## En la Raspberry

```sh
sudo apt install -y python3-nacl python3-serial python3-gpiozero python3-pytest
cd ~/faronet-github && git pull --ff-only
cd ~
git clone https://github.com/JuankGO/redes-proyecto1-faronet.git faronet-juank
cd faronet-juank
git checkout -b pigpio c7a3b9b
git apply ~/faronet-github/parches/juank-pigpio.patch
python3 -m pytest tests -q
```

Esperado: `140 passed` (sus 135 + 5 nuevas). En la Pi 2 puede tardar unos minutos.

Prueba óptica con un solo Faro (LED IR apuntando a su propio PT333):

```sh
python3 -m faro.medir loopback --uart pigpio --baudios 1200 --tramas 10
```

Cada trama debe decir `OK` y al final `BER: 0.00e+00`. Cada trama tarda unos 2 s.
Si hay errores, probar `--baudios 300` (la velocidad que ya funcionó, unos 9 s por trama).
En todas sus demás herramientas, usar `--uart pigpio` en lugar de `--uart /dev/ttyAMA0`
y el mismo `--baudios` en ambos Faros.
