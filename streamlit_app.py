"""Main function to run the application."""
import os

import streamlit as st

from src.email_handler import EmailHandler
from src.llm_handler import LLMHandler
from src.rag_handler import RAGHandler
from src.utils import get_config

st.title("em AI l")

config = get_config()

if "rag_service" not in st.session_state:
    rag_service = RAGHandler(**config["rag"])
    if "faiss_index" not in os.listdir("./data/"):
        email_handler = EmailHandler(**config["email"])
        email_handler.initialise_set_up()
        rag_service.initialise_set_up()
    else:
        rag_service.set_embeddings()
        rag_service.load_vectorestore()
    st.session_state.rag_service = rag_service
if "llm_handler" not in st.session_state:
    llm_handler = LLMHandler(**config["llm"]["model"])
    llm_handler.start_llamafile()
    llm_handler.set_llm(**config["llm"]["model_config"])
    st.session_state.llm_handler = llm_handler


def generate_response(input_text: str):
    """Generate a response by the LLM based on input from the user.

    Args:
        input_text (str): input text from the user.
    """
    rag_service = st.session_state.rag_service
    llm_handler = st.session_state.llm_handler
    context = rag_service.get_context(input_text)
    prompt = llm_handler.prepare_prompt(input_text, context)
    st.write_stream(llm_handler.llm_stream(prompt))


with st.form("my_form"):
    text = st.text_area("Enter text:", "")
    submitted = st.form_submit_button("Submit")
    if submitted:
        generate_response(text)
