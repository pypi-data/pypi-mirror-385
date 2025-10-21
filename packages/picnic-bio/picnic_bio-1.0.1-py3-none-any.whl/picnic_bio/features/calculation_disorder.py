import sys

import numpy as np
import pandas as pd

SYS_EXIT_ERROR_MSG = "ERROR: The import of iupred2a_lib failed! Most like the PYTHONPATH has not been set correctly according to the README file."


def calculation_percentatile(prot: pd.DataFrame) -> pd.DataFrame:

    thr_names = [5, 25, 50, 75, 95]
    for d_thr in thr_names:
        prot["iupred_" + str(d_thr)] = prot["iupred"].apply(lambda x: np.percentile(x, d_thr))

    return prot


def calculate_disorder(prot: pd.DataFrame) -> pd.DataFrame:
    try:
        import iupred2a_lib

        prot["iupred"] = None
        for index, row in prot.iterrows():
            res = iupred2a_lib.iupred(row["sequence"], "long")
            prot.at[index, "iupred"] = res[0]

        df = calculation_percentatile(prot)
        return df
    except ImportError:
        sys.exit(SYS_EXIT_ERROR_MSG)


def calculation_percentatile_one(iupred_list: list) -> dict:

    dres = {}
    thr_names = [5, 25, 50, 75, 95]
    for d_thr in thr_names:
        dres["iupred_" + str(d_thr)] = np.percentile(iupred_list, d_thr)
    return dres


def calculate_disorder_one(sequence: str) -> dict:
    try:
        import iupred2a_lib

        dres = {}
        dres["iupred"] = iupred2a_lib.iupred(sequence, "long")[0]
        df = calculation_percentatile_one(dres["iupred"])
        return df
    except ImportError:
        sys.exit(SYS_EXIT_ERROR_MSG)


if __name__ == "__main__":
    print("Disorder calculation")  # noqa: T201
