import re
from pypdf import PdfReader
import io

def extract_text_from_pdf(pdf_file) -> str:
    """
    Extracts all text from a PDF file.
    pdf_file can be a file path (str) or a file-like object (BytesIO/UploadedFile).
    """
    text = ""
    try:
        reader = PdfReader(pdf_file)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    except Exception as e:
        raise ValueError(f"Failed to extract text from PDF: {str(e)}")
    return text

def clean_text(text: str) -> str:
    """
    Cleans the extracted text by normalizing whitespaces.
    """
    # Replace multiple whitespaces/newlines with a single space
    cleaned = re.sub(r'\s+', ' ', text)
    return cleaned.strip()

def extract_email(text: str) -> str:
    """
    Extracts the first email address found in the text.
    """
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    match = re.search(pattern, text)
    return match.group(0) if match else ""

def extract_phone(text: str) -> str:
    """
    Extracts the first phone number found in the text.
    Supports formats like +1-123-456-7890, (123) 456-7890, 123-456-7890, etc.
    """
    # Look for common phone number patterns
    pattern = r'(?:\+?\d{1,3}[-. ]?)?\(?\d{3}\)?[-. ]?\d{3}[-. ]?\d{4}'
    match = re.search(pattern, text)
    return match.group(0) if match else ""

def extract_candidate_name(text: str) -> str:
    """
    Tries to guess the candidate's name.
    Heuristic: Often the first 2-3 words of the resume text,
    excluding common headers.
    """
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if not lines:
        return "Candidate"
    
    first_line = lines[0]
    # Check if first line contains common resume labels, if so try next
    common_labels = ["resume", "cv", "curriculum vitae", "profile", "summary"]
    if any(label in first_line.lower() for label in common_labels) and len(lines) > 1:
        first_line = lines[1]
        
    # Take words up to 4 words from the line
    words = first_line.split()
    if len(words) >= 1 and len(words) <= 4:
        # Check if they look like a name (alphabetic mainly)
        candidate = " ".join(words)
        if re.match(r'^[a-zA-Z\s\.\-\’]+$', candidate):
            return candidate
            
    return "Candidate"
