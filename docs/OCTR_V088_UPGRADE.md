# OCTR v0.8.8 fork preview

The fork uses [OCTR v0.8.8](https://github.com/Ryu7w7/OCTR-NitroFueled-PC/releases/tag/v0.8.8)
as its base. That release includes an experimental DirectX 11 renderer, live graphics
controls, launcher responsiveness improvements, and high-FPS collision and native-renderer
portrait fixes.

The integration carries over Arabic and RTL launcher support, themes and the `--tab`
option, strict patch `Expected` checks, damaged archive detection, staged update merges,
and experimental Vulkan FSR 3.1.6 frame generation. The Windows launcher now stages its
own update merges in a sibling directory before publishing the completed game folder.
The live frame-generation control
follows the approach documented by the
[GetLostIn fork](https://github.com/GetLostIn/CTR-NitroFueled-PC/blob/v0.4/docs/sacredfire/16-framegen.md).
This build uses color-only optical flow. See [frame generation](sacredfire/16-framegen.md)
for the available controls and supported formats.

## Windows checks on November 17, 2026

- A fresh build produced the runtime, Windows launcher and GPU capability utility. The
  targeted suites ran 118 tests with 112 passes and six skips.
- On AMD Radeon integrated graphics, EUR 1.21 (`CUSA14876`) ran the Vulkan renderer with
  FSR enabled and synchronization validation active. The driver fell back from Mailbox
  to FIFO. The runtime reported at least 1,800 generated-and-real pairs queued, no
  presentation synchronization hazards or acquire semaphore reuse errors, and exit code
  0. Vulkan still reported the geometry-shader interface error `08743`.
- USA 1.21 (`CUSA13795`) ran the DirectX 11 renderer on the same machine, reported at
  least 3,600 pictures presented and exited with code 0. This was a startup and
  presentation smoke test. The tests used separate profiles and caches.
- The portable runtime also booted the USA dump in Vulkan with frame generation off
  and exited with code 0. The graphics-menu archive test passed on both dumps.
- A Windows harness ran the launcher's merge worker against planning and copy failures,
  successful retries, update precedence, hard links and existing destination preservation.

Queued frames measure submissions. A fresh GPU order capture, visible pacing and artifact
checks, and sustained race tests are still needed for this build. The
[November 5 report](FRAMEGEN_VALIDATION.md) describes earlier binaries.
