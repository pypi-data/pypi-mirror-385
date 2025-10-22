import csv
import json
import sys
from typing import Optional, Iterator, Dict, Any

from arlas.cli.utils import clean_str, is_int, is_float


def read_ndjson_generator(
    file_path: str,
    max_lines: int = -1
) -> Iterator[Dict[str, Any]]:
    """
    Reads a NDJSON file line by line. Handles each line as a separate JSON object.

    Args:
        file_path (str): Path to the NDJSON file.
        max_lines (int, optional): Maximum number of lines to read. Defaults to -1 (read all).

    Yields:
        Iterator[Dict[str, Any]]: Each parsed JSON object from the file.
    """
    with open(file_path, "rb") as f:
        for i, line in enumerate(f, 1):
            if i > max_lines > -1:
                break
            line = line.strip()
            if not line:  # Skip empty lines
                continue
            try:
                # Parse each line individually as JSON
                yield json.loads(line)
            except json.JSONDecodeError as e:
                print(f"Error parsing line {i}: {e}", file=sys.stderr)
                continue


def read_csv_generator(
    file_path: str,
    max_lines: int = -1,
    delimiter: Optional[str] = None,
    quotechar: Optional[str] = None,
    encoding: str = 'utf-8',
    fields_mapping: dict = {}
) -> Iterator[Dict[str, Any]]:
    """
    Reads a CSV file with headers line by line with efficient memory usage.
    Optimized for large files and designed to work with CSV files that have a header row.

    Args:
        file_path (str): Path to the CSV file.
        max_lines (int, optional): Maximum number of lines to read.
                                   -1 means read all lines. Defaults to -1.
        delimiter (str, optional): Delimiter character. Defaults to None.
        quotechar (str, optional): Character used for quoting fields. Defaults to None.
        encoding (str, optional): File encoding. Defaults to 'utf-8'.
        fields_mapping (dict, optional): ES fields mapping types

    Yields:
        Iterator[Dict[str, Any]]: Each row from the CSV file as a dictionary.
                                   Keys are column names from the header row.
                                   Values are converted to appropriate Python types.

    Raises:
        FileNotFoundError: If the file doesn't exist.
        ValueError: If the file is empty or doesn't have a header row.
    """
    try:
        with open(file_path, mode='r', encoding=encoding, newline='') as f:
            # Pre-read: Detect the file dialect (separator, quotechar) from first lines
            NB_LINES_PREREAD = 5
            sample = "".join([next(f) for _ in range(NB_LINES_PREREAD)])
            dialect = csv.Sniffer().sniff(sample, delimiters=delimiter)
            if quotechar is not None:
                dialect.quotechar = quotechar
            f.seek(0)  # Get back to file beginning

            # Read file
            reader = csv.DictReader(f, skipinitialspace=True, dialect=dialect)

            # Check if file is empty
            if not reader.fieldnames:
                raise ValueError("CSV file is empty or has no header row")

            # Clean columns names
            clean_fields_names = clean_columns_name(list(reader.fieldnames))
            reader.fieldnames = clean_fields_names

            # Iterate rows
            line_count = 0
            for row in reader:
                line_count += 1
                if line_count > max_lines > -1:
                    break

                # Convert empty strings to None and try to convert types
                processed_row = {}
                for key, value in row.items():
                    if value == '':
                        pass
                    if len(fields_mapping) > 0:
                        # Use elastic mapping types
                        if fields_mapping[key] == 'long':
                            processed_row[key] = int(value)
                        elif fields_mapping[key] == 'double':
                            processed_row[key] = float(value)
                        elif fields_mapping[key] in ["geo_shape", "geo_point"]:
                            if value.strip().startswith('{') and value.strip().endswith('}'):
                                try:
                                    geom = json.loads(value)
                                    if not ("type" in geom and "coordinates" in geom):
                                        print(f"Error: Missing geojson keys for field '{key}': {value}")
                                    else:
                                        processed_row[key] = geom
                                except json.JSONDecodeError:
                                    print(f"Error: Invalid JSON for field '{key}': {value}")
                        elif fields_mapping[key] == 'boolean':
                            processed_row[key] = value.lower() == 'true'
                        else:
                            processed_row[key] = value

                    else:
                        # Try type conversions
                        if isinstance(value, str):
                            # Try to convert to int
                            if is_int(value):
                                processed_row[key] = int(value)
                            # Try to convert to float
                            elif is_float(value):
                                processed_row[key] = float(value)
                            # Try to convert to boolean
                            elif value.lower() in ('true', 'false'):
                                processed_row[key] = value.lower() == 'true'
                            else:
                                processed_row[key] = value
                        else:
                            processed_row[key] = value
                yield processed_row

    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except Exception as e:
        raise ValueError(f"Error reading CSV file: {e}")


def get_data_generator(file_path: str, file_type: str = "", max_lines: int = -1, fields_mapping: dict = {}):
    """
    Returns a generator to read data from a file based on its type.

    This function automatically selects the appropriate reader based on the file type
    and returns a generator that yields one document at a time, making it memory-efficient
    for large files.

    Args:
        file_path (str):
            Path to the input file.

        file_type (str):
            Type of the file. Can be one of "json" for JSON/NDJSON files or "csv" for CSV files
            If None, the function will attempt to detect the type from the file extension.

        max_lines (int, optional):
            Maximum number of lines to read from the file.
            If -1, reads all lines in the file. Defaults to -1.

        fields_mapping (dict, optional):
            ES fields mapping types

    Returns:
        Iterator[dict]:
            A generator that yields one document at a time from the file.
            Each document is a dictionary representing one record from the file.

    Raises:
        TypeError:
            If the file type is not supported or cannot be determined.
        FileNotFoundError:
            If the specified file does not exist.
    """
    if file_type == "json" or file_path.endswith(".json") or file_path.endswith(".ndjson"):
        data_generator = read_ndjson_generator(file_path=file_path, max_lines=max_lines)
    elif file_type == "csv" or file_path.endswith(".csv"):
        data_generator = read_csv_generator(file_path=file_path, max_lines=max_lines, delimiter=",",
                                            fields_mapping=fields_mapping)
    else:
        raise TypeError(f"Unknow type for file: '{file_path}'")
    return data_generator


def clean_columns_name(columns_name: list[str]) -> list[str]:
    """
    Clean a list of column names to make them valid identifiers.
    If a column name is modified, a warning message is printed to indicate the change.

    Args:
        columns_name (list[str]): List of column names to clean (can contain accents, spaces, or special characters).

    Returns:
        list[str]: List of cleaned column names, without accents, and with underscores replacing non-alphanumeric chars.
    """
    cleaned_columns_names = []
    for orig_name in columns_name:
        clean_name = clean_str(orig_name)
        if clean_name != orig_name:
            print(f"Warning: Column '{orig_name}' has been renamed '{clean_name}' to prevent any encoding issues")
        cleaned_columns_names.append(clean_name)
    return cleaned_columns_names
