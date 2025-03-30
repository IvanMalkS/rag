import logging
import os

def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("rag_system.log"),
            logging.StreamHandler()
        ]
    )
    os.environ['USER_AGENT'] = 'MyRAGBot/1.0 (+https://myproject.com)'