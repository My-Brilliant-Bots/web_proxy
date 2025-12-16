
import os
import re
from datetime import datetime

def read_file_content(file_name):
    """
    Opens a file, reads its entire content into memory, and returns it as a string.
    """
    try:
        with open(file_name, 'r', encoding='utf-8') as f:
            content = f.read()

        chunks = []
        for i in range(0, len(content), 200000):
            chunks.append(content[i:i + 200000])
        return chunks
    except FileNotFoundError:
        print(f"Error: File '{file_name}' not found.")
        return None
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return None

def get_latest_traffic_log_file(directory):
    """
    Queries all files having the format traffic.log-{YYYYMMDD} in the given directory
    and returns the newest/latest filename with its full filepath.
    """
    latest_file = None
    latest_date = None
    log_pattern = re.compile(r"traffic\.log-(\d{8})")

    if not os.path.isdir(directory):
        print(f"Error: Directory '{directory}' not found.")
        return None

    for filename in os.listdir(directory):
        match = log_pattern.match(filename)
        if match:
            file_date_str = match.group(1)
            try:
                file_date = datetime.strptime(file_date_str, "%Y%m%d")
                if latest_date is None or file_date > latest_date:
                    latest_date = file_date
                    latest_file = os.path.join(directory, filename)
            except ValueError:
                # Ignore files with malformed date strings
                continue
    return latest_file


