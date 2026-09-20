from src.graph.graph_queries import *

class ContextBuilder:
    """Converts graph query results → human-readable structured text."""

    def __init__(self, db_client):
        self.db_client = db_client

    def get_context(self, user_id: str, new_movie_genres: list = None, new_movie_themes: list = None) -> str:
        """
        Го влече контекстот од Neo4j за специфичен корисник.
        Ако имаме карактеристики за новиот филм, ги користи за да најде слични филмови.
        """
        context_data = {}

        # 1. Извлекување на Топ Жанрови (Твој Query 1)
        genre_result = self.db.run_query(USER_GENRE_PREFS, {"uid": user_id})
        if genre_result:
            context_data["genre_preferences"] = [
                {"genre": row["genre"], "count": row["count"], "avg_rating": row["avg_rating"]}
                for row in genre_result
            ]

        # 2. Извлекување на Тематски Сентимент (Твој Query 3 - Прилагоден)
        # Ако не сме пратиле специфични теми од новиот филм, влечеме генерални топ теми
        if new_movie_themes:
            theme_result = self.db.run_query(USER_THEME_SENTIMENT, {"uid": user_id, "query_themes": new_movie_themes})
        else:
            # Fallback: Општи омилени теми на корисникот ако немаме конкретни за пребарување
            fallback_query = """
            MATCH (u:User {user_id: $uid})-[r:REVIEWED]->(m:Movie)-[:HAS_FEATURE]->(t:Theme)
            WITH t.name AS theme, AVG(r.rating) AS avg_rating, COUNT(m) AS count
            ORDER BY count DESC LIMIT 5
            RETURN theme, avg_rating
            """
            theme_result = self.db.run_query(fallback_query, {"uid": user_id})

        if theme_result:
            context_data["theme_sentiment"] = [
                {"theme": row["theme"], "avg_rating": row["avg_rating"]}
                for row in theme_result
            ]

        # 3. Извлекување на Слични Филмови (Твој Query 2)
        # Ова се извршува само ако знаеме кои жанрови ги бараме
        if new_movie_genres:
            similar_result = self.db.run_query(SIMILAR_MOVIES_BY_USER, {
                "uid": user_id,
                "query_term": "",  # Можеш да пратиш и дел од насловот овде ако го имаш
                "query_genres": new_movie_genres
            })
            if similar_result:
                context_data["similar_reviewed"] = [
                    {"movie": row["movie"], "tag": row["tag"], "rating": row["rating"]}
                    for row in similar_result
                ]

        # Го праќаме речникот во твојата build функција за да се претвори во стринг
        return self.build(context_data)

    
    def build(self, context: dict) -> str:
        parts = []

        if context.get("genre_preferences"):
            genre_str = ", ".join(
                f"{p['genre']} ({p['count']} movies, avg: {p['avg_rating']:.1f}★)"
                for p in context["genre_preferences"][:5]
            )
            parts.append(f"Top genre preferences: {genre_str}")

        if context.get("similar_reviewed"):
            movie_str = "; ".join(
                f"'{m['movie']}' [{m['tag']}] ({m['rating']}★)"
                for m in context["similar_reviewed"]
            )
            parts.append(f"Similar movies this user reviewed: {movie_str}")

        if context.get("theme_sentiment"):
            theme_str = "; ".join(
                f"{t['theme']} (avg {t['avg_rating']:.1f}★)"
                for t in context["theme_sentiment"]
            )
            parts.append(f"User's feeling toward relevant themes: {theme_str}")


        if not parts:
            return "No personalization context available."
        else:
            return "\n".join(parts)
