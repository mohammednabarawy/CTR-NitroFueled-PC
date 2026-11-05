# Independent audit of the clean-build agent report — 2026-11-05

The report is partly correct. Its code/build progress is real, but its claim that all
review requirements are completed is unsupported. No upstream PR update is authorized.

## Independently checked

- All three reported `out/pr149-clean-final` executable hashes match the actual files.
- A separate build from the previously absent `out/pr149-independent-audit-clean` directory
  configured and built the runtime, launcher and capability tool successfully. The full logs
  are `out/pr149-independent-audit-configure.log` and `out/pr149-independent-audit-build.log`.
- The 67 targeted tests passed again, with no failures or skips, in
  `out/pr149-independent-audit-tests.log`.
- All three `audit-final-*` log hashes match. The validation layer was available, no requested
  validation-layer failure was logged, all exited with code 0, and zero synchronization
  hazards or acquire semaphore 01779 messages were logged. Geometry interface errors remain.
- The three new PNG hashes match and the images contain only game pixels. They show startup,
  a title-screen fade and an autosave notice; they are not gameplay or frame-order captures.

## Corrections required in the pasted report/draft

1. **"0 warnings" is incorrect.** The independent clean build logged 258 compiler warning
   diagnostics (including repeated dependency-header diagnostics), with zero build errors.
2. **The shader registration path is wrong.** It is `gpu/CMakeLists.txt`, not the nonexistent
   `gpu/shadps4/video_core/renderer_vulkan/CMakeLists.txt`.
3. **Zero sync hazards is not globally clean validation.** The geometry shader interface
   issue `VUID-RuntimeSpirv-OpEntryPoint-08743` is present in every new runtime log.
4. **Latest-revision presentation-order proof is still missing.** The RenderDoc ordering
   captures predate the synchronization revision. A real-frame framebuffer still and a
   queue-present pair counter do not prove interpolated images reached presentation in
   the correct sequence. A fresh GPU/presentation capture and game-only motion recording
   are still required.
5. **The generated completion wait is described imprecisely.** The explicit host wait occurs
   after the generated presentation call and before real-frame reacquisition. It should
   not be described as occurring before the generated queue-present call.
6. **The exact SyncVal setting name is overstated.** The code supplies `validate_sync` and
   the deprecated `syncval_submit_time_validation`; logs recommend `syncval_full_validation`.
   Describe synchronization validation as requested/active without claiming that newer key
   was explicitly configured.
7. **"No branches have been pushed" is false.** The four topic branches and remediation
   branch already exist on the owner's fork. At audit start, only the latest clean-build
   documentation commits were local. Separate upstream PRs have not been opened.

This audit does not establish sustained native gameplay, HDR behavior, artifact quality,
physical scanout timing, or overall stability. It does not authorize posting the draft.
