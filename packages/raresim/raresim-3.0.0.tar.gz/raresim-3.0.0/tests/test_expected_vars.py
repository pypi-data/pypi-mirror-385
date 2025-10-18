import unittest
import tempfile
import os
import pandas as pd
import numpy as np
from raresim.calculate.expected_vars import (
    read_mac_bins,
    afs,
    nvariants,
    fit_afs,
    fit_nvars,
    DEFAULT_PARAMS
)


class TestExpectedVars(unittest.TestCase):
    def setUp(self):
        """Create temporary files for testing"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary files"""
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)

    def test_read_mac_bins_csv(self):
        """Test reading MAC bins from CSV file"""
        csv_file = os.path.join(self.temp_dir, "macs.csv")
        with open(csv_file, "w") as f:
            f.write("Lower,Upper\n")
            f.write("1,1\n")
            f.write("2,2\n")
            f.write("3,5\n")
        
        macs = read_mac_bins(csv_file)
        self.assertEqual(len(macs), 3)
        self.assertEqual(macs[0], (1, 1))
        self.assertEqual(macs[1], (2, 2))
        self.assertEqual(macs[2], (3, 5))

    def test_read_mac_bins_txt(self):
        """Test reading MAC bins from TXT file"""
        txt_file = os.path.join(self.temp_dir, "macs.txt")
        with open(txt_file, "w") as f:
            f.write("Lower\tUpper\n")
            f.write("1\t1\n")
            f.write("2\t2\n")
            f.write("3\t5\n")
        
        macs = read_mac_bins(txt_file)
        self.assertEqual(len(macs), 3)
        self.assertEqual(macs[0], (1, 1))

    def test_nvariants(self):
        """Test calculating number of variants"""
        n = 10000
        omega = 0.65
        phi = 0.15
        reg_size = 1.0
        weight = 1.0
        
        result = nvariants(n, omega, phi, reg_size, weight)
        self.assertIsInstance(result, float)
        self.assertGreater(result, 0)

    def test_afs(self):
        """Test allele frequency spectrum calculation"""
        alpha = 1.5
        beta = -0.3
        b = 0.25
        macs = [(1, 1), (2, 2), (3, 5)]
        
        result = afs(alpha, beta, b, macs)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0][0], 1)
        self.assertEqual(result[0][1], 1)
        self.assertIsInstance(result[0][2], float)

    def test_fit_afs(self):
        """Test fitting AFS parameters"""
        # Create sample data
        df = pd.DataFrame({
            'Lower': [1, 2, 3, 6],
            'Upper': [1, 2, 5, 10],
            'Prop': [0.4, 0.25, 0.2, 0.15]
        })
        
        alpha, beta, b = fit_afs(df)
        self.assertIsInstance(alpha, float)
        self.assertIsInstance(beta, float)
        self.assertIsInstance(b, float)
        self.assertGreater(alpha, 0)

    def test_fit_nvars(self):
        """Test fitting nvar parameters"""
        # Create sample data
        df = pd.DataFrame({
            'sample_size': [1000, 5000, 10000, 20000],
            'nvars_per_kb': [50, 150, 250, 400]
        })
        
        omega, phi = fit_nvars(df)
        self.assertIsInstance(omega, float)
        self.assertIsInstance(phi, float)
        self.assertGreater(omega, 0)
        self.assertGreater(phi, 0)
        self.assertLess(omega, 1)

    def test_default_params(self):
        """Test that default parameters exist for all populations"""
        populations = ['AFR', 'EAS', 'NFE', 'SAS']
        for pop in populations:
            self.assertIn(pop, DEFAULT_PARAMS)
            params = DEFAULT_PARAMS[pop]
            self.assertIn('alpha', params)
            self.assertIn('beta', params)
            self.assertIn('omega', params)
            self.assertIn('phi', params)
            self.assertIn('b', params)

    def test_afs_invalid_bins(self):
        """Test AFS with unordered bins raises exception"""
        alpha = 1.5
        beta = -0.3
        b = 0.25
        macs = [(3, 5), (1, 1), (2, 2)]  # Unordered
        
        with self.assertRaises(Exception):
            afs(alpha, beta, b, macs)


if __name__ == '__main__':
    unittest.main()
