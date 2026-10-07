from src.graph.neo_client import Neo4jClient


def inspect_graph():
    db = Neo4jClient(uri="bolt://localhost:7687", user="neo4j", password="password123")

    print("=== 1. Број на јазли по тип (Node Labels) ===")
    records = db.run_query("MATCH (n) RETURN labels(n) AS label, count(*) AS count ORDER BY count DESC")
    for r in records:
        print(f" - {r['label']}: {r['count']}")

    print("\n=== 2. Број на релации по тип (Relationship Types) ===")
    records = db.run_query("MATCH ()-[r]->() RETURN type(r) AS rel_type, count(*) AS count ORDER BY count DESC")
    for r in records:
        print(f" - {r['rel_type']}: {r['count']}")

    print("\n=== 3. Проверка за изолирани јазли (Disconnected Nodes) ===")
    records = db.run_query("MATCH (n) WHERE NOT (n)-[]-() RETURN labels(n) AS label, count(*) AS count")
    if records:
        for r in records:
            print(f" ⚠️ Изолирани {r['label']}: {r['count']}")
    else:
        print(" ✅ Нема изолирани јазли.")

    print("\n=== 4. Анализа на релациите за еден примерок корисник (User 110) ===")
    sample_q = """
    MATCH (u:User {user_id: '110'})-[r:REVIEWED]->(m:Movie)
    OPTIONAL MATCH (m)-[r2]->(f)
    RETURN count(DISTINCT m) AS reviewed_movies, 
           count(DISTINCT r2) AS movie_features,
           collect(DISTINCT type(r2)) AS feature_types
    """
    records = db.run_query(sample_q)
    for r in records:
        print(f" - Гледани филмови: {r['reviewed_movies']}")
        print(f" - Поврзани карактеристики (Features): {r['movie_features']}")
        print(f" - Типови релации од филмовите: {r['feature_types']}")

    db.close()


if __name__ == "__main__":
    inspect_graph()