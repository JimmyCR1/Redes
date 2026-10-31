"""CLI mínima: A consulta; B solo responde. No enviar desde ambos a la vez."""
import argparse
import time
from DispositivoLuzAdaptador import (
    DispositivoLuzAdaptador, address, encode, REQUEST, RESPONSE,
)

# Mismo cableado en ambos Faros: cada uno va en su propia Raspberry.
PINS = {'A': (17, 27, 22, 23, 24), 'B': (17, 27, 22, 23, 24)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['address', 'rotate', 'serve', 'ping'])
    parser.add_argument('--node', required=True, choices=PINS)
    parser.add_argument('--state', help='Archivo de dirección pública persistente')
    parser.add_argument('--peer', help='Dirección hexadecimal del otro Faro')
    parser.add_argument('--message', default='Hola Faro')
    parser.add_argument('--count', type=int, default=3)
    args = parser.parse_args()
    state = args.state or f'~/.local/state/faronet/{args.node}.addr'
    own = address(state, args.command == 'rotate')
    if args.command in ('address', 'rotate'):
        print(own.hex())
        return
    if (args.command == 'ping' and args.node != 'A') or (args.command == 'serve' and args.node != 'B'):
        parser.error('Acceso al medio: A ejecuta ping y B ejecuta serve')
    try:
        peer = bytes.fromhex(args.peer or '')
    except ValueError:
        parser.error('--peer debe ser hexadecimal')
    if len(peer) != 6:
        parser.error('--peer debe contener 12 caracteres hexadecimales')
    payload = args.message.encode('utf-8')
    if len(payload) > 105 or not 1 <= args.count <= 65536:
        parser.error('Máximo 105 bytes UTF-8; count entre 1 y 65536')
    device = DispositivoLuzAdaptador(*PINS[args.node])
    try:
        if args.command == 'serve':
            print('B listo. Ctrl+C para salir. No se guardan mensajes.')
            while True:
                frame = device.receive()
                if frame:
                    src, dst, seq, data, kind = frame
                    if src == peer and dst == own and kind == REQUEST:
                        time.sleep(.1)
                        device.send(encode(own, peer, seq, data, RESPONSE))
        else:
            passed = 0
            start = time.monotonic()
            for seq in range(args.count):
                device.send(encode(own, peer, seq, payload))
                deadline = time.monotonic() + 8
                ok = False
                while time.monotonic() < deadline:
                    frame = device.receive(max(.01, deadline - time.monotonic()))
                    if frame == (peer, own, seq, payload, RESPONSE):
                        ok = True
                        break
                passed += ok
                print(f'Consulta {seq + 1}: {"OK" if ok else "sin respuesta válida"}')
                time.sleep(.2)
            elapsed = time.monotonic() - start
            print(f'{passed}/{args.count}; errores CRC/cabecera={device.parser.errors}; '
                  f'goodput ida/vuelta={passed * len(payload) * 8 / elapsed:.2f} bit/s')
            if passed != args.count:
                raise SystemExit(1)
    finally:
        device.close()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
