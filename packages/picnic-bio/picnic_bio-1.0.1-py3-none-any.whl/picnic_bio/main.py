import argparse
import os
import shutil
import sys

from .prediction.inference_model import inference_model_with_go_one, inference_model_without_go_one

parser = argparse.ArgumentParser(
    prog="PICNIC",
    description="PICNIC (Proteins Involved in CoNdensates In Cells) is a machine learning-based model that predicts proteins involved in biomolecular condensates.",
)
parser.add_argument(
    "is_automated",
    help="True if automated pipeline (works for proteins with length < 1400 aa, with precalculated Alphafold2 model, deposited to UniprotKB), else manual pipeline (uniprot_id, Alphafold2 model(s) and fasta file are needed to be provided as input)",
)  # positional argument
parser.add_argument(
    "path_af",
    help="directory with pdb files, created by Alphafold2 for the protein in the format. "
    "For smaller proteins ( < 1400 aa length) AlphaFold2 provides one model, that should be named: AF-uniprot_id-F1-v{j}.pdb, where j is a version number. "
    "In case of large proteins Alphafold2 provides more than one file, and all of them should be stored in one directory and named: "
    "'AF-uniprot_id-F{i}-v{j}.pdb', where i is a number of model, j is a version number.",
)  # positional argument
parser.add_argument(
    "uniprot_id",
    help="protein identifier in UniprotKB (should correspond to the name 'uniprot_id' for Alphafold2 models, stored in directory_af_models)",
)  # positional argument
parser.add_argument(
    "is_go",
    help="boolean flag; if 'True', picnic_go score (picnic version with Gene Ontology features) will be calculated, "
    "Gene Ontology terms are retrieved in this case from UniprotKB by uniprot_id identifier; otherwise default picnic score will be printed (without Gene Ontology annotation)",
)  # positional argument
parser.add_argument(
    "--path_fasta_file",
    required=False,
    help="directory with sequence file in fasta format",
)  # optional argument


def check_pythonpath():
    """Check that the PYTHONPATH env var is set correctly according to the documentation - README file."""
    warning_message = "ERROR: PYTHONPATH not set correctly according to the README file."
    if "PYTHONPATH" not in os.environ:
        sys.exit(f"{warning_message}\nDetected empty PYTHONPATH!")
    else:
        contains_iupred = False
        python_paths: list = os.environ["PYTHONPATH"].split(os.pathsep)
        for path in python_paths:
            if "iupred2a" in path:
                contains_iupred = True
                break
        if not contains_iupred:
            sys.exit(
                f"{warning_message}\nIUPred2A not added correctly to the PYTHONPATH!\n"
                f"Detected the following PYTHONPATH: {os.environ['PYTHONPATH']}"
            )


def check_stride_executable():
    """Make sure STRIDE executable is available"""
    path = shutil.which("stride")
    if path is None:
        sys.exit(
            f"ERROR: STRIDE not installed correctly or stride binary not added to the systems path according to the README file!\n"
            f"Detected the following system PATH: {os.environ['PATH']}"
        )


def initial_requirements_check():
    """Check if required external dependencies are installed correctly, before executing PICNIC main flow."""
    check_pythonpath()
    check_stride_executable()


def main():
    initial_requirements_check()
    args = parser.parse_args()
    path_af = args.path_af
    is_automated = args.is_automated
    uniprot_id = args.uniprot_id
    isgo = args.is_go
    if is_automated == "True":
        if isgo == "True":
            picnic_go, _ = inference_model_with_go_one(path_af, path_af, uniprot_id, True)
            print("Automated pipeline: Picnic_go score for " + uniprot_id + " = " + str(picnic_go))  # noqa: T201
        else:
            picnic, _ = inference_model_without_go_one(path_af, path_af, uniprot_id, True)
            print("Automated pipeline: Picnic score for " + uniprot_id + " = " + str(picnic))  # noqa: T201
    else:
        fasta_dir = args.path_fasta_file
        if isgo == "True":
            picnic_go, _ = inference_model_with_go_one(fasta_dir, path_af, uniprot_id, False)
            print("Manual pipeline: Picnic_go score for " + uniprot_id + " = " + str(picnic_go))  # noqa: T201
        else:
            picnic, _ = inference_model_without_go_one(fasta_dir, path_af, uniprot_id, False)
            print("Manual pipeline: Picnic score for " + uniprot_id + " = " + str(picnic))  # noqa: T201


if __name__ == "__main__":
    main()
