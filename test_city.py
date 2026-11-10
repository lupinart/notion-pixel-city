"""Run in a disposable /private/tmp/codex-builds copy."""
import unittest
from datetime import datetime, timezone
from xml.etree import ElementTree as ET
from city import render, taipei_time, scene_for


class CityTest(unittest.TestCase):
    def test_wide_cover_has_full_sky_and_fixed_heading(self):
        root = ET.fromstring(render(scene='day', cover=True))
        self.assertEqual(root.attrib['viewBox'], '0 0 3600 600')
        self.assertEqual(len(root.findall('.//{http://www.w3.org/2000/svg}g[@id="heading-text"]')), 1)

    def test_timezone_and_scene_boundaries(self):
        stamp = taipei_time(datetime(2026, 12, 31, 16, 0, tzinfo=timezone.utc))
        self.assertEqual(stamp.isoformat(), '2027-01-01T00:00:00+08:00')
        for hour, scene in [(0, 'night'), (5, 'night'), (6, 'day'),
                            (16, 'day'), (17, 'dusk'), (18, 'dusk'), (19, 'night')]:
            self.assertEqual(scene_for(stamp.replace(hour=hour)), scene)

    def test_self_contained_svg_and_deterministic_lights(self):
        stamp = taipei_time(datetime(2026, 11, 10, tzinfo=timezone.utc))
        for scene in ('day', 'dusk', 'night'):
            svg = render(stamp, scene)
            root = ET.fromstring(svg)
            self.assertEqual(root.attrib['viewBox'], '0 0 1500 600')
            self.assertIn('2026-11-10', svg)
            self.assertIn('prefers-reduced-motion', svg)
            self.assertNotIn('<script', svg)
            self.assertNotIn('href=', svg)
            self.assertNotIn('<text', svg)
            self.assertNotIn('font-family', svg)
            self.assertIn('aria-label="PAI任務管理"', svg)
            self.assertEqual(svg, render(stamp, scene))
        with self.assertRaises(ValueError):
            render(stamp, 'bad')


if __name__ == '__main__':
    unittest.main()
