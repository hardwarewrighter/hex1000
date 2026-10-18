#!/usr/bin/env python3
"""Generate the physical-header cable map; reject assignments absent from headers."""
import base64
import json
from pathlib import Path
from html import escape

ROOT = Path(__file__).resolve().parent.parent
LEFT = ['13','5V','5V','GND','GND','47','45','46','11','9','10','24','23','22','18','17','16','15','27','28']
RIGHT = ['44','GND','GND','3V3','3V3','BL702-30','BL702-29','BL702-26','40','41','38','39','42','35','34','20','19','29','30','31']
YS = [82,103,123,144,164,185,206,226,247,268,289,309,330,351,371,392,413,433,454,475]
COLORS = {'row':'#1769aa','col':'#087f5b','op':'#8034a8','spi':'#b85c00','power':'#c62828','gnd':'#202020','unused':'#70777f'}
net = json.loads((ROOT/'hex1000.net').read_text())
assigned = {}
for wire in net['connections']:
    if wire['from'].startswith('TANG_1K:PIN'):
        pin=wire['from'].split(':PIN')[1]
        assert pin in LEFT+RIGHT, f'FPGA pin {pin} is not on the documented side headers'
        assert pin not in assigned, f'duplicate FPGA pin {pin}'
        assigned[pin]=wire['to']
assert len(assigned)==15
assert assigned['15']=='KEYPAD:R1' and assigned['16']=='KEYPAD:R2'
assert assigned['20']=='KEYPAD:C2' and assigned['35']=='KEYPAD:C3'

def txt(x,y,s,size=20,color='#17212b',anchor='start',weight='normal'):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{weight}">{escape(s)}</text>'
def line(x1,y1,x2,y2,color,width=3):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}"/>'
def start(w,h,title):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img"><title>{escape(title)}</title><rect width="100%" height="100%" fill="white"/><g font-family="DejaVu Sans, sans-serif">']

def label(pin):
    if pin not in assigned:
        names={'13':'Button A - leave free','44':'Button B - leave free','47':'27 MHz clock - leave free','9':'Onboard red LED - leave free','10':'Onboard blue LED - leave free','11':'Onboard green LED - leave free','42':'MODE1 - leave free'}
        return names.get(pin,'Programmer GPIO - DO NOT USE' if pin.startswith('BL702') else 'Leave free'), 'unused'
    to=assigned[pin]
    if to.startswith('KEYPAD:R'): return f'{to.split(":")[1]} keypad  (through 1 kohm)', 'row'
    if to.startswith('KEYPAD:C'): return f'{to.split(":")[1]} keypad', 'col'
    if to.startswith('BUTTON_STRIP:'):
        k=to.split(':')[1]; return f'{k} operator  ({dict(K1="+",K2="-",K3="*",K4="=")[k]})','op'
    dest={'74AHCT125:A1':'DIN via shifter pin 2','74AHCT125:A2':'CS/LOAD via shifter pin 5','74AHCT125:A3':'CLK via shifter pin 9'}
    return dest[to],'spi'

parts=start(1400,1120,'HEX1000 Tang Nano 1K physical Dupont cable map')
parts += [txt(40,43,'Tang Nano 1K: physical Dupont cable map',30,weight='bold'),txt(40,77,'Component side facing you. USB connector UP. Match the board photo; do not count chip pins.',21),txt(40,106,'Colored labels identify cables. Gray connections stay unused. Package numbers are shown for software.',18)]
photo=base64.b64encode((ROOT/'docs/images/sipeed-tangnano1k-pinmap.png').read_bytes()).decode()
parts.append(f'<svg x="560" y="125" width="240" height="690" viewBox="274 10 168 483"><image width="720" height="562" xlink:href="data:image/png;base64,{photo}"/></svg>')
parts += [txt(680,151,'USB',19,'#fff',anchor='middle',weight='bold')]
for side,pins in [('left',LEFT),('right',RIGHT)]:
    for i,pin in enumerate(pins):
        y=125+(YS[i]-10)*690/483
        text,kind=label(pin)
        if side=='left' and i==1: text,kind='5V rail: display VCC + shifter pin 14','power'
        if side=='left' and i==3: text,kind='GND rail: strip GND + display + shifter','gnd'
        if pin in ('5V','GND','3V3') and kind=='unused': text=f'{pin} - leave free'
        c=COLORS[kind]; active=kind!='unused'
        if side=='left':
            parts += [txt(46,y+6,text,18,c,weight='bold' if active else 'normal'),txt(542,y+6,pin,16,c,anchor='end'),line(550,y,610 if i==0 else 576,y,c,4 if active else 1)]
            x=610 if i==0 else 576
        else:
            parts += [line(743 if i==0 else 780,y,824,y,c,4 if active else 1),txt(838,y+6,pin.replace("BL702-", "BL:"),16,c),txt(900,y+6,text,18,c,weight='bold' if active else 'normal')]
            x=743 if i==0 else 780
        parts.append(f'<circle cx="{x}" cy="{y}" r="6" fill="white" stroke="{c}" stroke-width="{3 if active else 1}"/>')
