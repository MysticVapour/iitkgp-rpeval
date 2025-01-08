import sqlite3
import json
import torch
import pathway as pw
from transformers import AutoTokenizer, AutoModel
from pathway.xpacks.llm.vector_store import VectorStore

# Load SciBERT model
tokenizer = AutoTokenizer.from_pretrained("allenai/scibert_scivocab_uncased")
model = AutoModel.from_pretrained("allenai/scibert_scivocab_uncased")

# Connect to SQLite database
DB_PATH = "db/research_papers.db"

# Define function to generate SciBERT embeddings
def generate_embedding(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    embedding = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
    return embedding.tolist()

# Load research papers from database
def fetch_research_papers():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, file_name, sections FROM labelled_data")
    papers = cursor.fetchall()
    conn.close()
    return papers

# Create a Pathway table for research papers
def create_pathway_table():
    papers = fetch_research_papers()
    rows = []
    
    for paper_id, file_name, sections_json in papers:
        try:
            sections = json.loads(sections_json)  # Parse JSON
            abstract = sections.get("abstract", "")  # Extract abstract
            full_text = " ".join(sections.values())  # Combine all sections
            embedding = generate_embedding(full_text)  # Generate embedding
            
            rows.append((paper_id, file_name, full_text, embedding))
        except Exception as e:
            print(f"Skipping paper {file_name} due to error: {e}")
    
    # Convert to Pathway table
    table = pw.debug.table_from_pandas(rows, schema=["id", "file_name", "text", "embedding"])
    return table

# Create Pathway Vector Store
def create_vector_store():
    pathway_table = create_pathway_table()
    vector_store = VectorStore(index_columns="embedding")
    vector_store.index(pathway_table)
    return vector_store
