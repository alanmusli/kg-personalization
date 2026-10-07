import ollama, re
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

client = None

def get_client():
    global client
    if client is None:
        client = InferenceClient()
    return client


BASELINE_PROMPT = """Predict the single most relevant short tag (1-3 words) for the following movie description. Output ONLY the tag. Do not include quotes, punctuation, or explanations.

Input: {query}
Tag:"""

RAG_PROMPT = """Based on the user's past interactions below, predict the single most relevant short tag (1-3 words) for the new movie description. Output ONLY the tag. Do not include quotes, punctuation, or explanations.

User's past interactions:
{retrieved_text}

New input: {query}
Tag:"""

KG_RAG_PROMPT = """You are an expert movie tagging assistant. Predict the single most relevant short tag (1-3 words) for a NEW movie based on the user's specific style.

EXAMPLE:
User Context: Top genres: Sci-Fi (avg 4.5★). Historically relevant themes: space travel; dystopia.
New Movie: "A team of astronauts travels through a wormhole."
Predicted Tag: space travel

Now, process the following:
USER'S HISTORICAL PREFERENCES:
{kg_context}

NEW MOVIE DESCRIPTION:
"{query}"

Output ONLY the final predicted tag. Do not include quotes or punctuation.
Predicted Tag:"""


def run_baseline(user_id: str, query: str) -> str:
    client = get_client()
    prompt = BASELINE_PROMPT.format(query=query)
    return client.predict(prompt)


def run_rag(user_id: str, query: str, retriever=None) -> str:
    client = get_client()
    db = Neo4jClient(uri="bolt://localhost:7687", user="neo4j", password="password123")
    results = db.run_query("""
          MATCH (u:User {user_id: $uid})-[r:REVIEWED]->(m:Movie)
          RETURN m.title AS title, r.tag AS tag
          ORDER BY m.title LIMIT 10
      """, {"uid": user_id})
    db.close()
    retrieved_text = "\n".join(f"- {r['title']}: tagged as '{r['tag']}'" for r in results)
    prompt = RAG_PROMPT.format(retrieved_text=retrieved_text, query=query)
    return client.predict(prompt)

def run_kg_rag(user_id: str, query: str, kg_context: str = None, candidate_tags: list = None) -> str:
    cli = get_client()

    if not kg_context:
        kg_context = "No personalization context available."

    clean_candidates = []
    if candidate_tags:
        if isinstance(candidate_tags, str):
            # Ако случајно стигнала како string "['tag1', 'tag2']"
            clean_candidates = [t.strip(" []'\"").lower() for t in candidate_tags.split(",")]
        elif isinstance(candidate_tags, list):
            clean_candidates = [str(t).strip().lower() for t in candidate_tags if t]

    if clean_candidates:
        tags_str = ", ".join([f"'{t}'" for t in clean_candidates])

        prompt = f"""You are a movie tagging classification system.

Select the SINGLE best tag for the movie description below.
You MUST choose ONLY ONE tag directly from the ALLOWED CANDIDATE TAGS list.

USER PREFERENCES CONTEXT:
{kg_context}

ALLOWED CANDIDATE TAGS:
[{tags_str}]

NEW MOVIE DESCRIPTION:
"{query}"

Respond ONLY with the chosen tag verbatim from the list. Do not write quotes or extra text.
Selected Tag:"""

        raw_pred = cli.predict(prompt).strip().lower()

        pred = re.sub(r'^(selected\s+)?tag:\s*', '', raw_pred)
        pred = re.sub(r'[^a-z0-9\s-]', '', pred).strip()

        if pred in clean_candidates:
            return pred

        for cand in clean_candidates:
            if cand in pred or pred in cand:
                return cand

        return clean_candidates[0]

    else:
        prompt = f"Predict a single 1-2 word movie tag for:\n{query}\nTag:"
        return cli.predict(prompt).strip().lower()