import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock
import networkx as nx

from app.itRWR_controller import run_itRWR_multipatient, extract_modules_from_graph


class TestRunItRWR(unittest.TestCase):

    def _make_mock_fig(self):
        fig = MagicMock()
        fig.to_dict.return_value = {"data": [], "layout": {}}
        return fig

    @patch("app.itRWR_controller.shutil.rmtree")
    @patch("app.itRWR_controller.create_zip")
    @patch("app.itRWR_controller.GraphHistory")
    @patch("app.itRWR_controller.get_layer_names")
    @patch("app.itRWR_controller.GraphVisualizer")
    @patch("app.itRWR_controller.MultiplexGraph")
    @patch("app.itRWR_controller.CommunityProcessor")
    @patch("app.itRWR_controller.generate_config")
    @patch("os.makedirs")
    @patch("os.path.exists", return_value=True)
    @patch("os.chdir")
    def test_run_itRWR_returns_expected_tuple(
        self, mock_chdir, mock_exists, mock_makedirs,
        mock_gen_config, mock_cp_cls, mock_mg_cls,
        mock_gv_cls, mock_get_layer_names,
        mock_gh, mock_create_zip, mock_rmtree
    ):
        from app.itRWR_controller import run_itRWR

        mock_cp = MagicMock()
        mock_cp.missing_seeds = []
        mock_cp_cls.return_value = mock_cp

        graph = nx.DiGraph()
        mock_mg = MagicMock()
        mock_mg.get_graph.return_value = (graph, ["1"])
        mock_mg_cls.return_value = mock_mg

        mock_fig = self._make_mock_fig()
        mock_gv = MagicMock()
        mock_gv.create_interactive_graph.return_value = mock_fig
        mock_gv_cls.return_value = mock_gv

        mock_get_layer_names.return_value = {"1": "Genes"}

        mock_record = MagicMock()
        mock_record.id = 42
        mock_gh.objects.create.return_value = mock_record

        with tempfile.TemporaryDirectory() as tmpdir:
            fig, returned_graph, layers, modules = run_itRWR(
                log_zip_dir=tmpdir,
                input_zip_path=os.path.join(tmpdir, "input.zip"),
                result_dir=tmpdir,
                liste_seeds=["GeneA"],
                nb_iterations=1,
                nb_nodes_per_layer=5,
                restart=0.7,
                user="alice",
                title="Test"
            )

        self.assertEqual(fig, mock_fig)
        self.assertIs(returned_graph, graph)
        self.assertEqual(layers, ["1"])
        self.assertEqual(modules, [])

    @patch("app.itRWR_controller.shutil.rmtree")
    @patch("app.itRWR_controller.create_zip")
    @patch("app.itRWR_controller.GraphHistory")
    @patch("app.itRWR_controller.get_layer_names")
    @patch("app.itRWR_controller.GraphVisualizer")
    @patch("app.itRWR_controller.MultiplexGraph")
    @patch("app.itRWR_controller.CommunityProcessor")
    @patch("app.itRWR_controller.generate_config")
    @patch("os.makedirs")
    @patch("os.path.exists", return_value=True)
    @patch("os.chdir")
    def test_run_itRWR_saves_expected_parameters(
        self, mock_chdir, mock_exists, mock_makedirs,
        mock_gen_config, mock_cp_cls, mock_mg_cls,
        mock_gv_cls, mock_get_layer_names,
        mock_gh, mock_create_zip, mock_rmtree
    ):
        from app.itRWR_controller import run_itRWR

        mock_cp = MagicMock()
        mock_cp.missing_seeds = ["MissingGene"]
        mock_cp_cls.return_value = mock_cp

        graph = nx.DiGraph()
        mock_mg = MagicMock()
        mock_mg.get_graph.return_value = (graph, ["1"])
        mock_mg_cls.return_value = mock_mg

        mock_fig = self._make_mock_fig()
        mock_gv = MagicMock()
        mock_gv.create_interactive_graph.return_value = mock_fig
        mock_gv_cls.return_value = mock_gv
        mock_get_layer_names.return_value = {"1": "Genes"}

        mock_record = MagicMock()
        mock_record.id = 7
        mock_gh.objects.create.return_value = mock_record

        with tempfile.TemporaryDirectory() as tmpdir:
            run_itRWR(
                log_zip_dir=tmpdir,
                input_zip_path=os.path.join(tmpdir, "input.zip"),
                result_dir=tmpdir,
                liste_seeds=["GeneB"],
                nb_iterations=2,
                nb_nodes_per_layer=10,
                restart=0.5,
                user="bob",
                title="Titre"
            )

        mock_gh.objects.create.assert_called_once()
        call_kwargs = mock_gh.objects.create.call_args[1]
        self.assertEqual(call_kwargs["user"], "bob")
        self.assertEqual(call_kwargs["title"], "Titre")
        self.assertIn("Iterations", call_kwargs["parameters"])
        self.assertEqual(call_kwargs["parameters"]["Missing seeds"], ["MissingGene"])
        self.assertIn("Modules", call_kwargs["parameters"])
        self.assertIn("Modules Count", call_kwargs["parameters"])


