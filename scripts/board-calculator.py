#!/usr/bin/env python3
"""Build/test physical Nano 1K calculator; explicit SRAM or persistent flash load."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

ROOT=Path(__file__).resolve().parent.parent
BOARD=ROOT/'boards/tangnano1k'
OUT=ROOT/'work/board/calculator'
EXPECTED={'clk':47, **{f'pad_row_n[{i}]':p for i,p in enumerate([15,16,27,28])},
          **{f'pad_col_n[{i}]':p for i,p in enumerate([31,20,35,34])},
          **{f'op_n[{i}]':p for i,p in enumerate([38,39,40,41])},
          'max_din':17,'max_load':18,'max_clk':19,'max_oe':23,
          **{f'led_n[{i}]':p for i,p in enumerate([9,10,11])}}
SOURCES=[BOARD/'calculator.v',BOARD/'calculator.cst',BOARD/'calculator.sdc',
         ROOT/'libs/Front/rtl/front.v',ROOT/'libs/Hex1000/rtl/hex1000.v']

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def run(command,log=None):
    print(' '.join(map(str,command)),flush=True)
    p=subprocess.run(list(map(str,command)),cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    if log:
        OUT.mkdir(parents=True,exist_ok=True);(OUT/log).write_text(p.stdout)
    if not log or p.returncode: print(p.stdout,end='',flush=True)
    p.check_returncode()
    return p.stdout

def constraints():
    text=(BOARD/'calculator.cst').read_text()
    locations=re.findall(r'IO_LOC "([\w\[\]]+)" (\d+);',text)
    if len(locations)!=len(EXPECTED) or {k:int(v) for k,v in locations}!=EXPECTED:
        raise RuntimeError('Calculator pin map does not match approved physical wiring')
    if len(set(EXPECTED.values()))!=len(EXPECTED): raise RuntimeError('Duplicate pins')
    if 'CLOCK_LOC "machine_clk" BUFG;' not in text: raise RuntimeError('Missing global machine clock constraint')
    for line in text.splitlines():
        if not line.strip(): continue
        if not re.fullmatch(r'(IO_LOC ".+" \d+;|IO_PORT ".+" IO_TYPE=LVCMOS33(?: PULL_MODE=UP| DRIVE=4)?;|CLOCK_LOC "machine_clk" BUFG;)',line):
            raise RuntimeError(f'Unexpected constraint: {line}')

def detect():
    output=run(['openFPGALoader','-b','tangnano1k','--detect'])
    ids=re.findall(r'idcode\s+(0x[0-9a-fA-F]+)',output)
    if len(ids)!=1 or int(ids[0],16)!=0x0100681b:
        raise RuntimeError('Refuse programming: need exactly one GW1NZ-1 ID 0x0100681b')
    return output

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['test','build','detect','load','flash'])
    parser.add_argument('--tools')
    args=parser.parse_args()
    if args.tools: os.environ['PATH']=str(Path(args.tools).resolve())+os.pathsep+os.environ['PATH']
    constraints();OUT.mkdir(parents=True,exist_ok=True)
    if args.action=='test':
        if not shutil.which('iverilog') or not shutil.which('vvp'):
            print('SKIPPED calculator RTL checks: iverilog/vvp not on PATH');return
        trace=run([ROOT/'scripts/xt','run',ROOT/'scripts/front-trace.xtl'], 'front-trace.txt')
        (OUT/'front-trace.txt').write_text(trace)
        run(['iverilog','-g2005-sv','-s','tb','-o',OUT/'front.vvp',
             ROOT/'libs/Front/rtl/front.v',ROOT/'libs/Front/rtl/front.tb.v'])
        run(['vvp',OUT/'front.vvp'],'model-test.log')
        for rows in [4,256]:
            run(['iverilog','-g2005-sv','-s','tb',f'-Ptb.TEST_ROWS={rows}',
                 '-o',OUT/'calculator.vvp',BOARD/'calculator.v',ROOT/'libs/Front/rtl/front.v',
                 ROOT/'libs/Hex1000/rtl/hex1000.v',BOARD/'calculator.tb.v'])
            run(['vvp',OUT/'calculator.vvp'],f'physical-test-{rows}.log')
        print('PASS panel/X_eTaL equivalence and physical wiring/SPI tests at accelerated and production debounce settings')
    elif args.action=='build':
        for tool in ['yosys','nextpnr-himbaechel','gowin_pack']:
            if not shutil.which(tool): raise RuntimeError(f'Missing {tool}; activate OSS CAD Suite')
        run(['yosys','-p','read_verilog boards/tangnano1k/calculator.v libs/Front/rtl/front.v libs/Hex1000/rtl/hex1000.v; '
             'synth_gowin -family gw1n -top hex1000_calculator -json work/board/calculator/synth.json'],'synth.log')
        ports=json.loads((OUT/'synth.json').read_text())['modules']['hex1000_calculator']['ports']
        names={}
        for name,port in ports.items():
            for i in range(len(port['bits'])):
                names[name if len(port['bits'])==1 else f'{name}[{i}]']=port['direction']
        if set(names)!=set(EXPECTED): raise RuntimeError('Top ports differ from pin map')
        for name,direction in names.items():
            wanted='input' if name=='clk' or name.startswith(('pad_col_n','op_n')) else 'output'
            if direction!=wanted: raise RuntimeError(f'Wrong pin direction: {name}')
        run(['nextpnr-himbaechel','--device','GW1NZ-LV1QN48C6/I5','--vopt','family=GW1NZ-1',
             '--vopt','sspi_as_gpio','--vopt',f'cst={BOARD/"calculator.cst"}',
             '--json',OUT/'synth.json','--write',OUT/'pnr.json','--freq','27',
             '--sdc',BOARD/'calculator.sdc','--report',OUT/'timing.json'],'pnr.log')
        report=json.loads((OUT/'timing.json').read_text())
        if any(c['achieved']<c['constraint'] for c in report['fmax'].values()): raise RuntimeError('Timing failed')
        run(['gowin_pack','-c','-d','GW1NZ-1','--sspi_as_gpio','--mspi_as_gpio','--cpu_as_gpio',
             '-o',OUT/'calculator.fs',OUT/'pnr.json'],'pack.log')
        (OUT/'manifest.json').write_text(json.dumps({'inputs':{str(p.relative_to(ROOT)):sha(p) for p in SOURCES},
             'bitstream_sha256':sha(OUT/'calculator.fs')},indent=2)+'\n')
        print('Built physical calculator; no hardware programmed')
    elif args.action=='detect': detect()
    else:
        manifest=json.loads((OUT/'manifest.json').read_text())
        if manifest['inputs']!={str(p.relative_to(ROOT)):sha(p) for p in SOURCES} or manifest['bitstream_sha256']!=sha(OUT/'calculator.fs'):
            raise RuntimeError('Stale source or modified image; rebuild before programming')
        identity=detect()
        mode='--write-flash' if args.action=='flash' else '--write-sram'
        output=run(['openFPGALoader','-b','tangnano1k',mode,OUT/'calculator.fs'])
        (OUT/f'{args.action}.log').write_text(identity+output)
        print(f'Calculator {args.action} completed; peripheral operation still needs user testing')

if __name__=='__main__': main()