parts += [txt(40,855,'Keypad: rows are driven LOW one at a time; columns and operator inputs use pull-ups.',19),txt(40,884,'No extra power/GND lead on the 8-wire passive keypad. The operator strip GND goes to the GND rail.',18),line(40,905,1360,905,'#bec6ce',1),txt(40,939,'MAX7219 signal cables: use its INPUT header (DIN), not the DOUT end.',21,weight='bold')]
for i,s in enumerate(['FPGA 17  ->  74AHCT125 pin 2 (1A)  ->  pin 3 (1Y)  ->  display DIN','FPGA 18  ->  74AHCT125 pin 5 (2A)  ->  pin 6 (2Y)  ->  display CS / LOAD','FPGA 19  ->  74AHCT125 pin 9 (3A)  ->  pin 8 (3Y)  ->  display CLK']):
    parts.append(txt(40,973+i*28,s,20,COLORS['spi']))
parts += [txt(40,1066,'See wiring.md and the level-shifter diagram for power, enable pins, resistors and decoupling.',18),txt(40,1097,'Board photo/pin order: Sipeed Nano 1K pinmap. Wiring proposal; firmware and hardware validation pending.',15)]
parts.append('</g></svg>')
(ROOT/'docs/images/dupont-board.svg').write_text('\n'.join(parts)+'\n')

parts=start(1400,680,'74AHCT125 14-pin DIP top-view wiring')
parts += [txt(40,45,'MAX7219 level shifter: 74AHCT125, 14-pin DIP',30,weight='bold'),txt(40,82,'Top view: notch UP. This pin numbering applies to the 14-pin DIP, not an arbitrary breakout module.',20)]
parts.append('<rect x="600" y="150" width="200" height="380" rx="15" fill="#202c37"/><path d="M675 150 A25 25 0 0 0 725 150" fill="white" stroke="white"/>')
parts += [txt(700,310,'74AHCT125',23,'white',anchor='middle'),txt(700,340,'notch up',18,'white',anchor='middle')]
left=[('1','1OE -> GND','gnd'),('2','1A <- FPGA 17','spi'),('3','1Y -> display DIN','spi'),('4','2OE -> GND','gnd'),('5','2A <- FPGA 18','spi'),('6','2Y -> display CS/LOAD','spi'),('7','GND -> common GND','gnd')]
right=[('14','VCC -> 5V','power'),('13','4OE -> 5V (unused gate off)','power'),('12','4A -> GND','gnd'),('11','4Y: leave unconnected','unused'),('10','3OE -> GND','gnd'),('9','3A <- FPGA 19','spi'),('8','3Y -> display CLK','spi')]
for pins,side in [(left,'left'),(right,'right')]:
    for i,(pin,s,kind) in enumerate(pins):
        y=195+i*48; c=COLORS[kind]
        if side=='left': parts += [txt(40,y+6,s,22,c),line(520,y,600,y,c),txt(614,y+6,pin,20,'white')]
        else: parts += [txt(786,y+6,pin,20,'white',anchor='end'),line(800,y,850,y,c),txt(872,y+6,s,22,c)]
parts += [txt(40,578,'Common 5V rail: Nano 1K 5V, shifter pin 14, shifter pin 13, display VCC.',21,COLORS['power']),txt(40,611,'Common GND: Nano GND, strip GND, display GND, shifter pins 1, 4, 7, 10, 12.',21),txt(40,644,'100 nF capacitor between pins 14 and 7, close to the chip. Board power/current validation still pending.',18),txt(40,670,'Source: TI SN74AHCT125 datasheet, pin configuration (top view). Disconnect USB before changing wires.',16)]
parts.append('</g></svg>')
(ROOT/'docs/images/level-shifter.svg').write_text('\n'.join(parts)+'\n')
print('PASS: 15 unique FPGA assignments all mapped to side headers; generated two SVG diagrams')

# Rendering is optional; do not install external tools from this script.
import shutil
import subprocess
if shutil.which('rsvg-convert'):
    for stem in ['dupont-board', 'level-shifter']:
        image = ROOT/'docs/images'/stem
        subprocess.run(['rsvg-convert', str(image.with_suffix('.svg')), '-o', str(image.with_suffix('.png'))], check=True)
else:
    print('SKIPPED PNG rendering: rsvg-convert not on PATH; SVG files are ready')
