import os
from PyPDF2 import PdfReader
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
    """Generate a messed-up version of the text using GPT with Markdown styling."""
    print("Sending original text to GPT for modification...")
    prompt = f"""
    Here is a research paper excerpt:
    ---
    {original_text}
    ---
    Using the following guidelines:
    {guidelines}
    Create a modified version of this paper with critical issues introduced. You MUST include ALL sections from the original paper (including abstract, introduction, methodology, results, conclusion, etc.) without omitting any content. Format the text using Markdown:
    - `#` for the main title
    - `##` for section headings (like Abstract, Introduction, etc.)
    - `###` for subsection headings
    - Bullet points (`-`) for lists where applicable
    - **Bold** for emphasized points
    - *Italics* for softer emphasis

    IMPORTANT:
    1. Do NOT omit or skip ANY section from the original paper
    2. The abstract section MUST be included and placed at the beginning
    3. Maintain the same structure and flow as the original paper
    4. Introduce intentional issues in methodologies, arguments, or claims as per guidelines
    5. Make the issues subtle enough that they aren't immediately obvious
    
    Your output should contain all the original text but with strategic modifications that make it unpublishable.
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


from markdown_pdf import MarkdownPdf, Section


def process_papers(input_folder, output_folder, guidelines):
    """Process all papers in a folder and save modified versions as PDF files."""
    print(f"Processing all papers in folder: {input_folder}")
    count = 1
    total = len(os.listdir(input_folder))
    for filename in os.listdir(input_folder):
        print("Printing file", count, " of ", total)
        count += 1
        if filename.endswith(".pdf"):
            input_path = os.path.join(input_folder, filename)
            pdf_output_path = os.path.join(
                output_folder, f"messed_up_{os.path.splitext(filename)[0]}_modified.pdf"
            )

            print(f"Processing file: {filename}")

            # Extract text
            original_text = extract_text_from_pdf(input_path)

            # Modify text using GPT
            messed_up_text = mess_up_text_with_gpt(original_text, guidelines)

            # Convert directly to PDF
            print(f"Converting to PDF: {pdf_output_path}")
            pdf = MarkdownPdf(toc_level=2)
            pdf.add_section(Section(f"{messed_up_text}"))
            pdf.meta["title"] = f"messed_up_paper_{filename}"
            pdf.save(pdf_output_path)

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

Note: Not all problems need not exist in the papers; it needs to be a mix of some or just one.
"""

print("Creating output directory if it does not exist...")
os.makedirs(output_folder, exist_ok=True)
print("Starting processing of research papers...")
process_papers(input_folder, output_folder, guidelines)
print("Processing completed.")
