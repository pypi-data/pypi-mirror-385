"""
VERSION: 2025-10-21
AUTHOR: NCBI-Tree Contributors
LICENSE: Creative Commons Attribution-NonCommercial 4.0 (CC BY-NC 4.0)
"""

import re
import time
import tarfile
import requests
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple
from functools import partial
from tqdm import tqdm
print = partial(print, flush=True)


'''
////////////////////////////////////////////////////////////

	SECTION-1: Download and extraction functions

////////////////////////////////////////////////////////////
'''
SANITIZE_TAXON_NAME = True
NAME_PRIORITIES = {"genbank common name": 0, "scientific name": 1}

def fetch_ftp_version_from_html(ftp_url, target_filename):
	"""Extract last modified date for target file from FTP HTML page"""
	try:
		response = requests.get(ftp_url, timeout=10)
		response.raise_for_status()
		html_content = response.text
		if "ncbi.nlm.nih.gov" in ftp_url:
			pattern = rf'<a href="{re.escape(target_filename)}">{re.escape(target_filename)}</a>\s+(\d{{4}}-\d{{2}}-\d{{2}} \d{{2}}:\d{{2}})'
			match = re.search(pattern, html_content)
			return match.group(1) if match else ""
		return ""
	except Exception as error:
		print(f"Warning: Could not fetch version from {ftp_url}: {error}")
		return ""

def download_file_with_progress(url, destination_path):
	"""Download file with progress bar using tqdm"""
	try:
		response = requests.get(url, stream=True, timeout=30)
		response.raise_for_status()
		total_size = int(response.headers.get('content-length', 0))
		block_size = 8192
		with open(destination_path, 'wb') as file_handle:
			with tqdm(total=total_size, unit='B', unit_scale=True, desc=f"Downloading {Path(destination_path).name}") as progress_bar:
				for chunk in response.iter_content(chunk_size=block_size):
					if chunk:
						file_handle.write(chunk)
						progress_bar.update(len(chunk))
		return True
	except Exception as error:
		print(f"Error: Failed to download file from {url}: {error}")
		return False

def extract_tar_gz_with_progress(tar_path, extract_to):
	"""Extract tar.gz file with progress bar"""
	try:
		with tarfile.open(tar_path, 'r:gz') as tar:
			members = tar.getmembers()
			with tqdm(total=len(members), desc=f"Extracting {Path(tar_path).name}") as progress_bar:
				for member in members:
					tar.extract(member, path=extract_to)
					progress_bar.update(1)
		return True
	except Exception as error:
		print(f"Error: Failed to extract {tar_path}: {error}")
		return False

def download_and_extract_taxonomy(output_dir, download_url=None, clean_intermediate=False):
	"""Download and extract NCBI taxonomy data"""
	output_path = Path(output_dir)
	output_path.mkdir(parents=True, exist_ok=True)
	default_url = "https://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdump.tar.gz"
	ftp_html_url = "https://ftp.ncbi.nlm.nih.gov/pub/taxonomy/"
	target_filename = "taxdump.tar.gz"
	if download_url is None:
		download_url = default_url
		print(f"Using default NCBI taxonomy URL: {download_url}")
	else:
		print(f"Using custom download URL: {download_url}")
	print("Fetching server version information...")
	version_string = fetch_ftp_version_from_html(ftp_html_url, target_filename)
	if version_string:
		version_folder_name = version_string.replace(' ', '-').replace(':', '-')
		print(f"Server version detected: {version_string}")
	else:
		version_folder_name = datetime.now().strftime('%Y-%m-%d-%H-%M')
		print(f"Could not detect server version, using current timestamp: {version_folder_name}")
	version_folder = output_path / version_folder_name
	version_folder.mkdir(parents=True, exist_ok=True)
	print(f"Working directory: {version_folder}")
	tar_file_path = version_folder / target_filename
	if tar_file_path.exists():
		print(f"Found existing download: {tar_file_path}")
	else:
		print(f"Downloading taxonomy data from: {download_url}")
		if not download_file_with_progress(download_url, tar_file_path):
			print("Error: Download failed")
			new_url = input("Enter an alternative download URL (or press Enter to cancel): ").strip()
			if new_url:
				print(f"Retrying download from: {new_url}")
				if not download_file_with_progress(new_url, tar_file_path):
					print("Error: Retry download failed")
					return None
				else:
					print(f"Downloaded: {tar_file_path}")
			else:
				return None
		else:
			print(f"Downloaded: {tar_file_path}")
	nodes_file = version_folder / "nodes.dmp"
	names_file = version_folder / "names.dmp"
	if nodes_file.exists() and names_file.exists():
		print(f"[INFO] Extracted files already exist, skipping extraction")
	else:
		print(f"Extracting taxonomy data to: {version_folder}")
		if not extract_tar_gz_with_progress(tar_file_path, version_folder):
			print("Error: Extraction failed")
			return None
	version_file = output_path / "version.txt"
	with open(version_file, 'w') as file_handle:
		file_handle.write(f"Updated on {datetime.now().strftime('%Y-%m-%d')} (YYYY-MM-DD)\n")
		if version_string:
			file_handle.write(f"Exact version information is fetched from FTP server's LastModified column: {ftp_html_url}\n")
			file_handle.write(f"Exact version: {version_string} ({target_filename})\n")
	print(f"Version information saved: {version_file}")
	if clean_intermediate:
		print("Cleaning up intermediate files (--no-cache enabled)...")
		if tar_file_path.exists():
			tar_file_path.unlink()
			print(f"Removed: {tar_file_path}")
	return version_folder


