#!/usr/bin/env python3
"""Prepare a slow 00000000 MAX7219 diagnostic; SRAM only, flash preserved."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parent.parent
BOARD=ROOT/'boards/tangnano1k'
OUT=ROOT/'work/board/display-probe'
SOURCES=[BOARD/f'display-probe.{ext}' for ext in ['v','cst','sdc']]
PINS={'clk':47,'max_din':17,'max_load':18,'max_clk':19,'max_oe':23,
      'led_n[0]':9,'led_n[1]':10,'led_n[2]':11}

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def run(command,log=None):
    print(' '.join(map(str,command)),flush=True)
    p=subprocess.run(list(map(str,command)),cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    if log:(OUT/log).write_text(p.stdout)
    if not log or p.returncode:print(p.stdout,end='',flush=True)
    p.check_returncode();return p.stdout

def test():
    run(['iverilog','-g2005-sv','-s','tb','-o',OUT/'probe.vvp',BOARD/'display-probe.v',BOARD/'display-probe.tb.v'])
    run(['vvp',OUT/'probe.vvp'],'simulation.log')
    print((OUT/'simulation.log').read_text(),end='')


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('action',choices=['test','build','load'])
    ap.add_argument('--tools');a=ap.parse_args()
    if a.tools:os.environ['PATH']=str(Path(a.tools).resolve())+os.pathsep+os.environ['PATH']
    OUT.mkdir(parents=True,exist_ok=True)
    loc=re.findall(r'IO_LOC "([\w\[\]]+)" (\d+);',(BOARD/'display-probe.cst').read_text())
    if len(loc)!=8 or {k:int(v) for k,v in loc}!=PINS:raise RuntimeError('Diagnostic pins changed; refusing')
    if a.action=='test':
        test()
    elif a.action=='build':
        test()
        run(['yosys','-p','read_verilog boards/tangnano1k/display-probe.v; synth_gowin -family gw1n -top display_probe -json work/board/display-probe/synth.json'],'synth.log')
        run(['nextpnr-himbaechel','--device','GW1NZ-LV1QN48C6/I5','--vopt','family=GW1NZ-1',
             '--vopt',f'cst={BOARD/"display-probe.cst"}','--json',OUT/'synth.json','--write',OUT/'pnr.json',
             '--freq','27','--sdc',BOARD/'display-probe.sdc','--report',OUT/'timing.json'],'pnr.log')
        run(['gowin_pack','-c','-d','GW1NZ-1','--sspi_as_gpio','--mspi_as_gpio','--cpu_as_gpio',
             '-o',OUT/'probe.fs',OUT/'pnr.json'],'pack.log')
        (OUT/'manifest.json').write_text(json.dumps({'inputs':{str(p.relative_to(ROOT)):sha(p) for p in SOURCES},'image':sha(OUT/'probe.fs')},indent=2)+'\n')
        print('Built display-only diagnostic; not loaded')
    else:
        m=json.loads((OUT/'manifest.json').read_text())
        if m['inputs']!={str(p.relative_to(ROOT)):sha(p) for p in SOURCES} or m['image']!=sha(OUT/'probe.fs'):
            raise RuntimeError('Stale diagnostic; rebuild')
        output=run(['openFPGALoader','-b','tangnano1k','--detect'])
        ids=re.findall(r'idcode\s+(0x[0-9a-fA-F]+)',output)
        if len(ids)!=1 or int(ids[0],16)!=0x0100681b:raise RuntimeError('Need exactly one GW1NZ-1')
        output+=run(['openFPGALoader','-b','tangnano1k','--write-sram',OUT/'probe.fs'])
        (OUT/'load.log').write_text(output)
        print('SRAM only. Expect 00000000 and blinking green. Power cycle restores calculator flash.')

if __name__=='__main__':main()
