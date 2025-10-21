import collections
import os

import requests

from ..exceptions import (
    CouldNotDownloadAlphaFoldModelError,
    CouldNotDownloadFASTAFileError,
    NoAlphaFoldModelProvidedError,
)
from ..stride import exec_stride


def get_dict():
    aadict = {
        "A": 1,
        "G": 1,
        "V": 1,
        "M": 2,
        "S": 2,
        "T": 2,
        "Y": 2,
        "C": 7,
        "D": 6,
        "E": 6,
        "R": 5,
        "K": 5,
        "I": 3,
        "L": 3,
        "F": 3,
        "P": 3,
        "N": 4,
        "Q": 4,
        "H": 4,
        "W": 4,
    }
    amino = sorted(list((aadict.keys())))
    thrarr = ["d", "l", "m", "h"]
    strideclass = sorted(["Coil", "Turn", "Strand", "AlphaHelix", "310Helix", "Bridge", "PiHelix"])
    keysd = list()
    for k in list(amino):
        for stride in strideclass:
            for thr in thrarr:
                keysd.append(str(k) + "-" + str(stride) + "-" + str(thr))

    d = dict.fromkeys(keysd, 0)
    return d


def produce_stride_output_af(af_models_path, name, stride_out_path):

    forstride = os.listdir(af_models_path)
    result = [i for i in forstride if (i.startswith("AF-" + name + "-") and i.endswith(".pdb"))]
    if len(result) == 0:
        raise NoAlphaFoldModelProvidedError(af_models_path)
    for f in result:
        exec_stride(af_models_path + f, output_name=f, output_dir=stride_out_path)
    return


def get_ordered_dict(result):
    d = dict()
    for r in result:
        nummstr = r[:-13]

        x = nummstr.rfind("-")
        numm = nummstr[x + 2 :]

        d[int(numm)] = r

    od = collections.OrderedDict(sorted(d.items()))
    return od


def stride_to_dict(fileloc, uni):
    dnumclass = {}
    dnumname = {}
    with open(fileloc + uni + ".stride") as stride:
        for line in stride:
            if line.startswith("ASG"):
                stridetext = line.split()
                resnum = int(stridetext[3])
                resname = stridetext[1]
                resclass = stridetext[6]
                dnumclass[resnum] = resclass
                dnumname[resnum] = resname
    return dnumclass, dnumname


def make_afmodels_to_one(result, location_to_store, location_stride):

    od = get_ordered_dict(result)
    d = {}
    dn = {}
    for k, v in od.items():
        d1, d2 = stride_to_dict(location_stride, v)
        s = set()
        with open(location_to_store + v) as file:
            rstart = 1
            for line in file:
                if line.startswith("DBREF"):
                    pdb = line.split()
                    rstart = int(pdb[8])
                if line.startswith("ATOM"):

                    resname = line[17:20]
                    resrel = int(line[22:26])
                    resnum = resrel + rstart - 1
                    bfactor = float(line[60:66].strip())
                    dn[resnum] = resname
                    sclass = d1[resrel]

                    if resrel not in s:
                        if resnum in d.keys():
                            d[resnum].append((sclass, bfactor))

                        else:
                            d[resnum] = []
                            d[resnum].append((sclass, bfactor))
                        s.add(resrel)

    return d, dn


def stride_af_annotation(loc_write, list_uniprotid, af_models_path, stride_output_path):

    forstride = os.listdir(af_models_path)
    for n in list_uniprotid:
        wf = open(loc_write + n + "f.txt", "w")
        result = [i for i in forstride if (i.startswith("AF-" + n + "-") and i.endswith(".pdb"))]
        if len(result) > 0:
            d, dn = make_afmodels_to_one(result, af_models_path, stride_output_path)
            for k, v in d.items():
                d_classcount = {}
                d_maxprob = {}
                # print(v)
                if len(v) == 1:
                    sclass = v[0][0]
                    plddt = v[0][1]
                elif len(v) > 1:
                    for pars in v:
                        sc = pars[0]
                        scount = pars[1]
                        if sc in d_classcount.keys():
                            d_classcount[sc] += 1
                        else:
                            d_classcount[sc] = 1
                        if sc in d_maxprob.keys():
                            oldcount = d_maxprob[sc]
                            d_maxprob[sc] = max(scount, oldcount)
                        else:
                            d_maxprob[sc] = scount

                    d_classcountsorted = sorted(d_classcount.items(), key=lambda x: x[1], reverse=True)

                    if len(d_classcountsorted) == 1:
                        sclass = d_classcountsorted[0][0]
                        plddt = d_maxprob[sclass]
                    else:
                        maxclass = d_classcountsorted[0][0]
                        maxcount = d_classcountsorted[0][1]
                        maxcount2 = d_classcountsorted[1][1]
                        if maxcount > maxcount2:
                            sclass = maxclass
                            plddt = d_maxprob[maxclass]
                        else:
                            smax = {}
                            for mpairs in d_classcountsorted:
                                if mpairs[1] == maxcount:
                                    smax[mpairs[0]] = d_maxprob[mpairs[0]]
                            smaxsorted = sorted(smax.items(), key=lambda x: x[1], reverse=True)
                            sclass = smaxsorted[0][0]
                            plddt = smaxsorted[0][1]

                wf.write(str(k) + " " + str(dn[k]) + " " + sclass + " " + str(plddt) + "\n")
            wf.flush()
            wf.close()

    return