'''
////////////////////////////////////////////////////////////

	SECTION-2: Name loading and processing functions

////////////////////////////////////////////////////////////
'''
def load_names(names_path: Path, name_priorities: Dict[int, int] = None) -> Dict[str, str]:
	"""Load taxonomy names from names.dmp with priority-based selection"""
	if name_priorities is None:
		name_priorities = NAME_PRIORITIES
	all_names: Dict[str, Dict[int, str]] = defaultdict(dict)
	with names_path.open(encoding='utf-8', errors='replace') as file_handle:
		for line in file_handle:
			tax_id, name, _, name_class, *_ = (column.strip() for column in line.split("|"))
			if not name or name == "Unknown":
				continue
			priority = name_priorities.get(name_class, 2)
			if priority >= 0 and (priority not in all_names[tax_id] or len(name) > len(all_names[tax_id][priority])):
				all_names[tax_id][priority] = name
	result = {}
	for tax_id, names_dict in all_names.items():
		combined_parts = []
		if 0 in names_dict and names_dict[0].strip():
			combined_parts.append(names_dict[0].strip())
		if 1 in names_dict and names_dict[1].strip():
			combined_parts.append(names_dict[1].strip())
		if not combined_parts and 2 in names_dict and names_dict[2].strip():
			combined_parts.append(names_dict[2].strip())
		seen = set()
		unique_parts = []
		for part in combined_parts:
			if part and part not in seen:
				seen.add(part)
				unique_parts.append(part)
		if len(unique_parts) == 1:
			result[tax_id] = unique_parts[0]
		elif len(unique_parts) > 1:
			result[tax_id] = "; ".join(unique_parts)
		else:
			result[tax_id] = f"taxon_{tax_id}"
	return result

def load_merged_taxa(merged_path: Path) -> Dict[str, str]:
	"""Load merged taxonomy IDs from merged.dmp"""
	if not merged_path.exists():
		print(f"[WARN] Merged.dmp not found: no replacements applied")
		return {}
	merged_map: Dict[str, str] = {}
	with merged_path.open(encoding='utf-8', errors='replace') as file_handle:
		for line in file_handle:
			old_id, new_id = (field.strip() for field in line.split("|")[:2])
			if old_id != new_id:
				merged_map[old_id] = new_id
	print(f"[INFO] Loaded {len(merged_map):,} merged-taxa pairs")
	return merged_map

def resolve_merged_chain(taxonomy_id: str, mapping: Dict[str, str]) -> str:
	"""Resolve chain of merged taxonomy IDs to final ID"""
	while taxonomy_id in mapping:
		taxonomy_id = mapping[taxonomy_id]
	return taxonomy_id


