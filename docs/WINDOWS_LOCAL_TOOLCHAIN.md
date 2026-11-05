# Workspace-local Windows toolchain

MSYS2 CLANG64 is installed under `out/toolchains/msys64`. Use the PowerShell wrapper to run
build commands with its compiler, Vulkan SDK components and pkg-config search paths:

```powershell
.\tools\with-clang64.ps1 -Command 'clang --version; cmake --version; pkg-config --modversion vulkan sdl3 libavcodec'
```

The wrapper restores the calling process's environment afterward. It does not change the
machine PATH or require an installation in `C:\msys64`. Its `MSYS2_ROOT` also lets
`msys2-env.sh` find this local installation.

Verified versions: Clang 23.1.4, CMake 4.4.5, Ninja 1.13.2, Vulkan headers/loader 1.4.363,
VMA 3.5.0, glslang 16.6.0, SDL3 3.4.18 and FFmpeg 9.0.2. The full clean runtime/launcher build
and all 64 aggregate targeted tests passed. See `out/pr149-final-build.log` and
`out/pr149-final-tests.log`. `out/msys2-installed-packages.txt` records all installed packages.

## Fresh build

Keep validation outputs separate from the existing runtime:

```powershell
.\tools\with-clang64.ps1 -Command 'cmake -S gpu -B out/pr149-clang64-clean -G Ninja -DCMAKE_BUILD_TYPE=RelWithDebInfo -DBB_LTO=OFF -DBB_PGO=off -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_EXPORT_COMPILE_COMMANDS=ON'
.\tools\with-clang64.ps1 -Command 'cmake --build out/pr149-clang64-clean --parallel 4 --target sacredfire bb-gpu-capabilities ctr-launcher'
```

These commands do not copy their executables over `bin/`, the repository-root launcher or
the existing `out/sacredfire.exe`. Dependency installation does not establish gameplay or
frame-generation correctness; build/runtime evidence belongs in `PR149_REMEDIATION.md`.

## Dependencies and provenance

The installation follows the package list in `packaging/windows/README.md`, plus the explicit
`mingw-w64-clang-x86_64-xz` package used for static liblzma linking. Pacman verifies its package
signatures. Installation output is saved in `out/msys2-install.log`.

The initial MSYS2 base came from the official `msys2/msys2-installer` release:

```text
Asset: msys2-base-x86_64-latest.sfx.exe
Verified SHA256: 496fdf71909e1e34ee2917216e09fab67c705500ea438d9a94053ec5500b4a74
```

Empty source dependencies were restored at the existing parent repository's pinned commits:

| Directory | Commit |
|---|---|
| `gpu/third_party/fsr-vulkan` | `c64f093404125e960813f95f1996c14780f0dd69` |
| `gpu/third_party/magic_enum` | `e046b69a3736d314fad813e159b1c192eaef92cd` |
| `gpu/third_party/miniz` | `2948eebafc5b9f1c69bebed80333e403a09bd62d` |
| `gpu/third_party/xbyak` | `cd6bad3cad2e07a3e277c23d2b1f065320024717` |
| `third_party/LibAtrac9` | `efca2e3af35562a09a9bb6deed90e45b4b824dc4` |

Their Git metadata is isolated under `out/source-dependencies/git`; `.git` pointer files in
those five directories allow the existing build script's patch checks to work without changing
the parent repository's Git metadata. Download URLs and archive SHA256 values are recorded in
`out/source-dependencies/restored.json`. FSR-Vulkan patches 0001–0006 were applied in order.
Keep `out/toolchains` and `out/source-dependencies/git` when clearing individual build folders.

## Updating packages

```powershell
.\tools\with-clang64.ps1 -Command 'pacman -Syu'
```

If MSYS2 updates its core runtime and asks for a new shell, run that command again in a fresh
wrapper invocation. Use one pacman process at a time.
