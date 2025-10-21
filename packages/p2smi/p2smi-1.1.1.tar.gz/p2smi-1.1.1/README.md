![p2smi banner](./p2smi.png)

# p2smi: Generation and Analysis of Drug-like Peptide SMILES Strings

**p2smi** is a Python toolkit for peptide design and analysis. 

It enables generation of peptide sequences, conversion to SMILES representations—including support for cyclic and noncanonical amino acids—and evaluation of molecular properties. The package also provides utilities for structural modification (e.g., N-methylation, PEGylation), synthesis feasibility assessment, and output in a dedicated .p2smi format that links peptide sequences to their corresponding SMILES.

Developed in support of [PeptideCLM](https://pubs.acs.org/doi/10.1021/acs.jcim.4c01441), a SMILES-based language model for modified peptides, p2smi provides an extensible foundation for computational peptide chemistry and machine-learning-driven molecular design.


## Features

- Generate random peptide sequences (with NCAAs, D-stereochemistry, and cyclization)
- Convert peptide FASTA files into valid SMILES strings
- Support five cyclization types: disulfide, head-to-tail, sidechain-to-sidechain, sidechain-to-N-term, sidechain-to-C-term
- Modify SMILES with user-defined N-methylation and PEGylation rates
- Evaluate synthetic feasibility based on common failure motifs
- Compute molecular properties (MW, logP, TPSA, Lipinski, etc.)

## Updates
- Version 1.1.1 - Added functionality to allow for user-defined cyclizing residue constraints
- Version 1.1.0 - Updated codebase, documentation, fixed bugs -- for JOSS review
- Version 1.0.0 - First release for JOSS submission


## Citation

If you use this tool, please cite:

*p2smi: A Python Toolkit for Peptide FASTA-to-SMILES Conversion and Molecular Property Analysis*.  
Feller, A. L. and Wilke, C. O. (2025).  
[arXiv](https://arxiv.org/abs/2505.00719)

A JOSS publication for this package is in review.

## Manuscript
- [PDF](manuscript/paper.pdf) | [Markdown](manuscript/paper.md)


## Directory

- [Installation](#installation)
- [Command-Line Tools](#command-line-tools)
- [Example Usage](#example-usage)
- [Future Work](#future-work)
- [Contributing](#for-contributors)
- [License](#license)


## Installation

Install from PyPI:

```bash
pip install p2smi
```

For local development:

```bash
git clone https://github.com/AaronFeller/p2smi.git
cd p2smi
pip install -e .[dev]
```


## Command-Line Tools

| Command             | Description |
|-------------------------|-------------------------------------------------------------------------------------------------------------------------|
| `generate-peptides`.    | **Summary:** Generates random peptide sequences with user-defined constraints including number of sequences, length range, NCAA percentage, D-stereochemistry rate, and cyclization types. Supports over 100 noncanonical amino acids (SwissSidechain).<br>**Input:** CLI arguments for generation settings and output filename.<br>**Output:** FASTA file with single-letter codes, including noncanonical residues. |
| `fasta2smi`             | **Summary:** Converts peptide sequences from FASTA format into SMILES, parsing cyclization tags from the FASTA header.<br>**Note:** Supports five cyclization types: disulfide (SS), head-to-tail (HT), sidechain-to-sidechain (SCSC), sidechain-to-head (SCNT), and sidechain-to-tail (SCCT). To define specific cyclizations, include notation in fasta file as described in the next section below.<br>**Input:** Peptide FASTA file, optional cyclization tags.<br>**Output:** `.p2smi` file containing amino acid sequence, cyclization type, and SMILES string. |
| `modify-smiles`         | **Summary:** Applies random N-methylation and PEGylation to SMILES strings. Modifications are probabilistic and tracked when input is in `.p2smi` format.<br>**Input:** Plaintext SMILES file or `.p2smi` file.<br>**Output:** Modified SMILES in same format as input, with changes recorded. |
| `smiles-props`          | **Summary:** Computes a wide range of molecular properties from SMILES, including MW, TPSA, logP, H-bond donors/acceptors, rotatable bonds, ring count, fraction Csp3, heavy atoms, formal charge, molecular formula, and Lipinski rule evaluation.<br>**Input:** SMILES text file or `.p2smi` file.<br>**Output:** JSON-formatted text file with calculated properties for each SMILES. |
| `synthesis-check`       | **Summary:** Evaluates peptide sequences for synthetic feasibility using hard-coded filters (e.g., N/Q at N-terminus, Gly/Pro motifs, Cys count, hydrophobicity, charge distribution). Currently supports natural amino acids only.<br>**Input:** FASTA file.<br>**Output:** FASTA file with headers annotated as PASS/FAIL. |

Use `--help` on any command for options:
```bash
fasta2smi --help
```

## Manually encoding cyclizations

Cyclizations can be specified directly in the FASTA header to control how fasta2smi interprets bond formation between residues.

Each cyclization tag begins with a two-letter code identifying the bond type (SS or SC), followed by a constraint mask of equal length to the peptide sequence, where:

- X marks positions left unconstrained
- C marks residues participating in a disulphide bond
- N marks residues with side-chain cyclization to N-term
- Z marks residues with side-chain cyclization to C-term
- if N and Z included, form side-chain to side-chain cyclization

### Supported Formats:

| Tag | Type | Description | Example header|
|------|------|-------------|----------|
| `SS` | Disulfide | Connects two cysteine residues | `>peptide\|SSXXXCXXXCX` |
| `HT` | Head-to-tail | Amide bond between N- and C-termini | `>peptide\|HT` |
| `SCSC` | Sidechain–Sidechain | Covalent link between two sidechains (e.g., Lys–Asp lactam) | `>peptide\|SCXXNXXXXXZ` |
| `SCNT` | Sidechain–N-Terminus | Link between N-terminus and a sidechain residue | `>peptide\|SCXXNXXXXXX` |
| `SCCT` | Sidechain–C-Terminus | Link between a sidechain residue and C-terminus | `>peptide\|SCXXXXXZXXX` |


## Example Usage

### Generate random peptides with constraints:

```bash
generate-peptides \
  --num 10 \
  --min_length 10 \
  --max_length 20 \
  --noncanonical 0.1 \
  --dextro 0.1 \
  --cyclization_constraints all \
  --outfile peptides.fasta
```

### Convert FASTA to SMILES:

```bash
fasta2smi -i peptides.fasta -o peptides.p2smi
```

### Modify SMILES strings:

```bash
modify-smiles -i peptides.p2smi -o modified.p2smi --peg_rate 0.2 --nmeth_rate 0.2 --nmeth_residues 0.2
```

### Compute molecular properties:

```bash
smiles-props -i modified.p2smi
```

### Check synthesis feasibility (natural AAs only):

```bash
generate-peptides -o nat_peptides.fasta
synthesis-check -i nat_peptides.fasta
```


## Future Work

- Extend synthesis rules to NCAAs and modified peptides
- Support alternative encodings (HELM, SELFIES)
- Batch processing and multiprocessing support
- Integration with predictive models
- Post-translational modification import pipelines


## For Contributors

You’re welcome to contribute! Suggestions, bugs, and pull requests are appreciated.

- 📂 [Open an Issue](https://github.com/AaronFeller/p2smi/issues)
- 🛠 Submit a pull request
- 📝 Improve the docs


## License

[MIT License](https://github.com/AaronFeller/p2smi/blob/master/LICENSE)