'''
////////////////////////////////////////////////////////////

	SECTION-3: Tree structure loading and processing

////////////////////////////////////////////////////////////
'''
def load_nodes(nodes_path: Path) -> Tuple[Dict[str, str], Dict[str, str]]:
	"""Load taxonomy nodes from nodes.dmp"""
	if not nodes_path.exists():
		raise FileNotFoundError(nodes_path)
	parent_map: Dict[str, str] = {}
	rank_map: Dict[str, str] = {}
	with nodes_path.open(encoding='utf-8', errors='replace') as file_handle:
		for line in file_handle:
			taxonomy_id, parent, rank, *_ = (field.strip() for field in line.split("|"))
			parent_map[taxonomy_id] = parent
			rank_map[taxonomy_id] = rank
	print(f"[INFO] Loaded {len(parent_map):,} nodes")
	return parent_map, rank_map

def apply_merged_replacements(parent_map: Dict[str, str], rank_map: Dict[str, str], merged_map: Dict[str, str]) -> None:
	"""Apply merged taxonomy ID replacements to parent and rank maps"""
	for old_taxonomy_id, new_taxonomy_id in merged_map.items():
		final_taxonomy_id = resolve_merged_chain(new_taxonomy_id, merged_map)
		if final_taxonomy_id in parent_map and old_taxonomy_id not in parent_map:
			parent_map[old_taxonomy_id] = parent_map[final_taxonomy_id]
			rank_map[old_taxonomy_id] = rank_map[final_taxonomy_id]

def build_tree_structure(parent_map: Dict[str, str]) -> Tuple[Dict[str, List[str]], List[str]]:
	"""Build child adjacency list and identify root nodes"""
	tree: Dict[str, List[str]] = defaultdict(list)
	for child, parent in parent_map.items():
		if child != parent:
			tree[parent].append(child)
	root_nodes = [taxonomy_id for taxonomy_id, parent in parent_map.items() if taxonomy_id == parent or parent not in parent_map]
	if "1" in parent_map:
		root_nodes = ["1"]
	return tree, root_nodes


'''
////////////////////////////////////////////////////////////

	SECTION-4: Name sanitization and formatting functions

////////////////////////////////////////////////////////////
'''
def sanitize_name(name: str) -> str:
	"""Sanitize taxonomic names for consistent display and filesystem usage"""
	if not name:
		return "Unknown"
	if not SANITIZE_TAXON_NAME:
		return name
	name = name.replace('-', '<->')
	name = name.replace('; ', ';').replace(' ', '-')
	parts = []
	for part in name.split(';'):
		subparts = []
		for subpart in part.split('-'):
			if subpart:
				subparts.append(subpart[0].upper() + subpart[1:].lower() if len(subpart) > 1 else subpart.upper())
		if subparts:
			parts.append('-'.join(subparts))
	name = ';'.join(parts)
	illegal_chars = '<>:"|?*\\/[]'
	for char in illegal_chars:
		name = name.replace(char, '')
	return name[:100] if len(name) > 100 else name if name else "Unknown"

def format_node_name(taxonomy_id: str, tax_names: Dict[str, str], merged_map: Dict[str, str]) -> str:
	"""Format node name handling merged taxonomy IDs"""
	if taxonomy_id in merged_map:
		final_id = resolve_merged_chain(taxonomy_id, merged_map)
		merged_name = sanitize_name(tax_names.get(final_id, f"taxon_{final_id}"))
		return f"merged into {final_id}:{merged_name}"
	else:
		return sanitize_name(tax_names.get(taxonomy_id, f"taxon_{taxonomy_id}"))


