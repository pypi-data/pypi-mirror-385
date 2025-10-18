import unittest
from raresim.common.exceptions import RaresimException, IllegalArgumentException


class TestExceptions(unittest.TestCase):
    def test_raresim_exception(self):
        """Test RaresimException can be raised and caught"""
        with self.assertRaises(RaresimException) as context:
            raise RaresimException("Test error message")
        self.assertIn("Test error message", str(context.exception))

    def test_illegal_argument_exception(self):
        """Test IllegalArgumentException can be raised and caught"""
        with self.assertRaises(IllegalArgumentException) as context:
            raise IllegalArgumentException("Invalid argument")
        self.assertIn("Invalid argument", str(context.exception))

    def test_illegal_argument_is_raresim_exception(self):
        """Test that IllegalArgumentException is a subclass of Exception"""
        # Both inherit from Exception independently
        self.assertTrue(issubclass(IllegalArgumentException, Exception))
        self.assertTrue(issubclass(RaresimException, Exception))


if __name__ == '__main__':
    unittest.main()
