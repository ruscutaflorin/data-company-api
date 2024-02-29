import requests
from bs4 import BeautifulSoup
import csv
import re
import time
def extractCompanyData(url):
    try:
        headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
        }
        response = requests.get(url, headers=headers, allow_redirects=True, timeout=5)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        phoneNumbers = re.findall(r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b', response.text)

        socialMediaLinks = [a['href'] for a in soup.find_all('a', href=True) if
                          a['href'].startswith(('http', 'www')) and 'facebook' in a['href'].lower()]

        addressElement = soup.find(class_='address')
        address = addressElement.text.strip() if addressElement else ''

        companyData = {
            'phone_numbers': phoneNumbers,
            'social_media_links': socialMediaLinks,
            'address': address,
        }

        return companyData

    except requests.exceptions.RequestException as e:
        print(f"Error retrieving data from {url}: {e}")
        return None


def processWebsites(path):
    totalWebsites = 0
    totalDataPoints = 0
    with open(path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            url = row.get('domain')
            if url:
                totalWebsites += 1
                if not url.startswith(('http://', 'https://')):
                    url = f'http://www.{url}'
                data = extractCompanyData(url)
                if data:
                    totalDataPoints += sum(map(len, data.values()))
                    print(f"Data for {url}:", data)

    print(f"\nAnalysis Results:")
    print(f"Total Websites Crawled: {totalWebsites}")
    print(f"Total Data Points Extracted: {totalDataPoints}")

start = time.time()
print(processWebsites("sample-websites.csv"))
end = time.time()
print("The time of execution of above program is :",
      (end-start) * 10**3, "ms")