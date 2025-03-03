# import numpy as np
# import random
# from itertools import combinations

# def generate_subsets(k):
#     """Generate all subsets of even and odd cardinality."""
#     elements = list(range(k))
#     even_subsets = [set(comb) for r in range(0, k + 1, 2) for comb in combinations(elements, r)]
#     odd_subsets = [set(comb) for r in range(1, k + 1, 2) for comb in combinations(elements, r)]
#     return even_subsets, odd_subsets

# def construct_matrices(k):
#     """Construct C0 and C1 matrices based on even and odd subsets."""
#     even_subsets, odd_subsets = generate_subsets(k)
#     num_columns = len(even_subsets)
#     C0 = np.zeros((k, num_columns), dtype=int)
#     C1 = np.zeros((k, num_columns), dtype=int)
#     for i in range(k):
#         for j, subset in enumerate(even_subsets):
#             if i in subset:
#                 C0[i, j] = 1
#         for j, subset in enumerate(odd_subsets):
#             if i in subset:
#                 C1[i, j] = 1
#     return C0, C1

# def generate_random_functions(n, k):
#     """Generate a collection of random functions mapping {1..n} -> {1..k}."""
#     return [lambda x, k=k: random.randint(0, k - 1) for _ in range(n * k)]


import numpy as np
import itertools

def generate_subsets(k):
    """Generate all subsets of even and odd cardinality."""
    elements = list(range(k))
    even_subsets = [set(comb) for r in range(0, k, 2) for comb in itertools.combinations(elements, r)]
    odd_subsets = [set(comb) for r in range(1, k + 1, 2) for comb in itertools.combinations(elements, r)]
    return even_subsets, odd_subsets

def construct_matrices(k):
    """Construct C0 and C1 matrices ensuring linear independence conditions."""
    even_subsets, odd_subsets = generate_subsets(k)
    num_columns = len(even_subsets)

    # Matrices must be k × 2^(k-1)
    C0 = np.zeros((k, 2**(k-1)), dtype=int)
    C1 = np.zeros((k, 2**(k-1)), dtype=int)

    # Fill matrices based on even and odd subset rules
    for i in range(k):
        for j, subset in enumerate(even_subsets):
            if i in subset:
                C0[i, j] = 1
        for j, subset in enumerate(odd_subsets):
            if i in subset:
                C1[i, j] = 1

    return C0, C1

import random

def generate_random_functions(n, k):
    """Generate random functions mapping {1..n} -> {1..k} ensuring uniform distribution."""
    H = []
    for _ in range(n):
        # Create a random function h: {1..n} -> {1..k}
        mapping = {i: random.randint(0, k - 1) for i in range(n)}
        H.append(lambda x, mapping=mapping: mapping[x])
    return H
