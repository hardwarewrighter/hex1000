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
variant_path = ROOT/'hex1000-txs0108e.net'
if variant_path.exists():
    variant = json.loads(variant_path.read_text())
    variant_pins = [c['from'].split(':PIN')[1] for c in variant['connections'] if c['from'].startswith('TANG_1K:PIN')]
    assert len(variant_pins)==16 and set(variant_pins)==set(assigned)|{'23'}
    assert all(pin in LEFT+RIGHT for pin in variant_pins)

assert assigned['15']=='KEYPAD:R1' and assigned['16']=='KEYPAD:R2'
assert assigned['20']=='KEYPAD:C2' and assigned['35']=='KEYPAD:C3'

def txt(x,y,s,size=20,color='#17212b',anchor='start',weight='normal'):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{weight}">{escape(s)}</text>'
def line(x1,y1,x2,y2,color,width=3):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}"/>'
def start(w,h,title):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img"><title>{escape(title)}</title><rect width="100%" height="100%" fill="white"/><g font-family="DejaVu Sans, sans-serif">']

def label(pin):
    if pin == '23': return 'OE -> TXS OE (optional; not 74)', 'spi'
    if pin not in assigned:
        names={'13':'Button A - leave free','44':'Button B - leave free','47':'27 MHz clock - leave free','9':'Onboard red LED - leave free','10':'Onboard blue LED - leave free','11':'Onboard green LED - leave free','42':'MODE1 - leave free'}
        return names.get(pin,'Programmer GPIO - DO NOT USE' if pin.startswith('BL702') else 'Leave free'), 'unused'
    to=assigned[pin]
    if to.startswith('KEYPAD:R'): return f'{to.split(":")[1]} keypad  (through 1 kohm)', 'row'
    if to.startswith('KEYPAD:C'): return f'{to.split(":")[1]} keypad', 'col'
    if to.startswith('BUTTON_STRIP:'):
        k=to.split(':')[1]; return f'{k} operator  ({dict(K1="+",K2="-",K3="*",K4="=")[k]})','op'
    dest={'74AHCT125:A1':'DIN via level shifter','74AHCT125:A2':'CS/LOAD via level shifter','74AHCT125:A3':'CLK via level shifter'}
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
        if side=='left' and i==1: text,kind='5V rail: display VCC + shifter 5V supply','power'
        if side=='left' and i==3: text,kind='GND rail: strip GND + display + shifter','gnd'
        if side=='right' and i==3: text,kind='3V3 -> TXS VCCA only', 'row'
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
for i,s in enumerate(['FPGA 17  ->  shifter 3.3V input  ->  shifter 5V output  ->  display DIN','FPGA 18  ->  shifter 3.3V input  ->  shifter 5V output  ->  display CS / LOAD','FPGA 19  ->  shifter 3.3V input  ->  shifter 5V output  ->  display CLK']):
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

# TXS0108E breakout alternative: logical labels, never assumed header order.
parts = start(1400,1200, 'TXS0108E breakout wiring for the Nano 1K and MAX7219')
parts += [txt(40,46,'TXS0108E: Nano 1K to MAX7219 display',30,weight='bold'),txt(40,82,'Logical connections: match the labels on YOUR breakout. Header order and chip pin numbers vary.',20)]
parts.append('<rect x="40" y="135" width="400" height="490" rx="16" fill="#eef4fa" stroke="#8da0b5"/><rect x="560" y="135" width="280" height="490" rx="16" fill="#f0f6f0" stroke="#8da58d"/><rect x="1040" y="135" width="320" height="490" rx="16" fill="#fff3e8" stroke="#c7a789"/>')
parts += [txt(64,178,'Tang Nano 1K',25,weight='bold'),txt(64,209,'USB UP, component side facing you',17),txt(700,178,'TXS0108E',25,anchor='middle',weight='bold'),txt(700,209,'A = 3.3V     B = 5V',18,anchor='middle'),txt(1060,178,'MAX7219 input header',23,weight='bold')]
for y,fpga,loc,a,b,display in [(300,'17','Left: fifth from bottom','A1','B1','DIN'),(400,'18','Left: sixth from bottom','A2','B2','CS / LOAD'),(500,'19','Right: fourth from bottom','A3','B3','CLK')]:
    c=COLORS['spi']
    parts += [txt(64,y-12,f'FPGA {fpga}',23,c,weight='bold'),txt(64,y+18,loc,17),line(440,y,560,y,c,4),txt(580,y+7,a,23,c),line(635,y,765,y,c,3),txt(820,y+7,b,23,c,anchor='end'),line(840,y,1040,y,c,4),txt(1060,y+7,display,24,c,weight='bold')]
