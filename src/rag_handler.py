"""Classes to handle RAG related actions."""
import os

import torch
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain_community.document_loaders import BSHTMLLoader, DirectoryLoader
from langchain_core.documents import Document
from langchain_text_splitters import HTMLSectionSplitter

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
HEADERS_TO_SPLIT_ON = [(f"h{i + 1}", f"Header{i + 1}") for i in range(15)]


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
        model: str = "sentence-transformers/all-mpnet-base-v2",
        nb_docs_returned: int = 20,
        fetch_k_docs: int = 200,
    ):
        """Initialise the class."""
        self.documents = None
        self.model = model
        self.split_docs = None
        self.vectorstore = None
        self.embedding = None
        self.nb_docs_returned = nb_docs_returned
        self.fetch_k_docs = fetch_k_docs

    def set_nb_docs_returned(self, nb_docs_returned):
        """Set nb_docs_returned."""
        self.nb_docs_returned = nb_docs_returned

    def set_fetch_k_docs(self, fetch_k_docs):
        """Set fetch_k_docs."""
        self.fetch_k_docs = fetch_k_docs

    def load_documents(self):
        """Load the documents."""
        loader = DirectoryLoader("data", show_progress=True, loader_cls=BSHTMLLoader, silent_errors=True)
        self.documents = loader.load()

    def split_documents(self):
        """Split the documents."""
        html_splitter = HTMLSectionSplitter(headers_to_split_on=HEADERS_TO_SPLIT_ON)
        self.split_docs = html_splitter.split_documents(self.documents)

    def set_vectorestore(self):
        """Set the vectore store."""
        embeddings = HuggingFaceEmbeddings(model_name=self.model, model_kwargs=CONFIG)
        self.vectorstore = FAISS.from_documents(self.split_docs, embeddings)
        self.embedding = embeddings

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
        return result
