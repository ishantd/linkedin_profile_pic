import os
import time
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import click
from tqdm import tqdm
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

CREDS_FILE = 'linkedin_creds.json'

def save_credentials(driver):
    cookies = driver.get_cookies()
    with open(CREDS_FILE, 'w') as f:
        json.dump(cookies, f)

def load_credentials(driver):
    with open(CREDS_FILE, 'r') as f:
        cookies = json.load(f)
    for cookie in cookies:
        driver.add_cookie(cookie)

def create_driver(headless=False):
    options = Options()
    options.add_argument("user-data-dir=.selenium")
    if headless:
        options.add_argument("--headless")
    
    return webdriver.Chrome(options=options)

def login_to_linkedin():
    print("🚀 We'll open LinkedIn for you to log in. This is a one-time process. 🔐")
    input("Press Enter to continue and come back here once you've logged in... 😊")
    
    driver = create_driver()
    
    driver.get("https://www.linkedin.com/login")
    print("🖥️ LinkedIn login page opened. Please log in.")
    input("If you're done logging in, press Enter again... 😊")
    
    save_credentials(driver)
    print("✅ Credentials saved! You're all set for future use. 🎉")
    
    driver.quit()

def get_profile_pictures(usernames, output_folder):
    print(f"🔍 Preparing to get profile pictures for {len(usernames)} users...")
    
    driver = create_driver(headless=True)
    
    driver.get("https://www.linkedin.com")
    load_credentials(driver)
    driver.refresh()

    os.makedirs(output_folder, exist_ok=True)

    for username in tqdm(usernames, desc="Getting profile pictures"):
        try:
            driver.get(f"https://www.linkedin.com/in/{username}/")
            time.sleep(2)  # Wait for page to load

            img_container = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".pv-top-card-profile-picture__container"))
            )
            img_element = img_container.find_element(By.TAG_NAME, "img")
            img_url = img_element.get_attribute("src")

            response = requests.get(img_url)
            content_type = response.headers['content-type']
            extension = content_type.split('/')[-1]

            with open(os.path.join(output_folder, f"{username}.{extension}"), "wb") as f:
                f.write(response.content)
            
        except Exception as e:
            print(f"Error getting profile picture for {username}: {str(e)}")

    driver.quit()

def extract_username(link):
    if "linkedin.com/in/" in link:
        return link.split("linkedin.com/in/")[1].strip('/')
    return link.strip()

@click.command()
@click.option('--usernames', prompt='Enter comma-separated LinkedIn usernames or URLs',
              help='Comma-separated list of LinkedIn usernames or URLs')
@click.option('--output', default=None, help='Output folder for images')
def cli(usernames, output):
    """Get profile pictures for LinkedIn users."""
    username_list = [extract_username(username) for username in usernames.split(',')]
    
    if not output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output = f"linkedin_images_{timestamp}"
    
    if not os.path.exists(CREDS_FILE):
        login_to_linkedin()
    
    get_profile_pictures(username_list, output)

if __name__ == "__main__":
    cli()
