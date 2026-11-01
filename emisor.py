"""Iniciador A sobre el montaje óptico probado: GPIO 17 TX y GPIO 27 RX.

Usar receptor.py en OTRA Raspberry. Para una sola Raspberry: prueba_proto.py.
"""
import argparse
import sys
import faro


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mensaje', help='Texto UTF-8, máximo 105 bytes')
    parser.add_argument('--peer', required=True, help='Dirección del Faro B, 12 hexadecimales')
    parser.add_argument('--count', type=int, default=5)
    args = parser.parse_args(argv)
    return faro.main(['ping', '--node', 'A', '--peer', args.peer,
                      '--message', args.mensaje, '--count', str(args.count)])


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
    except RuntimeError as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
