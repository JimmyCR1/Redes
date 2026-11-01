"""Comprueba conectividad prevista, no continuidad física ni patillajes reales."""
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def col_num(label):
    result=0
    for letter in label:result=result*26+ord(letter)-64
    return result

def coord(pad):
    match=re.fullmatch(r'([A-Z]+)([0-9]{2})',pad)
    if not match:raise ValueError(pad)
    return col_num(match[1]),int(match[2])

def verify(data):
    parent={}
    def find(x):
        parent.setdefault(x,x)
        if parent[x]!=x:parent[x]=find(parent[x])
        return parent[x]
    def join(a,b):parent[find(a)]=find(b)
    parts={p['id']:p for p in data['parts']}
    occupied={}
    for p in parts.values():
        for terminal,pad in p['pins'].items():
            assert pad not in occupied, f'Dos piezas en {pad}'
            occupied[pad]=f"{p['id']}.{terminal}"
            c,r=coord(pad)
            assert 1<=c<=33 and 1<=r<=48,pad
    bus_pads=set()
    for bus in data['buses']:
        ca,ra=coord(bus['a']);cb,rb=coord(bus['b'])
        assert ca==cb
        column=re.match('[A-Z]+',bus['a'])[0]
        for row in range(ra,rb+1):
            pad=f'{column}{row:02}'
            assert pad not in occupied,f'Componente invade barra: {pad}'
            assert pad not in bus_pads,f'Barras coinciden: {pad}'
            bus_pads.add(pad);join(bus['a'],pad)
    labels=set()
    for wire in data['wires']:
        assert wire['id'] not in labels
        labels.add(wire['id'])
        for pad in (wire['a'],wire['b']):
            assert pad in occupied or pad in bus_pads,f'Extremo sin terminal: {wire}'
        for pad in wire['via']:
            c,r=coord(pad);assert 1<=c<=33 and 1<=r<=48,pad
        join(wire['a'],wire['b'])
    roots={}
    def pad_of(terminal):
        id,pin=terminal.split('.')
        return parts[id]['pins'][pin]
    for name,terminals in data['nets'].items():
        connected={find(pad_of(t)) for t in terminals}
        assert len(connected)==1,f'Red incompleta: {name}'
        root=connected.pop()
        assert root not in roots,f'Corto entre {name} y {roots.get(root)}'
        roots[root]=name
    for wire in data['wires']:
        assert roots[find(wire['a'])]==wire['net'],wire
    for name in ('libre1','libre2'):
        pad=parts['SW1']['pins'][name]
        assert all(pad not in (w['a'],w['b']) for w in data['wires'])
    assert len(data['wires'])==24 and len(data['buses'])==2
    assert parts['R1']['value']=='330 Ω'
    assert parts['R2']['value']=='2,2 kΩ'
    assert parts['R3']['value']==parts['R4']['value']=='10 kΩ'
    assert parts['R5']['value']==parts['R6']['value']=='1 kΩ'
    assert (coord('T33')[0]-coord('O33')[0])*2.54==12.7
    assert (coord('O35')[1]-coord('O33')[1])*2.54==5.08
    import sys
    sys.path.insert(0,str(ROOT))
    from faro import PINS
    mapping={p['name']:p['bcm'] for p in data['raspberry']}
    assert tuple(mapping[k] for k in ('TX','RX','TX_LED','RX_LED','PANIC'))==PINS['A']==PINS['B']
    for pin in data['raspberry']:
        assert parts['J1']['pins'][pin['name']]==pin['pad']
    return len(roots)

if __name__=='__main__':
    data=json.loads((ROOT/'docs/placa/diseno.json').read_text())
    print(f'OK: {verify(data)} redes separadas, 24 cables, 2 barras, agujeros sin piezas duplicadas, GPIO coincidentes. No es una prueba eléctrica.')
