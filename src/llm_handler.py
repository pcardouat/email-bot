"""Class to handle everything related to the LLM."""
import os
import platform
import subprocess

import requests
from langchain_community.llms.llamafile import Llamafile

LLM_DIR = os.path.join(os.path.dirname(__file__), "..", "llm")


class LLMHandler:
    """Class for the LLM."""

    def __init__(self, model_url: str, model_name: str):
        """Initialise the class."""
        self.llm = None
        self.model_url = model_url
        self.model_name = model_name

    def set_llm_config(self, model_url, model_name):
        """Set model_url."""
        self.model_url = model_url
        self.model_name = model_name

    def download_model(self):
        """Download the LLM if not present."""
        print(f"Downloading {self.model_name}")
        response = requests.get(self.model_url, stream=True)
        response.raise_for_status()
        with open(os.path.join(LLM_DIR, self.model_name), "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:  # Filter out keep-alive new chunks
                    f.write(chunk)
        print("Download successful")
        # Change the file permission to make it executable
        print("Making the llamafile executable")
        if platform.system() == "Windows":
            pass
            # TODO: make the file executable for Windows users
        try:
            subprocess.run(["sudo", "chmod", "+x", os.path.join(LLM_DIR, self.model_name)], check=True)
            print("Llamafile set up done.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to set permissions: {e}")
            raise e
        except Exception as e:
            print(f"Something went wrong while making the llamafile executable: {e}")
            raise e

    def start_llamafile(self):
        """Start the llamafile."""
        if not os.path.exists(os.path.join(LLM_DIR, self.model_name)):
            self.download_model()
        try:
            subprocess.Popen(f"{os.path.join(LLM_DIR, self.model_name)} -ngl 9999 --server --nobrowser", shell=True)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            raise e

    def set_llm(self, **kwargs):
        """Set the LLM once the llamafile has started."""
        self.llm = Llamafile(**kwargs)

    def prepare_prompt(self, query, context) -> str:
        """Prepare the prompt for the model."""
        prompt = f"""<|user|>
        You are an AI assistant having access to my emails. I have a question: {query}.
        Here is some emails to help you answer : {context}
        Provide a short answer based on those emails. Remember, the question is: {query}.
        <|assistant|>"""
        return prompt

    def llm_stream(self, input_text):
        """Generate a response by the LLM in a stream way."""
        yield self.llm.stream(input_text)

    def llm_invoke(self, input_text):
        """Generate a response not in a stream way."""
        self.llm.invoke(input_text)
