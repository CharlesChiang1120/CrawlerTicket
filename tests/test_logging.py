import unittest
import os
import logging
from crawler.crawler import setup_logging

class TestLoggingSetup(unittest.TestCase):

    def test_setup_logging(self):
        logger = setup_logging()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        log_dir = os.path.join(script_dir, '..', 'crawler', 'log')
        log_file_path = os.path.join(log_dir, 'crawler.log')

        # Check if log file exists
        self.assertTrue(os.path.exists(log_file_path), "Log file does not exist.")

        # Check if logger is set up correctly
        self.assertEqual(logger.level, logging.WARNING, "Logger level is not set to WARNING.")
        self.assertEqual(len(logger.handlers), 1, "Logger should have one handler.")
        self.assertIsInstance(logger.handlers[0], logging.FileHandler, "Logger handler is not FileHandler.")

if __name__ == '__main__':
    unittest.main()
