# Experimental frame generation: local evidence — 2026-11-05

Status: **not certified stable**. No upstream PR update is authorized. Test binaries are built
from the independent frame-generation worktree; saves and caches are isolated per case.

## What is implemented

The presenter runs FSR 3.1.6 color-only optical flow on completed 8-bit frames, HUD included.
It submits an interpolated image before its corresponding real image, with half-interval
spacing after generation in non-FIFO modes. Startup INI/environment settings select it.
Game velocity/depth input, HUD-less snapshots, runtime hotkeys and launcher controls remain
unconnected. Unsupported HDR formats bypass generation.

## Completed evidence

- Clean Windows build of the runtime, launcher and capability tool in
  `out/pr149-split-build/framegen`; both frame-generation tests passed, including 13
  driverless presenter scenarios. These tests do not execute FSR shaders.
- EUR 1.21 regular renderer reached the title and menus with generation off and on. FIFO,
  Mailbox and Immediate have been exercised. An Immediate run reached a completed three-lap
  race, with 28,200 successful generated/real pairs before a normal exit (code 0).
- USA CUSA13795 1.21 reached the title with generation off (30 FPS overlay), and the menu
  and intro with generation enabled in FIFO (approximately 60 FPS presentation overlay).
  The overlay is not a physical-scanout measurement. Maximizing resized the active FSR
  context from 1466x825 to 1793x1009; visible output continued. Minimize and restore also
  recovered visible animated output with generation still active.
- A later USA Immediate session reached live race rendering (observed past 1:13), logged
  34,200 successful pairs across the whole session and exited normally. The total includes
  menus and intro; it is not a race-duration or completed-lap measurement.
- Native-renderer startup comparisons also reached visible title/intro output in both EUR
  and USA, off and on, using Mailbox. Logs explicitly confirm native-only drawing. Disabled
  runs show a 30 FPS overlay; enabled runs show approximately 60 FPS and successful pairs.
  These are startup observations, not native-renderer sustained-race acceptance.
  USA native resize recreated the 1793x1009 FSR context and resumed pairs; minimize/restore
  recovered visible title animation as well.
  The [run summary](evidence/framegen-runtime-runs.json) records executable/log hashes,
  clean exits and logged validation counts. A listed layer alone does not certify coverage.
- Four consecutive RenderDoc 1.47 GPU captures replayed successfully. Actual swapchain blits
  alternate generated output, `Frame image #0`, generated output, `Frame image #1`.
  The generated captures include the additional compute dispatches and copy work. The local
  replay report is `out/runtime-evidence/eur-fsr3-mailbox-capture/pair-analysis.json`.
  A [sanitized summary with capture hashes](evidence/framegen-gpu-order.json) is in Git.

| Capture | Blit event | Source | Dispatches | Presents |
|---|---:|---|---:|---:|
| `capture_frame46564.rdc` | 2496 | Generated image 6249 | 54 | 1 |
| `capture_frame46565.rdc` | 2201 | Real frame image 0 | 17 | 1 |
| `capture_frame46566.rdc` | 2496 | Generated image 6338 | 54 | 1 |
| `capture_frame46567.rdc` | 32 | Real frame image 1 | 0 | 1 |

The exported blit-source textures were inspected: expected orange character/blue background
colors are visible. An eight-second GPU desktop-duplication title recording also shows the
game. These observations support submitted GPU image ordering and visible output; they do
not measure physical scanout or prove that Mailbox displayed every queued image.

A USA FIFO intro recording after resize/restore also contains visible game output. Fast
motion shows interpolation artifacts; this recording does not establish acceptable quality.

The first GDI recording was black and is rejected as evidence. A race recording included
desktop content outside the moved game window; it and its contact sheet were removed.
The clean title and intro clips were cropped to game pixels only, reviewed in contact sheets
and retained locally as `eur-fsr3-fifo/title-game-only.mp4` and
`usa-fsr3-fifo/intro-game-only.mp4` beneath `out/runtime-evidence`. Their wider originals and
the older screenshots with window borders were removed. GPU texture exports contain game
output directly. Future evidence must use game-buffer capture and exclude all desktop/apps.
No screenshots, recordings or raw GPU captures were pushed to the fork.
The [capture audit](evidence/framegen-capture-audit.json) records retained filenames, hashes
and crop rectangles without embedding any media. Earlier automatic chat previews cannot be
changed; subsequent retained evidence must contain only game pixels.
PresentMon could not start its ETW session because this Windows account lacks the required
elevated session access. No system permissions were changed.

## Validation findings

Vulkan validation identified a real frame-generation bug: SDK copies used images lacking
transfer-source/destination usage. Both flags were added and the corrected runtime rebuilt.
The corrected Immediate run produced no instances of the earlier
`VUID-VkImageMemoryBarrier-oldLayout-01212` or `VUID-vkCmdCopyImage-aspect-06662`.

Vulkan Synchronization Validation also surfaced two presenter lifecycle issues:
1. `SYNC-HAZARD-WRITE-AFTER-PRESENT`: SyncVal tracks swapchain image presentation release via
   host fence waits (`SyncValidator::WaitForFence` calling `ApplyAcquireWait`). Passing
   `VK_NULL_HANDLE` for the acquire fence prevented SyncVal from recording present completion,
   while `PresentImage` omitted `dstStageMask = eBottomOfPipe` when transitioning to
   `ePresentSrcKHR`. A dedicated acquire fence pool with host wait/reset and compliant bottom-of-pipe
   barriers resolved this hazard (0 instances across both disabled and FSR 3.1 runs).
2. `VUID-vkAcquireNextImageKHR-semaphore-01779`: In FIFO mode with frame generation active,
   `image_acquired` was restricted to `image_count` (3) semaphores while presenting 2 images
   per guest frame. Skipping `present_scheduler.Wait(generated_tick)` in FIFO mode allowed
   semaphore reuse while previous submissions were still pending. Expanding the acquire semaphore
   ring buffer to 16 slots and synchronizing generated submission completion eliminated this error.

The baseline geometry input interface issue `VUID-RuntimeSpirv-OpEntryPoint-08743` originates in
the guest PS4 shader translator pipeline and remains separate from presenter synchronization.
Recent sync-validation comparison logs include `out/test-eur-off-mailbox-fix-console.log`,
`out/test-eur-fsr3-mailbox-fix-console.log`, and `out/test-usa-fsr3-fifo-fix-console.log`.

## Still required

- Complete native-renderer sustained-race comparisons and USA sustained-race checks.
- Extend resize and minimize/restore observations to gameplay and repeated stress cycles.
- Exercise actual HDR bypass on an HDR swapchain; driverless coverage alone is insufficient.
- Finish race/pacing and artifact checks in both regions. Capture physical presentation
  timing when ETW access is available; review visible motion for ghosting/HUD artifacts.
- Resolve or separately establish the baseline validation findings before claiming stability.

Raw GPU captures, extracted textures, game files, saves, caches and game-only recordings stay local.
