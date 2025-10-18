import unittest
import tempfile
import os
from raresim.common.legend import Legend, LegendReaderWriter
from raresim.common.exceptions import IllegalArgumentException


class TestLegend(unittest.TestCase):
    def setUp(self):
        """Set up a basic legend for testing"""
        self.header = ["id", "position", "a0", "a1", "fun"]
        self.legend = Legend(self.header)
        self.legend.add_row(["rs123", "1000", "A", "G", "fun"])
        self.legend.add_row(["rs456", "2000", "C", "T", "syn"])
        self.legend.add_row(["rs789", "3000", "G", "A", "fun"])

    def test_get_header(self):
        """Test getting the header"""
        self.assertEqual(self.legend.get_header(), self.header)

    def test_row_count(self):
        """Test row count"""
        self.assertEqual(self.legend.row_count(), 3)

    def test_add_row(self):
        """Test adding a row"""
        self.legend.add_row(["rs999", "4000", "T", "C", "syn"])
        self.assertEqual(self.legend.row_count(), 4)

    def test_remove_row(self):
        """Test removing a row"""
        self.legend.remove_row(1)
        self.assertEqual(self.legend.row_count(), 2)
        self.assertEqual(self.legend.get_row(1)["id"], "rs789")

    def test_get_row(self):
        """Test getting a row as dictionary"""
        row = self.legend.get_row(0)
        self.assertEqual(row["id"], "rs123")
        self.assertEqual(row["position"], "1000")
        self.assertEqual(row["a0"], "A")
        self.assertEqual(row["a1"], "G")
        self.assertEqual(row["fun"], "fun")

    def test_get_row_as_list(self):
        """Test getting a row as list"""
        row = self.legend.get_row_as_list(1)
        self.assertEqual(row, ["rs456", "2000", "C", "T", "syn"])

    def test_getitem(self):
        """Test __getitem__ method"""
        row = self.legend[2]
        self.assertEqual(row["id"], "rs789")


class TestLegendReaderWriter(unittest.TestCase):
    def setUp(self):
        """Create a temporary legend file for testing"""
        self.temp_dir = tempfile.mkdtemp()
        self.legend_file = os.path.join(self.temp_dir, "test.legend")
        
        # Write a test legend file
        with open(self.legend_file, "w") as f:
            f.write("id\tposition\ta0\ta1\tfun\n")
            f.write("rs123\t1000\tA\tG\tfun\n")
            f.write("rs456\t2000\tC\tT\tsyn\n")
            f.write("rs789\t3000\tG\tA\tfun\n")

    def tearDown(self):
        """Clean up temporary files"""
        if os.path.exists(self.legend_file):
            os.remove(self.legend_file)
        os.rmdir(self.temp_dir)

    def test_load_legend(self):
        """Test loading a legend from file"""
        legend = LegendReaderWriter.load_legend(self.legend_file)
        self.assertEqual(legend.row_count(), 3)
        self.assertEqual(legend.get_header(), ["id", "position", "a0", "a1", "fun"])
        self.assertEqual(legend[0]["id"], "rs123")

    def test_load_legend_nonexistent_file(self):
        """Test loading a legend from a non-existent file"""
        with self.assertRaises(IllegalArgumentException):
            LegendReaderWriter.load_legend("nonexistent.legend")

    def test_write_legend(self):
        """Test writing a legend to file"""
        # Create a legend
        legend = Legend(["id", "position", "a0", "a1"])
        legend.add_row(["rs111", "500", "T", "C"])
        legend.add_row(["rs222", "1500", "G", "A"])
        
        # Write it
        output_file = os.path.join(self.temp_dir, "output.legend")
        LegendReaderWriter.write_legend(legend, output_file)
        
        # Read it back
        loaded_legend = LegendReaderWriter.load_legend(output_file)
        self.assertEqual(loaded_legend.row_count(), 2)
        self.assertEqual(loaded_legend[0]["id"], "rs111")
        self.assertEqual(loaded_legend[1]["position"], "1500")
        
        # Clean up
        os.remove(output_file)


if __name__ == '__main__':
    unittest.main()
