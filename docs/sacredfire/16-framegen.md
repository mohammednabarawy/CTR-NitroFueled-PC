# Frame generation (experimental presenter integration)

The local remediation connects the implementation to `Presenter::Present`. Driverless
control-flow tests and an isolated clean shader build cover parts of the integration.
A full clean Windows application build has now passed with the local CLANG64 toolchain.
Local GPU captures show alternating generated and real swapchain blits, and visible title
output has been recorded. Physical scanout, the full runtime matrix and remaining validation
errors are still open; see the validation report below.

`bbport.ini` `framegen=off|fsr3` (`fsr`, `on` and `1` from test builds also mean `fsr3`;
`BB_FRAMEGEN` for scripts). The file/environment setting is loaded at startup and defaults to
off. This revision has no launcher or in-game frame-generation control. The presenter handles
changes to the settings atomic, but editing the file while playing does not reload it.

## What it does

AMD FSR 3.1.6 frame interpolation (optical flow + frame interpolation, using the
`ffx-vulkan::fsr3-vk-framegeneration-3.1.6` slice of
[FireBurn/FSR-Vulkan](https://github.com/FireBurn/FSR-Vulkan), MIT) runs on every finished
frame and computes an intermediate image between it and the previous one. The presenter queues
that generated image first, followed by the real image. Non-FIFO modes wait half a smoothed
game-frame interval between them, measured after generation completes on the GPU. FIFO uses
the swapchain's refresh pacing. Physical scanout and smoothness still require runtime validation.

```
game frames      N-1 ───────────────── N ───────────────── N+1
shown            N-1      G(N-1,N)     N      G(N,N+1)     N+1
                 |<-- T/2 -->|<-- T/2 -->|
```

It works on the presenter's finished frame (post-processing done, HUD included); the port's own
menu and FPS counter are drawn afterwards on every present. Generation is suppressed while the
port's settings menu is open. The call path takes the finished frame independently of upscaler
selection and supports both regular and native-renderer presentation paths.

**The current presenter supplies color only.** Flat far depth and zero motion let optical flow
carry motion. Although `CtrFrameGen::Inputs` has optional game-vector and HUD-less inputs, they
are not connected. Reading `CtrFsr3`'s shared working images from the swap thread would race the
next guest frame. Supporting those inputs requires per-frame snapshots with matching lifetime,
size, format and synchronization. The game's HUD is currently part of the interpolated image.

## How to get a smooth result

- **A 120 Hz or faster screen.** Frame generation aims to double what is shown: at 144 Hz the ideal is
  the game at about 72 FPS (fps limit 72) and 144 images on screen. At 60 Hz it has nothing to
  gain.
- **Present mode.** With `Fifo` (V-Sync) the two presents go out one refresh apart by themselves
  and the game settles at half the refresh rate. With `Mailbox`/`Immediate` the presenter waits
  half a game frame between the generated and the real present (the smoothed frame time).
- The existing swapchain image-count policy is retained; extra buffering is not implemented.

## Implementation

- `vk_ctr_framegen.{h,cpp}` (`CtrFrameGen`, owned by the presenter). One FSR 3.1.6 context per
  frame size (render size = frame size, so the game-motion and optical-flow modes share it and
  switching between them only resets the history, never rebuilds the context).
- `Presenter::Present` → `CtrFrameGen::Record`: after acquiring a presentable swapchain image,
  on `present_scheduler`, with the producer's submission issued before the present submission:
  1. the frame (General, MUTABLE_FORMAT) is read raw through a UNORM view of its own byte
     order and copied to an RGBA8 image (`fg_convert.comp`), the only backbuffer format 3.1.6
     takes;
  2. prepare (optical flow + dilation) and dispatch (interpolation) into an RGBA8 image. The
     3.1.5 bridge leaves sampled imports in SHADER_READ_ONLY, so they are imported that way and
     moved there and back around the calls;
  3. the result is copied back into a per-presenter-frame output image in the frame's own
     format (BGRA swaps red and blue back), written through an RGBA8 storage view
     (MUTABLE_FORMAT + EXTENDED_USAGE). The presenter blits it exactly like the real frame.
- `Presenter::PresentImage` blits either image, draws the overlay and submits through
  `SubmitPresentImage`, waiting on the acquired-image semaphore and the producer's ready tick.
  Only the real submission resets/signals `Frame::present_done`. A generated present followed
  by acquisition failure drains `present_scheduler` before returning the slot for reuse.
- Context creation, recording, output reads, retirement and resets all belong to the swap
  thread and `present_scheduler`. Size changes and live disable cannot destroy an output still
  read by another presentation thread. Frame ids are retired after the owning scheduler tick
  completes (`Scheduler::IsFree`).
- History resets: the first frame, a new frame size, a switch between game motion and optical
  flow, more than 100 ms between prepared frames (loads, pauses, hitches), skipped or reused
  frames, swapchain recreation, menu transitions and unsupported HDR. A reset frame goes out alone.
- `gpu/CMakeLists.txt` registers `fg_convert.comp` and links
  `ffx-vulkan::fsr3-vk-framegeneration-3.1.6`; both are required in a clean build.

### FSR-Vulkan patches (`gpu/patches/fsr-vulkan`)

- `0003`: the 3.1.6 wrapper tags the bridge frame on Prepare and retires its transient
  descriptor sets and constant buffers in RetireFrame (they leaked until out of memory).
- `0004`: stages per-pass constant buffers into persistent 256 KiB mapped slabs rather than
  making a Vulkan allocation per constant buffer.
- `0005`: adds a host-visible uniform-buffer fallback when combined device-local/host-visible
  memory cannot be allocated.
- `0006`: adds the optional HUD-less color resource to the bridge API. The presenter currently
  supplies no separate HUD-less image.

## Log lines

```
FrameGen: FSR 3.1.6 context 1920x1080, 59.7 MB
FrameGen: generating at 1920x1080 (optical flow, no HUD-less frame yet)
FrameGen: queued generated before real; total 600 pairs (16.67 ms, Fifo)
FrameGen: <reason>; off for this session
```

The pair line is emitted after the first successful pair of queue-present calls and every
600 successful pairs thereafter. It counts queue-present success, not physical scanout:
Mailbox may discard a queued image. Capture visible motion and presentation timing before
making doubled-FPS or readiness claims.

## Validation

- `tests/test_framegen_presenter.py` compiles the production `Present` and
  `SubmitPresentImage` methods against fake WSI/FFX collaborators. It checks generated-before-real
  order, producer waits, real-only fence signaling, Mailbox spacing, and skipped-frame recovery.
  It does not execute `PresentImage`'s Vulkan commands or the FSR shaders.
- `tests/test_framegen_build.py` uses the actual host-shader CMake function and registration to
  build `fg_convert_comp.h` in a new directory. It does not replace a full application build.
- See [FRAMEGEN_VALIDATION.md](../FRAMEGEN_VALIDATION.md) for local results, findings and
  the remaining runtime acceptance checks.

## Known limits

- The HUD is interpolated with the frame (fast HUD elements can shimmer); separating it would
  need the game's display pass to draw into two buffers.
- 8-bit frames only (HDR swapchains skip generation).
- DLSS Frame Generation is not wired (it needs RTX 40+, Streamline and Reflex).
