import sqlite3
import json
from pw_util.pw_vectorise import generate_embedding, fetch_research_papers

DB_PATH = "db/research_papers.db"

# Connect to database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Ensure embedding column exists
try:
    cursor.execute("ALTER TABLE labelled_data ADD COLUMN embedding TEXT;")
except sqlite3.OperationalError:
    print("Column 'embedding' already exists.")

# Update embeddings for each paper
papers = fetch_research_papers()
for paper_id, file_name, sections_json in papers:
    try:
        sections = json.loads(sections_json)
        full_text = " ".join(sections.values())
        embedding = generate_embedding(full_text)
        embedding_json = json.dumps(embedding)  # Convert to JSON for storage

        cursor.execute("UPDATE labelled_data SET embedding = ? WHERE id = ?", (embedding_json, paper_id))
    except Exception as e:
        print(f"Skipping {file_name}: {e}")

conn.commit()
conn.close()
print("Embedding update complete!")
