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

if __name__=='__main__': unittest.main()
