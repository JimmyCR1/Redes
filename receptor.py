"""Respondedor B sobre el montaje óptico probado: GPIO 17 TX y GPIO 27 RX.

Devuelve cada consulta válida por luz. Usar emisor.py en OTRA Raspberry.
"""
import argparse
import sys
import faro


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--peer', required=True, help='Dirección del Faro A, 12 hexadecimales')
    args = parser.parse_args(argv)
    return faro.main(['serve', '--node', 'B', '--peer', args.peer])


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
    except RuntimeError as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
