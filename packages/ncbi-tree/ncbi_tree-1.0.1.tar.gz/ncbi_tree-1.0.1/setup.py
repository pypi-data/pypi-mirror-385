"""
VERSION: 2025-10-21
AUTHOR: NCBI-Tree Contributors
LICENSE: Creative Commons Attribution-NonCommercial 4.0 (CC BY-NC 4.0)
"""

from setuptools import setup, find_packages
from pathlib import Path

readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding='utf-8') if readme_file.exists() else ""

setup(
	name="ncbi-tree",
	version="1.0.1",
	author="NCBI-Tree Contributors",
	author_email="",
	description="ncbi-tree is an open source, cross-platform command-line tool for downloading the latest NCBI taxonomy database and converting it to Newick tree format (.tre), with optional plain-text visualization (.txt)",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/phylobridge/ncbi-tree",
	packages=find_packages(where='.', include=['ncbi_tree*']),
	classifiers=[
		"Development Status :: 5 - Production/Stable",
		"Intended Audience :: Science/Research",
		"Intended Audience :: Developers",
		"Intended Audience :: Education",
		"Intended Audience :: Healthcare Industry",
		"License :: Free for non-commercial use",
		"Operating System :: OS Independent",
		"Operating System :: POSIX :: Linux",
		"Operating System :: MacOS",
		"Operating System :: Microsoft :: Windows",
		"Programming Language :: Python :: 3",
		"Programming Language :: Python :: 3.8",
		"Programming Language :: Python :: 3.9",
		"Programming Language :: Python :: 3.10",
		"Programming Language :: Python :: 3.11",
		"Programming Language :: Python :: 3.12",
		"Programming Language :: Python :: 3.13",
		"Topic :: Scientific/Engineering :: Bio-Informatics",
		"Topic :: Scientific/Engineering :: Information Analysis",
		"Topic :: Scientific/Engineering :: Visualization",
		"Topic :: Software Development :: Libraries :: Python Modules",
		"Topic :: Database",
		"Environment :: Console",
		"Natural Language :: English",
	],
	keywords=[
		"ncbi", "taxonomy", "phylogeny", "bioinformatics", "newick", "tree", "phylogenetic",
		"ncbi-taxonomy", "taxdump", "taxonomic-tree", "species-tree", "tree-of-life",
		"phylogenetic-tree", "taxonomy-database", "taxonomy-parser", "taxonomy-analysis",
		"biology", "genomics", "evolution", "evolutionary-biology", "systematics",
		"species-classification", "organism-classification", "taxonomic-hierarchy",
		"computational-biology", "metagenomics", "biodiversity", "clade-analysis",
		"taxon-names", "taxonomy-ids", "merged-taxa", "rank-distribution",
		"phylogenetics", "phylogenomics", "comparative-genomics", "tree-builder",
		"ncbi-tools", "bio-tools", "data-pipeline", "text-tree", "tsv-mapping"
	],
	python_requires=">=3.8",
	install_requires=[
		"requests>=2.25.0",
		"tqdm>=4.50.0",
	],
	entry_points={
		'console_scripts': [
			'ncbi-tree=ncbi_tree.cli:main',
		],
	},
	license="CC BY-NC 4.0",
	project_urls={
		"Homepage": "https://github.com/phylobridge/ncbi-tree",
		"Documentation": "https://github.com/phylobridge/ncbi-tree#readme",
		"Bug Reports": "https://github.com/phylobridge/ncbi-tree/issues",
		"Source": "https://github.com/phylobridge/ncbi-tree",
		"NCBI Taxonomy": "https://www.ncbi.nlm.nih.gov/taxonomy",
	},
)
