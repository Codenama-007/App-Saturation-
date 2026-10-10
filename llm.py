import re

from langchain_ollama import ChatOllama

from config import LLM_MODEL

llm = ChatOllama(model=LLM_MODEL, temperature=0)


def strip_think(text: str) -> str:
    """Remove <think>...</think> blocks some models emit."""
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()


def ask(prompt: str) -> str:
    return strip_think(llm.invoke(prompt).content)