import sqlite3

# Connect to database
conn = sqlite3.connect("db/research_papers.db")
cursor = conn.cursor()

# IDs to delete
problematic_ids = [
    "3580305.3599533",
    "3580305.3599294",
    "3580305.3599418",
    "3035_Exposing_Limitations_of_L",
    "messed_up_2501.03226v1_modified",
]

# Delete each problematic entry
for paper_id in problematic_ids:
    cursor.execute("DELETE FROM labelled_data WHERE id = ?", (paper_id,))
    print(f"Deleted entry with ID: {paper_id}")

# Commit changes and close connection
conn.commit()
conn.close()
