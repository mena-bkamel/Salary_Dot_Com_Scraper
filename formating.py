import time


class Format:
    def __init__(self, **kwargs):
        self.kw = kwargs
        self.header_row = []
        self.col_definition_db = {}

    def create_dict_template(self, records, header, key_word: str):
        dic = {key_word: ""}

        dic[key_word] = [dict(zip(header, record)) for record in records]
        return dic

    def format_columns_db(self):
        """
        Formats column definitions based on provided data types.
        Converts input types into SQLite-compatible data types.
        """
        for col_name, col_type in self.kw.items():
            self.header_row.append(col_name)

            col_type = col_type.lower()
            if col_type in ("null", "none"):
                self.col_definition_db[col_name] = "NULL"
            elif col_type in ("integer", "int", "boolean"):
                self.col_definition_db[col_name] = "INTEGER"
            elif col_type in ("float", "real"):
                self.col_definition_db[col_name] = "REAL"
            elif col_type in ("text", "str", "string"):
                self.col_definition_db[col_name] = "TEXT"
            elif col_type == "blob":
                self.col_definition_db[col_name] = "BLOB"
            else:
                raise ValueError(f"Unsupported data type for column '{col_name}': {col_type}")
        return self


def time_it(func):
    """
    This function is a decorator that measures the execution time of the
    decorated function.

    Args:
        func: The function to be decorated.

    Returns:
        The decorated function.
    """

    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Function '{func.__name__}' executed in {elapsed_time:.4f} seconds.")
        return result

    return wrapper
