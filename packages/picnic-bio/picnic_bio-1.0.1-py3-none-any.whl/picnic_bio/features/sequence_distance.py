import itertools


def get_dict_for_dist(thrarr):
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
    keys = list(itertools.combinations(amino, 2))
    keysd = list()
    for k in list(aadict.keys()):
        for thr in thrarr:
            keysd.append(str(k) + "," + str(thr) + str(k))
    for pair in list(keys):
        for thr in thrarr:
            keysd.append(str(pair[0]) + "," + str(thr) + str(pair[1]))
    d = dict.fromkeys(keysd, 0)
    return d, keys


def calc_distance_sequence_short(sequence: str) -> dict:
    thrarr = [1, 2, 3, 4, 5]

    d, keys = get_dict_for_dist(thrarr)
    for i in range(len(sequence)):
        for j in range(i + 1, len(sequence)):
            val = sorted((sequence[i], sequence[j]))
            thr_curr = abs(i - j)
            if thr_curr <= 5:
                thr_str = str(val[0]) + "," + str(thr_curr) + str(val[1])
                if thr_str in d.keys():
                    d[thr_str] += 1

    for k, v in d.items():
        d[k] = float(v) / ((len(sequence)))

    return d


def calc_distance_sequence_long(sequence):
    thrarr = [0, 20, 40, 60]

    d, keys = get_dict_for_dist(thrarr)
    for i in range(len(sequence)):
        for j in range(i + 1, len(sequence)):
            val = sorted((sequence[i], sequence[j]))
            thr_curr = (abs(i - j) // 20) * 20
            if thr_curr < 80:
                thr_str = str(val[0]) + "," + str(thr_curr) + str(val[1])
                if thr_str in d.keys():
                    d[thr_str] += 1

    for k, v in d.items():
        d[k] = float(v) / (20 * (len(sequence)))

    return d


def calculate_dist_features_one(sequence: str) -> dict:

    prot = {}
    thrarr = [0, 20, 40, 60]
    thrarr2 = [1, 2, 3, 4, 5]
    d, keys = get_dict_for_dist(thrarr)
    resval = [str(k) for k in sorted(d.keys())]
    for kel in resval:
        prot[kel] = 0
    d, keys = get_dict_for_dist(thrarr2)
    resval = [str(k) for k in sorted(d.keys())]
    for kel in resval:
        prot[kel] = 0

    res_long = calc_distance_sequence_long(sequence)

    res_short = calc_distance_sequence_short(sequence)
    all_fea = {**res_long, **res_short}
    return all_fea


if __name__ == "__main__":
    print("Sequence features")  # noqa: T201
