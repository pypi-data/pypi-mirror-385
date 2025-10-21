import math


def k1complexity(sequence: str, window_size: int) -> float:

    if len(sequence) < window_size:
        return None
    k1s = []
    for i in range(len(sequence) - window_size + 1):
        sequence_chunk = sequence[i : i + window_size]
        aa_seq = {}
        for aa in sequence_chunk:
            aa_seq[aa] = 1 if aa not in aa_seq else aa_seq[aa] + 1

        fact_product = 1
        for aa_count in aa_seq.values():
            fact_product *= math.factorial(aa_count)
        k1 = 1 / window_size * math.log(math.factorial(window_size) // fact_product, 10)
        k1s.append(k1)

    return min(k1s)


def calculate_k40_k60_complexity_one(sequence: str) -> dict:

    res40 = k1complexity(sequence, 40)
    res60 = k1complexity(sequence, 60)
    dres = {}
    dres["k1_40"] = res40
    dres["k1_60"] = res60

    return dres


if __name__ == "__main__":
    print("Complexity")  # noqa: T201
