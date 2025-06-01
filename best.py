#!/usr/bin/env python3
import subprocess
import sys
import time
import csv
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 0) install dependencies in venv
subprocess.run([sys.executable, "-m", "pip", "install", "selenium"])

# 1) ChromeDriver + persistent profile settings
chrome_options = Options()
chrome_options.add_argument("user-data-dir=/Users/jake/.config/selenium-profile")
service = Service('/usr/local/bin/chromedriver')

# 2) MANUAL LOGIN STEP
login_driver = webdriver.Chrome(service=service, options=chrome_options)
login_driver.get("https://www.linkedin.com/login")
print("⏳ Please log in to LinkedIn and complete any 2FA in the opened browser.")
input("🔐 Once you’re logged in and see your LinkedIn feed, hit Enter here…")
login_driver.quit()

# 3) keywords to search
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
    """Scroll & click ‘Show more results’ until it’s gone."""
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        try:
            btn = driver.find_element(
                By.XPATH,
                "//button[contains(@aria-label,'Load more results') or contains(., 'Show more results')]"
            )
            driver.execute_script("arguments[0].click();", btn)
            time.sleep(2)
        except NoSuchElementException:
            break

def smart_wait(driver):
    """Wait for at least one profile card, or raise TimeoutException."""
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".org-people-profile-card__profile-info"))
    )
    time.sleep(2)

def scrape_cards(driver, people_url, tag, profiles, expand=False):
    driver.get(people_url)
    try:
        smart_wait(driver)
    except TimeoutException:
        print(f"⏭️ No results for '{tag}'. Skipping.")
        return

    if expand:
        load_all_results(driver)

    cards = driver.find_elements(By.CSS_SELECTOR, ".org-people-profile-card__profile-info")
    for card in cards:
        try:
            name_el = card.find_element(By.CSS_SELECTOR, ".artdeco-entity-lockup__title a")
            profile_url = name_el.get_attribute('href')
            name = name_el.text.strip()
            headline = card.find_element(
                By.CSS_SELECTOR, ".artdeco-entity-lockup__subtitle"
            ).text.strip()
            try:
                mutual = card.find_element(
                    By.CSS_SELECTOR, ".artdeco-entity-lockup__caption"
                ).text.strip()
            except NoSuchElementException:
                mutual = "N/A"

            rec = profiles.setdefault(profile_url, {
                'name': name,
                'headline': headline,
                'mutual_connections': mutual,
                'matched': set(),
                'profile_url': profile_url
            })
            rec['matched'].add(tag)

        except Exception as e:
            print(f"❗ parse error on '{tag}':", e)
            continue

# ——————— main loop ———————
people_urls = input("🏢 Enter LinkedIn company people pages (comma-separated): ").split(",")

# ensure output folder exists
output_dir = "/Users/jake/Desktop/coding/LinkedIn/One_more_time/companies"
os.makedirs(output_dir, exist_ok=True)

for people_url in [u.strip() for u in people_urls if u.strip()]:
    company = people_url.rstrip("/").split("/")[-2]
    profiles = {}

    # 4) scrape 2nd-degree WITHOUT expansion
    base_url = f"{people_url}?facetNetwork=%5B%22S%22%5D"
    print("🔍 2nd-degree:", base_url)
    driver_2nd = webdriver.Chrome(service=service, options=chrome_options)
    scrape_cards(driver_2nd, base_url, "2nd-degree", profiles, expand=False)
    driver_2nd.quit()

    # 5) scrape each keyword WITH expansion
    driver_kw = webdriver.Chrome(service=service, options=chrome_options)
    for term in search_terms:
        url = f"{people_url}?keywords={term.replace(' ', '%20')}"
        print(f"🔍 keyword '{term}':", url)
        scrape_cards(driver_kw, url, term, profiles, expand=True)
    driver_kw.quit()

    # 6) write CSV into the companies/ folder
    fn = os.path.join(output_dir, f"{company}_connections_and_keywords.csv")
    with open(fn, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "Name", "Mutual Connections", "Matched Tags",
            "Headline", "Profile URL"
        ])
        for rec in profiles.values():
            w.writerow([
                rec['name'],
                rec['mutual_connections'],
                "; ".join(sorted(rec['matched'])),
                rec['headline'],
                rec['profile_url']
            ])

    print(f"✅ Done! Results saved to {fn}")
