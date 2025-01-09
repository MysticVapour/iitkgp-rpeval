import sqlite3
import pandas as pd
import json
import torch
from torch.utils.data import Dataset, DataLoader, random_split
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments,
)

# -------------------- #
# 1. Connect to SQLite #
# -------------------- #
# Replace 'your_database.db' with the actual path to your database
conn = sqlite3.connect("db/research_papers.db")

# Load the dataset from SQLite into a Pandas DataFrame
query = "SELECT * FROM labelled_data"
df = pd.read_sql_query(query, conn)

# Close the connection
conn.close()

# ---------------------------- #
# 2. Preprocess and Combine Sections
# ---------------------------- #


# Function to combine sections into structured input
def combine_sections(sections_str):
    """
    Parse the JSON string and combine sections into structured input for the model.
    The input JSON has format {"output": text}
    """
    sections = json.loads(sections_str)
    return sections.get("output", "")


# Apply preprocessing to combine sections
df["text"] = df["sections"].apply(combine_sections)
df["label"] = df["publishable"].astype(int)  # Ensure labels are integers (0 or 1)

# ------------------------- #
# 3. Define a Custom Dataset
# ------------------------- #


class PapersDataset(Dataset):
    """
    PyTorch Dataset for text classification.
    """

    def __init__(self, texts, labels, tokenizer, max_length=512):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = self.texts[idx]
        label = self.labels[idx]

        # Tokenize the text
        encoding = self.tokenizer(
            text,
            max_length=self.max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )

        return {
            "input_ids": encoding["input_ids"].squeeze(),
            "attention_mask": encoding["attention_mask"].squeeze(),
            "labels": torch.tensor(label, dtype=torch.long),
        }


# ------------------------- #
# 4. Load SciBERT and Tokenizer
# ------------------------- #

# Load SciBERT tokenizer and model
model_name = "allenai/scibert_scivocab_uncased"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)

# Prepare the dataset
dataset = PapersDataset(
    texts=df["text"].tolist(), labels=df["label"].tolist(), tokenizer=tokenizer
)

# -------------------- #
# 5. Train/Test Split
# -------------------- #

# Split into training and validation datasets (80-20 split)
train_size = int(0.8 * len(dataset))
val_size = len(dataset) - train_size
train_dataset, val_dataset = random_split(dataset, [train_size, val_size])

# --------------------------- #
# 6. Define Training Arguments
# --------------------------- #

training_args = TrainingArguments(
    output_dir="scibert_output",  # Directory to save model checkpoints
    num_train_epochs=5,  # Number of training epochs
    per_device_train_batch_size=2,  # Adjust based on available GPU memory
    per_device_eval_batch_size=2,
    evaluation_strategy="epoch",  # Evaluate after every epoch
    logging_dir="scibert_logs",  # Directory for logs
    logging_steps=10,  # Log every 10 steps
    save_strategy="epoch",  # Save checkpoint after each epoch
    learning_rate=5e-5,  # Initial learning rate
    weight_decay=0.01,  # Weight decay for regularization
    load_best_model_at_end=True,  # Load the best model after training
)

# ------------------- #
# 7. Train the Model
# ------------------- #

# Initialize the Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    tokenizer=tokenizer,
)

# Start training
trainer.train()

# -------------------- #
# 8. Evaluate the Model
# -------------------- #

# Evaluate on the validation dataset
eval_results = trainer.evaluate()
print("Evaluation Results:", eval_results)

# ---------------------- #
# 9. Save the Fine-Tuned Model
# ---------------------- #
# Save the fine-tuned model and tokenizer
model.save_pretrained("scibert_finetuned")
tokenizer.save_pretrained("scibert_finetuned")
