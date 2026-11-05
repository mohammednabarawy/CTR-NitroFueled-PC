# Frame-generation remediation audit — 2026-11-05

This independent branch contains experimental color-only interpolation, presenter integration,
shader/build wiring and acquire synchronization changes. See [FRAMEGEN_VALIDATION.md](FRAMEGEN_VALIDATION.md)
for runtime evidence and remaining acceptance checks.

The independent runtime incrementally rebuilt successfully and both frame-generation tests
passed (13 presenter lifecycle scenarios, including FIFO completion waits). Three startup/title
runs used the installed Vulkan validation layer and closed normally, logging no synchronization
hazards or acquire semaphore 01779 errors. Geometry-shader interface errors remain.

The later clean-final runs use the consolidated remediation checkout's binary, not a new
clean build of every split branch. All three original clean-final artifact hashes and runtime
log hashes were independently checked. A separate empty-directory build of the consolidated
checkout passed with 258 compiler warning diagnostics and zero build errors. The earlier
"zero warnings" claim is withdrawn. See [PR149_AGENT_AUDIT.md](PR149_AGENT_AUDIT.md).

The three older test-*-fix logs remain excluded as validation evidence because their requested
layer was unavailable and they exited nonzero. Per-run fingerprints and actual exit/layer
status are recorded in the evidence JSON.

The existing RenderDoc ordering captures predate the latest synchronization revision.
Fresh presentation-order evidence, sustained native races, physical timing, HDR and artifact
quality remain unproven. Pushes are restricted to separate fork branches; PR #149 is unchanged.
