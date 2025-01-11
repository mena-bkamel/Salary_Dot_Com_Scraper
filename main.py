import csv
import json
import re
from time import sleep
import requests
from requests.exceptions import *
from bs4 import BeautifulSoup


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


def extract_salary_info(job_title, job_city) -> tuple:
    """Extract and return salary information"""
    template = 'https://www.salary.com/research/salary/alternate/{}-salary/{}'

    job_title = job_title.replace(" ", "-").lower()
    url = template.format(job_title, job_city)
    response = get_html(url)

    soup = BeautifulSoup(response.text, 'html.parser')
    pattern = re.compile(r'Occupation')
    script = soup.find('script', {'type': 'application/ld+json'}, string=pattern)
    try:
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

    except AttributeError:
        pass

    else:
        data = (job_title, location, description, ntile_10, ntile_25, ntile_50, ntile_75, ntile_90)
        return data


def main(job_title):
    """Extract salary data from top us cities"""

    with open('largest_cities.csv', newline='') as file:
        reader = csv.reader(file)
        cities = [city for row in reader for city in row]

    salary_data = []
    for city in cities:
        print(f"{city}....")
        result = extract_salary_info(job_title, city)
        if result:
            salary_data.append(result)
            sleep(0.5)

    with open('salary-results.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Title', 'Location', 'Description', 'nTile10', 'nTile25', 'nTile50', 'nTile75', 'nTile90'])
        writer.writerows(salary_data)

    return salary_data


if __name__ == '__main__':

    main('senior accountant')
