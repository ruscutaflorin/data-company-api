import requests
from bs4 import BeautifulSoup
import csv
import re
import time
from concurrent.futures import ThreadPoolExecutor
import pandas as pd

def extract_company_data(url):
    try:
        headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
        }
        response = requests.get(url, headers=headers, allow_redirects=True, timeout=5)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        prefix = "http://www."
        modifiedString = url[len(prefix):]

        phone_numbers = re.findall(r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b|\b\(\d{3}\)\s?\d{3}[-.\s]?\d{4}\b', response.text)

        social_media_platforms = [
            'facebook', 'twitter', 'linkedin', 'instagram', 'pinterest',
            'snapchat', 'tumblr', 'reddit', 'youtube', 'vimeo', 'tiktok',
            'whatsapp', 'telegram', 'discord', 'flickr', 'quora', 'medium',
            'yelp', 'googleplus', 'behance'
        ]

        social_media_links = [
            a['href'] for a in soup.find_all('a', href=True) if
            a['href'].startswith(('http', 'www')) and any(
                platform in a['href'].lower() for platform in social_media_platforms)
        ]

        common_address_classes = ['address', 'street-address', 'location', 'adr', 'hq']
        address_element = soup.find(class_=common_address_classes)
        if not address_element:
            address_element = soup.find('address')

        address = address_element.text.strip() if address_element else ''

        company_data = {
            'domain':modifiedString,
            'phone_numbers': phone_numbers,
            'social_media_links': social_media_links,
            'address': address,
        }

        return company_data

    except requests.exceptions.RequestException as e:
        print(f"Error retrieving data from {url}: {e}")
        return None

def process_website(url):
    data = extract_company_data(url)
    if data:
        print(f"Data for {url}:", data)
        return data
    return None

def process_websites_parallel(path):
    total_websites = 0
    total_data_points = 0

    with open(path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        urls = [f'http://www.{row["domain"]}' if not row["domain"].startswith(('http://', 'https://')) else row["domain"] for row in reader]

    extracted_data_list = []
    with ThreadPoolExecutor() as executor:
        for data in executor.map(process_website, urls):
            if data:
                extracted_data_list.append(data)
                total_websites += 1
                total_data_points += sum(map(len, data.values()))

    print(f"\nAnalysis Results:")
    print(f"Total Websites Crawled: {total_websites}")
    print(f"Total Data Points Extracted: {total_data_points}")

    # Save extracted data to a temporary CSV
    temp_csv_path = 'temp_extracted_data.csv'
    with open(temp_csv_path, 'w', newline='', encoding='utf-8') as temp_csv_file:
        fieldnames = ['domain', 'phone_numbers', 'social_media_links', 'address']
        writer = csv.DictWriter(temp_csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for data in extracted_data_list:
            writer.writerow({'domain': data.get('domain', ''),
                             'phone_numbers': ', '.join(data.get('phone_numbers', [])),
                             'social_media_links': ', '.join(data.get('social_media_links', [])),
                             'address': data.get('address', '')})

    original_df = pd.read_csv(path)

    extracted_df = pd.read_csv(temp_csv_path)
    extracted_df.to_csv("extracted.csv", index=False)

    # Merge the two DataFrames on the 'domain' column
    merged_df = pd.merge(original_df, extracted_df, on='domain', how='left')

    merged_df.to_csv('merged_output.csv', index=False)

    # Remove the temporary CSV file
    import os
    os.remove(temp_csv_path)

start = time.time()
process_websites_parallel("sample-websites.csv")
end = time.time()
print("The time of execution of the program is:", (end - start), "seconds")
