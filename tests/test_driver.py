from selenium import webdriver
import unittest
from crawler.crawler import setup_driver

class TestDriverSetup(unittest.TestCase):

    def test_setup_driver(self):
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
        screen_resolution = "1920x1080"
        driver = setup_driver(user_agent, screen_resolution)
        
        # Check if driver is an instance of WebDriver
        self.assertIsInstance(driver, webdriver.Chrome, "Driver is not an instance of WebDriver.")
        
        driver.quit()

if __name__ == '__main__':
    unittest.main()
