import unittest
from raresim.common.sparse import SparseMatrix
from raresim.common.legend import Legend
from raresim.engine.utils import print_bin, adjust_for_protected_variants, add_protected_rows_back


class TestUtils(unittest.TestCase):
    def setUp(self):
        """Set up test data"""
        self.bins = [
            (1, 1, 10.0),
            (2, 2, 5.0),
            (3, 5, 3.0)
        ]
        self.bin_assignments = {
            0: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            1: [10, 11, 12, 13, 14],
            2: [15, 16, 17],
            3: []
        }

    def test_print_bin(self):
        """Test print_bin function (just ensure it doesn't crash)"""
        try:
            print_bin(self.bins, self.bin_assignments)
        except Exception as e:
            self.fail(f"print_bin raised an exception: {e}")

    def test_adjust_for_protected_variants(self):
        """Test adjusting for protected variants"""
        # Create a legend with protected variants
        legend = Legend(["id", "position", "protected"])
        for i in range(20):
            protected = "1" if i in [0, 5, 10] else "0"
            legend.add_row([f"rs{i}", str(i * 1000), protected])
        
        # Use lists instead of tuples so they can be modified
        bins_copy = [[b[0], b[1], b[2]] for b in self.bins]
        bin_assignments_copy = {k: v.copy() for k, v in self.bin_assignments.items()}
        
        protected_vars = adjust_for_protected_variants(bins_copy, bin_assignments_copy, legend)
        
        # Check that protected variants were removed from bin assignments
        self.assertNotIn(0, bin_assignments_copy[0])
        self.assertNotIn(5, bin_assignments_copy[0])
        self.assertNotIn(10, bin_assignments_copy[1])
        
        # Check that protected variants are tracked
        self.assertIn(0, protected_vars[0])
        self.assertIn(5, protected_vars[0])
        self.assertIn(10, protected_vars[1])

    def test_add_protected_rows_back(self):
        """Test adding protected rows back"""
        # Use lists instead of tuples so they can be modified
        bins_copy = [[b[0], b[1], b[2]] for b in self.bins]
        bin_assignments_copy = {k: v.copy() for k, v in self.bin_assignments.items()}
        
        protected_vars_per_bin = {
            0: [0, 5],
            1: [10],
            2: [],
            3: []
        }
        
        original_count_0 = bins_copy[0][2]
        original_count_1 = bins_copy[1][2]
        
        add_protected_rows_back(bins_copy, bin_assignments_copy, protected_vars_per_bin)
        
        # Check that expected counts were updated
        self.assertEqual(bins_copy[0][2], original_count_0 + 2)
        self.assertEqual(bins_copy[1][2], original_count_1 + 1)
        
        # Check that protected variants were added back
        self.assertIn(0, bin_assignments_copy[0])
        self.assertIn(5, bin_assignments_copy[0])
        self.assertIn(10, bin_assignments_copy[1])


if __name__ == '__main__':
    unittest.main()
