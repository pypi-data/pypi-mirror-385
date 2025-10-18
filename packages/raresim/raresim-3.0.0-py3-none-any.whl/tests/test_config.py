import unittest
from argparse import Namespace
from raresim.engine.config import RunConfig
from raresim.common.exceptions import IllegalArgumentException


class TestRunConfig(unittest.TestCase):
    def test_standard_run_type(self):
        """Test standard run type configuration"""
        args = Namespace(
            exp_bins="bins.txt",
            exp_fun_bins=None,
            exp_syn_bins=None,
            fun_bins_only=None,
            syn_bins_only=None,
            prob=False,
            z=False,
            small_sample=False,
            activation_threshold=10,
            stop_threshold=20
        )
        config = RunConfig(args)
        self.assertEqual(config.run_type, "standard")
        self.assertFalse(config.remove_zeroed_rows)
        self.assertFalse(config.is_probabilistic)

    def test_func_split_run_type(self):
        """Test functional split run type configuration"""
        args = Namespace(
            exp_bins=None,
            exp_fun_bins="fun_bins.txt",
            exp_syn_bins="syn_bins.txt",
            fun_bins_only=None,
            syn_bins_only=None,
            prob=False,
            z=True,
            small_sample=True,
            activation_threshold=15,
            stop_threshold=25
        )
        config = RunConfig(args)
        self.assertEqual(config.run_type, "func_split")
        self.assertTrue(config.remove_zeroed_rows)
        self.assertTrue(config.small_sample)

    def test_fun_only_run_type(self):
        """Test functional only run type configuration"""
        args = Namespace(
            exp_bins=None,
            exp_fun_bins=None,
            exp_syn_bins=None,
            fun_bins_only="fun_bins.txt",
            syn_bins_only=None,
            prob=False,
            z=False,
            small_sample=False,
            activation_threshold=10,
            stop_threshold=20
        )
        config = RunConfig(args)
        self.assertEqual(config.run_type, "fun_only")

    def test_syn_only_run_type(self):
        """Test synonymous only run type configuration"""
        args = Namespace(
            exp_bins=None,
            exp_fun_bins=None,
            exp_syn_bins=None,
            fun_bins_only=None,
            syn_bins_only="syn_bins.txt",
            prob=False,
            z=False,
            small_sample=False,
            activation_threshold=10,
            stop_threshold=20
        )
        config = RunConfig(args)
        self.assertEqual(config.run_type, "syn_only")

    def test_probabilistic_run_type(self):
        """Test probabilistic run type configuration"""
        args = Namespace(
            exp_bins=None,
            exp_fun_bins=None,
            exp_syn_bins=None,
            fun_bins_only=None,
            syn_bins_only=None,
            prob=True,
            z=False,
            small_sample=False,
            activation_threshold=10,
            stop_threshold=20
        )
        config = RunConfig(args)
        self.assertEqual(config.run_type, "probabilistic")
        self.assertTrue(config.is_probabilistic)

    def test_invalid_configuration(self):
        """Test invalid configuration raises exception"""
        args = Namespace(
            exp_bins=None,
            exp_fun_bins="fun_bins.txt",  # Only one of the pair
            exp_syn_bins=None,
            fun_bins_only=None,
            syn_bins_only=None,
            prob=False,
            z=False,
            small_sample=False,
            activation_threshold=10,
            stop_threshold=20
        )
        with self.assertRaises(IllegalArgumentException):
            RunConfig(args)


if __name__ == '__main__':
    unittest.main()
