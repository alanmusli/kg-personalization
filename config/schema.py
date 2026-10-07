from enum import Enum

class EntityType(str, Enum):
    USER = "User"
    MOVIE = "Movie"
    GENRE = "Genre"
    ACTOR = "Actor"
    DIRECTOR = "Director"
    TAG = "Tag"
    THEME = "Theme"
    SENTIMENT = "Sentiment"

class RelationType(str, Enum):
    REVIEWED = "REVIEWED"
    TAGGED_AS = "TAGGED_AS"
    HAS_GENRE = "HAS_GENRE"
    FEATURES = "FEATURES"
    DIRECTED_BY = "DIRECTED_BY"
    HAS_THEME = "HAS_THEME"
    PREFERS_GENRE = "PREFERS_GENRE"
    PREFERS_THEME = "PREFERS_THEME"
    RELATED_TO = "RELATED_TO"  # Додадено за заштита при непознати релации

SCHEMA_DESCRIPTION = """
Entity types: User, Movie, Genre, Actor, Director, Tag, Theme
Relation types:
  - (User)-[REVIEWED {rating, tag}]->(Movie)
  - (Movie)-[HAS_GENRE]->(Genre)
  - (Movie)-[FEATURES]->(Actor)
  - (Movie)-[DIRECTED_BY]->(Director)
  - (Movie)-[HAS_THEME]->(Theme)
  - (User)-[PREFERS_GENRE {strength}]->(Genre)
"""

RELATION_MAPPER = {
    "reviewed": RelationType.REVIEWED,
    "has_genre": RelationType.HAS_GENRE,
    "hasgenre": RelationType.HAS_GENRE,
    "features": RelationType.FEATURES,
    "features_actor": RelationType.FEATURES,
    "acted_in": RelationType.FEATURES,
    "directed_by": RelationType.DIRECTED_BY,
    "directedby": RelationType.DIRECTED_BY,
    "has_theme": RelationType.HAS_THEME,
    "hastheme": RelationType.HAS_THEME,
    "prefers_genre": RelationType.PREFERS_GENRE,
    "prefers_theme": RelationType.PREFERS_THEME,
}

def map_to_relation_type(raw_relation: str) -> RelationType:
    """Секогаш враќа валиден RelationType Enum."""
    if not raw_relation:
        return RelationType.RELATED_TO

    rel_clean = raw_relation.lower().strip().replace(" ", "_").replace("-", "_")

    # 1. Проверка во точното мапирање
    if rel_clean in RELATION_MAPPER:
        return RELATION_MAPPER[rel_clean]

    # 2. Heuristic fallback за пронаоѓање клучни зборови
    if any(k in rel_clean for k in ["director", "directed", "dir"]):
        return RelationType.DIRECTED_BY
    elif any(k in rel_clean for k in ["actor", "star", "cast", "features", "acts"]):
        return RelationType.FEATURES
    elif any(k in rel_clean for k in ["genre", "category", "type"]):
        return RelationType.HAS_GENRE
    elif any(k in rel_clean for k in ["theme", "about", "topic", "subject"]):
        return RelationType.HAS_THEME
    elif any(k in rel_clean for k in ["review", "rated", "watched"]):
        return RelationType.REVIEWED
    elif any(k in rel_clean for k in ["prefer", "likes", "favorite"]):
        return RelationType.PREFERS_GENRE

    return RelationType.RELATED_TO

def sanitize_name(name: str) -> str:
    """Чистење и нормализирање на името на ентитетот."""
    return name.strip().lower() if name else ""