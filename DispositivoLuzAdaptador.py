"""Faro v1: prueba óptica de consulta/respuesta; no implementa la mesh.

Requiere pigpiod en la Raspberry Pi. La importación y el códec no requieren GPIO.
"""
import binascii
import os
from pathlib import Path
import struct
import time

SYNC = b'\xa5\x5a\xa5\x5a'
VERSION = 1
FRAME_SIZE = 128
PAYLOAD_SIZE = 105
HEADER = struct.Struct('!4sBB6s6sHB')
# Byte de relleno tras cada trama: el lector de pigpio cierra un byte en el
# siguiente cambio de luz; sin él, los últimos bits en 1 del CRC se leían como 0.
TRAILER = b'\x00'
REQUEST, RESPONSE = 1, 2


def encode(src, dst, seq, payload, kind=REQUEST):
    if len(src) != 6 or len(dst) != 6:
        raise ValueError('Las direcciones deben tener 6 bytes')
    if len(payload) > PAYLOAD_SIZE:
        raise ValueError('Máximo 105 bytes de contenido')
    if kind not in (REQUEST, RESPONSE):
        raise ValueError('Tipo desconocido')
    body = HEADER.pack(SYNC, VERSION, kind, src, dst, seq, len(payload))
    body += payload.ljust(PAYLOAD_SIZE, b'\0')
    return body + struct.pack('!H', binascii.crc_hqx(body, 0xffff))


def decode(frame):
    if len(frame) != FRAME_SIZE:
        raise ValueError('Tamaño incorrecto')
    if binascii.crc_hqx(frame[:-2], 0xffff) != int.from_bytes(frame[-2:], 'big'):
        raise ValueError('CRC incorrecto')
    sync, version, kind, src, dst, seq, size = HEADER.unpack(frame[:HEADER.size])
    if sync != SYNC or version != VERSION or kind not in (REQUEST, RESPONSE):
        raise ValueError('Cabecera no soportada')
    if size > PAYLOAD_SIZE:
        raise ValueError('Longitud inválida')
    return src, dst, seq, frame[HEADER.size:HEADER.size + size], kind


class Parser:
    def __init__(self):
        self.buffer = bytearray()
        self.errors = 0
        self.last_bad = None  # Última trama rechazada, para diagnóstico.

    def feed(self, data):
        self.buffer.extend(data)
        result = []
        while True:
            start = self.buffer.find(SYNC)
            if start < 0:
                self.buffer[:] = self.buffer[-3:]
                break
            del self.buffer[:start]
            if len(self.buffer) < FRAME_SIZE:
                break
            try:
                frame = decode(bytes(self.buffer[:FRAME_SIZE]))
            except ValueError:
                self.errors += 1
                self.last_bad = bytes(self.buffer[:FRAME_SIZE])
                del self.buffer[0]
            else:
                del self.buffer[:FRAME_SIZE]
                result.append(frame)
        return result


def address(path, rotate=False):
    """Dirección pública persistente; NO almacenar llaves en este archivo."""
    path = Path(path).expanduser()
    if path.exists() and not rotate:
        value = bytes.fromhex(path.read_text().strip())
        if len(value) != 6:
            raise ValueError('Archivo de dirección inválido')
        return value
    path.parent.mkdir(parents=True, exist_ok=True)
    value = bytearray(os.urandom(6))
    value[0] = (value[0] | 2) & 0xfe
    temporary = path.with_suffix('.tmp')
    temporary.write_text(bytes(value).hex() + '\n')
    temporary.replace(path)
    return bytes(value)


class DispositivoLuzAdaptador:
    def __init__(self, tx, rx, tx_led, rx_led, panic, baud=300):
        import pigpio
        self.gpio = pigpio
        self.pi = pigpio.pi()
        if not self.pi.connected:
            raise RuntimeError('No se pudo conectar con pigpiod')
        self.tx, self.rx = tx, rx
        self.tx_led, self.rx_led = tx_led, rx_led
        self.panic_pin, self.baud = panic, baud
        self.stopped = False
        self.parser = Parser()
        self.pending = []
        for pin in (tx, tx_led, rx_led):
            self.pi.set_mode(pin, pigpio.OUTPUT)
            self.pi.write(pin, 0)
        self.pi.set_mode(rx, pigpio.INPUT)
        self.pi.set_pull_up_down(rx, pigpio.PUD_UP)
        self.pi.set_mode(panic, pigpio.INPUT)
        self.pi.set_pull_up_down(panic, pigpio.PUD_UP)
        self.pi.bb_serial_read_open(rx, baud, 8)
        # Fototransistor: luz -> nivel bajo. UART: reposo -> nivel alto.
        self.pi.bb_serial_invert(rx, 1)
        self.pi.set_glitch_filter(panic, 10000)
        self.callback = self.pi.callback(panic, pigpio.FALLING_EDGE, self._panic)
        self.pi.write(tx, 1)  # Reposo óptico encendido, limitado por resistencia.
        if self.pi.read(panic) == 0:
            self._panic(panic, 0, 0)

    def _panic(self, pin, level, tick):
        self.stopped = True
        self.pi.wave_tx_stop()
        self.pi.write(self.tx, 0)
        self.parser.buffer.clear()
        self.pending.clear()
        self.pi.write(self.tx_led, 1)
        self.pi.write(self.rx_led, 1)

    def check(self):
        if self.stopped:
            raise RuntimeError('Pánico activado: reinicia el proceso para continuar')

    def send(self, frame):
        self.check()
        decode(frame)
        self.pi.write(self.tx_led, 1)
        self.pi.wave_add_new()
        self.pi.wave_add_serial(self.tx, self.baud, frame + TRAILER, offset=10000)
        wave = self.pi.wave_create()
        try:
            self.check()
            self.pi.wave_send_once(wave)
            while self.pi.wave_tx_busy():
                self.check()
                time.sleep(.01)
            self.check()
        finally:
            self.pi.wave_delete(wave)
            if not self.stopped:
                self.pi.write(self.tx_led, 0)

    def receive(self, timeout=8):
        end = time.monotonic() + timeout
        while time.monotonic() < end:
            self.check()
            if self.pending:
                self.pi.write(self.rx_led, 1)
                result = self.pending.pop(0)
                time.sleep(.05)
                self.pi.write(self.rx_led, 0)
                return result
            count, data = self.pi.bb_serial_read(self.rx)
            if count:
                self.pending.extend(self.parser.feed(data))
            time.sleep(.005)
        return None

    def close(self):
        self.callback.cancel()
        self.pi.bb_serial_read_close(self.rx)
        for pin in (self.tx, self.tx_led, self.rx_led):
            self.pi.write(pin, 0)
        self.pi.stop()