parts += [txt(64,581,'3.3V + 5V + common GND below',18),txt(700,580,'A4-A8 / B4-B8 unused',17,anchor='middle'),txt(1060,580,'Use DIN end, not DOUT',18)]
parts += [txt(40,675,'Power and enable cables',24,weight='bold')]
rows=[('Nano 3V3  ->  TXS VCCA / VA / VCC_A','#1769aa'),('Nano 5V  ->  TXS VCCB / VB / VCC_B  AND  display VCC',COLORS['power']),('Nano GND  ->  TXS GND  AND  display GND  (same ground as button strip)',COLORS['gnd'])]
for i,(s,c) in enumerate(rows): parts.append(txt(40,714+i*32,s,22,c))
parts += [txt(40,822,'OE ENABLE: a signal wire plus a resistor BRANCH to ground',23,weight='bold')]
parts += [txt(40,874,'Nano FPGA 23',23,COLORS['spi'],weight='bold'),txt(40,904,'Left, eighth hole from bottom',18),line(370,868,1040,868,COLORS['spi'],4),txt(1060,875,'TXS OE',25,COLORS['spi'],weight='bold')]
parts.append('<circle cx="700" cy="868" r="7" fill="#b85c00"/>')
parts += [line(700,868,700,910,COLORS['spi']),'<rect x="687" y="910" width="26" height="70" fill="white" stroke="#202020" stroke-width="3"/>',txt(740,943,'10 kohm resistor',23,weight='bold'),txt(740,972,'10,000 ohms',18),line(700,980,700,1010,COLORS['gnd']),line(660,1010,740,1010,COLORS['gnd']),line(672,1020,728,1020,COLORS['gnd']),line(685,1030,715,1030,COLORS['gnd']),txt(700,1062,'Common GND (Nano + TXS + display)',20,anchor='middle')]
parts += [txt(40,1100,'The resistor is a branch to GND, not in series with the OE signal wire. OE must not float.',19),txt(40,1128,'Do not tie OE to 3V3 or 5V when driven by FPGA 23. Firmware raises OE after about 39 ms.',19),txt(40,1156,'Keep signal wires short. Add 100 nF per supply if absent on the breakout. Rewire only with USB unplugged.',18),txt(40,1186,'Source: TI TXS0108E datasheet. Match breakout labels; this drawing does not specify its header order.',16)]
parts.append('</g></svg>')
(ROOT/'docs/images/txs0108e-wiring.svg').write_text('\n'.join(parts)+'\n')

print('PASS: 15 unique FPGA assignments all mapped to side headers; generated three SVG diagrams')

# Rendering is optional; do not install external tools from this script.
import shutil
import subprocess
if shutil.which('rsvg-convert'):
    for stem in ['dupont-board', 'level-shifter', 'txs0108e-wiring']:
        image = ROOT/'docs/images'/stem
        subprocess.run(['rsvg-convert', str(image.with_suffix('.svg')), '-o', str(image.with_suffix('.png'))], check=True)
else:
    print('SKIPPED PNG rendering: rsvg-convert not on PATH; SVG files are ready')
