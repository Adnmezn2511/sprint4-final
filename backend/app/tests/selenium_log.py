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
import glob
import shutil

# Récupérer le répertoire du fichier d'exécution
current_dir = os.path.dirname(os.path.abspath(__file__))
download_dir = os.path.join(current_dir, "telechargement_test")

# Créer le dossier de téléchargement s'il n'existe pas
if not os.path.exists(download_dir):
    os.makedirs(download_dir)
    

class TestDownloadFromLog(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Configure browser options
        cls.options = webdriver.ChromeOptions()
        cls.options.add_argument("--headless")  # Remove for visible browser
        prefs = {
            "download.default_directory": download_dir,  # dossier de téléchargement
            "download.prompt_for_download": False,         # pas de demande de confirmation
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        cls.options.add_experimental_option("prefs", prefs)

        # Démarrer le driver avec les options configurées
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
        
        cls.driver.find_element(By.CSS_SELECTOR, ".seed-card:nth-child(1)").click()
        cls.driver.find_element(By.CSS_SELECTOR, ".seed-card:nth-child(2)").click()
        cls.driver.find_element(By.CSS_SELECTOR, ".fa-check").click()
        cls.driver.find_element(By.CSS_SELECTOR, ".search-input").click()
        cls.driver.find_element(By.CSS_SELECTOR, ".search-input").send_keys("c1")
        cls.driver.find_element(By.CSS_SELECTOR, ".seed-card:nth-child(3)").click()
        cls.driver.find_element(By.CSS_SELECTOR, ".fa-check").click()
        cls.driver.find_element(By.ID, "title").click()
        cls.driver.find_element(By.ID, "title").send_keys("title")
        cls.driver.find_element(By.ID, "user").click()
        cls.driver.find_element(By.ID, "user").send_keys("user")
        cls.driver.find_element(By.ID, "steps").send_keys("2")
        cls.driver.find_element(By.ID, "steps").click()
        # self.vars["window_handles"] = self.driver.window_handles
        cls.driver.find_element(By.CSS_SELECTOR, ".mma-button").click()
        # Attendre le chargement
        cls.wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "loading-container")))

        # Vérifier la nouvelle fenêtre
        WebDriverWait(cls.driver, 15).until(lambda d: len(d.window_handles) == 2)
        
        original_window = cls.driver.current_window_handle
        # Basculer vers la nouvelle fenêtre
        new_window = [window for window in cls.driver.window_handles if window != original_window][0]
        cls.driver.switch_to.window(new_window)

        # Vérifier le contenu de la nouvelle fenêtre
        cls.wait.until(EC.title_contains("Graph"))
        plotly_container = cls.wait.until(EC.visibility_of_element_located((By.ID, "plotly-container")))
        # Fermer la nouvelle fenêtre et revenir
        cls.driver.close()
        cls.driver.switch_to.window(original_window)
        
        cls.driver.get("http://localhost:3000/logs")
        time.sleep(1)  # Add small delay if needed for client-side routing

        
    def get_first_history_row(self):
        return self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.log tbody tr:first-child"))
        )

    
    def test_1_download_action(self):
        """Test du téléchargement du ZIP"""
        try:
            # Trouver et cliquer sur le bouton
            download_btn = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".download-btn"))
            )
            download_btn.click()
           # Attendre qu'un fichier .zip apparaisse dans le dossier de téléchargement
            timeout = 30  # secondes
            start_time = time.time()
            fichier_zip = None
            
            while True:
                # Récupérer la liste des fichiers se terminant par .zip
                fichiers = [f for f in os.listdir(download_dir) if f.endswith('.zip')]
                if fichiers:
                    fichier_zip = fichiers[0]
                    break
                time.sleep(1)
                if time.time() - start_time > timeout:
                    raise Exception("Le téléchargement a pris trop de temps.")

            

            
            
        except IndexError:
            self.fail("Aucune entrée d'historique disponible pour le test")

    def test_2_view_action(self):
        """Test de la visualisation du graphique"""
        try:
            original_window = self.driver.current_window_handle
            row = self.get_first_history_row()
            view_btn = row.find_element(By.CLASS_NAME, "view-btn")
            
            view_btn.click()
            
            # Basculer vers la nouvelle fenêtre
            self.wait.until(EC.number_of_windows_to_be(2))
            new_window = [w for w in self.driver.window_handles if w != original_window][0]
            self.driver.switch_to.window(new_window)
            
            # Vérifier le contenu
            self.wait.until(EC.title_contains("Graph"))
            plotly_container = self.wait.until(
                EC.visibility_of_element_located((By.ID, "plotly-container"))
            )
            try:
                self.assertTrue(EC.title_contains("Graph"))


            except TimeoutException as e:
                self.fail(f"URL didn't change {str(e)}")
            
            # Fermer la fenêtre
            self.driver.close()
            self.driver.switch_to.window(original_window)

        except IndexError:
            self.fail("Aucune entrée d'historique disponible pour le test")

    def test_3_delete_action(self):
        """Test de la suppression d'entrée"""
        try:
            row = self.get_first_history_row()
            entry_id = row.find_element(By.TAG_NAME, "td").text
            delete_btn = row.find_element(By.CLASS_NAME, "delete-btn")
            
            delete_btn.click()
            
            # Gérer l'alerte de confirmation
            WebDriverWait(self.driver, 5).until(EC.alert_is_present())
            alert = self.driver.switch_to.alert
            alert.accept()
            
            # Vérifier la disparition de la ligne
            self.wait.until(
                EC.invisibility_of_element_located((By.XPATH, f"//td[text()='{entry_id}']"))
            )
            
            # Vérifier le message si historique vide
            if len(self.driver.find_elements(By.TAG_NAME, "tr")) == 0:
                no_history_msg = self.driver.find_element(By.CLASS_NAME, "no-hist")
                self.assertEqual(no_history_msg.text, "No history available")

        except IndexError:
            self.fail("Aucune entrée d'historique disponible pour le test")

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        # Nettoyer le dossier de téléchargement (supprime tout le dossier)
        if os.path.exists(download_dir):
            shutil.rmtree(download_dir)
            print("Le dossier de téléchargement a été nettoyé.")

if __name__ == "__main__":
    unittest.main()