'''
////////////////////////////////////////////////////////////

	SECTION-5: Tree output generation functions

////////////////////////////////////////////////////////////
'''
def dump_text_tree(taxonomy_id: str, depth: int, output_lines: List[str], tree: Dict[str, List[str]], rank_map: Dict[str, str], tax_names: Dict[str, str], merged_map: Dict[str, str], prefix: str = ""):
	"""Recursively dump the subtree with proper text tree formatting"""
	rank = rank_map.get(taxonomy_id, "no rank")
	name = format_node_name(taxonomy_id, tax_names, merged_map)
	children = sorted(tree.get(taxonomy_id, []), key=lambda x: int(x) if x.isdigit() else 0)
	if depth == 0:
		line = f"{rank}: {taxonomy_id}:{name}"
	else:
		line = f"{prefix}{rank}: {taxonomy_id}:{name}"
	output_lines.append(line)
	for i, child in enumerate(children):
		is_last = (i == len(children) - 1)
		if depth == 0:
			child_prefix = "├─ " if not is_last else "└─ "
		else:
			if prefix.endswith("├─ "):
				cont_prefix = prefix[:-3] + "│  "
			elif prefix.endswith("└─ "):
				cont_prefix = prefix[:-3] + "   "
			else:
				cont_prefix = prefix
			child_prefix = cont_prefix + ("├─ " if not is_last else "└─ ")
		dump_text_tree(child, depth + 1, output_lines, tree, rank_map, tax_names, merged_map, child_prefix)

def generate_newick_tree_simple(taxonomy_id: str, tree: Dict[str, List[str]]) -> str:
	"""Generate Newick format tree with only NCBI taxa IDs"""
	children = sorted(tree.get(taxonomy_id, []), key=lambda x: int(x) if x.isdigit() else 0)
	if not children:
		return taxonomy_id
	child_strings = []
	for child in children:
		child_strings.append(generate_newick_tree_simple(child, tree))
	return f"({','.join(child_strings)}){taxonomy_id}"

def generate_newick_tree_with_names(taxonomy_id: str, tree: Dict[str, List[str]], rank_map: Dict[str, str], tax_names: Dict[str, str], merged_map: Dict[str, str]) -> str:
	"""Generate Newick format tree with rank:taxa_id:name format"""
	children = sorted(tree.get(taxonomy_id, []), key=lambda x: int(x) if x.isdigit() else 0)
	rank = rank_map.get(taxonomy_id, "no_rank")
	name = format_node_name(taxonomy_id, tax_names, merged_map).replace(':', '_').replace(';', '_').replace(' ', '_').replace('(', '_').replace(')', '_').replace(',', '_')
	node_label = f"{rank}:{taxonomy_id}:{name}"
	if not children:
		return node_label
	child_strings = []
	for child in children:
		child_strings.append(generate_newick_tree_with_names(child, tree, rank_map, tax_names, merged_map))
	return f"({','.join(child_strings)}){node_label}"

def calculate_tree_depth(taxonomy_id: str, tree: Dict[str, List[str]], depth: int = 0) -> int:
	"""Calculate maximum depth of tree from given node"""
	children = tree.get(taxonomy_id, [])
	if not children:
		return depth
	return max(calculate_tree_depth(child, tree, depth + 1) for child in children)

