"""Prueba local de un Faro: su LED IR apunta a su propio PT333 en la misma protoboard.

Ejecutar en la Raspberry, desde la carpeta del repositorio:
    python3 prueba_proto.py --count 5   # haz destapado: deben llegar todas
    python3 prueba_proto.py --tapado    # haz tapado con cartón: no debe llegar ninguna
"""
import argparse
import time
from DispositivoLuzAdaptador import DispositivoLuzAdaptador, decode, encode
from faro import PINS

# Direcciones fijas: solo para esta prueba local, no se guardan.
ORIGEN = bytes.fromhex('020000000001')
DESTINO = bytes.fromhex('020000000002')


def estatica(device):
    """Lee el receptor con el emisor apagado y encendido. Con luz: (1, 0)."""
    device.pi.write(device.tx, 0)
    time.sleep(.2)
    apagado = device.pi.read(device.rx)
    device.pi.write(device.tx, 1)
    time.sleep(.2)
    encendido = device.pi.read(device.rx)
    return apagado, encendido


def vaciar(device):
    """Descarta bytes y tramas viejas para no confundirlas con la siguiente."""
    while device.receive(.3) is not None:
        pass


def intercambio(device, count):
    correctas = 0
    for seq in range(count):
        trama = encode(ORIGEN, DESTINO, seq, f'Hola Faro {seq + 1}'.encode())
        vaciar(device)
        inicio = time.monotonic()
        device.send(trama)
        ok = device.receive(3) == decode(trama)
        correctas += ok
        print(f'Trama {seq + 1}/{count}: {"OK" if ok else "NO LLEGO"} '
              f'({time.monotonic() - inicio:.1f} s)')
    return correctas


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--count', type=int, default=5)
    parser.add_argument('--tapado', action='store_true',
                        help='El haz está tapado: se espera que no llegue ninguna trama')
    args = parser.parse_args()
    if not 1 <= args.count <= 100:
        parser.error('count entre 1 y 100')
    device = DispositivoLuzAdaptador(*PINS['A'])
    try:
        apagado, encendido = estatica(device)
        print(f'Receptor con emisor apagado={apagado}, encendido={encendido}')
        if not args.tapado and (apagado, encendido) != (1, 0):
            print('El receptor no ve el emisor: revisa que las puntas se miren '
                  'a 5-10 mm y que nada tape el camino. Se esperaba 1 y 0.')
            raise SystemExit(1)
        if args.tapado and encendido == 0:
            print('Aviso: el receptor todavía detecta luz con el haz tapado.')
        print(f'Enviando {args.count} tramas; cada una tarda unos 4-5 segundos...')
        correctas = intercambio(device, args.count)
        print(f'{correctas}/{args.count} correctas; tramas descartadas por '
              f'CRC/cabecera={device.parser.errors}')
        if args.tapado:
            if correctas:
                print('FALLO: llegaron tramas con el haz tapado.')
                raise SystemExit(1)
            print('PRUEBA CON HAZ TAPADO CORRECTA')
        else:
            if correctas != args.count:
                print('FALLO: no llegaron todas las tramas.')
                raise SystemExit(1)
            print('PRUEBA OPTICA LOCAL CORRECTA')
    except RuntimeError as error:
        print(f'Detenido: {error}')
        raise SystemExit(1)
    finally:
        device.close()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
