import os
from pathlib import Path
from typing import Optional

from Bio import SeqIO

from ..exceptions import CouldNotParseFASTAFileError
from ..features.calculation_disorder import calculate_disorder_one
from ..features.goterms import calculate_3dir_go_one
from ..features.sequence_complexity import calculate_k40_k60_complexity_one
from ..features.sequence_distance import calculate_dist_features_one
from ..features.sequence_structure_AF2 import (
    calculate_sequence_structure_af_pipe_one_af,
    get_af_model_from_api,
    get_fasta_from_api,
)


def calculate_pipeline_one(path_af: str, name: str, input_fasta, go_flag=False, go_folder_path: Path = None) -> dict:

    fasta_sequences = SeqIO.parse(open(input_fasta), "fasta")
    records = []
    for fasta in fasta_sequences:
        records.append(str(fasta.seq))
    sequence = records[0]
    d_af = calculate_sequence_structure_af_pipe_one_af(path_af, name)
    d_disorder = calculate_disorder_one(sequence)
    d_dist = calculate_dist_features_one(sequence)
    d_comp = calculate_k40_k60_complexity_one(sequence)
    if go_flag:
        d_go = calculate_3dir_go_one(name, go_folder_path)
        allfea = {**d_disorder, **d_dist, **d_go, **d_comp, **d_af}
    else:
        allfea = {**d_disorder, **d_dist, **d_comp, **d_af}

    return allfea


def calculate_pipeline_automated_one(
    path_output: str, name: str, go_flag=False, go_folder_path: Path = None
) -> Optional[dict]:
    path_uni = os.path.join(path_output, name)
    if not path_uni.endswith(os.sep):
        path_uni += os.sep
    if not os.path.isdir(path_uni):
        os.mkdir(path_uni)
    get_af_model_from_api(name, path_uni)
    input_fasta = get_fasta_from_api(name, path_uni)
    fasta_sequences = SeqIO.parse(open(input_fasta), "fasta")
    records = []
    for fasta in fasta_sequences:
        records.append(str(fasta.seq))
    if len(records) > 0:
        sequence = records[0]
        d_af = calculate_sequence_structure_af_pipe_one_af(path_uni, name)
        d_disorder = calculate_disorder_one(sequence)
        d_dist = calculate_dist_features_one(sequence)
        d_comp = calculate_k40_k60_complexity_one(sequence)
        if go_flag:
            d_go = calculate_3dir_go_one(name, go_folder_path)
            allfea = {**d_disorder, **d_dist, **d_go, **d_comp, **d_af}
        else:
            allfea = {**d_disorder, **d_dist, **d_comp, **d_af}

        return allfea
    else:
        raise CouldNotParseFASTAFileError(input_fasta)


if __name__ == "__main__":
    print("Calculate pipeline")  # noqa: T201
