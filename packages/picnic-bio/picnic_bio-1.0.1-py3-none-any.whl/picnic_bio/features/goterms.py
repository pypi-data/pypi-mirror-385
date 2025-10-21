import json
from pathlib import Path

import pandas as pd
import requests

from ..exceptions import NoGoAnnotationFoundError


def get_go_from_api(uniprot_id: str) -> set[str]:
    """Retrieve a set of GO annotations for the given protein id from UniProt REST API.

    raise NoGoAnnotationFound exception if no GO terms could be fetched from UniProt.
    """
    go_terms = set()
    try:
        url = f"https://rest.uniprot.org/uniprotkb/search?query={uniprot_id}&format=json"
        all_fastas = requests.get(url).text
    except (requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout):
        print("Could not connect to the UniProt REST API! Try again later.")  # noqa: T201
        raise
    obj = json.loads(all_fastas)

    for song in obj["results"]:
        for attribute, value in song.items():
            if attribute == "uniProtKBCrossReferences":
                for db in value:
                    if db["database"] == "GO":
                        go_terms.add(db["id"])

    if len(go_terms) == 0:
        raise NoGoAnnotationFoundError(uniprot_id=uniprot_id)
    return go_terms


def calculate_3dir_go_one(uniprot_id: str, input_file_path: Path) -> dict:

    go = {}
    prot = {}
    go["go_terms_molecular_functions"] = "mf_2500_freq_all.json"
    go["go_terms_biological_processes"] = "bp_2500_freq_all.json"
    go["go_terms_cellular_component"] = "cc_2000_freq_all.json"

    go2 = {}
    go2["go_terms_molecular_functions"] = "mf_2500_freq.txt"
    go2["go_terms_biological_processes"] = "bp_2500_freq.txt"
    go2["go_terms_cellular_component"] = "cc_2000_freq.txt"

    for k, v in go.items():
        mf = pd.read_csv(input_file_path / go2[k], sep=" ")
        mft = set(mf["num"])
        with open(input_file_path / v) as json_file:
            mf = json.load(json_file)
        for kel in mft:
            prot[kel] = 0

        map_terms = mf

        translated = set()
        go_terms: set[str] = get_go_from_api(uniprot_id)

        for t in go_terms:
            t = t.strip()

            if t in map_terms.keys():
                for el in map_terms[t]:
                    translated.add(el)

        for t in sorted(mft):
            num = list(translated).count(t)
            prot[t] = num

    return prot


if __name__ == "__main__":
    print("GO terms")  # noqa: T201
