import unittest
from decimal import Decimal

from calculator import register_input, solve, solve_arr_psc


class TimerMathTests(unittest.TestCase):
    def test_all_four_parameters(self):
        known = dict(period_s=Decimal("0.001"), arr=999, psc=79, clock_hz=Decimal(80_000_000))
        self.assertEqual(solve("T", **known).value, Decimal("0.001"))
        self.assertEqual(solve("Output frequency", **known).value, Decimal(500))
        self.assertEqual(solve("Clock", **known).value, Decimal(80_000_000))
        self.assertEqual(solve("ARR", **known).register, 999)
        self.assertEqual(solve("PSC", **known).register, 79)

    def test_fractional_register_reports_achieved_period(self):
        result = solve("ARR", period_s=Decimal("0.0015"), psc=0, clock_hz=Decimal(1000))
        self.assertEqual(result.value, Decimal("0.5"))
        self.assertEqual(result.register, 1)
        self.assertEqual(result.achieved_period_s, Decimal("0.002"))
        self.assertGreater(result.error_percent, 0)

    def test_register_range_and_validation(self):
        self.assertEqual(solve("ARR", period_s=Decimal(1), psc=0, clock_hz=Decimal(100_000), arr_bits=32).register, 99_999)
        self.assertEqual(solve("ARR", period_s=Decimal(1), psc=0, clock_hz=Decimal(100_000), arr_bits=16).register, 65_535)
        with self.assertRaises(ValueError):
            register_input("1.5", "PSC", 65535)
        with self.assertRaises(ValueError):
            solve("Clock", period_s=Decimal(0), arr=1, psc=1)

    def test_pair_solver_uses_target_period_and_clock(self):
        result = solve_arr_psc(Decimal("0.001"), Decimal(80_000_000))
        self.assertEqual((result.arr, result.psc), (39_999, 1))
        self.assertEqual(result.achieved_period_s, Decimal("0.001"))
        self.assertEqual(result.error_percent, 0)

    def test_pair_solver_picks_nearest_possible_period(self):
        result = solve_arr_psc(Decimal("0.0015"), Decimal(1000))
        self.assertEqual((result.arr, result.psc), (1, 0))
        self.assertEqual(result.achieved_period_s, Decimal("0.002"))

    def test_pair_solver_supports_32_bit_arr(self):
        result = solve_arr_psc(Decimal(1), Decimal(100_000), 32)
        self.assertEqual((result.arr, result.psc), (99_999, 0))

    def test_frequency_target_can_be_used_for_registers_and_clock(self):
        period_s = 1 / (2 * Decimal(500))
        self.assertEqual(solve("ARR", period_s=period_s, psc=79, clock_hz=Decimal(80_000_000)).register, 999)
        self.assertEqual(solve("Clock", period_s=period_s, arr=999, psc=79).value, Decimal(80_000_000))
        pair = solve_arr_psc(period_s, Decimal(80_000_000))
        self.assertEqual((pair.arr, pair.psc), (39_999, 1))


if __name__ == "__main__":
    unittest.main()
