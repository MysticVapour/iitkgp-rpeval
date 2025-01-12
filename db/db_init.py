import sqlite3

# Connect to SQLite database
conn = sqlite3.connect("db/research_papers.db")
cursor = conn.cursor()

# Create tables
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS labelled_data (
    id TEXT PRIMARY KEY,
    file_name TEXT,
    publishable INTEGER,
    conference TEXT,
    sections TEXT
)
"""
)
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS unlabelled_data (
    id TEXT PRIMARY KEY,
    file_name TEXT,
    sections TEXT
)
"""
)
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS results (
    paper_id TEXT PRIMARY KEY,
    publishable INTEGER,
    conference TEXT,
    rationale TEXT
)
"""
)
conn.commit()
print("Database successfully initialized")
conn.close()
