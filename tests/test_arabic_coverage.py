"""Keep Arabic key coverage and Windows formatting intact as launcher text changes."""
from paths import ROOT
import json
import re
import unittest

from test_launcher_locales import translated_texts

LITERAL = r'"(?:[^"\\]|\\.)*"'
LITERALS = rf'(?:{LITERAL}\s*)+'
PRINTF = re.compile(r'%(?:\d+\$)?[-+#0 ]*(?:\d+|\*)?(?:\.(?:\d+|\*))?(?:hh|ll|[hljztL])?[diuoxXfFeEgGaAcspn%]')
TECHNICAL_LABELS = {'AMD FSR 1', 'Steam', 'Vulkan (shadPS4)', ' - Vulkan '}


def windows_table():
    source = (ROOT / 'launcher/windows/launcher_locales.h').read_text(encoding='utf8')
    arabic = source.split('{"ar", {', 1)[1].split('}}', 1)[0]
    return {json.loads(key): json.loads(value) for key, value in
            re.findall(r'\{(' + LITERAL + r'),\s*(' + LITERAL + r')\}', arabic)}


class ArabicCoverageTests(unittest.TestCase):
    def test_gtk_key_coverage(self):
        table = json.loads((ROOT / 'launcher/locales/ar.json').read_text(encoding='utf8'))
        self.assertEqual(set(table), translated_texts())
        self.assert_no_english_fallback(table)

    def test_windows_literal_key_coverage(self):
        source = (ROOT / 'launcher/windows/launcher.cpp').read_text(encoding='utf8')
        keys = {''.join(json.loads(part) for part in re.findall(LITERAL, match.group(2)))
                for match in re.finditer(r'\bT\(\s*(' + LITERALS + r')\s*,\s*(' +
                                         LITERALS + r')\s*\)', source)}
        self.assertGreater(len(keys), 300)
        self.assertFalse(keys - windows_table().keys(), 'Missing literal Windows translations')

    def test_windows_translation_formats(self):
        table = windows_table()
        self.assert_no_english_fallback(table)
        for key, value in table.items():
            with self.subTest(text=key):
                # Percentages such as "100% save" are literal UI text, not printf slots.
                source = re.sub(r'(?<=\d)%(?=\s|$)', '', key)
                translated = re.sub(r'(?<=\d)%(?=\s|$)', '', value)
                self.assertEqual(PRINTF.findall(source), PRINTF.findall(translated))
                self.assertEqual(key.count('\n'), value.count('\n'))

    def assert_no_english_fallback(self, table):
        for key, value in table.items():
            if re.search(r'[A-Za-z]{3}', key) and key not in TECHNICAL_LABELS:
                with self.subTest(text=key):
                    self.assertRegex(value, r'[\u0600-\u06ff]')


if __name__ == '__main__':
    unittest.main()
