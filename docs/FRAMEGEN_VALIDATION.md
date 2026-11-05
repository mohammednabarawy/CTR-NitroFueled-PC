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
  `out/pr149-split-build/framegen` and reproducible clean build from an empty directory in
  `out/pr149-clean-final` producing `sacredfire.exe` (`f9ecfc3c0073870d99be967475330d6e552e7daf830e79297ac3448c33ccfb59`),
  `CTR-NitroFueled-PC.exe` (`0f6f841f2f6ad3dbf44ed8ab2a8646ac6ff37cc41990187b9f48c48e91c51f79`), and
  `bb-gpu-capabilities.exe` (`e86711919e2ac7246fc622656014f4428c1ac88e7d313854b1ca8b5b9614b5fb`) with zero warnings.
  Both frame-generation tests passed, including 13 driverless presenter scenarios. These tests do not execute FSR shaders.
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
  These captures predate the later acquire-fence synchronization revision; they do not
  certify physical presentation order or quality for the latest revision.

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

The synchronization revision expands the acquire semaphore/fence pool to at least 16 slots
(`max(image_count * 4, 16)`), waits for generated GPU completion in FIFO as well as non-FIFO,
waits/resets acquire fences on the host, and uses bottom-of-pipe presentation barriers.
Acquire-fence wait/reset failures are now checked instead of silently continuing. The
driverless harness also asserts generated completion before the real frame in FIFO.

The first three `test-*-fix` logs are **excluded as validation evidence**: each reports
`Requested layer VK_LAYER_KHRONOS_validation is not available` and exits with code
`4294967295`. Previous `validation_layer_listed=true` and `clean_exit=true` fields were
incorrect and have been corrected. Historical cases retain their own executable fingerprints;
new runs no longer inherit the old executable hash.

Fresh runs explicitly supplied the Windows path to the local validation manifest, requested
both core and synchronization validation, and ended by closing the game normally:

| Audit case | Generation | Mode | WRITE-AFTER-PRESENT | 01779 | All logged sync hazards | Exit |
|---|---|---|---:|---:|---:|---:|
| `audit-eur-off-mailbox` | off | Mailbox | 0 | 0 | 0 | 0 |
| `audit-eur-fsr3-mailbox` | fsr3 | Mailbox | 0 | 0 | 0 | 0 |
| `audit-usa-fsr3-fifo` | fsr3 | Fifo | 0 | 0 | 0 | 0 |

The enabled runs logged 6,000 and 7,200 successful generated/real pairs respectively. These
are startup/title observations, not completed races or measured 60 FPS physical scanout.
The new USA snapshot was read directly from the game's BGRA buffer; it contains no desktop.

A subsequent validation audit of the clean scratch build (`out/pr149-clean-final`) under full
Khronos Validation + SyncVal with graceful window teardown (`WM_CLOSE` -> `SDL_EVENT_QUIT`)
confirmed 0 hazards across all three cases:

| Clean build audit case | Generation | Mode | WRITE-AFTER-PRESENT | 01779 | All sync hazards | Generated pairs | Exit |
|---|---|---|---:|---:|---:|---:|---:|
| `audit-final-eur-off-mailbox` | off | Mailbox | 0 | 0 | 0 | 0 | 0 |
| `audit-final-eur-fsr3-mailbox` | fsr3 | Mailbox | 0 | 0 | 0 | 600 | 0 |
| `audit-final-usa-fsr3-fifo` | fsr3 | Fifo | 0 | 0 | 0 | 600 | 0 |

Direct game framebuffer captures (`f000_final_1466x825_bgra.raw` decoded to `game-only.png`)
were recorded for each `audit-final-*` run directly from the Vulkan temporal upscaler dump trigger,
confirming rendered title/menu content without OS window chrome or desktop artifacts.

These results support the combined synchronization change for the observed intervals, not
an isolated causal proof for each change. An acquire fence is optional when a semaphore is
provided: the [Vulkan acquire contract](https://docs.vulkan.org/refpages/latest/refpages/source/vkAcquireNextImageKHR.html)
requires the reused semaphore to have no pending operations. SyncVal handles acquired images
through both host fence waits and
[submit semaphore waits](https://github.com/KhronosGroup/Vulkan-ValidationLayers/blob/main/layers/sync/sync_submit.cpp).
It is therefore inaccurate to claim that only a host acquire-fence wait can synchronize
presentation, or that every valid presentation transition requires bottom-of-pipe.

The geometry input interface issue `VUID-RuntimeSpirv-OpEntryPoint-08743` is still logged in
all three audit runs. Its cause has not been resolved or certified harmless.

## Still required

- Complete native-renderer sustained-race comparisons and USA sustained-race checks.
- Extend resize and minimize/restore observations to gameplay and repeated stress cycles.
- Exercise actual HDR bypass on an HDR swapchain; driverless coverage alone is insufficient.
- Finish race/pacing and artifact checks in both regions. Capture physical presentation
  timing when ETW access is available; review visible motion for ghosting/HUD artifacts.
- Resolve or separately establish the baseline validation findings before claiming stability.

Raw GPU captures, extracted textures, game files, saves, caches and game-only recordings stay local.
