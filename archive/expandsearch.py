import subprocess
import sys
import time
import csv
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Ensure required packages are installed
required_packages = ["selenium"]
for package in required_packages:
    subprocess.run([sys.executable, "-m", "pip", "install", package])

# Set up ChromeDriver with persistent profile
chrome_options = Options()
chrome_options.add_argument("user-data-dir=/Users/jake/.config/selenium-profile")
service = Service('/usr/local/bin/chromedriver')

# Log into LinkedIn
driver = webdriver.Chrome(service=service, options=chrome_options)
driver.get("https://www.linkedin.com/login")
print("⏳ Please log in to LinkedIn and complete 2FA in the opened browser. You have 10 seconds...")
time.sleep(10)
input("🔐 Press Enter once you have completed login and 2FA...")
driver.quit()

# Ask for multiple LinkedIn company people page URLs
urls_input = input("🏢 Enter LinkedIn company people page URLs separated by commas: ")
people_urls = [url.strip() for url in urls_input.split(",") if url.strip()]

# Define search keywords
search_terms = [
    "university of chicago booth",
    "coast guard academy",
    "mckinsey",
    "u.s. coast guard",
    "navy",
    "army",
    "marines",
    "air force",
    "breakline"
]

def load_all_results(driver):
    while True:
        try:
            show_more = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Load more results']")
            driver.execute_script("arguments[0].click();", show_more)
            time.sleep(2)
        except NoSuchElementException:
            break

def smart_wait(driver):
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".org-people-profile-card__profile-info"))
        )
        time.sleep(2)  # Add 2 extra second after the element appears
    except Exception as e:
        print("Smart wait timeout: ", e)

def search_keyword(driver, term, people_url, company_name, results, processed_profiles):
    filtered_url = f"{people_url}?keywords={term.replace(' ', '%20')}"
    print(f"🔍 Searching for keyword '{term}': {filtered_url}")
    driver.get(filtered_url)
    smart_wait(driver)
    load_all_results(driver)

    cards = driver.find_elements(By.CSS_SELECTOR, ".org-people-profile-card__profile-info")

    for card in cards:
        try:
            name_element = card.find_element(By.CSS_SELECTOR, ".artdeco-entity-lockup__title a")
            name = name_element.text.strip()
            profile_url = name_element.get_attribute('href')

            if profile_url in processed_profiles:
                continue

            headline_element = card.find_element(By.CSS_SELECTOR, ".artdeco-entity-lockup__subtitle")
            headline = headline_element.text.strip()

            try:
                mutual_element = card.find_element(By.CSS_SELECTOR, ".artdeco-entity-lockup__caption")
                mutual_connections = mutual_element.text.strip()
            except:
                mutual_connections = "N/A"

            first_name = name.split()[0]
            message = f"Hi {first_name}, I saw your background in {term}, so I wanted to reach out and learn more about your role at {company_name.capitalize()}."

            results.append([name, mutual_connections, term, headline, message, profile_url])
            processed_profiles.add(profile_url)
        except Exception as e:
            print(f"Error parsing card: {e}")
            continue

for people_url in people_urls:
    company_name = people_url.rstrip('/').split('/')[-2]
    results = []
    processed_profiles = set()

    driver = webdriver.Chrome(service=service, options=chrome_options)

    base_filtered_url = f"{people_url}?facetNetwork=%5B\"S\"%5D"
    print(f"🔍 Searching for all 2nd-degree connections: {base_filtered_url}")
    driver.get(base_filtered_url)
    smart_wait(driver)
    load_all_results(driver)

    cards = driver.find_elements(By.CSS_SELECTOR, ".org-people-profile-card__profile-info")
    for card in cards:
        try:
            name_element = card.find_element(By.CSS_SELECTOR, ".artdeco-entity-lockup__title a")
            name = name_element.text.strip()
            profile_url = name_element.get_attribute('href')

            if profile_url in processed_profiles:
                continue

            headline_element = card.find_element(By.CSS_SELECTOR, ".artdeco-entity-lockup__subtitle")
            headline = headline_element.text.strip()

            try:
                mutual_element = card.find_element(By.CSS_SELECTOR, ".artdeco-entity-lockup__caption")
                mutual_connections = mutual_element.text.strip()
            except:
                mutual_connections = "N/A"

            first_name = name.split()[0]
            message = f"Hi {first_name}, I saw we are 2nd-degree connections and I wanted to learn more about your role at {company_name.capitalize()}."

            results.append([name, mutual_connections, "", headline, message, profile_url])
            processed_profiles.add(profile_url)
        except Exception as e:
            print(f"Error parsing card: {e}")
            continue

    for term in search_terms:
        search_keyword(driver, term, people_url, company_name, results, processed_profiles)

    filename = f"{company_name}_connections_and_keywords.csv"
    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Mutual Connections", "Matched Keyword", "Headline", "Outreach Message", "Profile URL"])
        writer.writerows(results)

    print(f"✅ Done! Results saved to {filename}")
    driver.quit()
