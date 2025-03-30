from typing import List
from bs4 import BeautifulSoup
import re
from langchain.schema import Document


def clean_html_content(html: str) -> str:
    soup = BeautifulSoup(html, 'html.parser')

    for element in soup(['script', 'style', 'nav', 'footer', 'aside', 'head']):
        element.decompose()

    text = soup.get_text()

    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)

    text = re.sub(r'Содержание\n.*?Примечания\n', '', text, flags=re.DOTALL)
    text = re.sub(r'Категории:.*', '', text, flags=re.DOTALL)

    return text.strip()

async def process_documents(docs: List[Document]) -> List[Document]:
    processed = []
    for doc in docs:
        cleaned_content = clean_html_content(doc.page_content)
        processed.append(Document(
            page_content=cleaned_content,
            metadata=doc.metadata
        ))
    return processed