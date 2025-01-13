import os
import json
import sqlite3
from pathlib import Path
import pypdf
import logging

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

conn = sqlite3.connect("db/research_papers.db")
cursor = conn.cursor()


def read_pdf(pdf_path):
    try:
        with open(pdf_path, "rb") as file:
            pdf_reader = pypdf.PdfReader(file, strict=False)
            text = []
            for page_num in range(len(pdf_reader.pages)):
                try:
                    page = pdf_reader.pages[page_num]
                    extracted_text = page.extract_text()
                    if extracted_text and not extracted_text.isspace():
                        text.append(extracted_text)
                except Exception as e:
                    logger.warning(f"Could not read page {page_num} in {pdf_path}: {e}")
                    continue
            return " ".join(text) if text else None
    except Exception as e:
        logger.error(f"Error reading PDF {pdf_path}: {e}")
        return None


def process_directory(dir_path, publishable, conference):
    # List of IDs we want to exclude (corrupted files)
    exclude_ids = [
        "2501.02870",
        "2501.02153",
        "2501.02715",
        "2501.02905",
        "2501.03152",
        "2501.02880",
        "2501.02793",
        "2501.02969",
        "2501.02894",
        "2501.03058",
        "2501.02997",
        "2501.01992",
        "2501.03153",
        "2501.03218",
        "2501.02770",
        "2501.02152",
        "2501.03130",
        "2501.00368",
        "2501.03132",
        "2501.02711",
        "2501.02906",
        "2501.03151",
        "2501.02615",
        "2501.03120",
        "2501.02860",
        "2501.02200",
        "2501.02976",
        "2501.03142",
        "2501.02453",
        "2501.03176",
        "2501.00829",
        "2501.02926",
        "2501.02221",
        "2501.02595",
        "2501.02621",
        "2501.03017",
        "2501.02738",
        "2501.03018",
        "2501.03229",
        "2501.03074",
        "2501.03005",
        "2501.03113",
        "2501.02626",
        "2501.02117",
        "2412.20694",
        "2501.02486",
        "2501.03190",
        "2501.02949",
        "2412.20980",
        "2501.02857",
        "2501.01725",
        "2501.02931",
        "2501.03225",
        "2501.03078",
        "2501.02758",
        "2501.03006",
        "2501.02851",
        "2501.02820",
        "2501.03095",
        "3580305.3599533",
        "3580305.3599294",
        "3580305.3599418",
    ]

    results = []
    path = Path(dir_path)

    for pdf_file in path.glob("*.pdf"):
        file_id = str(pdf_file.stem)
        file_name = pdf_file.name

        # Ignore excluded files
        if "messed_up" in file_name:
            paper_id = file_name.split("messed_up_")[1].split("v1")[0]
            if paper_id in exclude_ids:
                logger.info(f"Skipping known corrupted file: {file_name}")
                continue

        text = read_pdf(pdf_file)
        if text:
            sections = json.dumps({"output": text})
            results.append((file_id, file_name, publishable, conference, sections))

    return results


def insert_data(folder_path, publishable, conference):
    print(f"Processing {conference} papers from {folder_path}")
    rows = process_directory(folder_path, publishable, conference)

    cursor.executemany(
        "INSERT OR IGNORE INTO labelled_data (id, file_name, publishable, conference, sections) VALUES (?, ?, ?, ?, ?)",
        rows,
    )
    conn.commit()
    print(f"Inserted {len(rows)} papers for {conference}")


# Process each conference directory
base_path = "KDSH_2025_Dataset_Extras"
conference_mapping = {
    "NeurIPS": ("NeurIPS", 1),
    "CVPR": ("CVPR", 1),
    "KDD": ("KDD", 1),
    "EMNLP": ("EMNLP", 1),
    "TMLR": ("TMLR", 1),
    "Unpublishable": ("NA", 0),
}

# Process all conferences
for folder, (conference, publishable) in conference_mapping.items():
    folder_path = os.path.join(base_path, folder)
    if os.path.exists(folder_path):
        insert_data(folder_path, publishable, conference)
    else:
        print(f"Warning: Directory not found - {folder_path}")

conn.close()
print("Database population completed")
