import tempfile
import unittest
from pathlib import Path
from DispositivoLuzAdaptador import *


class ProtocolTests(unittest.TestCase):
    def setUp(self):
        self.a, self.b = bytes.fromhex('020000000001'), bytes.fromhex('020000000002')

    def test_roundtrip_and_fixed_size(self):
        for data in (b'', 'Hola Costa Rica'.encode(), bytes(range(105))):
            frame = encode(self.a, self.b, 65535, data)
            self.assertEqual(len(frame), 128)
            self.assertEqual(decode(frame), (self.a, self.b, 65535, data, REQUEST))

    def test_every_single_bit_error_rejected(self):
        frame = encode(self.a, self.b, 1, b'prueba')
        for bit in range(1024):
            damaged = bytearray(frame)
            damaged[bit // 8] ^= 1 << (bit % 8)
            with self.assertRaises(ValueError):
                decode(damaged)

    def test_stream_recovers_after_noise_and_corruption(self):
        frame = encode(self.a, self.b, 2, b'ok')
        bad = bytearray(frame)
        bad[50] ^= 1
        parser = Parser()
        results = []
        for byte in b'noise' + bad + frame + frame:
            results += parser.feed(bytes([byte]))
        self.assertEqual(results, [decode(frame), decode(frame)])
        self.assertEqual(parser.errors, 1)
        self.assertEqual(parser.last_bad, bytes(bad))

    def test_version_rejected_even_with_valid_crc(self):
        frame = bytearray(encode(self.a, self.b, 1, b'x'))
        frame[4] = 2
        frame[-2:] = binascii.crc_hqx(frame[:-2], 0xffff).to_bytes(2, 'big')
        with self.assertRaises(ValueError):
            decode(frame)

    def test_oversize(self):
        with self.assertRaises(ValueError):
            encode(self.a, self.b, 0, b'x' * 106)

    def test_persistent_and_rotating_address(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'node.addr'
            first = address(path)
            self.assertEqual(first, address(path))
            second = address(path, rotate=True)
            self.assertNotEqual(first, second)
            self.assertEqual(address(path), second)


if __name__ == '__main__':
    unittest.main()
