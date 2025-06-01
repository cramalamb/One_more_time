import subprocess
import sys
import os
import csv
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Ensure required packages are installed
required_packages = ["beautifulsoup4", "selenium", "lxml"]
for package in required_packages:
    subprocess.run([sys.executable, "-m", "pip", "install", package])

# Set up ChromeDriver with persistent profile
chrome_options = Options()
chrome_options.add_argument("user-data-dir=/Users/jake/.config/selenium-profile")
service = Service('/usr/local/bin/chromedriver')
browser = webdriver.Chrome(service=service, options=chrome_options)

# Log into LinkedIn
browser.get("https://www.linkedin.com/login")
print("⏳ Please log in to LinkedIn and complete 2FA in the opened browser. You have 10 seconds...")
time.sleep(10)
input("🔐 Press Enter once you have completed login and 2FA...")

# Ask for LinkedIn company people page URL
people_url = input("🏢 Enter the LinkedIn company people page URL (e.g., https://www.linkedin.com/company/example/people/): ")
company_name = people_url.rstrip('/').split('/')[-2]

# Define background filters
search_terms = [
    "university of chicago booth",
    "coast guard academy",
    "mckinsey",
    "u.s. coast guard",
    "navy",
    "army",
    "marines",
    "air force"
]

# Collect results
results = []

for term in search_terms:
    print(f"🔍 Searching for: {term}")
    search_url = f"{people_url}?keywords={term.replace(' ', '%20')}"
    browser.get(search_url)
    time.sleep(2)  # Reduced sleep for faster performance

    soup = BeautifulSoup(browser.page_source, 'lxml')
    cards = soup.select(".org-people-profile-card__profile-info")

    for card in cards:
        name_tag = card.find('div', class_='artdeco-entity-lockup__title')
        headline_tag = card.find('div', class_='artdeco-entity-lockup__subtitle')
        link_tag = card.find('a', class_='app-aware-link')

        name = name_tag.get_text(strip=True) if name_tag else "Unknown"
        headline = headline_tag.get_text(strip=True) if headline_tag else "Unknown"
        profile_url = link_tag['href'] if link_tag and link_tag.has_attr('href') else "Unknown"

        message = f"Hi {name.split()[0]}, I saw your background in {term}, so I wanted to reach out and learn more about your role at {company_name.capitalize()}."
        results.append([name, profile_url, term, headline, message])

# Save to CSV
filename = f"{company_name}_quick_filter_results.csv"
with open(filename, "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Name", "Profile URL", "Matched Term", "Headline", "Outreach Message"])
    writer.writerows(results)

print(f"✅ Done! Results saved to {filename}")
