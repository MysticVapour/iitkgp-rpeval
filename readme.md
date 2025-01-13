# Kharagpur Data Science Hackathon 2025 Code Submission

## Team : aditiherur

This repository contains the complete setup and solutions for the KDSH 2025 tasks. It includes modules for database management, model training, nearest-neighbor-based classification, and dataset augmentation. Below are the details for setting up the environment, running the code, and understanding the structure of the repository.

---

## Repository Structure

### Root Directory

- **`requirements.txt`**: Contains all required Python dependencies for the project.
- **`.env`**: Environment configuration file (if needed for credentials or settings).
- **`readme.md`**: This README file.
- **`credentials.json`**: Credentials for accessing external resources like Google Drive, if applicable.

### Folders

1. **`db/`**:

   - Scripts to initialize, populate, and update the SQLite database used for storing research paper information.
   - **Key Files**:
     - `db_init.py`: Initializes the database structure.
     - `db_populate.py`: Populates the database using the Pathway connector and research paper files.
     - `db_populate_local.py`: Loads the augmented dataset into the database.
     - `db_rand.py`: Ignore (Internal use for corrupted files.)

2. **`fine_tune_scibert/`**:

   - Contains notebooks and scripts for training and evaluating models for Tasks 1 and 2.
   - **Key Files**:
     - `finetune_chunking.ipynb`: Notebook to fine-tune SciBERT for binary classification (Task 1).
     - `nearest_neighbour.ipynb`: Notebook for embedding-based nearest neighbor classification (Task 2).
     - `plain_scibert.ipynb`: A simpler version of Task 1's model without fine-tuning.
     - `finetune.ipynb`: A simpler version of Task 1's model with fine-tuning but without chunking.

3. **`augment_rp/`**:

   - Scripts for augmenting datasets to create additional labeled data.
   - **Key Files**:
     - `augment_rp.py`: Script to process and augment research papers into publishable and unpublishable papers.
     - **`input_rp/`**: Folder containing raw input research papers.
     - **`output_rp/`**: Folder containing the augmented research papers.

4. **`pw_util/`**:

   - Utility scripts for working with Pathway connectors and vectorization.
   - **Key Files**:
     - `pw_connector.py`: Handles data ingestion using Pathway connectors.
     - `pw_vectorise.py`: Handles embedding generation and vector store operations.

5. **`KDSH_2025_Dataset_Extras/`**:
   - Augmented dataset for KDSH 2025.
   - **Subfolders**:
     - `Publishable`: Research papers collected from previous conferences (2023/24).
     - `Unpublishable`: Artificially created unpublishable papers using Arxiv papers and rewriting techniques.

---

## Setup Instructions

### Dependency Setup

1. Create a Python virtual environment (Python 3.11.5 is recommended):
   ```bash
   python3.11 -m venv .venv
   ```
2. Activate the virtual environment:
   ```bash
   source .venv/bin/activate
   ```
3. Install the required dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```

### Database Setup

1. Initialize the database:
   ```bash
   python3 -m db.db_init
   ```
2. Populate the database with research papers from Google Drive:
   ```bash
   python3 -m db.db_populate
   ```
3. Load augmented files into the database:
   ```bash
   python3 -m db.db_populate_local
   ```

---

## Model Training and Evaluation

### Task 1: Fine-Tune SciBERT for Publishability Classification

Note: On a Macbook Pro with M3 Pro, the model training took 70 minutes
A GPU with CUDA would be recommended for training.
Note: Make sure your OPENAI key is set, check last section in this readme for help.

1. Open the `finetune_chunking.ipynb` notebook in the `fine_tune_scibert/` folder.
2. Run all cells to fine-tune the SciBERT model for binary classification (publishable vs. unpublishable).
3. Review validation results directly in the notebook.
4. **Important**: Run the final cell in this notebook to update the results table, to prepare for the next task.

### Task 2: Nearest-Neighbor Classification

Note: You need not run cell 4, 5, 6 if you're not interested in evaluation

1. Open the `nearest_neighbour.ipynb` notebook in the `fine_tune_scibert/` folder.
2. Run all cells to generate embeddings and perform nearest-neighbor classification for assigning conferences.
3. Review validation results directly in the notebook.
4. **Important**: Run the last cell in this notebook to extract results.csv for final output. (Should show up in `fine_tune_scibert` folder.)

---

## Dataset Augmentation

### Process Overview

1. **Publishable Papers**:

   - Papers were collected from previous year conference websites (2023).
   - Located in the `Publishable` folder within `KDSH_2025_Dataset_Extras/`.

2. **Unpublishable Papers**:
   - Papers were generated by modifying 100 Arxiv papers using careful prompting and rewriting.
   - Located in the `Unpublishable` folder within `KDSH_2025_Dataset_Extras/`.

### Augmentation Steps

Note: Make sure your OPENAI key is set, check last section in this readme for help.

- **Important**: Don't worry about running this if you already have the `KDSH_2025_Dataset_Extras/` folder in your repository. Run this only if you're interested in augmentation.

1. Place raw research papers in the `input_rp` folder within `augment_rp/`.
2. Run the augmentation script:
   ```bash
   python3 augment_rp/augment_rp.py
   ```
3. Processed files will be saved in the `output_rp/` folder.

---

### OpenAI API Key Setup

For some steps, you will need to add your OpenAI API key in your environemnt variables

- For Windows:
  ```bash
  set OPENAI_API_KEY=your-api-key-here
  ```
- For Mac:
  ```bash
  export OPENAI_API_KEY='your-api-key-here'
  ```

Now you can run the code as usual and it will automatically utilize your key.

## Contact

For any issues or questions, contact **adgoch11@gmail.com** or call **+91 7338572728**.
