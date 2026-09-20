import ollama
from ollama import Client
from src.retrieval.context_builder import ContextBuilder
from src.graph.neo_client import Neo4jClient

class InferenceClient:
    def __init__(self, model: str = "qwen2.5:7b", host: str = "http://100.121.134.70:11434"):
        self.model = model
        self.client = Client(host=host)
        self.db_client = Neo4jClient(uri="bolt://localhost:7687", user="neo4j", password="password123")


    def predict(self, prompt: str) -> str:
        response = self.client.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.0}
        )
        return response["message"]["content"].strip()


client = InferenceClient()
context_builder = ContextBuilder(db_client=client.db_client)


BASELINE_PROMPT = """Given the following input, predict the most appropriate tag.

Input: {query}
Tag:"""

RAG_PROMPT = """Based on the user's past interactions below, predict the most appropriate tag for the new input.

User's past interactions:
{retrieved_text}

New input: {query}
Tag:"""

KG_RAG_PROMPT = """You are a personalization engine. Use the user's structured preference profile below to predict how this specific user would tag the following item.

USER PREFERENCE PROFILE (from Knowledge Graph):
{kg_context}

NEW ITEM TO TAG:
{query}

Based on this user's demonstrated preferences, patterns, and past tagging behavior, predict the most appropriate tag. Respond with only the tag."""



def run_baseline(user_id: str, query: str) -> str:
    prompt = BASELINE_PROMPT.format(query=query)
    return client.predict(prompt)


def run_rag(user_id: str, query: str, retriever=None) -> str:
    retrieved_docs = retriever.get_text_history(user_id, query) if retriever else "User previously liked Sci-Fi movies."
    prompt = RAG_PROMPT.format(retrieved_text=retrieved_docs, query=query)
    return client.predict(prompt)


def run_kg_rag(user_id: str, query: str, graph_store=None) -> str:
    raw_graph_data = graph_store.query_user_subgraph(user_id, query) if graph_store else {
        "genre_preferences": [{"genre": "Sci-Fi", "count": 12, "avg_rating": 4.5}],
        "similar_reviewed": [{"movie": "Inception", "tag": "mind-bending", "rating": 5}],
        "theme_sentiment": [{"theme": "space travel", "avg_rating": 4.8}]
    }

    kg_context_str = context_builder.build(raw_graph_data)

    prompt = KG_RAG_PROMPT.format(kg_context=kg_context_str, query=query)
    return client.predict(prompt)