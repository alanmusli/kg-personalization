import time
from src.data_loader.dataset_parser import DataParser
from src.extraction.entity_extractor import EntityExtractor
from src.extraction.resolver import EntityResolver
from src.graph.graph_builder import GraphBuilder
from src.graph.neo_client import Neo4jClient


def main():
    print(" Initializing Knowledge Graph Build Process...")

    # 1. Initialize Clients and Dependencies
    # Adjust Neo4j connection parameters to match your setup
    neo4j_client = Neo4jClient()
    extractor = EntityExtractor(model="qwen2.5:7b")
    resolver = EntityResolver()
    builder = GraphBuilder(extractor, resolver, neo4j_client)

    # 2. Parse Raw Dataset
    parser = DataParser()
    questions, _ = parser.load()
    user_profiles = parser.get_user_profiles(questions)

    total_users = len(user_profiles)
    print(f"📦 Loaded {total_users} user profiles from LaMP-2 dev split.")

    start_time = time.time()

    # 3. Populate Neo4j Graph User-by-User
    for idx, (user_id, profile_items) in enumerate(
        list(user_profiles.items())[:30], start=1
    ):
        check_query = "MATCH (u:User {user_id: $uid}) RETURN u LIMIT 1"
        is_processed = neo4j_client.run_query(check_query, {"uid": user_id})

        if is_processed:
            print(f"[{idx}/{total_users}] The users {user_id} is already in the database...")
            continue
            
        print(
            f"[{idx}/{total_users}] Building graph for user ID: {user_id}..."
        )

        try:
            builder.build_user_graph(user_id, profile_items)
        except Exception as e:
            print(f"⚠️ Failed to build graph for user {user_id}: {e}")
            continue

    elapsed = time.time() - start_time
    print(f"\n Knowledge Graph construction complete in {elapsed:.2f}s!")

    # Close Neo4j driver connection cleanly
    neo4j_client.close()


if __name__ == "__main__":
    main()