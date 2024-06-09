"""Classes to handle RAG related actions."""
import os
import shutil

import torch
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.environ["CURL_CA_BUNDLE"] = ""
CONFIG = {}


def set_config():
    """Set the vector store."""
    if torch.cuda.is_available():
        CONFIG["device"] = "cuda"
    else:
        CONFIG["device"] = "cpu"


class RAGHandler:
    """Basic class to use RAG."""

    def __init__(
        self,
        model: str = "lewispons/email-classifiers",
        nb_docs_returned: int = 5,
        fetch_k_docs: int = 200,
        chunk_size: int = 1000,
        chunk_overlap: int = 20,
        threshold: float = 0.8,
    ):
        """Initialise the class."""
        self.documents = None
        self.model = model
        self.split_docs = None
        self.vectorstore = None
        self.embedding = None
        self.nb_docs_returned = nb_docs_returned
        self.fetch_k_docs = fetch_k_docs
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.threshold = threshold

    def set_nb_docs_returned(self, nb_docs_returned):
        """Set nb_docs_returned."""
        self.nb_docs_returned = nb_docs_returned

    def set_fetch_k_docs(self, fetch_k_docs):
        """Set fetch_k_docs."""
        self.fetch_k_docs = fetch_k_docs

    def set_chunk_size(self, chunk_size):
        """Set the chunk_size."""
        self.chunk_size = chunk_size

    def set_chunk_overlap(self, chunk_overlap):
        """Set the chunk_size."""
        self.chunk_overlap = chunk_overlap

    def load_documents(self):
        """Load the documents."""
        print("Load emails for ingestion to vector store.")
        loader = DirectoryLoader("data", show_progress=True, loader_cls=TextLoader, silent_errors=True)
        print("Email loading successful.")
        self.documents = loader.load()

    def split_documents(self):
        """Split the documents."""
        print("Start emails splitting for vector store ingestion.")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)
        print("Emails splitting successful.")
        self.split_docs = text_splitter.split_documents(self.documents)

    def set_embeddings(self):
        """Set the embedding with appropriate model."""
        embeddings = HuggingFaceEmbeddings(model_name=self.model, model_kwargs=CONFIG)
        self.embedding = embeddings

    def set_vectorestore(self):
        """Set the vectore store."""
        print("Start setting up the vector store.")
        set_config()
        embeddings = HuggingFaceEmbeddings(model_name=self.model, model_kwargs=CONFIG)
        self.vectorstore = FAISS.from_documents(self.split_docs, embeddings)
        self.embedding = embeddings
        print("Vector store set up successfully.")
        print("Cleaning...")
        for item in os.listdir("./data/"):
            if item not in [".gitkeep", ".DS_Store"]:
                try:
                    shutil.rmtree("./data/" + item)
                except Exception as e:
                    print(f"Something went wrong: {e}")
                    raise e
        print("Cleaning done.")

    def save_vectorestore(self):
        """Save the vectore store."""
        self.vectorstore.save_local(os.path.join(DATA_DIR, "faiss_index"))

    def load_vectorestore(self):
        """Load the vectorestore."""
        vectorstore = FAISS.load_local(
            os.path.join(DATA_DIR, "faiss_index"), self.embedding, allow_dangerous_deserialization=True
        )
        self.vectorstore = vectorstore

    def query_vectorestore(self, query) -> list[tuple[Document, float]]:
        """Query the vector store based on a query and retrieve the most relevant documents."""
        result = self.vectorstore.similarity_search_with_score(  # type: ignore[attr-defined]
            query, k=self.nb_docs_returned, fetch_k=self.fetch_k_docs
        )
        print("Documents found: ")
        filtered_res: list[tuple[Document, float]] = []
        for doc, score in result:
            if score < self.threshold:
                filtered_res.append((doc, score))
                print(doc.page_content)
                print(score)
                print()
        return filtered_res

    def get_context(self, query) -> str:
        """Get context for a query."""
        context_docs = self.query_vectorestore(query)
        context_text = "\n------\n".join([doc.page_content for doc, _ in context_docs])
        return context_text

    def initialise_set_up(self):
        """Initialise the set up."""
        self.load_documents()
        self.split_documents()
        self.set_vectorestore()
        self.save_vectorestore()
