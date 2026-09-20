from src.graph.neo_client import Neo4jClient
from src.extraction.entity_extractor import EntityExtractor
from src.graph.graph_queries import *

class GraphRetriever:
    def __init__(self, neo4j_client: Neo4jClient, extractor: EntityExtractor):
        self.db = neo4j_client
        self.extractor = extractor

    def retrieve(self, user_id: str, query: str) -> dict:
        query_result = self.extractor.extract(query)
        query_genres = [e.name for e in query_result.entities if e.type == "Genre"]
        query_themes = [e.name for e in query_result.entities if e.type == "Theme"]

        return {
            "genre_preferences": self.db.run_query(
                USER_GENRE_PREFS, {"uid": user_id}
            ),
            "similar_reviewed": self.db.run_query(
                SIMILAR_MOVIES_BY_USER,
                {"uid": user_id, "query_term": query, "query_genres": query_genres}
            ),
            "theme_sentiment": self.db.run_query(
                USER_THEME_SENTIMENT,
                {"uid": user_id, "query_themes": query_themes}
            ),
        }