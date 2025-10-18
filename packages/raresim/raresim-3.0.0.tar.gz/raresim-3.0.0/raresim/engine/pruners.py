from abc import ABC, abstractmethod

from raresim.engine.config import RunConfig
from raresim.engine.utils import *


class Pruner(ABC):
    @abstractmethod
    def transform(self) -> None:
       pass

class StandardPruner(Pruner):
    def __init__(self, config: RunConfig, bins: list, legend: Legend, matrix: SparseMatrix):
        """
        Constructor for the DefaultTransformer.

        :param config: The RunConfig object describing the run
        :param bins: A list of bin definitions, each as a tuple of (lower, upper, target)
        :param legend: The Legend object describing the input data
        :param matrix: The SparseMatrix object containing the input data
        """
        self.__config: RunConfig = config
        self.__bins = bins
        self.__legend: Legend = legend
        self.__matrix: SparseMatrix = matrix

    def transform(self) -> None:
        """
        Transform the input data according to the bin definitions provided.

        The following steps are performed:

        1. Assign each row to a bin
        2. Prune the bins to reach the desired ACs
        3. Print the new allele frequency distribution
        4. Remove the rows marked for removal from the input data

        :return: A TransformerResult object
        """
        bin_assignments = self.assign_bins()

        print('Input allele frequency distribution:')
        print_bin(self.__bins, bin_assignments)

        protected_vars_per_bin = {}
        if self.__config.args.keep_protected:
            protected_vars_per_bin = adjust_for_protected_variants(self.__bins, bin_assignments, self.__legend)
            if self.__config.args.verbose:
                print("Input allele frequency distribution (with protected variants pulled out):")
                print_bin(self.__bins, bin_assignments)

        extra_rows = []
        prune_bins(extra_rows, bin_assignments, self.__legend, self.__matrix, self.__bins, self.__config.activation_threshold, self.__config.stop_threshold)

        if self.__config.args.keep_protected:
            if self.__config.args.verbose:
                print("Output allele frequency distribution (without protected variants added back):")
                print_bin(self.__bins, bin_assignments)
            add_protected_rows_back(self.__bins, bin_assignments, protected_vars_per_bin)

        print('\nNew allele frequency distribution:')
        print_bin(self.__bins, bin_assignments)

        rows_to_keep = self.get_all_kept_rows(bin_assignments)

        trimmed_vars_file = open(
            f'{self.__config.args.output_legend if self.__config.args.output_legend is not None else self.__config.args.input_legend}-pruned-variants', 'w')
        trimmed_vars_file.write("\t".join(self.__legend.get_header()) + '\n')
        for row in range(self.__matrix.num_rows()):
            if row not in rows_to_keep:
                trimmed_vars_file.write("\t".join([y for x, y in self.__legend[row].items()]) + '\n')
                self.__matrix.prune_row(row, self.__matrix.row_num(row))
                if self.__matrix.row_num(row) != 0:
                    raise Exception(
                        "ERROR: Trimming pruned row to a row of zeros did not work. Failing so that we don't write a bad haps file.")

        rows_to_keep.sort()
        trimmed_vars_file.close()
        if self.__config.remove_zeroed_rows:
            rows_to_remove = [x for x in range(self.__matrix.num_rows()) if x not in rows_to_keep]
            for rowId in rows_to_remove[::-1]:
                self.__legend.remove_row(rowId)
                self.__matrix.remove_row(rowId)

    def get_all_kept_rows(self, bin_assignments: dict) -> list:
        """
        Return a list of all row IDs that are kept after pruning.

        Parameters
        ----------
        bin_assignments : dict
            A dictionary mapping bin IDs to lists of row IDs assigned to each bin.

        Returns
        -------
        list
            A list of all row IDs that are kept after pruning.
        """
        all_kept_rows = []
        mode = self.__config.run_type
        for bin_id in bin_assignments:
            all_kept_rows += bin_assignments[bin_id]
            
        if mode == 'fun_only':
            for row_id in range(self.__legend.row_count()):
                if self.__legend[row_id]['fun'] == 'syn':
                    all_kept_rows.append(row_id)

        elif mode == 'syn_only':
            for row_id in range(self.__legend.row_count()):
                if self.__legend[row_id]['fun'] == 'fun':
                    all_kept_rows.append(row_id)
                    
        all_kept_rows.sort()
        return list(dict.fromkeys(all_kept_rows))

    def get_bin(self, val):
        """
        Return the index of the bin that contains the given value.

        Parameters
        ----------
        val : int
            The value to search for in the bins.

        Returns
        -------
        int
            The index of the bin in which the value was found, or the length of the bins if the value was not found.
        """
        for i in range(len(self.__bins)):
            if self.__bins[i][0] <= val <= self.__bins[i][1]:
                return i
        return len(self.__bins)

    def assign_bins(self):
        """
        Assign each row in the matrix to a bin according to its allele count.

        Returns a dictionary where the keys are the bin indices and the values are
        lists of row indices in the matrix that belong to the bin.

        Row indices are assigned in the order they appear in the matrix, and bin
        indices are assigned in the order they appear in `self.__bins`.

        If the row's allele count is 0 and the `--zero` flag is not set, the row is
        not assigned to a bin.

        :return: A dictionary of bin indices to lists of row indices
        :rtype: dict
        """
        bin_assignments = {binId: [] for binId in range(len(self.__bins) + 1)}
        row_i = 0
        for row in range(self.__matrix.num_rows()):
            row_num = self.__matrix.row_num(row)
            if row_num > 0:
                if self.__config.run_type == 'fun_only':
                    if self.__legend[row_i]['fun'] != 'fun':
                        row_i += 1
                        continue
                elif self.__config.run_type == 'syn_only':
                    if self.__legend[row_i]['fun'] != 'syn':
                        row_i += 1
                        continue
                bin_id = self.get_bin(row_num)
                target_map = bin_assignments
                if bin_id not in target_map:
                    target_map[bin_id] = []
                target_map[bin_id].append(row_i)
            row_i += 1
        return bin_assignments


