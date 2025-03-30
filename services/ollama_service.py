import aiohttp
import logging
import os

from dotenv import load_dotenv
from langchain_community.llms.ollama import Ollama

logger = logging.getLogger(__name__)
load_dotenv()

class OllamaService:
    def __init__(self):
        self.model_name = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.timeout = float(os.getenv("OLLAMA_TIMEOUT", "60"))

        self.temperature = float(os.getenv("OLLAMA_TEMPERATURE", "0.3"))
        self.top_p = float(os.getenv("OLLAMA_TOP_P", "0.9"))
        self.repeat_penalty = float(os.getenv("OLLAMA_REPEAT_PENALTY", "1.1"))

        self.llm = Ollama(
            model=self.model_name,
            base_url=self.base_url,
            temperature=self.temperature,
            top_p=self.top_p,
            repeat_penalty=self.repeat_penalty,
            timeout=int(self.timeout)
        )

    async def generate_response(self, prompt: str) -> str:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                        f"{self.base_url}/api/generate",
                        json={
                            "model": self.model_name,
                            "prompt": prompt,
                            "stream": False,
                            "options": {
                                "temperature": self.temperature,
                                "top_p": self.top_p,
                                "repeat_penalty": self.repeat_penalty
                            }
                        },
                        timeout=self.timeout
                ) as resp:
                    result = await resp.json()
                    logger.debug(f"Ollama response received for prompt: {prompt[:100]}...")
                    return result.get("response", "").strip()
        except aiohttp.ClientError as e:
            logger.error(f"Network error connecting to Ollama: {str(e)}")
            raise ConnectionError(f"Failed to connect to Ollama at {self.base_url}") from e
        except Exception as e:
            logger.error(f"Unexpected error during generation: {str(e)}")
            raise RuntimeError("Failed to generate response") from e