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

# Navigate to the people page with 2nd-degree connection filter
filtered_url = f"{people_url}?facetNetwork=%5B\"S\"%5D"  # 'S' denotes 2nd-degree connections on LinkedIn
print(f"🔍 Navigating to filtered 2nd-degree connections: {filtered_url}")
driver.get(filtered_url)
time.sleep(10)  # Allow extra time for page content to load

# Collect results
results = []

# Find all profile cards
cards = driver.find_elements(By.CSS_SELECTOR, ".org-people-profile-card__profile-info")

for card in cards:
    try:
        name_element = card.find_element(By.CSS_SELECTOR, ".artdeco-entity-lockup__title a")
        name = name_element.text.strip()
        profile_url = name_element.get_attribute('href')

        headline_element = card.find_element(By.CSS_SELECTOR, ".artdeco-entity-lockup__subtitle")
        headline = headline_element.text.strip()

        # Attempt to find connection degree (e.g., "2nd")
        try:
            connection_element = card.find_element(By.CSS_SELECTOR, ".artdeco-entity-lockup__badge")
            connection_degree = connection_element.text.strip()
        except:
            connection_degree = "N/A"

        first_name = name.split()[0]
        message = f"Hi {first_name}, I saw we are 2nd-degree connections and I wanted to learn more about your role at {company_name.capitalize()}."

        results.append([name, connection_degree, headline, message, profile_url])
    except Exception as e:
        print(f"Error parsing card: {e}")
        continue

# Save to CSV
filename = f"{company_name}_2nd_degree_connections.csv"
with open(filename, "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Name", "Connection Degree", "Headline", "Outreach Message", "Profile URL"])
    writer.writerows(results)

print(f"✅ Done! Results saved to {filename}")
driver.quit()
