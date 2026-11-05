# Frame-generation remediation audit — 2026-11-05

This independent branch adds experimental color-only interpolation, presenter integration,
shader/build wiring and acquire synchronization changes. See [FRAMEGEN_VALIDATION.md](FRAMEGEN_VALIDATION.md)
for runtime evidence and remaining acceptance checks.

The latest runtime incrementally rebuilt successfully, and both frame-generation tests
passed (13 presenter lifecycle scenarios, including the FIFO completion assertion). Three
new startup/title runs used the installed Vulkan validation layer, requested synchronization
validation and closed normally. They logged zero presentation hazards and zero acquire
semaphore 01779 errors; geometry-shader interface errors remain.

The prior three test-*-fix logs are excluded as validation evidence because their requested
validation layer was unavailable and they exited nonzero. The evidence JSON now records
actual exit codes, layer availability and per-run executable/source fingerprints.

Stability, sustained native races, physical display timing, HDR and artifact quality remain
unproven. Pushes are restricted to the owner's separate fork branches; PR #149 is unchanged.
