import csv
import json
import sqlite3
import pandas as pd


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


def create_db(db_name: str = "salary_results.db", table_name="salary", columns: dict = None):
    """
       Create a database and a table with specified columns.

       Parameters:
       - db_name: Name of the database file (default: "file.db").
       - table_name: Name of the table to create (default: "Product").
       - columns: A dictionary where keys are column names and values are their SQL data types.
                  Example: {"product_name": "TEXT NOT NULL", "price": "REAL", "num_reviews": "TEXT"}
       """
    if not columns:
        print("Error: The 'columns' parameter is required to define the table structure. "
              "It should be a dictionary like this example:")
        print({
            "product_name": "TEXT NOT NULL",
            "price": "REAL",
            "num_reviews": "TEXT",
            "url": "TEXT",
            "date": "TEXT"
        })
        return

    column_definitions = ", ".join([f"{col_name} {col_type}" for col_name, col_type in columns.items()])
    column_definitions = f"id INTEGER PRIMARY KEY AUTOINCREMENT, {column_definitions}"
    if not db_name.endswith(".db"):
        db_name = db_name.replace(" ", "_") + ".db"

    table_name = table_name.replace(' ', '_').lower()
    try:
        with sqlite3.connect(db_name) as conn:

            cursor = conn.cursor()
            cursor.execute(f'''CREATE TABLE IF NOT EXISTS 
                    "{table_name}" (
                        {column_definitions}
                        )''')
            conn.commit()
            print(f"Database '{db_name}' and table '{table_name}' created successfully.")

            return db_name, table_name, [col_name for col_name in columns]

    except sqlite3.Error as err:
        print(f"Error creating database or table: {err}")


def insert_records(db_name: str, table_name, columns_names: list, records: list[tuple]):
    """
    Insert a list of tuples into the specified database table.

    Parameters:
    - db_name: Name of the database file.
    - table_name: Name of the table where records will be inserted.
    - records: A list of tuples, where each tuple represents a row of data.
    """
    db_name = db_name.lower()
    if not db_name.endswith(".db"):
        db_name = db_name.replace(" ", "_") + ".db"

    table_name = table_name.replace(' ', '_')

    try:
        with sqlite3.connect(db_name) as conn:
            cursor = conn.cursor()
            col_names = ", ".join(columns_names)
            placeholders = ", ".join(["?" for value in columns_names])
            query = f"INSERT INTO '{table_name}' ({col_names}) VALUES ({placeholders})"
            cursor.executemany(query, records)
            conn.commit()

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
