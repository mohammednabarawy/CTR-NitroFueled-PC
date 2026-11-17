# Local remediation and fork validation — 2026-11-05

The original combined change is `2022d2e99fd67aeb545aa9246fbfa8bb02c2669d`.
The upstream PR and its head branch are intentionally unchanged. Corrections and split
changes belong only on separate `codex/pr149-*` branches in the owner's fork until stable.
Existing installed binaries and saves were preserved; runtime tests use isolated directories.

## Changes

- Frame generation belongs to the presentation scheduler and runs on finished frames.
  Generated images are submitted before real images. Only the real submission signals the
  reuse fence; skipped acquisitions, size changes and unsupported formats invalidate history.
  The shader is registered in CMake and the FSR 3.1.6 frame-generation library is linked.
- Runtime Vulkan validation exposed missing transfer usage on FSR working images. Both
  transfer-source and transfer-destination usage flags are now included.
- Synchronization changes add an acquire semaphore/fence ring of at least 16 slots, host
  acquire-fence waits with checked wait/reset results, bottom-of-pipe presentation barriers,
  and generated GPU completion waits in every mode. Three reruns with validation available
  logged zero presentation hazards and zero 01779 errors; broader stability remains unproven.
- Patch Expected references must be valid, cover the overwrite, and match exactly one site.
  When Signature is also supplied, Expected verifies that resolved site.
- Recognizable truncated/damaged IGA archives are rejected. Dump merges build in a sibling
  staging directory and publish by rename, cleaning staging after failure.
- The launcher implements its advertised `--tab` startup argument.
- Documentation describes color-only optical flow. Game velocity vectors, HUD-less frames,
  a frame-generation launcher control and in-game toggles are not implemented.

## Builds and tests

The isolated full clean Windows build produced `sacredfire.exe`, the launcher and the GPU
capability tool. The final incremental rebuild passed after the usage-flag fix and launcher
argument correction. See `out/pr149-final-build.log`.
The later audit rebuilt the runtime and launcher after the synchronization and Arabic fixes
(`out/pr149-audit-build.log`), and rebuilt the independent Arabic launcher and frame-generation
runtime (`out/pr149-split/arabic-audit-build.log`, `framegen-audit-build.log`).

A subsequent reproducible clean build from an empty directory was performed in `out/pr149-clean-final`
producing `sacredfire.exe` (`f9ecfc3c0073870d99be967475330d6e552e7daf830e79297ac3448c33ccfb59`),
`CTR-NitroFueled-PC.exe` (`0f6f841f2f6ad3dbf44ed8ab2a8646ac6ff37cc41990187b9f48c48e91c51f79`), and
`bb-gpu-capabilities.exe` (`e86711919e2ac7246fc622656014f4428c1ac88e7d313854b1ca8b5b9614b5fb`). An independent
empty-directory rebuild in `out/pr149-independent-audit-clean` passed with 258 compiler warning
diagnostics and zero build errors; the earlier "zero warnings" claim was incorrect. Validation
runs against the original clean binary (`audit-final-*`) logged zero synchronization hazards and
exit code 0 across EUR baseline, EUR FSR3 Mailbox, and USA FSR3 FIFO. Geometry interface errors remain.

The latest aggregate targeted run passed **67 tests**, with no skips or failures, in
`out/pr149-audit-tests.log`: 30 patch, 15 game-check, seven merge, five locale/Arabic, two
frame-generation and eight telemetry tests. The presenter test contains 13 driverless
scenarios; these test production control flow but do not execute Vulkan or FSR shaders.

Four independent branches were prepared against upstream main
`569f22ead1612610a3e6c2d998dab191d34440df`:

| Branch suffix | Independent checks |
|---|---|
| `arabic` | Launcher build and five locale/coverage tests; 449 GTK keys and 531 Windows entries |
| `themes` | Launcher build, including `--tab` |
| `patch-behavior` | 55 patch/archive/merge tests, preserving current upstream tests |
| `framegen` | Clean runtime, launcher and capability-tool build; two frame-generation tests |

The independent branches are for fork review. The original combined history was preserved.
See [WINDOWS_LOCAL_TOOLCHAIN.md](WINDOWS_LOCAL_TOOLCHAIN.md) for the local dependency setup.

## Runtime evidence and remaining gates

See [FRAMEGEN_VALIDATION.md](FRAMEGEN_VALIDATION.md) for captures, observed results and open
acceptance checks. A successful build, queue counters and a GPU-only readback are insufficient
to certify display order or gameplay stability. Large GPU captures, game files, extracted
textures, recordings, caches and unrelated untracked files are excluded from Git.
