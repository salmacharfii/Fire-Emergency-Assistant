import chromadb                                    # the vector database
from openai import OpenAI                          # client for the OpenAI API
from langchain_text_splitters import RecursiveCharacterTextSplitter   # cuts text at paragraph, line, then word borders

from config import (CHROMA_DIR, COLLECTION_NAME, EMBED_MODEL,
                    CHUNK_SIZE, CHUNK_OVERLAP, BATCH_SIZE)   # settings from config.py (this also loads .env)
from ingest import load_pdfs                       # Day 1 function: PDFs to pages

client = OpenAI()                                  # reads OPENAI_API_KEY from the environment


def chunk_pages(pages):                            # pages in, chunks out
    splitter = RecursiveCharacterTextSplitter(     # the splitter tries to break at paragraphs first, then lines, then words
        chunk_size=CHUNK_SIZE,                     # maximum characters per chunk (800)
        chunk_overlap=CHUNK_OVERLAP,               # characters shared with the previous chunk (100)
    )
    chunks = []                                    # collects all chunks
    for page in pages:                             # one page at a time, so a chunk never crosses a page border
        for i, piece in enumerate(splitter.split_text(page["text"])):   # i = position of the chunk on this page
            chunks.append({                        # one dictionary per chunk
                "id": f'{page["source_doc"]}-p{page["page"]}-c{i}',   # unique id, e.g. brandschutz.pdf-p3-c0
                "text": piece,                     # the chunk text
                "metadata": {                      # information stored next to the vector
                    "source_doc": page["source_doc"],   # file name for the citation
                    "doc_type": page["doc_type"],       # company or standards
                    "page": page["page"],               # page number for the citation
                    "language": "en",  # put the file names of your German PDFs in the set; every other file counts as English
                },
            })
    return chunks                                  # list of chunk dictionaries


def embed(texts):                                  # list of strings in, list of vectors out
    response = client.embeddings.create(model=EMBED_MODEL, input=texts)   # one API call for the whole list
    return [item.embedding for item in response.data]   # keep only the vectors, in the same order


def build_index():
    chroma = chromadb.PersistentClient(path=str(CHROMA_DIR))   # a database saved in the chroma_db folder
    try:
        chroma.delete_collection(COLLECTION_NAME)  # remove the old index, so a re-run never creates duplicates
    except Exception:                              # first run: there is nothing to delete
        pass
    collection = chroma.create_collection(         # create a fresh, empty collection
        name=COLLECTION_NAME,                      # "fire_safety"
        metadata={"hnsw:space": "cosine"},         # measure closeness as cosine distance
    )
    chunks = chunk_pages(load_pdfs())              # Day 1 pages become chunks
    for start in range(0, len(chunks), BATCH_SIZE):    # walk through the chunks 100 at a time
        batch = chunks[start:start + BATCH_SIZE]   # the current slice of up to 100 chunks
        collection.add(                            # store the slice in Chroma
            ids=[c["id"] for c in batch],          # unique ids
            documents=[c["text"] for c in batch],  # the chunk texts
            embeddings=embed([c["text"] for c in batch]),   # their vectors
            metadatas=[c["metadata"] for c in batch],       # source, page, type, language
        )
    print(f"{len(chunks)} chunks written, collection holds {collection.count()}")   # both numbers must be equal


if __name__ == "__main__":                         # runs only with: py build_index.py
    build_index()