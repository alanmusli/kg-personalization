EXTRACTION_PROMPT = """You are an expert at extracting structured knowledge from text.

Given the following user interaction from a movie platform, extract all entities
and relationships.

ALLOWED ENTITY TYPES: Movie, Genre, Actor, Director, Tag, Theme
ALLOWED RELATION TYPES:
  - (Movie)-[HAS_GENRE]->(Genre)
  - (Movie)-[FEATURES]->(Actor)
  - (Movie)-[DIRECTED_BY]->(Director)
  - (Movie)-[HAS_THEME]->(Theme)

USER INTERACTION:
{user_interaction_text}

Extract all entities and relations you can identify from this text.
For movies, try to identify genre, actors, directors, and thematic elements.
For tags, normalize them to lowercase.

Return your answer as structured JSON."""