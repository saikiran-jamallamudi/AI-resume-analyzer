"""Resume text extraction helpers."""

from io import BytesIO

from docx import Document
import fitz


ALLOWED_EXTENSIONS = {".pdf", ".docx"}
MAX_EXTRACTED_CHARS = 100_000


def extract_resume_text(filename, file_bytes):
    lower = (filename or "").lower()
    stream = BytesIO(file_bytes)

    if lower.endswith(".pdf"):
        try:
            document = fitz.open(stream=stream, filetype="pdf")
            text = "\n".join(page.get_text("text") for page in document)
            document.close()
        except Exception as exc:
            raise ValueError("Could not read this PDF. Make sure it is a valid PDF.") from exc
    elif lower.endswith(".docx"):
        try:
            document = Document(stream)
            parts = [paragraph.text for paragraph in document.paragraphs]
            for table in document.tables:
                for row in table.rows:
                    parts.append(" | ".join(cell.text for cell in row.cells))
            text = "\n".join(parts)
        except Exception as exc:
            raise ValueError("Could not read this DOCX. Make sure it is a valid Word document.") from exc
    else:
        raise ValueError("Unsupported file type. Upload a PDF or DOCX file.")

    text = text.strip()
    if not text:
        raise ValueError(
            "No selectable text was found. This app does not perform OCR; "
            "paste the resume text or upload a text-based PDF/DOCX."
        )
    if len(text) > MAX_EXTRACTED_CHARS:
        text = text[:MAX_EXTRACTED_CHARS]
    return text
