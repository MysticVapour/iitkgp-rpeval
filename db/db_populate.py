import os
import json
import sqlite3
from dotenv import load_dotenv
import pathway as pw
from pw_util.pw_connector import create_table, process_table

# Load environment variables
load_dotenv()

# Folder IDs
FOLDER_IDS = {
    "unlabelled": os.getenv("UNLABELLED_FOLDER_ID"),
    "non_publishable": os.getenv("NONPUBLISHABLE_FOLDER_ID"),
    "non_publishable_extra": os.getenv("NONPUBLISHABLE_EXTRA_FOLDER_ID"),
    "cvpr": os.getenv("CVPR_PUB_FOLDER_ID"),
    "cvpr_extra": os.getenv("CVPR_EXTRA_FOLDER_ID"),
    "emnlp": os.getenv("EMNLP_PUB_FOLDER_ID"),
    "emnlp_extra": os.getenv("EMNLP_EXTRA_FOLDER_ID"),
    "kdd": os.getenv("KDD_PUB_FOLDER_ID"),
    "kdd_extra": os.getenv("KDD_EXTRA_FOLDER_ID"),
    "neurips": os.getenv("NEURIPS_PUB_FOLDER_ID"),
    "neurips_extra": os.getenv("NEURIPS_EXTRA_FOLDER_ID"),
    "tmlr": os.getenv("TMLR_PUB_FOLDER_ID"),
    "tmlr_extra": os.getenv("TMLR_EXTRA_FOLDER_ID"),
}

# Connect to SQLite database
conn = sqlite3.connect("db/research_papers.db")
cursor = conn.cursor()


# Helper function to convert a Pathway table to a Pandas DataFrame
def table_to_pandas(table):
    df = pw.debug.table_to_pandas(table)
    df = df.reset_index()  # Reset the index
    df = df.drop(["index"], axis=1)  # Drop the index column
    return df


def insert_data(folder_type, folder_id, publishable=None, conference=None):
    print(f"DEBUG: Processing folder_type='{folder_type}', folder_id='{folder_id}'")
    table = create_table(folder_id)
    print("DEBUG: Created Pathway table")

    structured_table = process_table(table)
    print("DEBUG: Processed Pathway table into structured_table")

    pw.run()
    print("DEBUG: Pathway computation completed")

    # Convert the Pathway table to a Pandas DataFrame
    df = table_to_pandas(structured_table)
    print(f"DEBUG: Converted structured_table to Pandas DataFrame with {len(df)} rows")

    rows = []
    for _, row in df.iterrows():
        # Convert file_id and file_name to strings (if they aren't already)
        file_id = str(row["file_id"])
        file_name = str(row["file_name"])
        print(f"DEBUG: Processing row: file_id={file_id}, file_name={file_name}")

        # Convert sections to a dictionary and then JSON
        try:
            sections_dict = json.loads(str(row["sections"]))  # Convert Json to dict
            # print(f"DEBUG: Converted sections to dictionary: {sections_dict}")
        except Exception as e:
            print(f"DEBUG: Failed to convert sections to dictionary: {e}")
            continue  # Skip this row if conversion fails

        sections_json = json.dumps(sections_dict)  # Serialize to JSON
        print(f"DEBUG: Serialized sections to JSON")

        if folder_type == "labelled":
            rows.append(
                (
                    file_id,
                    file_name,
                    publishable,
                    conference,
                    sections_json,
                )
            )
        elif folder_type == "unlabelled":
            rows.append((file_id, file_name, sections_json))

    # Insert rows into the database
    if folder_type == "labelled":
        cursor.executemany(
            "INSERT OR IGNORE INTO labelled_data (id, file_name, publishable, conference, sections) VALUES (?, ?, ?, ?, ?)",
            rows,
        )
        print(f"DEBUG: Inserted {len(rows)} rows into labelled_data")
    elif folder_type == "unlabelled":
        cursor.executemany(
            "INSERT OR IGNORE INTO unlabelled_data (id, file_name, sections) VALUES (?, ?, ?)",
            rows,
        )
        print(f"DEBUG: Inserted {len(rows)} rows into unlabelled_data")

    conn.commit()
    print(f"DEBUG: Committed changes to the database for folder_type='{folder_type}'")


# Insert data for labelled papers
insert_data("labelled", FOLDER_IDS["non_publishable"], publishable=0, conference="NA")
insert_data("labelled", FOLDER_IDS["cvpr"], publishable=1, conference="CVPR")
insert_data("labelled", FOLDER_IDS["emnlp"], publishable=1, conference="EMNLP")
insert_data("labelled", FOLDER_IDS["kdd"], publishable=1, conference="KDD")
insert_data("labelled", FOLDER_IDS["neurips"], publishable=1, conference="NeurIPS")
insert_data("labelled", FOLDER_IDS["tmlr"], publishable=1, conference="TMLR")

# Insert data for unlabelled papers
insert_data("unlabelled", FOLDER_IDS["unlabelled"])

# Close the database connection
conn.close()
