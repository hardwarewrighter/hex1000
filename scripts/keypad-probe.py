#!/usr/bin/env python3
"""Raw keypad row/column diagnostic; SRAM only, calculator flash preserved."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parent.parent
BOARD=ROOT/'boards/tangnano1k'
OUT=ROOT/'work/board/keypad-probe'
SOURCES=[BOARD/f'keypad-probe.{ext}' for ext in ['v','cst','sdc']]
PINS={'clk':47,'max_din':17,'max_load':18,'max_clk':19,'max_oe':23,
      'led_n[0]':9,'led_n[1]':10,'led_n[2]':11,
      **{f'pad_row_n[{i}]':p for i,p in enumerate([15,16,27,28])},
      **{f'pad_col_n[{i}]':p for i,p in enumerate([31,20,35,34])}}

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def run(command,log=None):
    print(' '.join(map(str,command)),flush=True)
    p=subprocess.run(list(map(str,command)),cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    if log:(OUT/log).write_text(p.stdout)
    if not log or p.returncode:print(p.stdout,end='',flush=True)
    p.check_returncode();return p.stdout

def test():
    run(['iverilog','-g2005-sv','-s','tb','-o',OUT/'probe.vvp',BOARD/'keypad-probe.v',BOARD/'keypad-probe.tb.v'])
    run(['vvp',OUT/'probe.vvp'],'simulation.log')
    print((OUT/'simulation.log').read_text(),end='')


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('action',choices=['test','build','load'])
    ap.add_argument('--tools');a=ap.parse_args()
    if a.tools:os.environ['PATH']=str(Path(a.tools).resolve())+os.pathsep+os.environ['PATH']
    OUT.mkdir(parents=True,exist_ok=True)
    loc=re.findall(r'IO_LOC "([\w\[\]]+)" (\d+);',(BOARD/'keypad-probe.cst').read_text())
    if len(loc)!=len(PINS) or {k:int(v) for k,v in loc}!=PINS:raise RuntimeError('Diagnostic pins changed; refusing')
    for i in range(4):
        if f'IO_PORT "pad_row_n[{i}]" IO_TYPE=LVCMOS33 DRIVE=4 TO=SIG;' not in (BOARD/'keypad-probe.cst').read_text():
            raise RuntimeError('Row output-enable polarity must be explicit TO=SIG')
    if a.action=='test':
        test()
    elif a.action=='build':
        test()
        run(['yosys','-p','read_verilog boards/tangnano1k/keypad-probe.v; synth_gowin -family gw1n -top keypad_probe -json work/board/keypad-probe/synth.json'],'synth.log')
        run(['nextpnr-himbaechel','--device','GW1NZ-LV1QN48C6/I5','--vopt','family=GW1NZ-1',
             '--vopt','sspi_as_gpio','--vopt',f'cst={BOARD/"keypad-probe.cst"}','--json',OUT/'synth.json','--write',OUT/'pnr.json',
             '--freq','27','--sdc',BOARD/'keypad-probe.sdc','--report',OUT/'timing.json'],'pnr.log')
        run(['gowin_pack','-d','GW1NZ-1','--sspi_as_gpio','--mspi_as_gpio','--cpu_as_gpio',
             '-o',OUT/'probe.fs',OUT/'pnr.json'],'pack.log')
        report=json.loads((OUT/'timing.json').read_text())
        if any(c['achieved']<c['constraint'] for c in report['fmax'].values()):raise RuntimeError('Timing failed')
        (OUT/'manifest.json').write_text(json.dumps({'inputs':{str(p.relative_to(ROOT)):sha(p) for p in SOURCES},'image':sha(OUT/'probe.fs')},indent=2)+'\n')
        print('Built raw keypad diagnostic; not loaded')
    else:
        m=json.loads((OUT/'manifest.json').read_text())
        if m['inputs']!={str(p.relative_to(ROOT)):sha(p) for p in SOURCES} or m['image']!=sha(OUT/'probe.fs'):
            raise RuntimeError('Stale diagnostic; rebuild')
        output=run(['openFPGALoader','-b','tangnano1k','--detect'])
        ids=re.findall(r'idcode\s+(0x[0-9a-fA-F]+)',output)
        if len(ids)!=1 or int(ids[0],16)!=0x0100681b:raise RuntimeError('Need exactly one GW1NZ-1')
        output+=run(['openFPGALoader','-b','tangnano1k','--write-sram',OUT/'probe.fs'])
        (OUT/'load.log').write_text(output)
        if not re.search(r'CRC check\s*:\s*Success',output) or re.search(r'CRC check\s*:\s*FAIL',output):raise RuntimeError('Programming CRC not verified')
        print('SRAM only: 000R000C, row 1..4 every two seconds; C column mask. Power cycle restores calculator.')

if __name__=='__main__':main()
