"""Offline evidence-state regressions; no network or temporary directories."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] /
                       'skills/ecommerce-seo-website-migration/scripts'))
import migration_checks as mc


class DispositionTests(unittest.TestCase):
    def trace(self):
        return {'error': '', 'loop': False,
                'hops': [('https://store.example/product', 200, '')],
                'head': {}, 'headers': {}, 'final_status': 200,
                'final_url': 'https://store.example/product'}

    def test_unknown_dispositions_cannot_pass(self):
        for decision in ('rerirect', 'Redirect', 'unexpected'):
            with self.subTest(decision=decision):
                state, problems = mc.evaluate({'disposition': decision}, self.trace())
                self.assertEqual(state, 'not_tested')
                self.assertTrue(problems)
                self.assertIn(decision, problems[0])

    def test_undecided_rows_remain_not_tested(self):
        for decision in ('', 'investigate'):
            with self.subTest(decision=decision):
                self.assertEqual(mc.evaluate({'disposition': decision}, self.trace())[0], 'not_tested')

    def test_supported_decisions_keep_their_checks(self):
        for decision, expected in [('retain', 'passed'), ('remove', 'failed'),
                                   ('redirect', 'failed'), ('consolidate', 'failed')]:
            with self.subTest(decision=decision):
                self.assertEqual(mc.evaluate({'disposition': decision}, self.trace())[0], expected)


if __name__ == '__main__':
    unittest.main()
