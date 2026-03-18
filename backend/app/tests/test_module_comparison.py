# backend/app/tests/test_module_comparison.py

"""
Unit tests for the module comparison service (US-D2).

Covers:
- Valid cohort inputs: intersection, union, differences, discriminant genes, summary
- Edge cases: no shared genes, identical patients, two-patient minimum
- Invalid inputs: single patient, empty dict, empty gene list, wrong type, None
"""

import unittest
import pytest
from app.services.module_comparison_service import compare_modules


class TestCompareModulesValid(unittest.TestCase):
    """Tests on valid multi-patient cohort inputs."""

    def setUp(self):
        self.patients = {
            "P1": ["EGFR", "BRCA1", "TP53"],
            "P2": ["BRCA1", "TP53", "LMNA"],
            "P3": ["TP53", "ATM", "SRC"],
        }

    # ------------------------------------------------------------------
    # Intersection
    # ------------------------------------------------------------------

    def test_intersection_contains_shared_genes(self):
        """TP53 is present in all three patients — must appear in intersection."""
        result = compare_modules(self.patients)
        self.assertIn("TP53", result["intersection"])

    def test_intersection_excludes_non_shared_genes(self):
        """EGFR and ATM are not in all patients — must not appear in intersection."""
        result = compare_modules(self.patients)
        self.assertNotIn("EGFR", result["intersection"])
        self.assertNotIn("ATM", result["intersection"])

    def test_intersection_is_sorted(self):
        """Intersection list must be alphabetically sorted."""
        result = compare_modules(self.patients)
        self.assertEqual(result["intersection"], sorted(result["intersection"]))

    # ------------------------------------------------------------------
    # Union
    # ------------------------------------------------------------------

    def test_union_contains_all_genes(self):
        """Every gene from every patient must appear in the union."""
        result = compare_modules(self.patients)
        for gene in ["EGFR", "BRCA1", "TP53", "LMNA", "ATM", "SRC"]:
            self.assertIn(gene, result["union"])

    def test_union_is_sorted(self):
        """Union list must be alphabetically sorted."""
        result = compare_modules(self.patients)
        self.assertEqual(result["union"], sorted(result["union"]))

    def test_union_has_no_duplicates(self):
        """Union must not contain duplicate gene entries."""
        result = compare_modules(self.patients)
        self.assertEqual(len(result["union"]), len(set(result["union"])))

    # ------------------------------------------------------------------
    # Differences
    # ------------------------------------------------------------------

    def test_differences_contains_patient_exclusive_genes(self):
        """EGFR is only in P1 — must appear in P1 differences."""
        result = compare_modules(self.patients)
        self.assertIn("EGFR", result["differences"]["P1"])

    def test_differences_excludes_shared_genes(self):
        """TP53 is shared across all patients — must not appear in any differences."""
        result = compare_modules(self.patients)
        for patient_id in self.patients:
            self.assertNotIn("TP53", result["differences"][patient_id])

    def test_differences_keys_match_all_patients(self):
        """Differences dict must contain an entry for every patient."""
        result = compare_modules(self.patients)
        self.assertEqual(set(result["differences"].keys()), set(self.patients.keys()))

    def test_differences_values_are_sorted(self):
        """Each patient difference list must be alphabetically sorted."""
        result = compare_modules(self.patients)
        for patient_id, genes in result["differences"].items():
            self.assertEqual(genes, sorted(genes))

    # ------------------------------------------------------------------
    # Discriminant genes
    # ------------------------------------------------------------------

    def test_discriminant_genes_are_truly_exclusive(self):
        """Each gene in discriminant_genes must appear in exactly one patient."""
        result = compare_modules(self.patients)
        for patient_id, genes in result["discriminant_genes"].items():
            for gene in genes:
                count = sum(
                    1 for p, g in self.patients.items() if gene in g
                )
                self.assertEqual(
                    count,
                    1,
                    msg=f"{gene} should be exclusive but found in {count} patients",
                )

    def test_discriminant_genes_is_subset_of_differences(self):
        """Discriminant genes must be a subset of the corresponding patient differences."""
        result = compare_modules(self.patients)
        for patient_id, genes in result["discriminant_genes"].items():
            for gene in genes:
                self.assertIn(gene, result["differences"][patient_id])

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    def test_summary_fields_are_present(self):
        """Summary block must contain all expected keys."""
        result = compare_modules(self.patients)
        self.assertIn("intersection_size", result["summary"])
        self.assertIn("union_size", result["summary"])
        self.assertIn("patients_with_discriminant_genes", result["summary"])

    def test_summary_intersection_size_matches_list(self):
        """summary.intersection_size must equal len(intersection)."""
        result = compare_modules(self.patients)
        self.assertEqual(
            result["summary"]["intersection_size"],
            len(result["intersection"]),
        )

    def test_summary_union_size_matches_list(self):
        """summary.union_size must equal len(union)."""
        result = compare_modules(self.patients)
        self.assertEqual(
            result["summary"]["union_size"],
            len(result["union"]),
        )

    def test_summary_patient_count_is_correct(self):
        """patient_count must equal the number of patients provided."""
        result = compare_modules(self.patients)
        self.assertEqual(result["patient_count"], len(self.patients))

    # ------------------------------------------------------------------
    # Edge cases
    # ------------------------------------------------------------------

    def test_two_patients_minimum_case(self):
        """Two patients is the minimum valid input — must not raise."""
        result = compare_modules({
            "P1": ["EGFR", "BRCA1"],
            "P2": ["BRCA1", "TP53"],
        })
        self.assertIn("BRCA1", result["intersection"])
        self.assertEqual(result["patient_count"], 2)

    def test_no_shared_genes_gives_empty_intersection(self):
        """Patients with completely distinct gene sets — intersection must be empty."""
        result = compare_modules({
            "P1": ["EGFR"],
            "P2": ["TP53"],
        })
        self.assertEqual(result["intersection"], [])
        self.assertEqual(result["summary"]["intersection_size"], 0)

    def test_identical_patients_gives_full_intersection(self):
        """Identical gene lists — intersection must equal union."""
        genes = ["EGFR", "BRCA1", "TP53"]
        result = compare_modules({
            "P1": genes,
            "P2": genes,
        })
        self.assertEqual(
            sorted(result["intersection"]),
            sorted(result["union"]),
        )

    def test_identical_patients_have_no_discriminant_genes(self):
        """Identical gene lists — no patient should have discriminant genes."""
        genes = ["EGFR", "BRCA1"]
        result = compare_modules({
            "P1": genes,
            "P2": genes,
        })
        self.assertEqual(result["discriminant_genes"], {})

    def test_single_gene_per_patient(self):
        """Each patient has exactly one unique gene — each must be discriminant."""
        result = compare_modules({
            "P1": ["EGFR"],
            "P2": ["TP53"],
            "P3": ["BRCA1"],
        })
        self.assertEqual(result["intersection"], [])
        self.assertEqual(len(result["discriminant_genes"]), 3)

    def test_large_cohort_runs_without_error(self):
        """Ten patients with overlapping genes — must complete without raising."""
        patients = {
            f"P{i}": [f"GENE_{j}" for j in range(i, i + 5)]
            for i in range(10)
        }
        result = compare_modules(patients)
        self.assertIn("intersection", result)
        self.assertIn("union", result)
        self.assertEqual(result["patient_count"], 10)


