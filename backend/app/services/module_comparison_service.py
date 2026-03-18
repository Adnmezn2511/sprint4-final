# backend/app/services/module_comparison_service.py

"""
Service for comparing gene module lists across multiple patients.
Provides intersection, union, per-patient differences,
and discriminant gene identification.
"""

from typing import Dict, List, Set


def compare_modules(patient_modules: Dict[str, List[str]]) -> Dict:
    """
    Compare gene module lists from multiple patients.

    Computes:
    - intersection: genes shared by ALL patients
    - union: genes present in AT LEAST ONE patient
    - differences: per patient, genes absent from all other patients
    - discriminant_genes: genes exclusive to exactly one patient

    :param patient_modules: Dict mapping patient IDs to their gene lists.
                            Example: {"P1": ["EGFR", "BRCA1"], "P2": ["BRCA1", "TP53"]}
    :raises ValueError: If fewer than 2 patients are provided,
                        or if any gene list is empty or not a list.
    :return: Dict with keys:
             - intersection (List[str])
             - union (List[str])
             - differences (Dict[str, List[str]])
             - discriminant_genes (Dict[str, List[str]])
             - patient_count (int)
             - summary (Dict)
    """
    if not patient_modules or len(patient_modules) < 2:
        raise ValueError(
            "At least two patient module lists are required for comparison."
        )

    for patient_id, genes in patient_modules.items():
        if not isinstance(genes, list) or len(genes) == 0:
            raise ValueError(
                f"Patient '{patient_id}' has an empty or invalid gene list."
            )

    # Convert each patient gene list to a set for set operations
    sets: Dict[str, Set[str]] = {
        patient_id: set(genes)
        for patient_id, genes in patient_modules.items()
    }

    all_sets = list(sets.values())

    # Intersection: genes present in ALL patients
    intersection: List[str] = sorted(
        all_sets[0].intersection(*all_sets[1:])
    )

    # Union: genes present in AT LEAST ONE patient
    union: List[str] = sorted(
        all_sets[0].union(*all_sets[1:])
    )

    # Differences: for each patient, genes not found in any other patient
    differences: Dict[str, List[str]] = {}
    for patient_id, gene_set in sets.items():
        other_sets = [s for pid, s in sets.items() if pid != patient_id]
        union_of_others = (
            other_sets[0].union(*other_sets[1:])
            if len(other_sets) > 1
            else other_sets[0]
        )
        differences[patient_id] = sorted(gene_set - union_of_others)

    # Discriminant genes: genes exclusive to exactly one patient
    discriminant_genes: Dict[str, List[str]] = {
        patient_id: genes
        for patient_id, genes in differences.items()
        if len(genes) > 0
    }

    return {
        "intersection": intersection,
        "union": union,
        "differences": differences,
        "discriminant_genes": discriminant_genes,
        "patient_count": len(patient_modules),
        "summary": {
            "intersection_size": len(intersection),
            "union_size": len(union),
            "patients_with_discriminant_genes": len(discriminant_genes),
        },
    }