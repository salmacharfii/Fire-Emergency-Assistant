from pypdf import PdfReader                # reads PDF files and extracts text page by page
from config import PDF_DIR                 # the data/pdfs folder defined in config.py


def load_pdfs():                           # returns one dictionary per PDF page
    pages = []                             # collects all pages from all PDFs
    for pdf_path in sorted(PDF_DIR.rglob("*.pdf")):     # every PDF in any sub-folder, in a stable order
        doc_type = pdf_path.parent.name                  # sub-folder name: "company" or "standards"
        reader = PdfReader(str(pdf_path))                # opens the PDF
        for page_number, page in enumerate(reader.pages, start=1):   # page numbers start at 1, like in a PDF viewer
            text = (page.extract_text() or "").strip()   # text of this page; empty string if none; trim spaces
            if not text:                                 # a page without text (image only)
                print(f"WARNING: no text on {pdf_path.name} page {page_number}")   # tell the user, do not hide it
                continue                                 # skip this page
            pages.append({                               # remember the page together with its origin
                "text": text,                            # the page text
                "source_doc": pdf_path.name,             # file name, shown later as the source
                "doc_type": doc_type,                    # company or standards
                "page": page_number,                     # page number, shown later in the citation
            })
    return pages                                         # hand the list to the caller


if __name__ == "__main__":                               # runs only with: py ingest.py
    pages = load_pdfs()                                  # read everything
    documents = {p["source_doc"] for p in pages}         # set of distinct file names
    print(f"{len(pages)} pages loaded from {len(documents)} documents")   # summary line
    for p in pages[:3]:                                  # show the first three pages as a sanity check
        print(p["source_doc"], "page", p["page"], "->", p["text"][:120].replace("\n", " "))   # first 120 characters