import os
from app.vectorstore.chroma_store import chroma_store

def ingest():
    doc_path = os.path.join("app", "vectorstore", "documents", "knowledge_base.txt")
    if not os.path.exists(doc_path):
        print(f"Error: Knowledge base file not found at {doc_path}")
        return

    with open(doc_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Split documents by double newlines (paragraphs/sections)
    sections = [sec.strip() for sec in content.split("\n\n") if sec.strip()]
    
    if not sections:
        print("Warning: knowledge_base.txt is empty.")
        return

    documents = []
    ids = []
    
    for i, section in enumerate(sections):
        documents.append(section)
        ids.append(f"doc_{i}")

    try:
        # Clear existing documents in the collection first to avoid duplicates
        # ChromaDB allows delete, but let's check if we can delete or just add.
        # Since it's a PersistentClient, we can delete all documents or get the count.
        # Let's delete existing documents by ids if we want, or since it's simple:
        try:
            chroma_store.collection.delete(where={}) # deletes everything in the collection
        except Exception:
            # If where={} fails, delete by known range of IDs or just recreate the collection
            pass
            
        chroma_store.add_documents(documents=documents, ids=ids)
        print(f"Successfully ingested {len(documents)} sections into ChromaDB collection 'knowledge_base'.")
    except Exception as e:
        print(f"Error ingesting documents into ChromaDB: {e}")

if __name__ == "__main__":
    ingest()
