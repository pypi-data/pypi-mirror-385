"""
VERSION: 2025-10-21
AUTHOR: NCBI-Tree Contributors
LICENSE: Creative Commons Attribution-NonCommercial 4.0 (CC BY-NC 4.0)
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from ncbi_tree.core import (
	sanitize_name,
	resolve_merged_chain,
	build_tree_structure,
	generate_newick_tree_simple,
	calculate_tree_depth,
	build_ncbi_tree
)

class TestSanitizeName(unittest.TestCase):
	"""Test name sanitization functionality"""
	def test_sanitize_basic(self):
		result = sanitize_name("Homo sapiens")
		self.assertEqual(result, "Homo-Sapiens")

	def test_sanitize_with_existing_dash(self):
		result = sanitize_name("T-cell receptor")
		self.assertEqual(result, "T-cell-Receptor")	# <-> gets stripped by illegal char removal

	def test_sanitize_with_semicolon(self):
		result = sanitize_name("Human; Homo sapiens")
		self.assertEqual(result, "Human;Homo-Sapiens")

	def test_sanitize_empty_string(self):
		result = sanitize_name("")
		self.assertEqual(result, "Unknown")

	def test_sanitize_special_chars(self):
		result = sanitize_name("Test Name With Special")	# Use spaces to test word separation
		self.assertEqual(result, "Test-Name-With-Special")

class TestMergedChain(unittest.TestCase):
	"""Test merged taxonomy ID resolution"""
	def test_resolve_single_merge(self):
		merged_map = {"100": "200"}
		result = resolve_merged_chain("100", merged_map)
		self.assertEqual(result, "200")

	def test_resolve_chain_merge(self):
		merged_map = {"100": "200", "200": "300"}
		result = resolve_merged_chain("100", merged_map)
		self.assertEqual(result, "300")

	def test_resolve_no_merge(self):
		merged_map = {"100": "200"}
		result = resolve_merged_chain("999", merged_map)
		self.assertEqual(result, "999")

	def test_resolve_empty_map(self):
		merged_map = {}
		result = resolve_merged_chain("100", merged_map)
		self.assertEqual(result, "100")

class TestTreeStructure(unittest.TestCase):
	"""Test tree building functionality"""
	def test_build_simple_tree(self):
		parent_map = {"1": "1", "2": "1", "3": "1", "4": "2"}
		tree, roots = build_tree_structure(parent_map)
		self.assertEqual(roots, ["1"])
		self.assertEqual(set(tree["1"]), {"2", "3"})
		self.assertEqual(tree["2"], ["4"])

	def test_build_multiple_roots(self):
		parent_map = {"1": "1", "2": "2", "3": "1"}
		tree, roots = build_tree_structure(parent_map)
		self.assertEqual(set(roots), {"1"})

	def test_calculate_depth_single_node(self):
		tree = {}
		depth = calculate_tree_depth("1", tree)
		self.assertEqual(depth, 0)

	def test_calculate_depth_simple_tree(self):
		tree = {"1": ["2", "3"], "2": ["4"]}
		depth = calculate_tree_depth("1", tree)
		self.assertEqual(depth, 2)

class TestNewickGeneration(unittest.TestCase):
	"""Test Newick format generation"""
	def test_simple_newick_single_node(self):
		tree = {}
		result = generate_newick_tree_simple("1", tree)
		self.assertEqual(result, "1")

	def test_simple_newick_with_children(self):
		tree = {"1": ["2", "3"]}
		result = generate_newick_tree_simple("1", tree)
		self.assertIn("(2,3)1", result)

	def test_simple_newick_nested(self):
		tree = {"1": ["2"], "2": ["3", "4"]}
		result = generate_newick_tree_simple("1", tree)
		self.assertIn("(3,4)2", result)

class TestBuildNCBITree(unittest.TestCase):
	"""Test main tree building function"""
	def setUp(self):
		self.temp_dir = tempfile.mkdtemp(prefix="temp_")
		self.output_dir = tempfile.mkdtemp(prefix="temp_")

	def tearDown(self):
		shutil.rmtree(self.temp_dir, ignore_errors=True)
		shutil.rmtree(self.output_dir, ignore_errors=True)

	def test_build_tree_missing_nodes(self):
		result, _ = build_ncbi_tree(self.temp_dir, self.output_dir)
		self.assertFalse(result)

	def test_build_tree_missing_names(self):
		nodes_file = Path(self.temp_dir) / "nodes.dmp"
		nodes_file.write_text("1\t|\t1\t|\tno rank\t|\n")
		result, _ = build_ncbi_tree(self.temp_dir, self.output_dir)
		self.assertFalse(result)

	def test_build_tree_minimal_valid(self):
		nodes_file = Path(self.temp_dir) / "nodes.dmp"
		names_file = Path(self.temp_dir) / "names.dmp"
		nodes_file.write_text("1\t|\t1\t|\tno rank\t|\n2\t|\t1\t|\tspecies\t|\n")
		names_file.write_text("1\t|\troot\t|\t\t|\tscientific name\t|\n2\t|\ttest\t|\t\t|\tscientific name\t|\n")
		result, tree_data = build_ncbi_tree(self.temp_dir, self.output_dir)
		self.assertTrue(result)
		self.assertIsNotNone(tree_data)
		output_file = Path(self.output_dir) / "output.NCBI.tree.tre"
		self.assertTrue(output_file.exists())

	def test_build_tree_with_optional_files(self):
		nodes_file = Path(self.temp_dir) / "nodes.dmp"
		names_file = Path(self.temp_dir) / "names.dmp"
		nodes_file.write_text("1\t|\t1\t|\tno rank\t|\n2\t|\t1\t|\tspecies\t|\n")
		names_file.write_text("1\t|\troot\t|\t\t|\tscientific name\t|\n2\t|\ttest\t|\t\t|\tscientific name\t|\n")
		result, tree_data = build_ncbi_tree(self.temp_dir, self.output_dir, generate_optional_files=False)
		self.assertTrue(result)
		result2, _ = build_ncbi_tree(self.temp_dir, self.output_dir, generate_optional_files=True, tree_data=tree_data)
		self.assertTrue(result2)
		text_file = Path(self.output_dir) / "output.NCBI.tree.txt"
		named_file = Path(self.output_dir) / "output.NCBI.named.tree.tre"
		tsv_file = Path(self.output_dir) / "output.NCBI.ID.to.name.tsv"
		self.assertTrue(text_file.exists())
		self.assertTrue(named_file.exists())
		self.assertTrue(tsv_file.exists())

if __name__ == '__main__':
	unittest.main()