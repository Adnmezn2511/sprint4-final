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

class TestMultiplexChoicePage(unittest.TestCase):
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

    def test_fullexec(self):
        self.driver.find_element(By.XPATH, '//*[@id="coucheSelect"]').click()
        #coucheSelect > option:nth-child(2)
        self.driver.find_element(By.ID, "coucheSelect").click()
        dropdown = self.driver.find_element(By.ID, "coucheSelect")
        dropdown.find_element(By.XPATH, "//option[. = 'layer1']").click()
        self.driver.find_element(By.CSS_SELECTOR, ".fa-chevron-right:nth-child(3)").click()
        
        # Verify navigation to MultiplexCHOICE page
        try:
            # Vérification supplémentaire
            current_url = self.driver.current_url
            self.assertIn("layer1", current_url)

        except TimeoutException as e:
            self.fail(f"URL didn't change {str(e)}")
    
    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

if __name__ == "__main__":
    unittest.main()