def stride_af_triads_one(fileloc, f, to_store):

    damino = {
        "CYS": "C",
        "ASP": "D",
        "SER": "S",
        "GLN": "Q",
        "LYS": "K",
        "ILE": "I",
        "PRO": "P",
        "THR": "T",
        "PHE": "F",
        "ASN": "N",
        "GLY": "G",
        "HIS": "H",
        "LEU": "L",
        "ARG": "R",
        "TRP": "W",
        "ALA": "A",
        "VAL": "V",
        "GLU": "E",
        "TYR": "Y",
        "MET": "M",
    }
    res = {}
    encode = 0
    d = get_dict()
    resval = [str(k) for k in sorted(d.keys())]

    for k in sorted(d.keys()):
        res[k] = 0
    with open(fileloc + f) as stride:
        for line in stride:
            encode += 1
            stridetext = line.split()
            am = damino[stridetext[1]]
            sclass = stridetext[2]
            prob = float(stridetext[3])
            if prob < 50:
                kprob = "d"
            elif prob >= 90:
                kprob = "h"
            elif prob < 70:
                kprob = "l"
            elif prob >= 70:
                kprob = "m"
            key = am + "-" + sclass + "-" + kprob
            if key in res.keys():
                res[key] += 1
            else:
                res[key] = 1

    if encode > 0:
        fout = open(to_store + f + "stride_triads", "w")
        fout.write("uniprot_id ")
        resstr = " ".join(resval)
        fout.write(resstr + " ")
        fout.write("\n")
        for k, v in res.items():
            res[k] = float(v) / (((encode)))

        resval = [str(v) for k, v in res.items()]
        resstr = " ".join(resval)
        fout.write(f[:-5] + " " + resstr + "\n")
        fout.flush()
        fout.close()

    return res


def calculate_sequence_structure_af_pipe_one_af(af_models_path, uniprot_id):

    produce_stride_output_af(af_models_path, uniprot_id, af_models_path)
    stride_af_annotation(af_models_path, [uniprot_id], af_models_path, af_models_path)
    af_fea = stride_af_triads_one(af_models_path, uniprot_id + "f.txt", af_models_path)

    return af_fea


def send_request_and_write_content_to_file(url: str, file_path: str):
    with open(file_path, "wb") as f:
        response = requests.get(url)
        response.raise_for_status()
        f.write(response.content)


def get_af_model_from_api(uniprot_id: str, path_file: str) -> str:
    # Ensure path_file ends with a directory separator
    if not path_file.endswith(os.sep):
        path_file += os.sep
    last_err = None
    for version in ["v6", "v7", "v8"]:
        try:
            url: str = f"https://alphafold.ebi.ac.uk/files/AF-{uniprot_id}-F1-model_{version}.pdb"
            file_path: str = f"{path_file}AF-{uniprot_id}-F1-model_{version}.pdb"
            send_request_and_write_content_to_file(url, file_path)
            return file_path
        except requests.exceptions.RequestException as err:
            last_err = err
    if last_err is not None:
        raise CouldNotDownloadAlphaFoldModelError(uniprot_id, last_err)


def get_fasta_from_api(uniprot_id: str, path_file) -> str:

    try:
        url = f"https://rest.uniprot.org/uniprotkb/{uniprot_id}.fasta"
        file_path = f"{path_file}{uniprot_id}.fasta"
        send_request_and_write_content_to_file(url, file_path)
    except requests.exceptions.RequestException as err:
        raise CouldNotDownloadFASTAFileError(uniprot_id, err)
    return file_path
