#!/usr/bin/env python3
"""Safety guards, without USB access or tool execution."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import shutil

spec = importlib.util.spec_from_file_location('selftest', Path(__file__).with_name('board-selftest.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class Guards(unittest.TestCase):
    def test_detect_rejects_wrong_or_ambiguous_device(self):
        for text in ['idcode 0x0100481b', '', 'idcode 0x0100681b\nidcode 0x0100681b']:
            with self.subTest(text=text), patch.object(module, 'run', return_value=text):
                with self.assertRaises(RuntimeError): module.detect()

    def test_detect_accepts_1k_only(self):
        with patch.object(module, 'run', return_value='idcode 0x100681b\nmodel GW1NZ-1'):
            module.detect()

    def test_constraints_reject_peripheral_pin(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for name in ['board.json', 'selftest.cst']:
                shutil.copy2(module.BOARD/name, root/name)
            p=root/'selftest.cst'
            p.write_text(p.read_text().replace('"led_n[0]" 9', '"led_n[0]" 17'))
            with patch.object(module,'BOARD',root):
                with self.assertRaises(AssertionError): module.check_constraints()

spec2 = importlib.util.spec_from_file_location('calculator', Path(__file__).with_name('board-calculator.py'))
calculator = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(calculator)

class CalculatorGuards(unittest.TestCase):
    def test_rejects_9k_and_ambiguous_chain(self):
        for text in ['idcode 0x0100481b', 'idcode 0x0100681b\nidcode 0x0100681b', '']:
            with self.subTest(text=text), patch.object(calculator,'run',return_value=text):
                with self.assertRaises(RuntimeError): calculator.detect()

    def test_rejects_non_header_column(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            text=(calculator.BOARD/'calculator.cst').read_text()
            (root/'calculator.cst').write_text(text.replace('"pad_col_n[1]" 20','"pad_col_n[1]" 32'))
            with patch.object(calculator,'BOARD',root):
                with self.assertRaises(RuntimeError): calculator.constraints()

    def test_approved_constraints(self):
        calculator.constraints()

if __name__=='__main__': unittest.main()
