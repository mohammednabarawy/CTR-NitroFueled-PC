# Fork-only review branches

The upstream PR and original `feat/fsr3-framegen-usa-eur-themes` head are unchanged.
No upstream PR description or review comment should be posted until the owner authorizes it.
These independent branches start from upstream main
`569f22ead1612610a3e6c2d998dab191d34440df`:

| Change | Fork branch | Scope and limits |
|---|---|---|
| Arabic | [codex/pr149-arabic](https://github.com/mohammednabarawy/CTR-NitroFueled-PC/tree/codex/pr149-arabic) | RTL shaping, 449 GTK keys and 531 Windows entries, with tests for static key coverage and format preservation. Preserves upstream Indonesian support. Visual layout and translation quality still need user review. |
| Themes | [codex/pr149-themes](https://github.com/mohammednabarawy/CTR-NitroFueled-PC/tree/codex/pr149-themes) | Five persisted launcher themes and actual startup `--tab` parsing. |
| Frame generation | [codex/pr149-framegen](https://github.com/mohammednabarawy/CTR-NitroFueled-PC/tree/codex/pr149-framegen) | Experimental color-only FSR 3.1.6, presenter wiring, build integration and control-flow tests. See the runtime report; stability is unproven. |
| Patch/archive/merge | [codex/pr149-patch-behavior](https://github.com/mohammednabarawy/CTR-NitroFueled-PC/tree/codex/pr149-patch-behavior) | Expected verification, damaged archive checks and staged publication of merges; 55 independent regression tests pass. |

`codex/pr149-remediation` preserves the original combined commit and adds the corrections and
aggregate evidence. It is a backup/review branch, not an independent replacement for the four
changes above. No force-push or rewrite of the original combined head is required.

## Frame-generation description decision

Use the description below when a future PR is authorized. Do not retain the original
depth/velocity, separated-HUD, runtime-toggle or verified-gameplay claims.

> Add experimental FSR 3.1.6 color-only optical-flow interpolation to presentation. Generated
> images are queued before their real frames, with separate frame-reuse fence handling and
> non-FIFO spacing. The feature defaults off and uses startup INI/environment settings.
> The HUD remains inside the interpolated color image; game velocity/depth inputs and
> frame-generation UI/hotkeys are not connected. Clean builds and regression tests pass.
> GPU capture and initial runtime observations are documented, but the full acceptance
> matrix and validation findings remain open.

The current decision is to narrow claims to the implemented behavior. Additional vector,
HUD-separation or toggle implementation would be a separate development task.
