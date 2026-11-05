from paths import ROOT
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock
import importlib.util

_spec = importlib.util.spec_from_file_location('merge_update', ROOT / 'tools/merge_update.py')
merge_update = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(merge_update)


def write(path, text='x'):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


class MergeUpdateTests(unittest.TestCase):
    def merge(self, base, update, out):
        return subprocess.run([sys.executable, str(ROOT / 'tools/merge_update.py'), str(base), str(update), str(out)],
                              capture_output=True, text=True)

    def test_ps4_layout(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            write(tmp / 'base/eboot.bin', 'old')
            write(tmp / 'base/sce_sys/param.sfo', 'base')
            write(tmp / 'base/sce_module/libc.prx')
            write(tmp / 'patch/eboot.bin', 'new')
            write(tmp / 'patch/sce_sys/param.sfo', 'patch')
            self.assertEqual(self.merge(tmp / 'base', tmp / 'patch', tmp / 'out').returncode, 0)
            self.assertEqual((tmp / 'out/eboot.bin').read_text(), 'new')
            self.assertEqual((tmp / 'out/sce_sys/param.sfo').read_text(), 'patch')
            self.assertTrue((tmp / 'out/sce_module/libc.prx').is_file())

    def test_pkg_tool_layout(self):
        # PS4 PKG Tool: Image0 holds the files, Sc0 the sce_sys ones; the update was fixed by
        # hand (eboot.bin and param.sfo copied out), which still counts as Image0 + Sc0.
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            write(tmp / 'base/Image0/eboot.bin', 'old')
            write(tmp / 'base/Image0/sce_module/libc.prx')
            write(tmp / 'base/Image0/memoryconfiguration.igz')
            write(tmp / 'base/Sc0/param.sfo', 'base')
            write(tmp / 'patch/Image0/eboot.bin', 'new')
            write(tmp / 'patch/Sc0/param.sfo', 'patch')
            write(tmp / 'patch/eboot.bin', 'new')
            write(tmp / 'patch/sce_sys/param.sfo', 'patch')
            self.assertEqual(self.merge(tmp / 'base', tmp / 'patch', tmp / 'out').returncode, 0)
            out = tmp / 'out'
            self.assertEqual((out / 'eboot.bin').read_text(), 'new')
            self.assertEqual((out / 'sce_sys/param.sfo').read_text(), 'patch')
            self.assertTrue((out / 'sce_module/libc.prx').is_file())
            self.assertTrue((out / 'memoryconfiguration.igz').is_file())
            self.assertFalse((out / 'Image0').exists())
            self.assertFalse((out / 'Sc0').exists())

    def test_not_a_game(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            (tmp / 'base').mkdir()
            write(tmp / 'patch/eboot.bin')
            self.assertNotEqual(self.merge(tmp / 'base', tmp / 'patch', tmp / 'out').returncode, 0)

    def sources(self, root):
        for folder, version in (('base', 'old'), ('patch', 'new')):
            write(root / folder / 'eboot.bin', version)
            write(root / folder / 'sce_sys/param.sfo', folder)
        return root / 'base', root / 'patch', root / 'out'

    def test_final_directory_is_published_only_after_complete_merge(self):
        with tempfile.TemporaryDirectory() as tmp:
            base, update, out = self.sources(Path(tmp))
            original = merge_update.add_tree
            def observe(*args, **kwargs):
                self.assertFalse(out.exists())
                self.assertTrue(args[1].name.endswith('.staging'))
                return original(*args, **kwargs)
            with mock.patch.object(merge_update, 'add_tree', side_effect=observe):
                merge_update.merge_game(base, update, out)
            self.assertEqual((out / 'eboot.bin').read_text(), 'new')
            self.assertEqual((base / 'eboot.bin').read_text(), 'old')
            self.assertEqual(list(out.parent.glob('.out.*.staging')), [])

    def test_copy_failure_leaves_no_partial_final_and_cleans_stage(self):
        with tempfile.TemporaryDirectory() as tmp:
            base, update, out = self.sources(Path(tmp))
            with mock.patch.object(merge_update, 'link_or_copy', side_effect=OSError('disk full')):
                with self.assertRaises(OSError):
                    merge_update.merge_game(base, update, out)
            self.assertFalse(out.exists())
            self.assertEqual(list(out.parent.glob('.out.*.staging')), [])
            self.assertEqual((base / 'eboot.bin').read_text(), 'old')
            self.assertEqual((update / 'eboot.bin').read_text(), 'new')

    def test_existing_output_and_nested_source_destination_are_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            base, update, out = self.sources(Path(tmp))
            write(out / 'keep.txt', 'keep')
            for target in (out, base, base / 'nested', update / 'nested'):
                with self.subTest(target=target), self.assertRaises(ValueError):
                    merge_update.merge_game(base, update, target)
            self.assertEqual((out / 'keep.txt').read_text(), 'keep')

    def test_copy_fallback_and_publication_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            base, update, out = self.sources(Path(tmp))
            with mock.patch.object(merge_update.os, 'link', side_effect=OSError('cross-device')):
                counts, _ = merge_update.merge_game(base, update, out)
            self.assertEqual(counts, {'linked': 0, 'copied': 4})
            self.assertEqual((out / 'eboot.bin').read_text(), 'new')
            failed = out.parent / 'failed'
            with mock.patch.object(merge_update.os, 'rename', side_effect=OSError('publish failed')):
                with self.assertRaises(OSError):
                    merge_update.merge_game(base, update, failed)
            self.assertFalse(failed.exists())
            self.assertEqual(list(out.parent.glob('.failed.*.staging')), [])


if __name__ == '__main__':
    unittest.main()
