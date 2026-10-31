import unittest
from DispositivoLuzAdaptador import decode
from prueba_proto import diferencias, intercambio, vaciar


class Espejo:
    """Simula emisor y receptor enfrentados: lo que se envía, llega."""
    def __init__(self, tapado=False):
        self.tapado = tapado
        self.pending = []

    def send(self, frame):
        if not self.tapado:
            self.pending.append(decode(frame))

    def receive(self, timeout=8):
        return self.pending.pop(0) if self.pending else None


class PruebaProtoTests(unittest.TestCase):
    def test_haz_destapado_llegan_todas(self):
        self.assertEqual(intercambio(Espejo(), 5), 5)

    def test_haz_tapado_no_llega_ninguna(self):
        self.assertEqual(intercambio(Espejo(tapado=True), 5), 0)

    def test_trama_vieja_no_cuenta_como_nueva(self):
        device = Espejo(tapado=True)
        device.pending.append(('vieja',))
        self.assertEqual(intercambio(device, 1), 0)

    def test_diferencias_marca_bytes_danados(self):
        self.assertEqual(diferencias(b'\x01\x02\x03', b'\x01\x06\x03'), [(1, 2, 6)])

    def test_vaciar_descarta_pendientes(self):
        device = Espejo()
        device.pending += [('a',), ('b',)]
        vaciar(device)
        self.assertEqual(device.pending, [])


if __name__ == '__main__':
    unittest.main()
