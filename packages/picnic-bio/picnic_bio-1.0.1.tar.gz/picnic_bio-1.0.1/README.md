<h1 align="center">
<img src="https://git.mpi-cbg.de/tothpetroczylab/picnic/-/raw/main/branding/logo/logo_picnic_v1.96113169.png" width="300">
</h1><br>

# PICNIC (Proteins Involved in CoNdensates In Cells)

[![Build Status](https://git.mpi-cbg.de/tothpetroczylab/picnic/badges/main/pipeline.svg)](https://git.mpi-cbg.de/tothpetroczylab/picnic/-/pipelines)
[![Coverage Status](https://git.mpi-cbg.de/tothpetroczylab/picnic/badges/main/coverage.svg)](https://git.mpi-cbg.de/tothpetroczylab/picnic/-/pipelines)
[![PyPI Version](https://img.shields.io/pypi/v/picnic-bio.svg)](https://pypi.org/project/picnic-bio/#history)
[![PyPI Downloads](https://img.shields.io/pypi/dm/picnic-bio.svg?label=PyPI%20downloads)](
https://pypi.org/project/picnic-bio/#files)
[![Nat Commun 15, 10668 (2024)](https://img.shields.io/badge/DOI-10.1038%2Fs41467_024_55089_x-blue)](
https://doi.org/10.1038/s41467-024-55089-x)
[![Python Versions](https://img.shields.io/pypi/pyversions/picnic-bio.svg)](https://pypi.org/project/picnic-bio/#description)
[![License](https://img.shields.io/pypi/l/picnic-bio.svg)](https://git.mpi-cbg.de/tothpetroczylab/picnic/-/blob/main/LICENSE)

PICNIC (Proteins Involved in CoNdensates In Cells) is a machine learning-based model that predicts proteins involved in biomolecular condensates. The first model (PICNIC) is based on sequence-based features and structure-based features derived from Alphafold2 models. Another model includes extended set of features based on Gene Ontology terms (PICNIC-GO). Although this model is biased by the already available annotations on proteins, it provides useful insights about specific protein properties that are enriched in proteins of biomolecular condensate. Overall, we recommend using PICNIC that is an unbiased predictor, and using PICNIC-GO for specific cases, for example for experimental hypothesis generation.

- [External software](#external-software)
- [Installation instructions](#installation-instructions)
  - [Requirements](#requirements)
  - [Install external requirements](#install-external-requirements)
  - [PICNIC is available on PyPI](#picnic-is-available-on-pypi)
  - [PICNIC is also installable from source](#picnic-is-also-installable-from-source)
  - [How to install PICNIC using Conda?](#how-to-install-picnic-using-conda)
- [How to use?](#how-to-use)
  - [Usage - Using PICNIC from command line](#usage---using-picnic-from-command-line)
  - [Examples](#examples)
  - [How to run the provided Jupyter notebook?](#how-to-run-the-provided-jupyter-notebook)
- [Publication](#publication)

## External software

*IUPred2A*

IUPred2A is a tool that predicts disordered protein regions. It is available for download via the link https://iupred2a.elte.hu/download_new
The downloaded archive should be unpacked into the "src/files/" directory.

*STRIDE*

STRIDE is a software for protein secondary structure assignment 
Installation guide can be found here https://webclu.bio.wzw.tum.de/stride/

## Installation instructions

A binary installer for the latest released version is available at the Python Package Index (PyPI).

### Requirements

* Python versions >=3.9,<3.13
* Download and unpack IUPred2A
  * Add IUPred2A to PYTHONPATH
* Download and unpack STRIDE
  * Add STRIDE binary to your system PATH


### Install external requirements

#### How to install STRIDE?

A complete installation guide can be found [here](https://webclu.bio.wzw.tum.de/stride/install.html) or simply
run the following commands:

```shell
mkdir stride
cd stride
curl -OL https://webclu.bio.wzw.tum.de/stride/stride.tar.gz
tar -zxf stride.tar.gz
make
export PATH="$PATH:$PWD"
```

#### How to install IUPred2A?

IUPred2A software is available for free only for academic users and it cannot be used for commercial purpose.
If you are an academic user, then you can download IUPred2A by filling out the following form [here](https://iupred2a.elte.hu/download_new).

```shell
# Step 1: Fill out the form above and download the IUPred2A tar ball
tar -zxf iupred2a.tar.gz
cd iupred2a
export PYTHONPATH="$PWD"
```

### PICNIC is available on PyPI

PICNIC officially supports Python versions >=3.9,<3.13.

```shell
python3 --version
Python 3.11.5

python3 -m venv picnic-env
source picnic-env/bin/activate
(picnic-env) % python -m pip install --upgrade pip
(picnic-env) % python -m pip install picnic_bio
```

### PICNIC is also installable from source

```shell
git clone git@git.mpi-cbg.de:atplab/picnic.git
```

Once you have a copy of the source, you can embed it in your own Python package, or install it into your site-packages easily

```shell
cd picnic
python3 -m venv picnic-env
source picnic-env/bin/activate
(picnic-env) % python -m pip install --upgrade pip
(picnic-env) % python -m pip install .
```

### How to install PICNIC using Conda?

There isn't any binary installer available on Conda yet. Though it is possible to install PICNIC within a virtual Conda environment.

Please note that in a conda environment you have to pre-install catboost, before installing picnic-bio itself, otherwise the installation will fail when compiling the catboost package from source code. Also it is recommended to use and set up [conda-forge](https://conda-forge.org/docs/user/introduction.html) to fetch pre-compiled versions of catboost.

We have documented how to get around the catboost installation issue.

```shell
conda config --add channels conda-forge
conda config --set channel_priority strict

# Choose one of the supported Python versions, when creating the Conda environment: >=3.9,<3.13
# conda create -n myenv python=[3.9, 3.10, 3.11, 3.12] catboost
# e.g.
conda create -n myenv python=3.11 catboost
conda activate myenv
(myenv) % python -m pip install picnic_bio
```

## How to use?

### Usage - Using PICNIC from command line

```
picnic <is_automated> <path_af> <protein_id> <is_go> --path_fasta_file <file>

usage: PICNIC [-h] [--path_fasta_file PATH_FASTA_FILE]
              is_automated path_af protein_id is_go

PICNIC (Proteins Involved in CoNdensates In Cells) is a machine learning-based
model that predicts proteins involved in biomolecular condensates.

positional arguments:
  is_automated          True if automated pipeline (works for proteins with
                        length < 1400 aa, with precalculated Alphafold2 model,
                        deposited to UniprotKB), else manual pipeline
                        (protein_id, Alphafold2 model(s) and fasta file are
                        needed to be provided as input)
  path_af               directory with pdb files, created by Alphafold2 for
                        the protein in the format. For smaller proteins ( <
                        1400 aa length) AlphaFold2 provides one model, that
                        should be named: AF-protein_id-F1-v{j}.pdb, where j is
                        a version number. In case of large proteins Alphafold2
                        provides more than one file, and all of them should be
                        stored in one directory and named: 'AF-
                        protein_id-F{i}-v{j}.pdb', where i is a number of
                        model, j is a version number.
  protein_id            protein identifier in UniprotKB (should correspond to
                        the name 'protein_id' for Alphafold2 models, stored in
                        directory_af_models)
  is_go                 boolean flag; if 'True', picnic_go score (picnic
                        version with Gene Ontology features) will be
                        calculated, Gene Ontology terms are retrieved in this
                        case from UniprotKB by protein_id identifier;
                        otherwise default picnic score will be printed
                        (without Gene Ontology annotation)

options:
  -h, --help            show this help message and exit
  --path_fasta_file PATH_FASTA_FILE
                        directory with sequence file in fasta format
```

### Examples

Run automated pipeline for a given UniProt Id:
```shell
picnic True notebooks/test_files/Q99720/ Q99720 True
```
Run manual pipeline for a given UniProt Id:
```shell
picnic False 'notebooks/test_files/O95613/' 'O95613' False --path_fasta_file 'notebooks/test_files/O95613/O95613.fasta.txt'
```
Run manual pipeline for your own protein sequence called MY_PROTEIN, which has no reference to UniProt:
```shell
picnic False 'notebooks/test_files/MY_PROTEIN/' 'MY_PROTEIN' False --path_fasta_file 'notebooks/test_files/MY_PROTEIN/my_protein.fasta'
```
Examples of using PICNIC are shown in a jupyter-notebook in notebooks folder.

### How to run the provided Jupyter notebook?

Examples of how to use and run PICNIC are shown in a provided Jupyter notebook. The notebook can be found under the
**notebooks** folder.

#### What is Jupyter Notebook?

Please read documentation [here](https://saturncloud.io/blog/how-to-launch-jupyter-notebook-from-your-terminal/#what-is-jupyter-notebook).


#### How to create a virtual environment and install all required Python packages.

Create a virtual environment by executing the command venv:
```shell
python -m venv /path/to/new/virtual/environment
# e.g.
python -m venv my_jupyter_env
```

Then install the classic Jupyter Notebook with:
```shell
source my_jupyter_env/bin/activate

pip install notebook
```
Also install picnic-bio from source in the same virtual environment...
```shell
pip install .
```

#### How to Launch Jupyter Notebook from Your Terminal?

In your terminal source the previously created virtual environment...
```shell
source my_jupyter_env/bin/activate
```
Launch Jupyter Notebook...
```shell
jupyter notebook
```
Open the example notebook called 'picnic_examples.ipynb' under the notebooks folder.  

## Publication
***PICNIC accurately predicts condensate-forming proteins regardless of their structural disorder across organisms.***
Anna Hadarovich, Hari Raj Singh, Soumyadeep Ghosh, Maxim Scheremetjew, Nadia Rostam, Anthony A. Hyman & Agnes Toth-Petroczy. 
Nature Communications volume 15, Article number: 10668 (2024). doi: [10.1038/s41467-024-55089-x](https://doi.org/10.1038/s41467-024-55089-x). PMID: [39663388](https://pubmed.ncbi.nlm.nih.gov/39663388/).

<a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-sa/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/">Creative Commons Attribution-ShareAlike 4.0 International License</a>.
