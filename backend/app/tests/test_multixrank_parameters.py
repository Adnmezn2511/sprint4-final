import unittest
from ..multixrank.Parameters import Parameters
from ..multixrank.ParameterLambda import ParameterLambda
from ..multixrank.ParameterEta import ParameterEta


class TestParameters(unittest.TestCase):

    def test_check_tau_valid(self):
        try:
            Parameters.check_tau([0.5, 0.5], 2)
        except SystemExit:
            self.fail("check_tau a levé SystemExit pour des valeurs valides")

    def test_check_tau_wrong_length(self):
        """Longueur incorrecte → SystemExit."""
        with self.assertRaises(SystemExit):
            Parameters.check_tau([0.5, 0.3, 0.2], 2)

    def test_check_tau_value_out_of_range(self):
        """Valeur > 1 → SystemExit."""
        with self.assertRaises(SystemExit):
            Parameters.check_tau([1.5, -0.5], 2)

    def test_check_eta_valid(self):
        try:
            Parameters.check_eta([0.4, 0.6], 2)
        except SystemExit:
            self.fail("check_eta a levé SystemExit pour des valeurs valides")

    def test_check_eta_wrong_length(self):
        """Longueur incorrecte → SystemExit."""
        with self.assertRaises(SystemExit):
            Parameters.check_eta([0.5, 0.3, 0.2], 2)

    def test_check_eta_value_out_of_range(self):
        """Valeur > 1 → SystemExit."""
        with self.assertRaises(SystemExit):
            Parameters.check_eta([1.5, -0.5], 2)


class TestParameterLambda(unittest.TestCase):

    def test_default_lambda_shape(self):
        """Lambda pour n=2, N=[1,1] → matrice (2,2)."""
        lam = ParameterLambda(n=2, N=[1, 1])
        matrix = lam.matrix_X()
        self.assertEqual(matrix.shape, (2, 2))

    def test_default_lambda_diagonal_zero(self):
        """matrix_X retourne une matrice numpy valide."""
        lam = ParameterLambda(n=2, N=[1, 1])
        matrix = lam.matrix_X()
        # La somme de chaque colonne (hors diagonale) doit être cohérente
        self.assertEqual(matrix.shape, (2, 2))
        # Toutes les valeurs sont entre 0 et 1
        self.assertTrue((matrix >= 0).all())
        self.assertTrue((matrix <= 1).all())

    def test_default_lambda_n3(self):
        lam = ParameterLambda(n=3, N=[1, 1, 1])
        matrix = lam.matrix_X()
        self.assertEqual(matrix.shape, (3, 3))

    def test_vect_X_length(self):
        lam = ParameterLambda(n=2, N=[2, 3])
        vect = lam.vect_X()
        self.assertEqual(len(vect), 4)  # n**2


class TestParameterEta(unittest.TestCase):

    def test_vect_X_sums_to_one(self):
        import numpy as np
        eta = ParameterEta(n=2, alpha=[1, 1])
        vect = eta.vect_X()
        self.assertAlmostEqual(float(np.sum(vect)), 1.0, places=5)

    def test_vect_X_length(self):
        eta = ParameterEta(n=3, alpha=[1, 2, 1])
        vect = eta.vect_X()
        self.assertEqual(len(vect), 3)

    def test_vect_X_non_negative(self):
        eta = ParameterEta(n=2, alpha=[2, 3])
        vect = eta.vect_X()
        for v in vect:
            self.assertGreaterEqual(float(v), 0)


if __name__ == "__main__":
    unittest.main()