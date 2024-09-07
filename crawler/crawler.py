import os
import random
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import concurrent.futures

# Set up logging
def setup_logging():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    log_dir = os.path.join(script_dir, 'log')
    os.makedirs(log_dir, exist_ok=True)
    log_file_path = os.path.join(log_dir, 'crawler.log')

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.WARNING)
    handler = logging.FileHandler(log_file_path, mode='w')
    handler.setLevel(logging.WARNING)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger

def setup_driver(user_agent, screen_resolution):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    chrome_driver_path = os.path.join(script_dir, '..', 'chromedriver', 'chromedriver.exe')

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    # chrome_options.add_argument("--disable-gpu")
    # chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument(f"user-agent={user_agent}")
    chrome_options.add_argument(f"--window-size={screen_resolution}")

    service = Service(executable_path=chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    return driver

def fetch_event_info(driver, logger):
    driver.get('https://kktix.com/')
    events_dict = {}
    
    try:
        wait = WebDriverWait(driver, 15)
        featured_activities_link = wait.until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[3]/div[2]/div/div/div[2]/div[2]/section[1]/div/ul/li[2]/a'))
        )
        featured_activities_link.click()

        wait.until(EC.presence_of_all_elements_located((By.XPATH, '//ul/li/a')))
        event_elements = driver.find_elements(By.XPATH, '//ul/li/a')

        for event_element in event_elements:
            try:
                activity_info = event_element.find_element(By.XPATH, './/figure/figcaption/div/div/div/div[1]/h2').text
                time = event_element.find_element(By.XPATH, './/div//span[1]').text
                ticket_link = event_element.get_attribute('href')
                image_url = event_element.find_element(By.XPATH, './/figure/img').get_attribute('src')
                events_dict[activity_info] = {'date': time, 'ticketLink': ticket_link, 'image': image_url}
            except Exception as e:
                logger.warning(f'Error extracting event details: {e}')
    
    finally:
        driver.quit()

    return events_dict

def main():
    logger = setup_logging()
    num_threads = 4

    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
    ]

    screen_resolutions = [
        "1280x720",
        "1920x1080",
        "2560x1440",
        "3840x2160",
    ]

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        user_agents_for_threads = random.sample(user_agents, num_threads)
        screen_resolutions_for_threads = random.choices(screen_resolutions, k=num_threads)
        future_to_params = {
            executor.submit(setup_driver, user_agent, screen_resolution): (user_agent, screen_resolution)
            for user_agent, screen_resolution in zip(user_agents_for_threads, screen_resolutions_for_threads)
        }
        results = []

        for future in concurrent.futures.as_completed(future_to_params):
            user_agent, screen_resolution = future_to_params[future]
            try:
                driver = future.result()
                events = fetch_event_info(driver, logger)
                results.append(events)
            except Exception as e:
                logger.warning(f'Error in thread with User-Agent {user_agent} and resolution {screen_resolution}: {e}')
    
    all_events = {}
    for result in results:
        all_events.update(result)

    for activity_info, info in all_events.items():
        print(f'Activity Info: {activity_info}')
        print(f'Date: {info["date"]}')
        print(f'Ticket Link: {info["ticketLink"]}')
        print(f'Image: {info["image"]}')
        print('-' * 40)

if __name__ == '__main__':
    main()