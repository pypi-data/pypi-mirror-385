import unittest
import tempfile
import os
from raresim.common.bins import loadBins


class TestBins(unittest.TestCase):
    def setUp(self):
        """Create a temporary bins file for testing"""
        self.temp_dir = tempfile.mkdtemp()
        self.bins_file = os.path.join(self.temp_dir, "test_bins.txt")
        
        # Write a test bins file
        with open(self.bins_file, "w") as f:
            f.write("Lower\tUpper\tExpected\n")
            f.write("1\t1\t20.5\n")
            f.write("2\t2\t10.3\n")
            f.write("3\t5\t5.7\n")
            f.write("6\t10\t3.2\n")

    def tearDown(self):
        """Clean up temporary files"""
        if os.path.exists(self.bins_file):
            os.remove(self.bins_file)
        os.rmdir(self.temp_dir)

    def test_load_bins(self):
        """Test loading bins from file"""
        bins = loadBins(self.bins_file)
        
        self.assertEqual(len(bins), 4)
        self.assertEqual(bins[0], [1, 1, 20.5])
        self.assertEqual(bins[1], [2, 2, 10.3])
        self.assertEqual(bins[2], [3, 5, 5.7])
        self.assertEqual(bins[3], [6, 10, 3.2])

    def test_load_bins_with_empty_lines(self):
        """Test loading bins with empty lines at the end"""
        bins_file_empty = os.path.join(self.temp_dir, "test_bins_empty.txt")
        with open(bins_file_empty, "w") as f:
            f.write("Lower\tUpper\tExpected\n")
            f.write("1\t1\t20.5\n")
            f.write("2\t2\t10.3\n")
            f.write("\n")
            f.write("\n")
        
        bins = loadBins(bins_file_empty)
        self.assertEqual(len(bins), 2)
        
        os.remove(bins_file_empty)


if __name__ == '__main__':
    unittest.main()
