import unittest
import time
import os
import pytest
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import TimeoutException

class TestSelectSeed(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Configure browser options
        cls.options = webdriver.ChromeOptions()
        cls.options.add_argument("--headless")  # Remove for visible browser
        cls.driver = webdriver.Chrome(options=cls.options)
        cls.wait = WebDriverWait(cls.driver, 15)
        
        # Get current script directory
        cls.script_dir = os.path.dirname(os.path.abspath(__file__))
        cls.zip_path = os.path.join(cls.script_dir, "test2.zip")
        
        # Verify test file exists
        if not os.path.isfile(cls.zip_path):
            raise FileNotFoundError("test2.zip not found in script directory")
        
        cls.driver.get("http://localhost:3000/multiplex")
        
        # Locate and interact with file input
        file_input = cls.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
        )
        file_input.send_keys(cls.zip_path)
        
        # Click upload button
        button_xpath = """
        //a[contains(@class, 'm-l-change-couche') 
            and count(.//i[contains(@class, 'fa-chevron-right')]) = 3]
        """

        upload_button = WebDriverWait(cls.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, button_xpath))
        )
        upload_button.click()
        
        # Wait for page transition
        time.sleep(1)  # Add small delay if needed for client-side routing
        
        cls.driver.find_element(By.XPATH, '//*[@id="coucheSelect"]').click()
        #coucheSelect > option:nth-child(2)
        cls.driver.find_element(By.ID, "coucheSelect").click()
        dropdown = cls.driver.find_element(By.ID, "coucheSelect")
        dropdown.find_element(By.XPATH, "//option[. = 'layer1']").click()
        cls.driver.find_element(By.CSS_SELECTOR, ".fa-chevron-right:nth-child(3)").click()
        
        time.sleep(1)  # Add small delay if needed for client-side routing

    def test_fullexec(self):
        # Stocker la fenêtre actuelle
        original_window = self.driver.current_window_handle
        
        self.driver.find_element(By.CSS_SELECTOR, ".seed-card:nth-child(1)").click()
        self.driver.find_element(By.CSS_SELECTOR, ".seed-card:nth-child(2)").click()
        self.driver.find_element(By.CSS_SELECTOR, ".fa-check").click()
        self.driver.find_element(By.CSS_SELECTOR, ".search-input").click()
        self.driver.find_element(By.CSS_SELECTOR, ".search-input").send_keys("c1")
        self.driver.find_element(By.CSS_SELECTOR, ".seed-card:nth-child(3)").click()
        self.driver.find_element(By.CSS_SELECTOR, ".fa-check").click()
        self.driver.find_element(By.ID, "title").click()
        self.driver.find_element(By.ID, "title").send_keys("title")
        self.driver.find_element(By.ID, "user").click()
        self.driver.find_element(By.ID, "user").send_keys("user")
        self.driver.find_element(By.ID, "steps").send_keys("2")
        self.driver.find_element(By.ID, "steps").click()
        # self.vars["window_handles"] = self.driver.window_handles
        self.driver.find_element(By.CSS_SELECTOR, ".mma-button").click()
        # Attendre le chargement
        self.wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "loading-container")))

        # Vérifier la nouvelle fenêtre
        WebDriverWait(self.driver, 15).until(lambda d: len(d.window_handles) == 2)
        
        # Basculer vers la nouvelle fenêtre
        new_window = [window for window in self.driver.window_handles if window != original_window][0]
        self.driver.switch_to.window(new_window)

        # Vérifier le contenu de la nouvelle fenêtre
        self.wait.until(EC.title_contains("Graph"))
        plotly_container = self.wait.until(EC.visibility_of_element_located((By.ID, "plotly-container")))
        try:
            # Vérifier la présence du script Plotly
            plotly_script = self.driver.find_elements(By.XPATH, "//script[contains(@src, 'plotly-latest.min.js')]")
            self.assertTrue(len(plotly_script) > 0, "Plotly script non chargé")


        except TimeoutException as e:
            self.fail(f"URL didn't change {str(e)}")

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

if __name__ == "__main__":
    unittest.main()