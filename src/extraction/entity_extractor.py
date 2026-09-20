import instructor
from ollama import Client as OllamaClient
from openai import OpenAI
from src.extraction.models import ExtractionResult
from src.extraction.prompts import EXTRACTION_PROMPT

class EntityExtractor:
    # def __init__(self, model: str = "qwen2.5:7b"):
    #     raw_client = OpenAI(
    #         base_url="http://localhost:11434/v1",
    #         api_key="ollama",
    #     )
    #     self.client = instructor.from_openai(raw_client, mode=instructor.Mode.JSON)
    #     self.model = model

    def __init__(self, model: str = "qwen2.5:7b", host: str = "http://100.121.134.70:11434/v1"):
        raw_client = OpenAI(
            base_url=host,
            api_key="ollama",
        )

        self.client = instructor.from_openai(raw_client, mode=instructor.Mode.JSON)
        self.model = model


        # self.client = instructor.from_ollama(
        #     OllamaClient(),
        #     mode=instructor.Mode.JSON,
        # )
        # self.model = model

    def extract(self, text: str) -> ExtractionResult:
        result = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "Extract entities and relations."},
                {"role": "user", "content": EXTRACTION_PROMPT.format(
                    user_interaction_text=text
                )}
            ],
            response_model=ExtractionResult,
        )
        return result