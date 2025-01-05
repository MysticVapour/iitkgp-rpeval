import pathway as pw
import PyPDF2
from io import BytesIO
import re


# Function to create a Pathway table for a given folder ID
def create_table(folder_id):
    return pw.io.gdrive.read(
        object_id=folder_id,
        service_user_credentials_file="credentials.json",
        mode="static",
        file_name_pattern="*.pdf",
        with_metadata=True,
    )


# Function to decode PDF content
def decode_pdf(pdf_bytes):
    try:
        pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_bytes))
        text = []
        for page in pdf_reader.pages:
            text.append(page.extract_text())
        return " ".join(text)
    except Exception as e:
        return f"Error decoding PDF: {str(e)}"


# Function to extract structured sections from text
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


# Function to process a Pathway table
def process_table(table):
    decoded_table = table.select(
        file_id=table._metadata["id"],
        file_name=table._metadata["name"],
        raw_text=pw.apply(decode_pdf, table.data),
    )
    structured_table = decoded_table.select(
        file_id=decoded_table.file_id,
        file_name=decoded_table.file_name,
        sections=pw.apply(extract_sections, decoded_table.raw_text),
    )
    return structured_table
