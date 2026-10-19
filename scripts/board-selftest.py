#!/usr/bin/env python3
"""Simulate/build a peripheral-free Nano 1K test; load SRAM only after ID check."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent.parent
BOARD = ROOT / 'boards/tangnano1k'
OUT = ROOT / 'work/board/selftest'
SOURCES = [BOARD/'selftest.v', BOARD/'selftest.cst', BOARD/'selftest.sdc',
           BOARD/'board.json', ROOT/'libs/Hex1000/rtl/hex1000.v']

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run(command, log=None):
    print(' '.join(map(str, command)), flush=True)
    result = subprocess.run(list(map(str, command)), cwd=ROOT, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if log:
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT/log).write_text(result.stdout)
    if not log or result.returncode:
        print(result.stdout, end='', flush=True)
    result.check_returncode()
    return result.stdout

def detect():
    output = run(['openFPGALoader', '-b', 'tangnano1k', '--detect'])
    ids = re.findall(r'idcode\s+(0x[0-9a-fA-F]+)', output)
    if len(ids) != 1 or int(ids[0], 16) != 0x0100681b:
        raise RuntimeError('Refusing load: require exactly one GW1NZ-1 ID 0x0100681b')
    return output

def check_constraints():
    cfg=json.loads((BOARD/'board.json').read_text())
    assert cfg['device']=='GW1NZ-LV1QN48C6/I5' and cfg['family']=='GW1NZ-1'
    expected={'clk':47,'led_n[0]':9,'led_n[1]':10,'led_n[2]':11}
    assert {k:v['pin'] for k,v in cfg['ports'].items()}==expected
    locations=re.findall(r'IO_LOC "([\w\[\]]+)" (\d+);', (BOARD/'selftest.cst').read_text())
    assert len(locations)==4 and {k:int(v) for k,v in locations}==expected

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['test','build','detect','load'])
    parser.add_argument('--tools', help='Optional OSS CAD Suite bin directory')
    args=parser.parse_args()
    if args.tools:
        os.environ['PATH']=str(Path(args.tools).resolve())+os.pathsep+os.environ['PATH']
    check_constraints()
    if args.action=='test':
        if not (shutil.which('iverilog') and shutil.which('vvp')):
            print('SKIPPED Nano 1K selftest simulation: iverilog/vvp not on PATH')
            return
        OUT.mkdir(parents=True,exist_ok=True)
        run(['iverilog','-g2005-sv','-s','tb','-o',OUT/'selftest.vvp',BOARD/'selftest.v',
             ROOT/'libs/Hex1000/rtl/hex1000.v',BOARD/'selftest.tb.v'])
        output=run(['vvp',OUT/'selftest.vvp'])
        if 'PASS: startup zero' not in output:
            raise RuntimeError('Missing selftest simulation success')
    elif args.action=='build':
        for tool in ['yosys','nextpnr-himbaechel','gowin_pack']:
            if not shutil.which(tool): raise RuntimeError(f'{tool} missing; activate OSS CAD Suite')
        OUT.mkdir(parents=True,exist_ok=True)
        # Invoke from repo root so paths are controlled, without interpolating user input.
        run(['yosys','-p','read_verilog boards/tangnano1k/selftest.v libs/Hex1000/rtl/hex1000.v; '
             'synth_gowin -family gw1n -top hex1000_selftest -json work/board/selftest/synth.json'], 'synth.log')
        ports=json.loads((OUT/'synth.json').read_text())['modules']['hex1000_selftest']['ports']
        assert {k:(v['direction'],len(v['bits'])) for k,v in ports.items()}=={'clk':('input',1),'led_n':('output',3)}
        run(['nextpnr-himbaechel','--device','GW1NZ-LV1QN48C6/I5',
             '--vopt','family=GW1NZ-1','--vopt',f'cst={BOARD / "selftest.cst"}',
             '--json',OUT/'synth.json','--write',OUT/'pnr.json','--freq','27',
             '--sdc',BOARD/'selftest.sdc','--report',OUT/'timing.json'], 'pnr.log')
        run(['gowin_pack','-c','-d','GW1NZ-1','-o',OUT/'selftest.fs',OUT/'pnr.json'], 'pack.log')
        manifest={'inputs':{str(p.relative_to(ROOT)):sha(p) for p in SOURCES},
                  'bitstream_sha256':sha(OUT/'selftest.fs')}
        (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
        print(f'Built {OUT / "selftest.fs"}; no device programmed')
    elif args.action=='detect': detect()
    else:
        manifest=json.loads((OUT/'manifest.json').read_text())
        if manifest['inputs']!={str(p.relative_to(ROOT)):sha(p) for p in SOURCES}:
            raise RuntimeError('Source changed since build; rebuild before loading')
        if manifest['bitstream_sha256']!=sha(OUT/'selftest.fs'):
            raise RuntimeError('Bitstream changed since build; refusing load')
        identity=detect()
        output=run(['openFPGALoader','-b','tangnano1k','--write-sram',OUT/'selftest.fs'])
        (OUT/'load.log').write_text(identity+output)
        print('SRAM load finished. Observe RGB: green/cyan heartbeat = pass; red = failure.')
        print('Flash unchanged. Replug USB to restore the existing flash image.')

if __name__=='__main__':
    main()
