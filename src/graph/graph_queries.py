
# Query 1: Get user's genre preferences (ranked by strength)
USER_GENRE_PREFS = """
MATCH (u:User {user_id: $uid})-[p:PREFERS_GENRE]->(g:Genre)
RETURN g.name AS genre, p.strength AS count, p.avg_rating AS avg_rating
ORDER BY p.strength DESC
LIMIT 10
"""

# Query 2: Find movies similar to a query movie via shared attributes
SIMILAR_MOVIES_BY_USER = """
MATCH (u:User {user_id: $uid})-[r:REVIEWED]->(m:Movie)
WHERE m.title CONTAINS $query_term OR
      EXISTS {
        MATCH (m)-[:HAS_GENRE]->(g:Genre)
        WHERE g.name IN $query_genres
      }
RETURN m.title AS movie, r.rating AS rating, r.tag AS tag,
       [(m)-[:HAS_GENRE]->(g) | g.name] AS genres
ORDER BY r.rating DESC
LIMIT 5
"""

# Query 3: Multi-hop — find user's sentiment toward specific themes
USER_THEME_SENTIMENT = """
MATCH (u:User {user_id: $uid})-[r:REVIEWED]->(m:Movie)-[:HAS_THEME]->(t:Theme)
WHERE t.name IN $query_themes
WITH t.name AS theme, COLLECT({movie: m.title, rating: r.rating}) AS reviews,
     AVG(r.rating) AS avg_rating
RETURN theme, avg_rating, reviews
"""

# Query 4: Full user profile summary via graph
USER_PROFILE_SUMMARY = """
MATCH (u:User {user_id: $uid})
OPTIONAL MATCH (u)-[p:PREFERS_GENRE]->(g:Genre)
WITH u, COLLECT({genre: g.name, strength: p.strength, avg_rating: p.avg_rating}) AS genre_prefs
OPTIONAL MATCH (u)-[:REVIEWED]->(m:Movie)
WITH u, genre_prefs, COUNT(m) AS total_reviews,
     AVG(m.avg_rating) AS overall_avg_rating
RETURN u.user_id AS user_id, total_reviews, overall_avg_rating, genre_prefs
"""