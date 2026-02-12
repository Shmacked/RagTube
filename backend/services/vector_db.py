from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from typing import Any, List, Optional, Dict
from datetime import datetime
import spacy


load_dotenv(dotenv_path="backend/.env")

PERSISTENT_DIRECTORY = "backend/chroma_store"
COLLECTION_NAME = "youtube_transcripts" # What kind of data we're storing
# EMBEDDING = OpenAIEmbeddings(model="text-embedding-3-small")
EMBEDDING = OpenAIEmbeddings(model="text-embedding-3-large")

vector_dbs = {
    COLLECTION_NAME: Chroma(persist_directory=PERSISTENT_DIRECTORY, embedding_function=EMBEDDING, collection_name=COLLECTION_NAME)
}


def get_or_create_vector_db(collection_name: str) -> Chroma:
    """
    Get a vector database.
    """
    collection = vector_dbs.get(collection_name)
    if not collection:
        collection = Chroma(persist_directory=PERSISTENT_DIRECTORY, embedding_function=EMBEDDING, collection_name=collection_name)
        vector_dbs[collection_name] = collection
    return collection

def delete_vector_db(collection_name: str) -> bool:
    try:
        collection = get_or_create_vector_db(collection_name)
        collection.delete_collection()
        if collection_name in vector_dbs:
            del vector_dbs[collection_name]
    except Exception as e:
        return False
    return True

def add_documents_to_db(collection_name: str, docs: List[Document]) -> int:
    collection = get_or_create_vector_db(collection_name)
    
    # Chunk the documents properly
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=128)
    split_docs = text_splitter.split_documents(docs)
    
    collection.add_documents(split_docs)
    return len(split_docs)

def add_text_to_vector_db(collection_name: str, text: str, metadata: Optional[Dict[str, Any]] = None) -> int:
    # Wrap raw text into a Document object
    if metadata is None:
        metadata = {}

    metadata["created_timestamp"] = int(datetime.now().timestamp()) # Unix timestamp

    doc = Document(page_content=text, metadata=metadata)
    return add_documents_to_db(collection_name, [doc])

def delete_vector_db_data(collection_name: str, data_ids: Optional[list[int]] = None, metadata_filter: Optional[Dict[str, Any]] = None) -> bool:
    try:
        collection = get_or_create_vector_db(collection_name)
        collection.delete(ids=data_ids, where=metadata_filter)
    except Exception as e:
        return False
    return True

def search_vector_db(collection_name: str, query: str, k: int = 5, _filter: Optional[Dict[str, Any]] = None) -> List[Document]:
    collection = get_or_create_vector_db(collection_name)
    return collection.similarity_search(query, k=k, filter=_filter)

def extract_entities(text: str) -> List[str]:
    nlp = spacy.load("en_core_web_md")
    doc = nlp(text)
    return [ent.text for ent in doc.ents]