class TestCompareModulesInvalid(unittest.TestCase):
    """Tests on invalid or missing input data."""

    def test_single_patient_raises_value_error(self):
        """Only one patient provided — must raise ValueError."""
        with self.assertRaises(ValueError) as ctx:
            compare_modules({"P1": ["EGFR"]})
        self.assertIn("At least two", str(ctx.exception))

    def test_empty_dict_raises_value_error(self):
        """Empty dict provided — must raise ValueError."""
        with self.assertRaises(ValueError):
            compare_modules({})

    def test_empty_gene_list_raises_value_error(self):
        """One patient has an empty gene list — must raise ValueError."""
        with self.assertRaises(ValueError) as ctx:
            compare_modules({"P1": ["EGFR"], "P2": []})
        self.assertIn("empty or invalid", str(ctx.exception))

    def test_non_list_gene_value_raises_value_error(self):
        """A patient's genes given as a string instead of a list — must raise ValueError."""
        with self.assertRaises(ValueError) as ctx:
            compare_modules({"P1": ["EGFR"], "P2": "BRCA1"})
        self.assertIn("empty or invalid", str(ctx.exception))

    def test_none_input_raises(self):
        """None as input — must raise ValueError or AttributeError."""
        with self.assertRaises((ValueError, AttributeError)):
            compare_modules(None)

    def test_patient_with_none_list_raises_value_error(self):
        """A patient mapped to None instead of a list — must raise ValueError."""
        with self.assertRaises(ValueError):
            compare_modules({"P1": ["EGFR"], "P2": None})

    def test_patient_with_integer_list_raises_value_error(self):
        """A patient mapped to an integer — must raise ValueError."""
        with self.assertRaises(ValueError):
            compare_modules({"P1": ["EGFR"], "P2": 42})


if __name__ == "__main__":
    unittest.main()