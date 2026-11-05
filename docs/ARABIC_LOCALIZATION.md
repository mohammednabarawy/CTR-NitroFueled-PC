# Arabic localization coverage

The independent `codex/pr149-arabic` branch based on upstream main has all **449 GTK keys**
and **531 Windows translation-table entries**. The older combined remediation branch has
440 GTK keys because its English launcher predates the nine newer upstream keys.

The audit completed 16 English fallback entries in the Windows table, added 31 missing
Windows strings (including multiline tooltips), and translated the two remaining legacy
16:10 descriptions in the combined branch. Numbers, resolutions, API/product names and
controller button identifiers intentionally retain their technical spelling.

`tests/test_arabic_coverage.py` checks the GTK English key set, Windows literal `T()` calls
(including concatenated string literals), Arabic content for translatable English labels,
printf placeholders and line breaks. Together with `test_launcher_locales.py`, five tests
pass on both branches. The independent Windows launcher build also passes.

The existing shaping implementation remains in the Windows launcher. Key coverage and
format preservation do not certify every dynamic UI string, visual RTL layout, or translation
quality. Those still require native-speaker/UI review.
