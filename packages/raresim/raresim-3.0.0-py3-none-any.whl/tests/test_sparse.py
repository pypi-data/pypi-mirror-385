import unittest
import tempfile
import os
from raresim.common.sparse import SparseMatrix, SparseMatrixReader, SparseMatrixWriter
from raresim.common.exceptions import IllegalArgumentException

class TestSparseMatrix(unittest.TestCase):
    def setUp(self):
        # Initialize a 3x5 sparse matrix (3 rows, 5 columns)
        self.matrix = SparseMatrix(cols=5)
        # Add rows first
        for _ in range(3):
            self.matrix.add_row([])
        # Now add values
        self.matrix.add(0, 1)
        self.matrix.add(0, 3)
        self.matrix.add(1, 2)
        self.matrix.add(2, 0)
        self.matrix.add(2, 4)

    def test_get(self):
        self.assertEqual(self.matrix.get(0, 1), 1)
        self.assertEqual(self.matrix.get(0, 2), 0)
        self.assertEqual(self.matrix.get(2, 4), 1)

    def test_get_row(self):
        self.assertEqual(self.matrix.get_row(0), [0, 1, 0, 1, 0])
        self.assertEqual(self.matrix.get_row(1), [0, 0, 1, 0, 0])
        self.assertEqual(self.matrix.get_row(2), [1, 0, 0, 0, 1])

    def test_get_row_raw(self):
        """Test getting raw row indices"""
        self.assertEqual(self.matrix.get_row_raw(0), [1, 3])
        self.assertEqual(self.matrix.get_row_raw(1), [2])
        self.assertEqual(self.matrix.get_row_raw(2), [0, 4])

    def test_add_remove(self):
        # Add a value and test
        self.matrix.add(0, 2)
        self.assertEqual(self.matrix.get(0, 2), 1)
        # Remove the value and test
        self.matrix.remove(0, 2)
        self.assertEqual(self.matrix.get(0, 2), 0)

    def test_num_rows_cols(self):
        self.assertEqual(self.matrix.num_rows(), 3)
        self.assertEqual(self.matrix.num_cols(), 5)

    def test_row_num(self):
        """Test getting number of 1s in a row"""
        self.assertEqual(self.matrix.row_num(0), 2)
        self.assertEqual(self.matrix.row_num(1), 1)
        self.assertEqual(self.matrix.row_num(2), 2)

    def test_remove_row(self):
        """Test removing a row"""
        self.matrix.remove_row(1)
        self.assertEqual(self.matrix.num_rows(), 2)
        self.assertEqual(self.matrix.get_row(1), [1, 0, 0, 0, 1])

    def test_prune_row(self):
        """Test pruning a row"""
        # Row 0 has 2 ones, prune 1
        self.matrix.prune_row(0, 1)
        self.assertEqual(self.matrix.row_num(0), 1)

    def test_set_col_count(self):
        """Test setting column count"""
        matrix = SparseMatrix()
        matrix.set_col_count(10)
        self.assertEqual(matrix.num_cols(), 10)


class TestSparseMatrixReader(unittest.TestCase):
    def setUp(self):
        """Create temporary test files"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary files"""
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)

    def test_load_nonexistent_file(self):
        """Test loading a non-existent file raises exception"""
        reader = SparseMatrixReader()
        with self.assertRaises(IllegalArgumentException):
            reader.loadSparseMatrix("nonexistent.haps")

    def test_load_uncompressed(self):
        """Test loading uncompressed haplotype file"""
        haps_file = os.path.join(self.temp_dir, "test.haps")
        with open(haps_file, "w") as f:
            f.write("0 1 0 1 0\n")
            f.write("0 0 1 0 0\n")
            f.write("1 0 0 0 1\n")
        
        reader = SparseMatrixReader()
        matrix = reader.loadSparseMatrix(haps_file)
        
        self.assertEqual(matrix.num_rows(), 3)
        self.assertEqual(matrix.num_cols(), 5)
        self.assertEqual(matrix.get(0, 1), 1)
        self.assertEqual(matrix.get(1, 2), 1)


class TestSparseMatrixWriter(unittest.TestCase):
    def setUp(self):
        """Create a test matrix and temporary directory"""
        self.temp_dir = tempfile.mkdtemp()
        self.matrix = SparseMatrix(cols=5)
        # Create more rows to avoid division by zero in progress reporting
        for i in range(20):
            self.matrix.add_row([i % 5])

    def tearDown(self):
        """Clean up temporary files"""
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)

    def test_write_uncompressed(self):
        """Test writing uncompressed file"""
        output_file = os.path.join(self.temp_dir, "output.haps")
        writer = SparseMatrixWriter()
        writer.writeToHapsFile(self.matrix, output_file, compression="")
        
        self.assertTrue(os.path.exists(output_file))
        
        # Read it back
        with open(output_file, "r") as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 20)
            # First row should have a 1 at position 0
            self.assertIn("1", lines[0].strip())

    def test_write_sm(self):
        """Test writing binary .sm file"""
        output_file = os.path.join(self.temp_dir, "output.sm")
        writer = SparseMatrixWriter()
        writer.writeToHapsFile(self.matrix, output_file, compression="sm")
        
        self.assertTrue(os.path.exists(output_file))
        
        # Read it back
        reader = SparseMatrixReader()
        loaded_matrix = reader.loadSparseMatrix(output_file)
        self.assertEqual(loaded_matrix.num_rows(), 20)
        self.assertEqual(loaded_matrix.num_cols(), 5)


if __name__ == '__main__':
    unittest.main()
