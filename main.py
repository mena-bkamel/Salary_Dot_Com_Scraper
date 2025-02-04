import csv
import json
import re
from time import sleep

import requests
from bs4 import BeautifulSoup

from formating import Format
from scrape_search_result import SearchResult
from store_data import create_db, insert_records, save_to_csv, save_to_json, save_to_excel
from test import time_it

job_titles = [
    "Python Developer",
    "Data Scientist",
    "Software Engineer",
    "Machine Learning Engineer",
    "Business Analyst",
    "Marketing Manager",
    "Product Manager",
    "Project Manager",
    "Full Stack Developer",
    "Cloud Architect",
    "User Experience (UX) Designer",
    "Data Analyst",
    "Data Engineer",
    "Natural Language Processing (NLP) Engineer",
    "Computer Vision Engineer",
    "Business Intelligence (BI) Analyst"
]


def save_to_sqlite3_db(data: list[tuple]):
    dtype_format = Format(job_title="str", job_location="str", job_description="str", nTile10="float", nTile25="float",
                          nTile50="float", nTile75="float", nTile90="float").format_columns_db()
    columns_db = dtype_format.col_definition_db
    db_name, table_name, columns_list = create_db(columns=columns_db)
    insert_records(db_name, table_name, columns_list, data)

def get_html(web_url):
    """Fetch the HTML content of a given URL."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    response = requests.get(web_url, headers)
    response.raise_for_status()
    return response


def extract_salary_info(job_title: str, job_city: str, job_url) -> tuple | None:
    """
        Extract salary information for a given job title and city from Salary.com.

        Args:
            job_title (str): The job title to search for (e.g., "senior developer").
            job_city (str): The city to search in (e.g., "new york").

        Returns:
            tuple: (job_title, location, description, ntile_10, ntile_25, ntile_50, ntile_75, ntile_90)
            or None if data cannot be extracted.
        """

    if not job_title or not job_city:
        print("Error: Both job_title and job_city are required.")
        return None

    url = f"{job_url}/{job_city}"

    try:
        response = get_html(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        pattern = re.compile(r'Occupation', re.IGNORECASE)
        script = soup.find('script', {'type': 'application/ld+json'}, string=pattern)

        if not script:
            print("Error: Could not find the script tag containing salary data.")
            return None

        # Parse the JSON data
        json_raw = script.contents[0]
        json_data = json.loads(json_raw)

        # extract salary data
        job_title = json_data.get('name', 'N/A')
        location = json_data.get('occupationLocation', [{}])[0].get('name', 'N/A')
        description = json_data.get('description', 'N/A')

        salary_data = json_data.get('estimatedSalary', [{}])[0]
        ntile_10 = salary_data.get('percentile10', 'N/A')
        ntile_25 = salary_data.get('percentile25', 'N/A')
        ntile_50 = salary_data.get('median', 'N/A')
        ntile_75 = salary_data.get('percentile75', 'N/A')
        ntile_90 = salary_data.get('percentile90', 'N/A')

        return job_title, location, description, ntile_10, ntile_25, ntile_50, ntile_75, ntile_90

    except requests.RequestException as e:
        print(f"HTTP request failed: {e}")
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON from the script tag.")
    except KeyError as e:
        print(f"Error: Missing key in JSON data - {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return None


@time_it
def main(job_titles: list, input_file='largest_cities.csv', output_file='salary_results'):
    """
       Extract salary data for a given job title from the largest US cities.

       Args:
           job_title (str): The job title to extract salary data for (e.g., "Software Engineer").
           input_file (str): Path to the CSV file containing city names (default: 'largest_cities.csv').
           output_file (str): Path to the output CSV file (default: 'salary_results.csv').

       Returns:
           list: A list of salary data tuples.
       """

    try:
        with open(input_file, newline='', encoding="utf-8") as file:
            reader = csv.reader(file)
            cities = [city.strip() for row in reader for city in row if city.strip()]

    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        return []

    except Exception as e:
        print(f"Error reading input file: {e}")
        return []

    salary_data = []
    batch_size = 10

    for job in job_titles[:3]:
        link = SearchResult().scrape_url_structure(job).first_link
        print(f"Processing {len(cities)} cities for job title '{job}'...")

        for i, city in enumerate(cities[:3], start=1):
            try:
                print(f"Processing city {i}/{len(cities)}: {city}...")
                result = extract_salary_info(job, city, link)
                if result:
                    salary_data.append(result)
            except Exception as e:
                print(f"Error processing city '{city}': {e}")

            if i % batch_size == 0:
                print(f"Sleeping after processing {batch_size} cities...")
                sleep(2)
            else:
                sleep(0.5)

    headers = ['Title', 'Location', 'Description', 'nTile10', 'nTile25', 'nTile50', 'nTile75', 'nTile90']
    if not save_to_csv(output_file, salary_data, headers) or not save_to_excel(output_file, salary_data,
                                                                               headers) or not save_to_json(
        output_file,
        salary_data,
        headers
    ):
        print("Failed to save results.")
        return []

    return salary_data


if __name__ == '__main__':
    record = main(job_titles)
    save_to_sqlite3_db(record)