class FunctionalSplitPruner(Pruner):
    def __init__(self, config: RunConfig, bins: dict, legend: Legend, matrix: SparseMatrix):
        self.__config: RunConfig = config
        self.__bins = bins
        self.__legend = legend
        self.__matrix = matrix

    def transform(self):
        """
        Perform the pruning operation on the data.

        This method prints the input and output allele frequency distributions,
        and returns a list of row indices that are kept after pruning.

        The input allele frequency distribution is printed in two parts:
        functional and synonymous. The output allele frequency distribution is
        also printed in two parts.

        If the `-z` flag is set, rows with 0 variants are removed from the
        input data.

        :return: A list of row indices that are kept after pruning
        :rtype: list
        """
        bin_assignments = self.assign_bins()

        print('Input allele frequency distribution:')
        print('Functional')
        print_bin(self.__bins['fun'], bin_assignments['fun'])
        print('\nSynonymous')
        print_bin(self.__bins['syn'], bin_assignments['syn'])

        protected_vars_per_bin = {}
        if self.__config.args.keep_protected:
            protected_vars_per_bin['fun'] = adjust_for_protected_variants(self.__bins['fun'], bin_assignments['fun'], self.__legend)
            protected_vars_per_bin['syn'] = adjust_for_protected_variants(self.__bins['syn'], bin_assignments['syn'], self.__legend)
            if self.__config.args.verbose:
                print("Input allele frequency distribution (with protected variants pulled out):")
                print('Functional')
                print_bin(self.__bins['fun'], bin_assignments['fun'])
                print('\nSynonymous')
                print_bin(self.__bins['syn'], bin_assignments['syn'])
        extra_rows = []

        extra_rows = {'fun': [], 'syn': []}
        prune_bins(extra_rows['fun'], bin_assignments['fun'], self.__legend, self.__matrix, self.__bins['fun'], self.__config.activation_threshold, self.__config.stop_threshold)
        prune_bins(extra_rows['syn'], bin_assignments['syn'], self.__legend, self.__matrix, self.__bins['syn'], self.__config.activation_threshold, self.__config.stop_threshold)

        if self.__config.args.keep_protected:
            if self.__config.args.verbose:
                print("Output allele frequency distribution (without protected variants added back):")
                print('Functional')
                print_bin(self.__bins['fun'], bin_assignments['fun'])
                print('\nSynonymous')
                print_bin(self.__bins['syn'], bin_assignments['syn'])
            add_protected_rows_back(self.__bins['fun'], bin_assignments['fun'], protected_vars_per_bin['fun'])
            add_protected_rows_back(self.__bins['syn'], bin_assignments['syn'], protected_vars_per_bin['syn'])
            
        print('\nNew allele frequency distribution:')
        print('Functional')
        print_bin(self.__bins['fun'], bin_assignments['fun'])
        print('\nSynonymous')
        print_bin(self.__bins['syn'], bin_assignments['syn'])

        rows_to_keep = self.get_all_kept_rows(bin_assignments)
        
        trimmed_vars_file = open(
            f'{self.__config.args.output_legend if self.__config.args.output_legend is not None else self.__config.args.input_legend}-pruned-variants', 'w')
        trimmed_vars_file.write("\t".join(self.__legend.get_header()) + '\n')
        for row in range(self.__matrix.num_rows()):
            if row not in rows_to_keep:
                trimmed_vars_file.write("\t".join([y for x, y in self.__legend[row].items()]) + '\n')
                self.__matrix.prune_row(row, self.__matrix.row_num(row))
                if self.__matrix.row_num(row) != 0:
                    raise Exception(
                        "ERROR: Trimming pruned row to a row of zeros did not work. Failing so that we don't write a bad haps file.")

        rows_to_keep.sort()
        trimmed_vars_file.close()
        if self.__config.remove_zeroed_rows:
            rows_to_remove = [x for x in range(self.__matrix.num_rows()) if x not in rows_to_keep]
            for rowId in rows_to_remove[::-1]:
                self.__legend.remove_row(rowId)
                self.__matrix.remove_row(rowId)


    def get_all_kept_rows(self, bin_assignments) -> list:
        """
        Return a list of all row IDs that are kept after pruning.

        Parameters
        ----------
        bin_assignments : dict
            A dictionary mapping bin IDs to lists of row IDs assigned to each bin.

        Returns
        -------
        list
            A list of all row IDs that are kept after pruning.
        """
        all_kept_rows = []
        for bin_id in range(len(bin_assignments['fun'])):
            all_kept_rows += bin_assignments['fun'][bin_id]
        for bin_id in range(len(bin_assignments['syn'])):
            all_kept_rows += bin_assignments['syn'][bin_id]


        return list(sorted(all_kept_rows))


    def assign_bins(self) -> dict:
        """
        Assign each row in the matrix to a bin according to its allele count and mode.

        In 'func_split' mode, rows are assigned to separate functional and synonymous bin groups
        based on the `fun` attribute of the legend. Each group contains bins indexed by a range
        of allele counts. Rows with zero allele count are not assigned to any bin.

        Returns
        -------
        dict
            A dictionary where keys are bin groups ('fun' or 'syn') and values are dictionaries
            mapping bin indices to lists of row indices in the matrix that belong to each bin.
        """
        
        bin_assignments = {
            'fun': {bin_id: [] for bin_id in range(len(self.__bins['fun']) + 1)},
            'syn': {bin_id: [] for bin_id in range(len(self.__bins['syn']) + 1)}
        }

        row_i = 0
        for row in range(self.__matrix.num_rows()):
            row_num = self.__matrix.row_num(row)
            if row_num > 0:
               
                bin_id = self.get_bin(row_num)
                
                target_map = bin_assignments[self.__legend[row_i]['fun']]
                    
                if bin_id not in target_map:
                    target_map[bin_id] = []
                target_map[bin_id].append(row_i)

            row_i += 1
        return bin_assignments

    def get_bin(self, val, row_id: int = 0):
        """
        Return the index of the bin that contains the given value.

        Parameters
        ----------
        val : int
            The value to search for in the bins.
        row_id : int, optional
            The row index in the legend to use when searching for functional/synonymous bins.
            Defaults to 0.

        Returns
        -------
        int
            The index of the bin in which the value was found, or the length of the bins if the value was not found.
        """
        bins = self.__bins[self.__legend[row_id]['fun']]
        for i in range(len(bins)):
            if bins[i][0] <= val <= bins[i][1]:
                return i
        return len(bins)

class ProbabilisticPruner(Pruner):
    def __init__(self, config: RunConfig, legend: Legend, matrix: SparseMatrix):
        self.__config: RunConfig = config
        self.__legend: Legend = legend
        self.__matrix: SparseMatrix = matrix

    def transform(self):
        """
        Iterate over the input data and probabilistically remove columns (i.e. variants) from rows
        according to the probabilities specified in the legend file.

        The probability of a variant being kept is given by the value in the 'prob' column of the legend.
        A random number between 0 and 1 is generated for each variant, and if the number is greater than
        the probability, the variant is removed from the data.

        :return: None
        """
        for row_index in range(self.__matrix.num_rows()):
            row = self.__matrix.get_row_raw(row_index)
            for col_index in row:
                flip = random.uniform(0, 1)
                legend_val = self.__legend[row_index]['prob']
                if legend_val == '.':
                    continue
                elif flip > float(legend_val):
                    self.__matrix.remove(row_index, col_index)
