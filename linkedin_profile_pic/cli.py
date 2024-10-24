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

def get_profile_pictures(usernames, output_folder, use_saved_creds):
    options = Options()
    options.add_argument("user-data-dir=selenium")
    driver = webdriver.Chrome(options=options)
    
    if use_saved_creds and os.path.exists(CREDS_FILE):
        driver.get("https://www.linkedin.com")
        load_credentials(driver)
        driver.refresh()
    else:
        driver.get("https://www.linkedin.com/login")
        input("Please log in to LinkedIn and press Enter when done...")
        save_credentials(driver)

    os.makedirs(output_folder, exist_ok=True)

    for username in tqdm(usernames, desc="Getting profile pictures"):
        try:
            driver.get(f"https://www.linkedin.com/in/{username}/")
            time.sleep(2)  # Wait for page to load

            img_container = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".pv-top-card-profile-picture__container"))
            )
            # get img element from img container
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

@click.command()
@click.option('--usernames', prompt='Enter comma-separated LinkedIn usernames',
              help='Comma-separated list of LinkedIn usernames')
@click.option('--output', default=None, help='Output folder for images')
@click.option('--use-saved-creds', is_flag=True, help='Use saved credentials if available')
def cli(usernames, output, use_saved_creds):
    """Get profile pictures for LinkedIn users."""
    username_list = [username.strip() for username in usernames.split(',')]
    
    if not output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output = f"linkedin_images_{timestamp}"
    
    if os.path.exists(CREDS_FILE) and not use_saved_creds:
        use_saved_creds = click.confirm("Credentials found. Do you want to use them?", default=True)
    
    get_profile_pictures(username_list, output, use_saved_creds)

if __name__ == "__main__":
    cli()
