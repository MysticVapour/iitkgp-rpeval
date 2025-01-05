import pathway as pw
import PyPDF2
from io import BytesIO
import re
from dotenv import load_dotenv
import os

load_dotenv()
NONPUBLISHABLE_FOLDER_ID = os.getenv("NONPUBLISHABLE_FOLDER_ID")

# Step 1: Read PDF files from GDrive folder
table = pw.io.gdrive.read(
    object_id=NONPUBLISHABLE_FOLDER_ID,
    service_user_credentials_file="credentials.json",
    mode="static",
    file_name_pattern="*.pdf",
    with_metadata=True,  # Include file metadata
)


# Step 2: Decode the raw PDF bytes and extract text
def decode_pdf(pdf_bytes):
    try:
        pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_bytes))
        text = []
        for page in pdf_reader.pages:
            text.append(page.extract_text())
        return " ".join(text)
    except Exception as e:
        return f"Error decoding PDF: {str(e)}"


# Step 3: Extract structured sections using regex
def extract_sections(text):
    sections = {
        "abstract": "",
        "introduction": "",
        "methodology": "",
        "results": "",
        "discussion": "",
        "conclusion": "",
    }
    try:
        text = re.sub(r"\n+", "\n", text)  # Normalize line breaks

        # Extract sections using case-insensitive regex
        sections["abstract"] = (
            re.search(
                r"(?i)(?<=abstract).*?(?=\n1\s|introduction|methods|methodology)",
                text,
                re.DOTALL,
            )
            .group(0)
            .strip()
        )
        sections["introduction"] = (
            re.search(
                r"(?i)(introduction).*?(?=\n1\s|methods|methodology|results)",
                text,
                re.DOTALL,
            )
            .group(0)
            .strip()
        )
        sections["methodology"] = (
            re.search(
                r"(?i)(methods|methodology).*?(?=\n1\s|results|discussion)",
                text,
                re.DOTALL,
            )
            .group(0)
            .strip()
        )
        sections["results"] = (
            re.search(
                r"(?i)(results).*?(?=\n1\s|discussion|conclusion)", text, re.DOTALL
            )
            .group(0)
            .strip()
        )
        sections["discussion"] = (
            re.search(r"(?i)(discussion).*?(?=\n1\s|conclusion)", text, re.DOTALL)
            .group(0)
            .strip()
        )
        sections["conclusion"] = (
            re.search(r"(?i)(conclusion).*", text, re.DOTALL).group(0).strip()
        )
    except AttributeError:
        pass  # Gracefully handle missing sections
    except Exception as e:
        print(f"Error extracting sections: {e}")
    return sections


# Step 4: Apply decoding and extraction functions to all files in the folder
decoded_table = table.select(
    file_id=table._metadata["id"],  # Unique identifier for each file
    file_name=table._metadata["name"],  # File name for debugging/logging
    mime_type=table._metadata["mimeType"],  # MIME type for validation
    modified_time=table._metadata["modifiedTime"],  # Last modification time
    raw_text=pw.apply(decode_pdf, table.data),  # Decoded text for each file
)

structured_table = decoded_table.select(
    file_id=decoded_table.file_id,  # Preserve unique file ID
    file_name=decoded_table.file_name,  # Preserve file name for readability
    mime_type=decoded_table.mime_type,  # Preserve MIME type
    modified_time=decoded_table.modified_time,  # Preserve modification time
    sections=pw.apply(
        extract_sections, decoded_table.raw_text
    ),  # Extract structured sections for each file
)

pw.run()

# Step 6: Debug the structured results
print("DEBUGGING TABLE OUTPUT:")
pw.debug.compute_and_print(structured_table)
