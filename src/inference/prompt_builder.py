
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

#System C: KG-RAG
KG_RAG_PROMPT = """You are a movie tagging classification system.

Your task is to select the SINGLE most accurate tag for a NEW movie description from the user's ALLOWED CANDIDATE TAGS list.

USER KNOWLEDGE GRAPH CONTEXT:
{kg_context}

ALLOWED CANDIDATE TAGS (MANDATORY: You MUST select your answer strictly from this list):
[{candidate_tags}]

NEW MOVIE DESCRIPTION:
"{query}"

CRITICAL RULES:
1. Choose EXACTLY ONE tag from the ALLOWED CANDIDATE TAGS list above that best fits the movie description.
2. DO NOT invent new tags or synonyms that are not in the candidate list.
3. Output ONLY the chosen tag verbatim. No explanations, no quotes, no extra words.

Selected Tag:"""