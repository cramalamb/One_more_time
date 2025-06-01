#!/usr/bin/env python3
import subprocess
import sys
import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# install dependencies in venv
subprocess.run([sys.executable, "-m", "pip", "install", "selenium"])

chrome_options = Options()
chrome_options.add_argument("user-data-dir=/Users/jake/.config/selenium-profile")
service = Service('/usr/local/bin/chromedriver')

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
            btn = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Load more results']")
            driver.execute_script("arguments[0].click();", btn)
            time.sleep(2)
        except NoSuchElementException:
            break

def smart_wait(driver):
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".org-people-profile-card__profile-info"))
    )
    time.sleep(2)

def scrape_cards(driver, people_url, tag, profiles):
    """
    tag is either "2nd-degree" or one of the keywords.
    profiles is a dict mapping profile_url -> record dict.
    """
    driver.get(people_url)
    smart_wait(driver)
    load_all_results(driver)

    cards = driver.find_elements(By.CSS_SELECTOR, ".org-people-profile-card__profile-info")
    for card in cards:
        try:
            name_el = card.find_element(By.CSS_SELECTOR, ".artdeco-entity-lockup__title a")
            profile_url = name_el.get_attribute('href')
            name = name_el.text.strip()

            # pull headline & mutual
            headline = card.find_element(
                By.CSS_SELECTOR, ".artdeco-entity-lockup__subtitle"
            ).text.strip()
            try:
                mutual = card.find_element(
                    By.CSS_SELECTOR, ".artdeco-entity-lockup__caption"
                ).text.strip()
            except NoSuchElementException:
                mutual = "N/A"

            # init or update this profile's record
            rec = profiles.setdefault(profile_url, {
                'name': name,
                'headline': headline,
                'mutual_connections': mutual,
                'matched': set(),
            })
            rec['matched'].add(tag)

        except Exception as e:
            print("❗ parse error:", e)
            continue

# ——————— main loop ———————
people_urls = input("🏢 Enter LinkedIn company people pages, comma-separated: ")\
               .split(",")

for people_url in [u.strip() for u in people_urls if u.strip()]:
    company = people_url.rstrip("/").split("/")[-2]
    profiles = {}

    # 1) scrape all 2nd-degree connections
    base_url = f"{people_url}?facetNetwork=%5B%22S%22%5D"
    print("🔍 2nd-degree:", base_url)
    scrape_cards(
        webdriver.Chrome(service=service, options=chrome_options),
        base_url,
        "2nd-degree",
        profiles
    )

    # 2) scrape each keyword
    driver = webdriver.Chrome(service=service, options=chrome_options)
    for term in search_terms:
        url = f"{people_url}?keywords={term.replace(' ', '%20')}"
        print(f"🔍 keyword '{term}':", url)
        scrape_cards(driver, url, term, profiles)
    driver.quit()

    # 3) write out one row per profile, joining all tags
    fn = f"{company}_connections_and_keywords.csv"
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
                # if you still want to auto-generate an outreach message, you can do it here
                rec.get('profile_url')  # assume you stored it if needed
            ])

    print(f"✅ Done! Results in {fn}")