def analyze_depth_distribution(taxonomy_id: str, tree: Dict[str, List[str]], rank_map: Dict[str, str], depth: int = 0) -> Dict[int, Dict[str, int]]:
	"""Analyze rank distribution by depth"""
	depth_ranks: Dict[int, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
	def traverse(node_id: str, current_depth: int):
		rank = rank_map.get(node_id, "no rank")
		depth_ranks[current_depth][rank] += 1
		for child in tree.get(node_id, []):
			traverse(child, current_depth + 1)
	traverse(taxonomy_id, depth)
	return depth_ranks

def find_deepest_path(tree: Dict[str, List[str]], rank_map: Dict[str, str], tax_names: Dict[str, str], root_id: str) -> List[str]:
	"""Find the deepest path in the taxonomy tree"""
	def get_path_depth(node_id: str, path: List[str]) -> Tuple[int, List[str]]:
		current_path = path + [node_id]
		children = tree.get(node_id, [])
		if not children:
			return len(current_path), current_path
		max_depth = 0
		deepest_path = current_path
		for child in children:
			child_depth, child_path = get_path_depth(child, current_path)
			if child_depth > max_depth:
				max_depth = child_depth
				deepest_path = child_path
		return max_depth, deepest_path
	_, deepest_path = get_path_depth(root_id, [])
	return deepest_path

def generate_taxonomy_report(tree: Dict[str, List[str]], rank_map: Dict[str, str], tax_names: Dict[str, str], merged_map: Dict[str, str], root_nodes: List[str], output_path: Path) -> None:
	"""Generate comprehensive taxonomy analysis report"""
	report_lines = []
	rank_counts = defaultdict(int)
	for rank in rank_map.values():
		rank_counts[rank] += 1
	report_lines.append("=" * 80)
	report_lines.append(f"Entries count by rank ({len(rank_counts)} total ranks):")
	sorted_ranks = sorted(rank_counts.items(), key=lambda x: x[1], reverse=True)
	max_rank_len = max(len(rank) for rank, _ in sorted_ranks)
	for rank, count in sorted_ranks:
		report_lines.append(f"\t{rank:<{max_rank_len}}  {count:>8} entries")
	report_lines.append("\n" + "=" * 80)
	if len(root_nodes) == 1:
		root_id = root_nodes[0]
		max_depth = calculate_tree_depth(root_id, tree)
		report_lines.append(f"Maximum tree depth: {max_depth}")
		deepest_path = find_deepest_path(tree, rank_map, tax_names, root_id)
		report_lines.append("Deepest taxonomic path:")
		for i, node_id in enumerate(deepest_path):
			rank = rank_map.get(node_id, "no rank")
			name = sanitize_name(tax_names.get(node_id, f"taxon_{node_id}"))
			indent = "\t" * (i + 1)
			report_lines.append(f"{indent}{rank}: {node_id}:{name}")
		report_lines.append("\n" + "=" * 80)
		depth_distribution = analyze_depth_distribution(root_id, tree, rank_map)
		report_lines.append("Rank distribution by depth in taxonomy:")
		for depth in sorted(depth_distribution.keys()):
			ranks_at_depth = depth_distribution[depth]
			total_at_depth = sum(ranks_at_depth.values())
			report_lines.append(f"\tDepth {depth} {total_at_depth:>6} total entries")
			sorted_depth_ranks = sorted(ranks_at_depth.items(), key=lambda x: x[1], reverse=True)
			for rank, count in sorted_depth_ranks[:10]:
				percentage = (count / total_at_depth) * 100
				report_lines.append(f"\t\t{rank:<15}  {count:>6} ({percentage:.1f}%)")
			if len(sorted_depth_ranks) > 10:
				remaining = sum(count for _, count in sorted_depth_ranks[10:])
				remaining_pct = (remaining / total_at_depth) * 100
				report_lines.append(f"\t\t{'others':<15}  {remaining:>6} ({remaining_pct:.1f}%)")
		report_lines.append("\n" + "=" * 80)
	total_entries = len(rank_map)
	report_lines.append(f"Total taxonomy entries: {total_entries:,}")
	report_lines.append(f"Total unique ranks: {len(rank_counts):,}")
	report_lines.append(f"Total merged taxa: {len(merged_map):,}")
	report_lines.append(f"Total named taxa: {len(tax_names):,}")
	output_report = output_path / "output.NCBI.report.txt"
	output_report.write_text("\n".join(report_lines), encoding='utf-8')
	print(f"[INFO] Wrote taxonomy analysis report to '{output_report.name}' ({len(report_lines):,} lines)")


'''
////////////////////////////////////////////////////////////

	SECTION-6: Main tree building function

////////////////////////////////////////////////////////////
'''
def build_ncbi_tree(taxonomy_folder, output_dir, generate_optional_files: bool = False, tree_data: Dict = None):
	"""Build NCBI taxonomy tree in Newick format"""
	taxonomy_path = Path(taxonomy_folder)
	output_path = Path(output_dir)
	output_path.mkdir(parents=True, exist_ok=True)
	if tree_data is None:
		nodes_file = taxonomy_path / "nodes.dmp"
		names_file = taxonomy_path / "names.dmp"
		merged_file = taxonomy_path / "merged.dmp"
		if not nodes_file.exists():
			print(f"[ERROR] nodes.dmp not found in {taxonomy_path}")
			return False, None
		if not names_file.exists():
			print(f"[ERROR] names.dmp not found in {taxonomy_path}")
			return False, None
		print(f"[INFO] Loading taxonomy data...")
		tax_names = load_names(names_file)
		print(f"[INFO] Loaded {len(tax_names):,} taxon names")
		print(f"[INFO] Applying merged taxonomy replacements...")
		merged_map = load_merged_taxa(merged_file)
		parent_map, rank_map = load_nodes(nodes_file)
		apply_merged_replacements(parent_map, rank_map, merged_map)
		print(f"[INFO] Building tree structure...")
		tree, root_nodes = build_tree_structure(parent_map)
		sorted_roots = sorted(root_nodes, key=lambda x: int(x) if x.isdigit() else 0)
		tree_data = {
			'tree': tree,
			'rank_map': rank_map,
			'tax_names': tax_names,
			'merged_map': merged_map,
			'sorted_roots': sorted_roots
		}
	else:
		tree = tree_data['tree']
		rank_map = tree_data['rank_map']
		tax_names = tree_data['tax_names']
		merged_map = tree_data['merged_map']
		sorted_roots = tree_data['sorted_roots']
	if not generate_optional_files:
		print(f"[INFO] Generating tree output...")
		if len(sorted_roots) == 1:
			print(f"[INFO] Generating Newick tree with NCBI IDs...")
			newick_simple = generate_newick_tree_simple(sorted_roots[0], tree) + ";"
		else:
			print(f"[INFO] Generating Newick tree with NCBI IDs for {len(sorted_roots)} roots...")
			newick_simple_trees = [generate_newick_tree_simple(root, tree) for root in sorted_roots]
			newick_simple = f"({','.join(newick_simple_trees)});"
		output_newick = output_path / "output.NCBI.tree.tre"
		output_newick.write_text(newick_simple, encoding='utf-8')
		print(f"[INFO] Wrote Newick tree (with only NCBI taxa IDs) to '{output_newick.name}'")
		print(f"[INFO] Generating taxonomy analysis report...")
		generate_taxonomy_report(tree, rank_map, tax_names, merged_map, sorted_roots, output_path)
		orphans = [taxonomy_id for taxonomy_id in merged_map if taxonomy_id not in parent_map]
		if orphans:
			print(f"[WARN] {len(orphans):,} merged tax_ids missing from nodes.dmp; first 10: {', '.join(orphans[:10])}")
		else:
			print(f"[INFO] No missing tax_ids detected")
		return True, tree_data
	else:
		print(f"[INFO] Generating optional output files...")
		text_lines: List[str] = []
		if len(sorted_roots) == 1:
			dump_text_tree(sorted_roots[0], 0, text_lines, tree, rank_map, tax_names, merged_map)
			newick_with_names = generate_newick_tree_with_names(sorted_roots[0], tree, rank_map, tax_names, merged_map) + ";"
		else:
			for i, root in enumerate(sorted_roots):
				if i > 0:
					text_lines.append("")
				dump_text_tree(root, 0, text_lines, tree, rank_map, tax_names, merged_map)
			newick_with_names_trees = [generate_newick_tree_with_names(root, tree, rank_map, tax_names, merged_map) for root in sorted_roots]
			newick_with_names = f"({','.join(newick_with_names_trees)});"
		output_text = output_path / "output.NCBI.tree.txt"
		output_text.write_text("\n".join(text_lines), encoding='utf-8')
		print(f"[INFO] Wrote text tree to '{output_text.name}' ({len(text_lines):,} lines)")
		output_newick_names = output_path / "output.NCBI.named.tree.tre"
		output_newick_names.write_text(newick_with_names, encoding='utf-8')
		print(f"[INFO] Wrote Newick tree (with ranks, NCBI taxa IDs, and names) to '{output_newick_names.name}'")
		output_id_to_name = output_path / "output.NCBI.ID.to.name.tsv"
		id_to_name_lines = ["NCBI_TaxID\tName\tRank"]
		for tax_id in sorted(tax_names.keys(), key=lambda x: int(x) if x.isdigit() else 0):
			name = sanitize_name(tax_names.get(tax_id, f"taxon_{tax_id}"))
			rank = rank_map.get(tax_id, "no rank")
			id_to_name_lines.append(f"{tax_id}\t{name}\t{rank}")
		output_id_to_name.write_text("\n".join(id_to_name_lines), encoding='utf-8')
		print(f"[INFO] Wrote ID to name mapping to '{output_id_to_name.name}' ({len(id_to_name_lines):,} lines)")
		return True, tree_data