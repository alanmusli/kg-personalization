from neo4j import GraphDatabase

URI = "bolt://localhost:7687"
AUTH = ("neo4j", "password123")

CONSTRAINTS_AND_INDEXES = [

    "CREATE CONSTRAINT user_id IF NOT EXISTS FOR (u:User) REQUIRE u.user_id IS UNIQUE",
    "CREATE CONSTRAINT movie_title IF NOT EXISTS FOR (m:Movie) REQUIRE m.title IS UNIQUE",
    "CREATE CONSTRAINT genre_name IF NOT EXISTS FOR (g:Genre) REQUIRE g.name IS UNIQUE",
    "CREATE CONSTRAINT actor_name IF NOT EXISTS FOR (a:Actor) REQUIRE a.name IS UNIQUE",
    "CREATE CONSTRAINT director_name IF NOT EXISTS FOR (d:Director) REQUIRE d.name IS UNIQUE",
    "CREATE CONSTRAINT tag_name IF NOT EXISTS FOR (t:Tag) REQUIRE t.name IS UNIQUE",

    "CREATE FULLTEXT INDEX movie_search IF NOT EXISTS FOR (m:Movie) ON EACH [m.title]"
]


def setup_database():
    driver = GraphDatabase.driver(URI, auth=AUTH)
    with driver.session() as session:
        print("Creating constraints and indexes in Neo4j...")
        for query in CONSTRAINTS_AND_INDEXES:
            session.run(query)
            print(f"  ✓ Executed: {query.split()[1]} {query.split()[2]}")

    driver.close()
    print("\nAll constraints and indexes created successfully!")


if __name__ == "__main__":
    setup_database()