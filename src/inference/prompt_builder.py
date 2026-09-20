
# System A: No personalization (baseline)
BASELINE_PROMPT = """Given the following input, predict the most appropriate tag.

Input: {query}
Tag:"""

# System B: Standard RAG (text retrieval baseline)
RAG_PROMPT = """Based on the user's past interactions below, predict the most
appropriate tag for the new input.

User's past interactions:
{retrieved_text}

New input: {query}
Tag:"""

# System C: KG-RAG
KG_RAG_PROMPT = """You are a personalization engine. Use the user's structured
preference profile below to predict how this specific user would tag the
following item.

USER PREFERENCE PROFILE (from Knowledge Graph):
{kg_context}

NEW ITEM TO TAG:
{query}

Based on this user's demonstrated preferences, patterns, and past tagging
behavior, predict the most appropriate tag. Respond with only the tag."""