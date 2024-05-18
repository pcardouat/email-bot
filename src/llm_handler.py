"""Class to handle everything related to the LLM."""
import os
import subprocess

import requests
from langchain_community.llms.llamafile import Llamafile

LLM_DIR = os.path.join(os.path.dirname(__file__), "..", "llm")


class LLMHandler:
    """Class for the LLM."""

    def __init__(self, llm_config: dict):
        """Initialise the class."""
        self.llm = None
        self.model_url = llm_config["model_url"]
        self.model_name = llm_config["model_name"]

    def set_llm_config(self, llm_config):
        """Set model_url."""
        self.model_url = llm_config["model_url"]
        self.model_name = llm_config["model_name"]

    def download_model(self):
        """Download the LLM if not present."""
        response = requests.get(self.model_url, stream=True)
        response.raise_for_status()
        with open(os.path.join(LLM_DIR, self.model_name), "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:  # Filter out keep-alive new chunks
                    f.write(chunk)

        # Change the file permission to make it executable
        os.chmod(os.path.join(LLM_DIR, self.model_name), 0o755)

    def start_llamafile(self):
        """Start the llamafile."""
        if not os.path.exists(os.path.join(LLM_DIR, self.model_name)):
            self.download_model()
        else:
            executable_path = os.path.join(LLM_DIR, self.model_name)
            args = [executable_path, "--server", "--nobrowser"]
            try:
                subprocess.run(args, check=True)
            except subprocess.CalledProcessError as e:
                print(f"Command failed with return code: {e.returncode}")
                print(f"Error message: {e}")
            except FileNotFoundError as e:
                print(f"Executable not found: {e}")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")

    def set_llm(self, **kwargs):
        """Set the LLM once the llamafile has started."""
        self.llm = Llamafile(**kwargs)

    def prepare_prompt(self, query, context) -> str:
        """Prepare the prompt for the model."""
        prompt = f"""|<user>|
        You are an AI assistant about my emails. I have a question: {query}.
        Here is some context to help you answer : {context}
        |<assistant>|"""
        return prompt
