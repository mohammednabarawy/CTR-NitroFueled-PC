"""Verify the real shader registration can generate its header in an empty build folder.

This isolates the host-shader rule from renderer dependencies. It is not a full GPU build.
Use CMAKE, NINJA and GLSLANG_COMPILER to supply tools outside PATH.
"""
from paths import ROOT
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest


class FrameGenBuildTests(unittest.TestCase):
    def test_shader_header_from_empty_build_directory(self):
        cmake = os.environ.get('CMAKE') or shutil.which('cmake')
        ninja = os.environ.get('NINJA') or shutil.which('ninja')
        glslang = (os.environ.get('GLSLANG_COMPILER') or shutil.which('glslang')
                   or shutil.which('glslangValidator'))
        if not all((cmake, ninja, glslang)):
            self.skipTest('CMake, Ninja and glslang required')
        source = (ROOT / 'gpu/CMakeLists.txt').read_text()
        function = re.search(r'function\(add_host_shader\b.*?endfunction\(\)', source, re.S)
        registration = re.search(r'^add_host_shader\(fg_convert\.comp\s+fg_convert_comp\)', source, re.M)
        self.assertIsNotNone(function)
        self.assertIsNotNone(registration, 'fg_convert.comp must be registered with the GPU build')
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            shaders = (ROOT / 'gpu/shadps4/video_core/host_shaders').as_posix()
            (folder / 'CMakeLists.txt').write_text(
                'cmake_minimum_required(VERSION 3.24)\nproject(framegen_shader NONE)\n'
                f'set(SHADER_SRC "{shaders}")\n'
                'set(SHADER_DIR "${CMAKE_CURRENT_BINARY_DIR}/include/video_core/host_shaders")\n'
                + function.group() + '\n' + registration.group()
                + '\nadd_custom_target(framegen_shader ALL DEPENDS ${SHADER_HEADERS})\n')
            build_dir = folder / 'build'
            header = build_dir / 'include/video_core/host_shaders/fg_convert_comp.h'
            self.assertFalse(header.exists())
            for command in ([cmake, '-S', str(folder), '-B', str(build_dir), '-G', 'Ninja',
                             '-DCMAKE_MAKE_PROGRAM=' + ninja, '-DGLSLANG_COMPILER=' + glslang],
                            [cmake, '--build', str(build_dir)]):
                run = subprocess.run(command, capture_output=True, text=True)
                self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            self.assertIn('FG_CONVERT_COMP', header.read_text())
