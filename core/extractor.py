"""
extractor.py
~~~~~~~~~~~~

Module responsible for extracting and structuring information from an exercise
statement from a PDF file.  Uses the `PyMuPDF` library (also known as ``fitz``)
to read and extract text from PDF pages.  After extraction, it performs a
series of basic heuristics to detect common sections in programming statements
(for example, "Input", "Output" or "Examples").  These heuristics can be
extended or replaced with more sophisticated natural language processing
techniques depending on the complexity of the statements.

The main goal is to return a normalized dictionary containing clearly
differentiated fields.  This dictionary will serve as input to the solution
generation and test case modules.

Dependencies:
 - PyMuPDF (`pip install pymupdf`)
 - re (regular expressions)
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Tuple

import fitz  # PyMuPDF


def extract_pdf_to_text(pdf_path: str) -> str:
    """Extracts all text from a PDF and concatenates it into a single string.

    Uses PyMuPDF (`fitz`) to iterate over PDF pages and obtain text in order.
    This approach is usually sufficient for exercise statements where text is
    presented in a linear fashion.

    :param pdf_path: Path to the PDF file.
    :return: String with the textual content of all pages.
    """
    pdf_path = str(pdf_path)
    doc = fitz.open(pdf_path)
    texts: List[str] = []
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        texts.append(page.get_text("text"))
    return "\n".join(texts)


SECTION_PATTERNS = {
    "statement": re.compile(r"^(?:statement|problem|instructions?)\b", re.IGNORECASE),
    "input": re.compile(r"^input\b", re.IGNORECASE),
    "output": re.compile(r"^output\b", re.IGNORECASE),
    "constraints": re.compile(r"^(?:constraints?|limits?)\b", re.IGNORECASE),
    "examples": re.compile(r"^examples?\b", re.IGNORECASE),
}


def parse_problem_text(text: str) -> Dict:
    """Analyzes a problem statement text and extracts the main sections.

    This function applies simple heuristics: it splits the text by lines and
    groups paragraphs into sections when it finds headers that match predefined
    regular expressions (see `SECTION_PATTERNS`).  Headers include words like
    "Input", "Output", "Constraints" and "Examples".  Everything that doesn't
    fit into these sections is classified as "statement".

    :param text: Complete text of the exercise.
    :return: Dictionary with keys ``statement``, ``input``, ``output``,
      ``constraints`` and ``examples`` (if detected).  Each key contains a list
      of text lines belonging to that section.
    """
    sections: Dict[str, List[str]] = {k: [] for k in SECTION_PATTERNS.keys()}
    current_section = "statement"
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        for name, pattern in SECTION_PATTERNS.items():
            if pattern.match(line):
                current_section = name
                # Remove the header from the line and move to the next
                line = line[len(pattern.match(line).group(0)):].strip()
                break
        sections[current_section].append(line)
    # Normalize empty lists to strings
    return {k: "\n".join(v).strip() for k, v in sections.items() if v}


def extract_and_parse(pdf_path: str) -> Dict:
    """Convenience function to extract a PDF and parse the obtained text.

    :param pdf_path: Path to the PDF file.
    :return: Dictionary structured according to :func:`parse_problem_text`.
    """
    text = extract_pdf_to_text(pdf_path)
    return parse_problem_text(text)