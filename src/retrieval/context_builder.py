import re
from src.graph.graph_queries import *

class ContextBuilder:
    """Converts graph query results → human-readable structured text."""

    def __init__(self, db_client):
        self.db_client = db_client
        self.db = db_client

    def get_user_candidate_tags_bfs(self, user_id: str) -> list:
        """
        2-Hop Multi-Hop BFS користејќи ја новата стандардизирана шема:
        (User)-[REVIEWED]->(Movie)-[HAS_GENRE|HAS_THEME|FEATURES|DIRECTED_BY]->(Feature)
        """
        query = """
        MATCH (u:User {user_id: $uid})-[r:REVIEWED]->(m:Movie)
        WHERE r.tag IS NOT NULL AND trim(r.tag) <> ''

        // 2-Hop BFS проодување низ стандардно дефинираните релации
        OPTIONAL MATCH (m)-[:HAS_GENRE|HAS_THEME|FEATURES|DIRECTED_BY]->(f)

        WITH r.tag AS tag, 
             r.rating AS rating,
             collect(DISTINCT coalesce(f.name, '')) AS features

        RETURN tag, 
               count(*) AS tag_freq, 
               avg(coalesce(rating, 4.0)) AS avg_rating
        ORDER BY tag_freq DESC, avg_rating DESC
        LIMIT 15
        """
        records = self.db.run_query(query, {"uid": str(user_id)})

        clean_tags = []
        for r in records:
            if r.get("tag"):
                clean = str(r["tag"]).strip().lower()
                clean = re.sub(r'[^a-z0-9\s-]', '', clean)
                if clean and clean not in clean_tags:
                    clean_tags.append(clean)

        return clean_tags

    def get_context(self, user_id: str, new_movie_genres: list = None, new_movie_themes: list = None) -> str:
        """
        Го влече контекстот од Neo4j за специфичен корисник.
        Ако имаме карактеристики за новиот филм, ги користи за да најде слични филмови.
        """
        context_data = {}

        # 1. Извлекување на Топ Жанрови (Твој Query 1)
        genre_result = self.db_client.run_query(USER_GENRE_PREFS, {"uid": user_id})
        if genre_result:
            context_data["genre_preferences"] = [
                {"genre": row["genre"], "count": row["count"], "avg_rating": row["avg_rating"]}
                for row in genre_result
            ]

        # 2. Извлекување на Тематски Сентимент (Твој Query 3)
        if new_movie_themes:
            theme_result = self.db_client.run_query(
                USER_THEME_SENTIMENT,
                {"uid": user_id, "query_themes": new_movie_themes}
            )
        else:
            fallback_query = """
            MATCH (u:User {user_id: $uid})-[:REVIEWED]->(m:Movie)-[:HAS_THEME]->(t:Theme)
            RETURN DISTINCT t.name AS theme
            LIMIT 5
            """
            theme_result = self.db_client.run_query(fallback_query, {"uid": user_id})

        if theme_result:
            context_data["theme_sentiment"] = [
                {"theme": row["theme"]}
                for row in theme_result
            ]

        # 3. Извлекување на Слични Филмови (Твој Query 2)
        if new_movie_genres:
            similar_result = self.db_client.run_query(SIMILAR_MOVIES_BY_USER, {
                "uid": user_id,
                "query_term": "",
                "query_genres": new_movie_genres
            })
            if similar_result:
                context_data["similar_reviewed"] = [
                    {"movie": row["movie"], "tag": row["tag"], "rating": row["rating"]}
                    for row in similar_result
                ]

        return self.build(context_data)

    def build(self, context: dict) -> str:
        parts = []

        if context.get("genre_preferences"):
            genre_parts = []
            for p in context["genre_preferences"][:5]:
                avg = p.get('avg_rating')
                rating_str = f", avg: {avg:.1f}★" if avg is not None and avg > 0 else ""
                genre_parts.append(f"{p['genre']} ({p['count']} movies{rating_str})")
            parts.append(f"Top genre preferences: {', '.join(genre_parts)}")

        if context.get("similar_reviewed"):
            movie_parts = []
            for m in context["similar_reviewed"]:
                rating = m.get('rating')
                rating_str = f" ({rating}★)" if rating is not None and rating > 0 else ""
                movie_parts.append(f"'{m['movie']}' [{m['tag']}]{rating_str}")
            parts.append(f"Similar movies this user reviewed: {'; '.join(movie_parts)}")

        if context.get("theme_sentiment"):
            theme_parts = []
            for t in context["theme_sentiment"]:
                avg = t.get('avg_rating')
                if avg is not None and avg > 0:
                    theme_parts.append(f"{t['theme']} (avg {avg:.1f}★)")
                else:
                    theme_parts.append(f"{t['theme']}")
            parts.append(f"User's historically relevant themes: {'; '.join(theme_parts)}")

        if not parts:
            return "No personalization context available."
        else:
            return "\n".join(parts)