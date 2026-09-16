from neo4j import GraphDatabase

class Neo4jClient:
    def __init__(self, uri="bolt://localhost:7687",
                 user="neo4j", password="password123"):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def run_query(self, query: str, parameters: dict = None):
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]

    def create_user_node(self, user_id: str):
        self.run_query(
            "MERGE (u:User {user_id: $uid})",
            {"uid": user_id}
        )

    def create_movie_node(self, title: str, properties: dict = None):
        props = properties or {}
        self.run_query(
            "MERGE (m:Movie {title: $title}) SET m += $props",
            {"title": title, "props": props}
        )

    def create_relationship(self, source_label, source_key, source_val,
                            rel_type, target_label, target_key, target_val,
                            rel_props=None):
        query = f"""
        MERGE (a:{source_label} {{{source_key}: $source_val}})
        MERGE (b:{target_label} {{{target_key}: $target_val}})
        MERGE (a)-[r:{rel_type}]->(b)
        SET r += $props
        """
        self.run_query(query, {
            "source_val": source_val,
            "target_val": target_val,
            "props": rel_props or {}
        })

    def close(self):
        self.driver.close()