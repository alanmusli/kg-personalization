import instructor
from ollama import Client as OllamaClient
from models import ExtractionResult
from prompts import EXTRACTION_PROMPT

class EntityExtractor:
    def __init__(self, model: str = "qwen2.5:7b"):
        self.client = instructor.from_ollama(
            OllamaClient(),
            mode=instructor.Mode.JSON,
        )
        self.model = model

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