import json
import pandas as pd
import csv


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
