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

The first GDI recording was black and is rejected as evidence. The race recording includes
desktop content outside the moved game window and is private, unsuitable for publication.
PresentMon could not start its ETW session because this Windows account lacks the required
elevated session access. No system permissions were changed.

## Validation findings

Vulkan validation identified a real frame-generation bug: SDK copies used images lacking
transfer-source/destination usage. Both flags were added and the corrected runtime rebuilt.
The corrected Immediate run produced no instances of the earlier
`VUID-VkImageMemoryBarrier-oldLayout-01212` or `VUID-vkCmdCopyImage-aspect-06662`.

Other errors remain: `VUID-RuntimeSpirv-OpEntryPoint-08743` (geometry input interface) and
`SYNC-HAZARD-WRITE-AFTER-PRESENT`. They also occur with generation disabled. Their causes
remain unresolved; they are not certified harmless. RenderDoc's empty replay debug-message
lists do not establish a globally clean validation run.

## Still required

- Complete native-renderer sustained-race comparisons and USA sustained-race checks.
- Extend resize and minimize/restore observations to gameplay and repeated stress cycles.
- Exercise actual HDR bypass on an HDR swapchain; driverless coverage alone is insufficient.
- Finish race/pacing and artifact checks in both regions. Capture physical presentation
  timing when ETW access is available; review visible motion for ghosting/HUD artifacts.
- Resolve or separately establish the baseline validation findings before claiming stability.

Raw captures, extracted textures, game files, saves, caches and desktop recordings stay local.
