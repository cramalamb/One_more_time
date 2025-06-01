import subprocess
import sys
import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Ensure required packages are installed
required_packages = ["selenium"]
for package in required_packages:
    subprocess.run([sys.executable, "-m", "pip", "install", package])

# Set up ChromeDriver with persistent profile
chrome_options = Options()
chrome_options.add_argument("user-data-dir=/Users/jake/.config/selenium-profile")
service = Service('/usr/local/bin/chromedriver')
driver = webdriver.Chrome(service=service, options=chrome_options)

# Log into LinkedIn
driver.get("https://www.linkedin.com/login")
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
    driver.get(search_url)
    time.sleep(10)  # Allow extra time for page content to load

    # Find all profile cards
    cards = driver.find_elements(By.CSS_SELECTOR, ".org-people-profile-card__profile-info")

    for card in cards:
        try:
            name_element = card.find_element(By.CSS_SELECTOR, ".artdeco-entity-lockup__title a")
            name = name_element.text.strip()
            profile_url = name_element.get_attribute('href')

            headline_element = card.find_element(By.CSS_SELECTOR, ".artdeco-entity-lockup__subtitle")
            headline = headline_element.text.strip()

            first_name = name.split()[0]
            message = f"Hi {first_name}, I saw your background in {term}, so I wanted to reach out and learn more about your role at {company_name.capitalize()}."

            results.append([name, term, headline, message, profile_url])
        except Exception as e:
            print(f"Error parsing card: {e}")
            continue

# Save to CSV
filename = f"{company_name}_quick_filter_results.csv"
with open(filename, "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Name", "Matched Term", "Headline", "Outreach Message", "Profile URL"])
    writer.writerows(results)

print(f"✅ Done! Results saved to {filename}")
driver.quit()
