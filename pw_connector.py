import pathway as pw
import pandas as pd
import PyPDF2
from io import BytesIO

table = pw.io.gdrive.read(
    object_id="1_xFmMlrNDR0wzzPsv6wXXdGz0eX6vaYb",
    service_user_credentials_file="credentials.json",
    mode="static",
    file_name_pattern="*.pdf",
)


# Decode the raw PDF bytes from the Pathway table
def decode_pdf(pdf_bytes):
    pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_bytes))
    text = []
    for page in pdf_reader.pages:
        text.append(page.extract_text())
    return " ".join(text)


# Apply the decoding function using pw.apply
decoded_table = table.select(decoded_data=pw.apply(decode_pdf, table.data))

# Run the computation
pw.run()

# Debug the results
pw.debug.compute_and_print(decoded_table)
