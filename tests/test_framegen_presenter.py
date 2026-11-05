"""Compile the actual Present orchestration against fake WSI/FFX objects.

These driverless tests cover ordering, producer waits and skipped-frame recovery. They do
not run Vulkan shaders or prove visible scanout. Set FRAMEGEN_TEST_CXX to a C++20 compiler
when it is not on PATH (clang-cl, clang++, g++ or cl).
"""
from paths import ROOT
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


class FrameGenPresenterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = os.environ.get('FRAMEGEN_TEST_CXX')
        if not compiler:
            compiler = next((p for name in ('clang++', 'g++', 'clang-cl', 'cl')
                             if (p := shutil.which(name))), None)
        if not compiler:
            raise unittest.SkipTest('C++20 compiler not found; set FRAMEGEN_TEST_CXX')
        cls.tmp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.tmp.cleanup)
        folder = Path(cls.tmp.name)
        presenter = (ROOT / 'gpu/shadps4/video_core/renderer_vulkan/vk_presenter.cpp').read_text()
        # Compile the production function unchanged; only its GPU/WSI collaborators are fakes.
        begin = presenter.index('void Presenter::Present(Frame*')
        end = presenter.index('bool Presenter::AcquirePresentImage()', begin)
        submit_begin = presenter.index('void Presenter::SubmitPresentImage(')
        submit_end = presenter.index('Frame* Presenter::GetRenderFrame()', submit_begin)
        harness = (ROOT / 'tests/fixtures/framegen_presenter_harness.cpp').read_text()
        source = folder / 'test.cpp'
        source.write_text(harness.replace('// @PRESENTER_IMPLEMENTATION@',
                                          presenter[begin:end] + presenter[submit_begin:submit_end]))
        cls.exe = folder / ('test.exe' if os.name == 'nt' else 'test')
        msvc = Path(compiler).stem.lower() in ('cl', 'clang-cl')
        args = ([compiler, '/nologo', '/std:c++20', '/EHsc', str(source), '/Fe:' + str(cls.exe)]
                if msvc else [compiler, '-std=c++20', '-pthread', str(source), '-o', str(cls.exe)])
        build = subprocess.run(args, cwd=folder, capture_output=True, text=True)
        if build.returncode:
            raise AssertionError(build.stdout + build.stderr)

    def test_frame_pair_lifecycle(self):
        for case in ('history', 'off', 'menu', 'reuse', 'nongame', 'minimized',
                     'generated-failure', 'reacquire-failure', 'real-failure', 'mailbox',
                     'gap', 'hdr', 'native'):
            with self.subTest(case=case):
                run = subprocess.run([str(self.exe), case], capture_output=True, text=True)
                self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