class TestItRWRController(unittest.TestCase):
    @patch("app.itRWR_controller.run_itRWR")
    def test_run_itRWR_multipatient_calls_run_itRWR_for_each_patient(self, mock_run_itRWR):
        log_zip_dir = "/tmp/log_zip"
        input_zip_path = "/tmp/input.zip"
        result_dir = "/tmp/result"
        dico_patient_seeds = {
            "BR664F": ["GENE1", "GENE2"],
            "BR101A": ["GENE3"],
        }
        nb_iterations = 5
        nb_nodes_per_layer = 10
        restart = 0.7
        user = "test_user"

        fig_br664f = MagicMock()
        fig_br101a = MagicMock()

        graph_1 = nx.DiGraph()
        graph_2 = nx.DiGraph()

        modules_br664f = [{"module_id": "M1", "size": 2, "nodes": ["A", "B"]}]
        modules_br101a = [{"module_id": "M1", "size": 1, "nodes": ["C"]}]

        mock_run_itRWR.side_effect = [
            (fig_br664f, graph_1, ["1"], modules_br664f),
            (fig_br101a, graph_2, ["1"], modules_br101a),
        ]

        with patch("app.itRWR_controller.merge_patient_graphs") as mock_merge, \
             patch("app.itRWR_controller.GraphVisualizer") as mock_gv_cls, \
             patch("app.itRWR_controller.create_fused_modules_interactive_graph") as mock_module_fig_gen, \
             patch("app.itRWR_controller.get_layer_names_from_zip", return_value={}), \
             patch("app.itRWR_controller.tempfile.NamedTemporaryFile") as mock_tmp, \
             patch("app.itRWR_controller.os.path.exists", return_value=False):
            mock_merged_g = nx.DiGraph()
            mock_merge.return_value = (mock_merged_g, ["1"])

            mock_gv = MagicMock()
            mock_merged_fig = MagicMock()
            mock_gv.create_interactive_graph.return_value = mock_merged_fig
            mock_gv_cls.return_value = mock_gv

            mock_merged_modules_fig = MagicMock()
            mock_module_fig_gen.return_value = (mock_merged_modules_fig, [])

            tmp_context = MagicMock()
            tmp_context.__enter__.return_value = MagicMock(name="/tmp/merged.html")
            tmp_context.__exit__.return_value = False
            mock_tmp.return_value = tmp_context

            figs, merged_fig, merged_modules_fig = run_itRWR_multipatient(
                log_zip_dir=log_zip_dir,
                input_zip_path=input_zip_path,
                result_dir=result_dir,
                dico_patient_seeds=dico_patient_seeds,
                nb_iterations=nb_iterations,
                nb_nodes_per_layer=nb_nodes_per_layer,
                restart=restart,
                user=user,
            )

        self.assertEqual(mock_run_itRWR.call_count, 2)
        self.assertIn("BR664F", figs)
        self.assertIn("BR101A", figs)
        self.assertEqual(figs["BR664F"], {"figure": fig_br664f, "modules": modules_br664f})
        self.assertEqual(figs["BR101A"], {"figure": fig_br101a, "modules": modules_br101a})
        self.assertIs(merged_fig, mock_merged_fig)
        self.assertIs(merged_modules_fig, mock_merged_modules_fig)

    @patch("app.itRWR_controller.run_itRWR")
    def test_run_itRWR_multipatient_skips_empty_seed_patients(self, mock_run_itRWR):
        fig = MagicMock()
        graph = nx.DiGraph()
        modules = [{"module_id": "M1", "size": 1, "nodes": ["GENE3"]}]
        mock_run_itRWR.return_value = (fig, graph, ["1"], modules)

        result, merged, merged_modules = run_itRWR_multipatient(
            log_zip_dir="/tmp/log_zip",
            input_zip_path="/tmp/input.zip",
            result_dir="/tmp/result",
            dico_patient_seeds={"BR664F": [], "BR101A": ["GENE3"]},
            nb_iterations=5,
            nb_nodes_per_layer=10,
            restart=0.7,
            user="test_user",
        )

        self.assertEqual(mock_run_itRWR.call_count, 1)
        self.assertIn("BR101A", result)
        self.assertNotIn("BR664F", result)
        self.assertEqual(result["BR101A"], {"figure": fig, "modules": modules})
        self.assertIsNone(merged)
        self.assertIsNone(merged_modules)

    @patch("app.itRWR_controller.run_itRWR")
    def test_run_itRWR_multipatient_raises_when_all_patients_have_empty_seeds(self, mock_run_itRWR):
        with self.assertRaises(ValueError) as exc:
            run_itRWR_multipatient(
                log_zip_dir="/tmp/log_zip",
                input_zip_path="/tmp/input.zip",
                result_dir="/tmp/result",
                dico_patient_seeds={"BR664F": [], "BR101A": []},
                nb_iterations=5,
                nb_nodes_per_layer=10,
                restart=0.7,
                user="test_user",
            )

        self.assertEqual(str(exc.exception), "No patients with seeds provided.")
        mock_run_itRWR.assert_not_called()

    @patch("app.itRWR_controller.run_itRWR")
    def test_run_itRWR_multipatient_raises_when_no_patient_provided(self, mock_run_itRWR):
        with self.assertRaises(ValueError) as exc:
            run_itRWR_multipatient(
                log_zip_dir="/tmp/log_zip",
                input_zip_path="/tmp/input.zip",
                result_dir="/tmp/result",
                dico_patient_seeds={},
                nb_iterations=5,
                nb_nodes_per_layer=10,
                restart=0.7,
                user="test_user",
            )

        self.assertEqual(str(exc.exception), "No patient seeds provided.")
        mock_run_itRWR.assert_not_called()


class TestExtractModulesFromGraph(unittest.TestCase):
    def test_extract_modules_from_directed_graph(self):
        graph = nx.DiGraph()
        graph.add_edge(("A", "1"), ("B", "1"))
        graph.add_edge(("B", "1"), ("A", "1"))
        graph.add_edge(("C", "1"), ("D", "1"))
        graph.add_edge(("D", "1"), ("C", "1"))

        graph.nodes[("A", "1")]["label"] = "A"
        graph.nodes[("B", "1")]["label"] = "B"
        graph.nodes[("C", "1")]["label"] = "C"
        graph.nodes[("D", "1")]["label"] = "D"

        modules = extract_modules_from_graph(graph)

        self.assertEqual(len(modules), 2)
        self.assertEqual(modules[0]["size"], 2)
        self.assertIn("nodes", modules[0])
        self.assertIn("module_id", modules[0])

    def test_extract_modules_from_empty_graph(self):
        graph = nx.DiGraph()
        modules = extract_modules_from_graph(graph)
        self.assertEqual(modules, [])


if __name__ == "__main__":
    unittest.main()
