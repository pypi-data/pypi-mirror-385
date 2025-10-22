"""
VERSION: 2025-10-21
AUTHOR: NCBI-Tree Contributors
LICENSE: Creative Commons Attribution-NonCommercial 4.0 (CC BY-NC 4.0)
"""

import sys
import time
import shutil
import argparse
import traceback
from pathlib import Path
from datetime import datetime
from functools import partial
from .core import download_and_extract_taxonomy, build_ncbi_tree
from . import __version__
print = partial(print, flush=True)


def main():
	"""Main CLI entry point for ncbi-tree"""
	parser = argparse.ArgumentParser(
		prog='ncbi-tree',
		description='Download NCBI taxonomy database and build phylogenetic trees in multiple formats',
		formatter_class=argparse.RawDescriptionHelpFormatter,
		epilog="""
DESCRIPTION:
  ncbi-tree, an open-source tool to convert NCBI Taxonomy to Newick tree
  
  Core output files are generated automatically:
    - output.NCBI.tree.tre: Newick tree with NCBI taxonomy IDs only
    - output.NCBI.report.txt: Exploratory taxonomy analysis and statistics
    - version.txt: Server timestamped version for downloaded taxdump.tar.gz
  
  After core files, you'll be prompted to generate optional files [y/n]:
    - output.NCBI.tree.txt: Plain-text tree with Unicode box-drawing
    - output.NCBI.named.tree.tre: Newick tree with rank:id:name labels
    - output.NCBI.ID.to.name.tsv: TSV mapping of IDs to names (TaxID, Name, Rank)

EXAMPLES:
  # Basic usage for downloading and building taxonomy tree
  ncbi-tree ./output
  
  # Clean up intermediate files after processing
  ncbi-tree ./output --no-cache
  
  # Keep original name formatting (don't sanitize spaces)
  ncbi-tree ./output --no-sanitize
  
  # Use custom NCBI mirror or local file
  ncbi-tree ./output --url https://mirror.org/taxdump.tar.gz

SEE ALSO:
  GitHub: https://github.com/PhyloBridge/ncbi-tree
  PyPI: https://pypi.org/project/ncbi-tree/
  NCBI Taxonomy: https://www.ncbi.nlm.nih.gov/taxonomy
		"""
	)
	parser.add_argument('output_directory', nargs='?', help='Output directory for all generated taxonomy files')
	parser.add_argument('--no-cache', '--clean', action='store_true', dest='no_cache', help='Remove intermediate files (tar.gz archive) after processing to save disk space')
	parser.add_argument('--url', type=str, default=None, help='Custom download URL for taxonomy data (default: https://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdump.tar.gz)')
	parser.add_argument('--no-sanitize', action='store_true', help='Disable name sanitization: keep original spaces, dashes, and special characters in taxon names')
	parser.add_argument('--version', action='version', version=f'ncbi-tree {__version__}')
	args = parser.parse_args()
	if not args.output_directory:
		parser.print_help()
		sys.exit(1)
	start_time = time.time()
	print("=" * 80)
	print(f"STARTING EXECUTION AT {datetime.now().strftime('%H:%M:%S ON %Y-%m-%d')}")
	print("=" * 80)
	print(f"ncbi-tree version {__version__}")
	print(f"Output directory: {args.output_directory}")
	print(f"Clean intermediate files: {args.no_cache}")
	if args.no_sanitize:
		import ncbi_tree.core as core_module
		core_module.SANITIZE_TAXON_NAME = False
		print(f"Name sanitization: disabled")
	print()
	try:
		taxonomy_folder = download_and_extract_taxonomy(
			output_dir=args.output_directory,
			download_url=args.url,
			clean_intermediate=args.no_cache
		)
		if taxonomy_folder is None:
			print("\n[ERROR] Failed to download or extract taxonomy data")
			sys.exit(1)
		print()
		success, tree_data = build_ncbi_tree(
			taxonomy_folder=taxonomy_folder,
			output_dir=args.output_directory,
			generate_optional_files=False
		)
		if not success:
			print("\n[ERROR] Failed to build taxonomy tree")
			sys.exit(1)
		total_execution_time = time.time() - start_time
		print("\n" + "=" * 80)
		print(f"EXECUTION COMPLETED SUCCESSFULLY IN {total_execution_time:.0f}s ({total_execution_time/3600:.2f}h)")
		print("=" * 80)
		output_path = Path(args.output_directory)
		print(f"\nGenerated core files:")
		print(f"  - {output_path / 'output.NCBI.tree.tre'}")
		print(f"  - {output_path / 'output.NCBI.report.txt'}")
		print(f"  - {output_path / 'version.txt'}")
		print("\n" + "=" * 80)
		response = input("\nWould you like to generate optional files (output.NCBI.tree.txt, output.NCBI.named.tree.tre, output.NCBI.ID.to.name.tsv)? [y/N]: ").strip().lower()
		if response in ['y', 'yes']:
			print("\n[INFO] Generating optional files...")
			optional_start = time.time()
			success, _ = build_ncbi_tree(
				taxonomy_folder=taxonomy_folder,
				output_dir=args.output_directory,
				generate_optional_files=True,
				tree_data=tree_data
			)
			if success:
				optional_time = time.time() - optional_start
				print(f"\n[INFO] Optional files generated in {optional_time:.0f}s")
				print(f"\nAdditional output files:")
				print(f"  - {output_path / 'output.NCBI.tree.txt'}")
				print(f"  - {output_path / 'output.NCBI.named.tree.tre'}")
				print(f"  - {output_path / 'output.NCBI.ID.to.name.tsv'}")
		else:
			print("\n[INFO] Skipping optional files generation")
		if args.no_cache:
			print("\n[INFO] Cleaning up version folder...")
			shutil.rmtree(taxonomy_folder)
			print(f"[INFO] Removed: {taxonomy_folder}")
	except KeyboardInterrupt:
		print("\n\nInterrupted by user (Ctrl+C)")
		sys.exit(130)
	except Exception as error:
		print(f"\n\nUnexpected error: {error}")
		traceback.print_exc()
		sys.exit(1)

if __name__ == '__main__':
	main()