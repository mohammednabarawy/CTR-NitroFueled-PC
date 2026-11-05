# Local changes to gpu/third_party/fsr-vulkan

The submodule points at upstream FireBurn/FSR-Vulkan (`c64f093`). `build.sh` applies the
patches here to its working tree when they are not applied yet:

- `0001-...`: `BB_FSR4_PROFILE` (GPU time per FSR 4 pass) and `BB_FSR4_STATS` (driver
  statistics of each pass) in the FSR 4 v07 provider.
- `0002-...`: `#include <mutex>` in the FFX Vulkan backend; libc++ (the Windows MSYS2 CLANG64
  build) does not include it transitively.
- `0003-...`: retire frame-generation bridge transients after the owning submission completes.
- `0004-...`: stage bridge constant buffers in mapped slabs.
- `0005-...`: fall back to host-visible uniform-buffer memory when the combined heap is unavailable.
- `0006-...`: accept an optional HUD-less input. The current presenter integration uses the
  finished color frame and does not yet supply a separate HUD-less snapshot.
