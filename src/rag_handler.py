"""Classes to handle RAG related actions."""
from langchain_community.document_loaders import BSHTMLLoader, DirectoryLoader
from langchain_text_splitters import HTMLSectionSplitter

HEADERS_TO_SPLIT_ON = [(f"h{i+1}", f"Header{i+1}") for i in range(15)]


class RAGHandler:
    """Basic class to use RAG."""

    def __init__(self, chunk_size, chunk_overlap):
        """Initialise the class."""
        self.documents = None
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.split_docs = None

    def load_documents(self):
        """Load the documents."""
        loader = DirectoryLoader("data", show_progress=True, loader_cls=BSHTMLLoader, silent_errors=True)
        self.documents = loader.load()

    def split_documents(self):
        """Split the documents."""
        html_splitter = HTMLSectionSplitter(headers_to_split_on=HEADERS_TO_SPLIT_ON)
        self.split_docs = html_splitter.split_documents(self.documents)
