import csv
import json
import re
from time import sleep
import requests
from requests.exceptions import *
from bs4 import BeautifulSoup

template = 'https://www.salary.com/research/salary/alternate/{}-salary/{}'

# build the url based on search criteria
position = 'senior-accountant'
city = 'charlotte-nc'


def get_html(web_url):
    error = True

    while error:
        try:
            res = requests.get(web_url)
        except ConnectTimeout:
            get_html(web_url)

        else:
            error = False
            return res


url = template.format(position, city)


response = get_html(url)

soup = BeautifulSoup(response.text, 'html.parser')
pattern = re.compile(r'Occupation')
script = soup.find('script', {'type': 'application/ld+json'}, string=pattern)

json_raw = script.contents[0]
json_data = json.loads(json_raw)

job_title = json_data['name']
location = json_data['occupationLocation'][0]['name']
description = json_data['description']

ntile_10 = json_data['estimatedSalary'][0]['percentile10']
ntile_25 = json_data['estimatedSalary'][0]['percentile25']
ntile_50 = json_data['estimatedSalary'][0]['median']
ntile_75 = json_data['estimatedSalary'][0]['percentile75']
ntile_90 = json_data['estimatedSalary'][0]['percentile90']

salary_data = (job_title, location, description, ntile_10, ntile_25, ntile_50, ntile_75, ntile_90)
print(salary_data)


def extract_salary_info(job_title, job_city):
    """Extract and return salary information"""
    template = 'https://www.salary.com/research/salary/alternate/{}-salary/{}'

    # build the url based on search criteria
    url = template.format(job_title, job_city)

    # request the raw html .. check for valid request
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return None
    except requests.exceptions.ConnectionError:
        return None

    # parse the html and extract json data
    soup = BeautifulSoup(response.text, 'html.parser')
    pattern = re.compile(r'Occupation')
    script = soup.find('script', {'type': 'application/ld+json'}, text=pattern)
    json_raw = script.contents[0]
    json_data = json.loads(json_raw)

    # extract salary data
    job_title = json_data['name']
    location = json_data['occupationLocation'][0]['name']
    description = json_data['description']

    ntile_10 = json_data['estimatedSalary'][0]['percentile10']
    ntile_25 = json_data['estimatedSalary'][0]['percentile25']
    ntile_50 = json_data['estimatedSalary'][0]['median']
    ntile_75 = json_data['estimatedSalary'][0]['percentile75']
    ntile_90 = json_data['estimatedSalary'][0]['percentile90']

    data = (job_title, location, description, ntile_10, ntile_25, ntile_50, ntile_75, ntile_90)
    return data


with open('largest_cities.csv', newline='') as file:
    reader = csv.reader(file)
    # a reader typically returns each row as a list... so I need to flatten the list to make a single list
    cities = [city for row in reader for city in row]

print(cities[:10])

salary_data = []

for city in cities:
    result = extract_salary_info('senior-accountant', city)
    if result:
        salary_data.append(result)
        sleep(0.5)

with open('salary-results.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Title', 'Location', 'Description', 'nTile10', 'nTile25', 'nTile50', 'nTile75', 'nTile90'])
    writer.writerows(salary_data)

# print the first 5 records
for row in salary_data[:5]:
    print(row)


def main(job_title):
    """Extract salary data from top us cities"""

    # get the list of largest us cities
    with open('largest_cities.csv', newline='') as f:
        reader = csv.reader(f)
        # a reader typically returns each row as a list... so I need to flatten the list to make a single list
        cities = [city for row in reader for city in row]

    # extract salary data for each city
    salary_data = []
    for city in cities:
        result = extract_salary_info(job_title, city)
        if result:
            salary_data.append(result)
            sleep(0.5)

    # save data to csv file
    with open('salary-results.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Title', 'Location', 'Description', 'nTile10', 'nTile25', 'nTile50', 'nTile75', 'nTile90'])
        writer.writerows(salary_data)

    return salary_data
