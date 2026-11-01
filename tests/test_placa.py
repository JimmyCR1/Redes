"""Detecta omisiones/cortos en el plano, sin confundirlo con una prueba física."""
import copy
import json
from pathlib import Path
import unittest
from tools.verificar_placa import verify

class PlacaTests(unittest.TestCase):
    def setUp(self):
        self.data=json.loads((Path(__file__).resolve().parents[1]/'docs/placa/diseno.json').read_text())
    def test_redes_del_esquema_completas_y_separadas(self):
        self.assertEqual(verify(self.data),12)
    def test_detecta_cable_de_base_omitido(self):
        self.data['wires']=[w for w in self.data['wires'] if w['id']!='W16']
        with self.assertRaises(AssertionError):verify(self.data)
    def test_detecta_corto_alimentacion_masa(self):
        self.data['wires'].append(dict(id='W25',a='N43',b='O43',net='GND',via=[]))
        with self.assertRaises(AssertionError):verify(self.data)
    def test_detecta_piezas_en_el_mismo_agujero(self):
        self.data['parts'][1]['pins']['C']='H05'
        with self.assertRaises(AssertionError):verify(self.data)

if __name__=='__main__':unittest.main()
