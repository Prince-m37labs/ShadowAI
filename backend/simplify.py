# Add this utility to simplify Groq output using LangChain and OpenAI
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
import os

def simplify_explanation(original: str) -> str:
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        return original  # fallback: return original if no key
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3, openai_api_key=openai_api_key)
    prompt = PromptTemplate.from_template("""
You are a simplifier for junior developers.
Rephrase the following explanation in plain, friendly terms:

{original}
""")
    return llm.invoke(prompt.format(original=original))
