import pathway as pw
import PyPDF2
from io import BytesIO
from dotenv import load_dotenv
import json
import os

load_dotenv()

# Function to extract structured sections from text
from openai import OpenAI

client = OpenAI()


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


def extract_sections(text):

    # sections = {
    #     "abstract": "",
    #     "introduction": "",
    #     "methodology": "",
    #     "results": "",
    #     "discussion": "",
    #     "conclusion": "",
    # }

    # json_template = """{"abstract": "", "introduction": "", "methodology": "", "results": "", "discussion": "", "conclusion": ""}"""

    # prompt = (
    #     "You are an expert in research papers. Extract the following sections from the given text: "
    #     "Abstract, Introduction, Methodology, Results, Discussion, and Conclusion. "
    #     "If a section is missing, leave it blank. Return the output as a JSON object of this format strictly: "
    #     f"{json_template}\n\n"
    #     f"Text: {text}"
    # )

    # try:
    #     # Use the OpenAI API to process the text
    #     completion = client.chat.completions.create(
    #         model="gpt-4o-mini",
    #         messages=[
    #             {
    #                 "role": "system",
    #                 "content": "You are a helpful assistant for research paper analysis.",
    #             },
    #             {"role": "user", "content": prompt},
    #         ],
    #         response_format={"type": "json_object"},
    #         temperature=0,
    #     )

    #     # Parse the response to extract sections
    #     gpt_response = completion.choices[0].message.content
    #     sections = json.loads(gpt_response)

    # except Exception as e:
    #     print(f"Error using GPT for section extraction: {e}")

    # return sections
    return {"output": str(text)}


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
