from neo4j import GraphDatabase

URI = "bolt://localhost:7687"
AUTH = ("neo4j", "password123")

CONSTRAINTS_AND_INDEXES = [

        "CREATE CONSTRAINT user_id_unique IF NOT EXISTS FOR (u:User) REQUIRE u.user_id IS UNIQUE",
        "CREATE CONSTRAINT movie_id_unique IF NOT EXISTS FOR (m:Movie) REQUIRE m.movie_id IS UNIQUE",
        "CREATE CONSTRAINT genre_name_unique IF NOT EXISTS FOR (g:Genre) REQUIRE g.name IS UNIQUE",
        "CREATE CONSTRAINT actor_name_unique IF NOT EXISTS FOR (a:Actor) REQUIRE a.name IS UNIQUE",
        "CREATE CONSTRAINT director_name_unique IF NOT EXISTS FOR (d:Director) REQUIRE d.name IS UNIQUE",
        "CREATE CONSTRAINT theme_name_unique IF NOT EXISTS FOR (t:Theme) REQUIRE t.name IS UNIQUE",
        "CREATE CONSTRAINT tag_name_unique IF NOT EXISTS FOR (tg:Tag) REQUIRE tg.name IS UNIQUE",

        "CREATE FULLTEXT INDEX movie_search IF NOT EXISTS FOR (m:Movie) ON EACH [m.title]"
]

def setup_database(clear_existing: bool = True):
    driver = GraphDatabase.driver(URI, auth=AUTH)
    with driver.session() as session:
        if clear_existing:
            print("Cleaning existing graph from Neo4j...")
            session.run("MATCH (n) DETACH DELETE n")
            print("Graph cleared successfully.\n")

        print("Creating constraints and indexes in Neo4j...")
        for query in CONSTRAINTS_AND_INDEXES:
            try:
                session.run(query)
                # Го печати типот на објектот што е креиран
                parts = query.split()
                obj_name = parts[2] if len(parts) > 2 else "index/constraint"
                print(f"Executed: {parts[1]} {obj_name}")
            except Exception as e:
                print(f"Warning on query [{query[:35]}...]: {e}")

    driver.close()
    print("\nAll constraints and indexes created successfully! Ready for graph rebuild.")


if __name__ == "__main__":
    setup_database(clear_existing=False)

