import csv
import json
import re
from time import sleep

import pandas as pd
import requests
from bs4 import BeautifulSoup


# pip install openpyxl

def get_html(web_url):
    """Fetch the HTML content of a given URL."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    response = requests.get(web_url, headers)
    response.raise_for_status()
    return response


def extract_salary_info(job_title: str, job_city: str) -> tuple | None:
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

    template = 'https://www.salary.com/research/salary/alternate/{}-salary/{}'

    job_title = job_title.replace(" ", "-").lower()
    url = template.format(job_title, job_city)

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


def save_to_excel(file_path, data, headers):
    """
    Save data to an Excel file.

    Args:
        file_path (str): Path to the output Excel file.
        data (list): A list of rows (tuples or lists) to save.
        headers (list): A list of column headers for the Excel file.

    Returns:
        bool: True if the file was saved successfully, False otherwise.
    """
    if not file_path.endswith(".xlsx"):
        file_path += ".xlsx"
    try:
        df = pd.DataFrame(data, columns=headers)
        df.to_excel(file_path, index=False, engine='openpyxl')
        print(f"Results saved to '{file_path}'.")
        return True
    except Exception as e:
        print(f"Error writing to file '{file_path}': {e}")
        return False


def save_to_csv(file_path, data, headers):
    """
    Save data to a CSV file.

    Args:
        file_path (str): Path to the output CSV file.
        data (list): A list of rows (tuples or lists) to save.
        headers (list): A list of column headers for the CSV file.

    Returns:
        bool: True if the file was saved successfully, False otherwise.
    """
    if not file_path.endswith(".csv"):
        file_path += ".csv"
    try:
        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            writer.writerows(data)
        print(f"Results saved to '{file_path}'.")
        return True
    except Exception as e:
        print(f"Error writing to file '{file_path}': {e}")
        return False


def save_to_json(file_path, data, headers):
    """
    Save data to a JSON file.

    Args:
        file_path (str): Path to the output JSON file.
        data (list): A list of rows (tuples or lists) to save.
        headers (list): A list of column headers for the JSON file.

    Returns:
        bool: True if the file was saved successfully, False otherwise.
    """
    if not file_path.endswith(".json"):
        file_path += ".json"
    try:
        # Convert data to a list of dictionaries
        json_data = [dict(zip(headers, row)) for row in data]
        # Save the data to a JSON file
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(json_data, file, indent=4, ensure_ascii=False)
        print(f"Results saved to '{file_path}'.")
        return True
    except Exception as e:
        print(f"Error writing to file '{file_path}': {e}")
        return False


def main(job_title, input_file='largest_cities.csv', output_file='salary_results.csv'):
    """
       Extract salary data for a given job title from the largest US cities.

       Args:
           job_title (str): The job title to extract salary data for (e.g., "Software Engineer").
           input_file (str): Path to the CSV file containing city names (default: 'largest_cities.csv').
           output_file (str): Path to the output CSV file (default: 'salary_results.csv').

       Returns:
           list: A list of salary data tuples.
       """
    if "." in output_file:
        output_file = output_file.split(".")[0]
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

    print(f"Processing {len(cities)} cities for job title '{job_title}'...")

    salary_data = []
    batch_size = 10
    for i, city in enumerate(cities, start=1):
        try:
            print(f"Processing city {i}/{len(cities)}: {city}...")
            result = extract_salary_info(job_title, city)
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
                                                                               headers) or not save_to_json(output_file,
                                                                                                            salary_data,
                                                                                                            headers):
        print("Failed to save results.")
        return []
    return salary_data


if __name__ == '__main__':
    main('senior accountant')

