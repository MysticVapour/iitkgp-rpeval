import os
from PyPDF2 import PdfReader, PdfWriter
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI()


def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    print(f"Extracting text from PDF: {pdf_path}")
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    print(f"Successfully extracted text from PDF: {pdf_path}")
    return text


def mess_up_text_with_gpt(original_text, guidelines):
    """Generate a messed-up version of the text using GPT."""
    print("Sending original text to GPT for modification...")
    prompt = f"""
    Here is a research paper excerpt:
    ---
    {original_text}
    ---
    Using the following guidelines:
    {guidelines}
    Introduce critical issues, such as inappropriate methodologies, incoherent arguments, or unsubstantiated claims, that affect the paper's suitability for publication. 
    The modified version should include one or a mix of these issues, but it should not contain all problems in every case.
    """
    # Use the OpenAI API to process the text
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that augments research papers to be unpublishable.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
    )
    print("GPT modification completed.")
    return completion.choices[0].message.content


def process_papers(input_folder, output_folder, guidelines):
    """Process all papers in a folder and save modified versions."""
    print(f"Processing all papers in folder: {input_folder}")
    for filename in os.listdir(input_folder):
        if filename.endswith(".pdf"):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, f"messed_up_{filename}")

            print(f"Processing file: {filename}")

            # Extract text
            original_text = extract_text_from_pdf(input_path)

            # Modify text using GPT
            messed_up_text = mess_up_text_with_gpt(original_text, guidelines)

            # Read the original PDF to get the page size
            print(f"Reading dimensions from the original PDF: {filename}")
            reader = PdfReader(input_path)
            first_page = reader.pages[0]
            width = first_page.mediabox.width
            height = first_page.mediabox.height
            print(f"Page dimensions for {filename} - Width: {width}, Height: {height}")

            # Create a writer and add a blank page
            print(f"Creating a new PDF for the messed-up paper: {filename}")
            writer = PdfWriter()
            writer.add_blank_page(width=width, height=height)

            # Save the blank page with messed-up text
            with open(output_path, "wb") as output_pdf:
                writer.write(output_pdf)
            print(f"Saved modified paper to: {output_path}")

    print(f"All files processed. Output saved to: {output_folder}")


# Example usage
input_folder = "input_rp"
output_folder = "output_rp"
guidelines = """
Critical issues, such as inappropriate methodologies, incoherent arguments, or
unsubstantiated claims, that affect the suitability of a paper for publication. For
instance, a research paper that applies methodologies or techniques that are not
well-suited to the problem being addressed, without adequate justification or
adaptation to the context, would be considered unsuitable. Similarly, a paper that
presents arguments that are unclear, disorganized, or lack logical coherence, or
one that claims results that appear unusually high or unrealistic without sufficient
evidence or proper validation, would also fall into the "Non-Publishable" category.

Note: Not all problems need to exist in the papers; it needs to be a mix of some or just one.
"""

print("Creating output directory if it does not exist...")
os.makedirs(output_folder, exist_ok=True)
print("Starting processing of research papers...")
process_papers(input_folder, output_folder, guidelines)
print("Processing completed.")
