import os
import shutil
import subprocess
import sys
from typing import List


def _run_subprocess(args: List[str]):
    """Generic function for running command line tools using Python's subprocess module.

    :param args: Provided tool command.
    """
    command = " ".join(args)
    try:
        subprocess.run(
            args=args,
            timeout=3600,
            check=True,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
    except subprocess.CalledProcessError as err:
        print(f"ERROR in src.stride: An error has occurred while running: {command}")  # noqa: T201
        print(f"RETURN CODE: {err.returncode}")  # noqa: T201
        print(f"{err.stderr}")  # noqa: T201
        print("Exiting program now.")  # noqa: T201
        sys.exit(err.returncode)


def exec_stride(pdb, output_name=None, output_dir=None) -> str:
    """
    This function is based on the following code in Prody:
        https://github.com/prody/ProDy/blob/ef3d678014beaff525a2f221fc3008ef51e4437b/prody/proteins/stride.py#L19

    Execute STRIDE program for a given *pdb* file. When no *outputname* is given, output
    name will be :file:`pdb.stride`.  :file:`.stride` extension will be
    appended automatically to *outputname*.  If :file:`outputdir` is given,
    STRIDE output and uncompressed PDB file will be written into this folder.
    Upon successful execution of :command:`stride pdb > out` command, output
    filename is returned.

    For more information on STRIDE see http://webclu.bio.wzw.tum.de/stride/.
    If you benefited from STRIDE, please consider citing [DF95]_.

    .. [DF95] Frishman D, Argos P. Knowledge-Based Protein Secondary Structure
       Assignment. *Proteins* **1995** 23:566-579.

    :param output_dir: STRIDE output directory.
    :param output_name: STRIDE output file name.
    :param pdb: PDB file path.

    :raises:
        EnvironmentError: If stride is NOT installed
        ValueError: If no pdb file provided
        subprocess.CalledProcessError: If stride cannot be executed
    :returns: A string which represents the concatenated path of the stride output file.
    """

    stride = shutil.which("stride")
    if stride is None:
        raise EnvironmentError("command not found: stride executable not found in one of the system paths!")
    assert output_name is None or isinstance(output_name, str), "output_name must be a string"
    assert output_dir is None or isinstance(output_dir, str), "output_dir must be a string"
    if pdb is None:
        raise ValueError("The provided pdb file value is not a valid file name!")

    if output_dir is None:
        output_dir = "."
    if output_name is None:
        out = os.path.join(output_dir, os.path.splitext(os.path.split(pdb)[1])[0] + ".stride")
    else:
        out = os.path.join(output_dir, output_name + ".stride")

    _run_subprocess([f"{stride}", f"-f{out}", pdb])
    return out
