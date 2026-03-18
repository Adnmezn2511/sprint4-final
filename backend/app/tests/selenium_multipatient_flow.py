import os
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TestMultipatientFlow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.options = webdriver.ChromeOptions()
        cls.options.add_argument("--headless")
        cls.options.add_argument("--no-sandbox")
        cls.options.add_argument("--disable-dev-shm-usage")

        cls.driver = webdriver.Chrome(options=cls.options)
        cls.wait = WebDriverWait(cls.driver, 60)

        cls.script_dir = os.path.dirname(os.path.abspath(__file__))
        cls.zip_path = os.path.join(cls.script_dir, "test2.zip")
        cls.seed_path = os.path.join(cls.script_dir, "test_multipatient_seeds.tsv")

        if not os.path.isfile(cls.zip_path):
            raise FileNotFoundError("test2.zip not found in script directory")
        if not os.path.isfile(cls.seed_path):
            raise FileNotFoundError("test_multipatient_seeds.tsv not found in script directory")

    def test_multipatient_user_flow(self):
        # 1) Arrive on home page and open Multiplex tab
        self.driver.get("http://localhost:3000/")
        multiplex_link = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/multiplex') and contains(., 'Multiplex') ]"))
        )
        multiplex_link.click()
        self.wait.until(EC.url_contains("/multiplex"))

        # 2) Upload multiplex zip
        zip_input = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#m-l-import"))
        )
        zip_input.send_keys(self.zip_path)

        upload_zip_btn = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.m-l-change-couche"))
        )
        upload_zip_btn.click()
        self.wait.until(EC.url_contains("/multiplex/type_choice"))

        # 3) Choose multi-patient mode
        multipatient_button = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Multi-Patient Multiplex') ]"))
        )
        multipatient_button.click()
        self.wait.until(EC.url_contains("/multiplex/seed-load"))

        # 4) Upload multipatient seed file
        seed_input = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#m-s-l-import"))
        )
        seed_input.send_keys(self.seed_path)

        upload_seed_btn = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.m-s-l-seed"))
        )
        upload_seed_btn.click()
        self.wait.until(EC.url_contains("/multiplex/multipatient"))

        # 5) Fill parameters and launch random walk
        user_input = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#user"))
        )
        user_input.clear()
        user_input.send_keys("selenium_user")

        steps_input = self.driver.find_element(By.CSS_SELECTOR, "#steps")
        steps_input.clear()
        steps_input.send_keys("1")

        top_input = self.driver.find_element(By.CSS_SELECTOR, "#top")
        top_input.clear()
        top_input.send_keys("5")

        restart_input = self.driver.find_element(By.CSS_SELECTOR, "#restart")
        restart_input.clear()
        restart_input.send_keys("0.7")

        start_button = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".mmma-button"))
        )
        start_button.click()

        # 6) Observe generated graph list per patient
        self.wait.until(EC.url_contains("/multiplex/multipatient/list"))
        graph_lines = self.wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".mml-graph-line"))
        )

        self.assertGreaterEqual(len(graph_lines), 2, "Expected at least two patient graphs in list")

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()


if __name__ == "__main__":
    unittest.main()
