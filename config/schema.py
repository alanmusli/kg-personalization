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
    FEATURES_ACTOR = "FEATURES"
    DIRECTED_BY = "DIRECTED_BY"
    HAS_THEME = "HAS_THEME"
    PREFERS_GENRE = "PREFERS_GENRE"
    PREFERS_THEME = "PREFERS_THEME"

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