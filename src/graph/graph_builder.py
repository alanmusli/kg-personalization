from src.graph.neo_client import Neo4jClient
from src.extraction.entity_extractor import EntityExtractor
from src.extraction.resolver import EntityResolver
from src.extraction.models import Entity, Relation


class GraphBuilder:
    def __init__(self, extractor: EntityExtractor, resolver: EntityResolver, neo4j_client: Neo4jClient):
        self.extractor = extractor
        self.resolver = resolver
        self.db = neo4j_client

    def build_user_graph(self, user_id: str, profile_items: list[dict]):
        print(f"Building graph for user: {user_id} ({len(profile_items)} items)")
        self.db.create_user_node(user_id)
        all_entities = []
        all_relations = []

        for item in profile_items:
            text = self.format_profile_item(item)
            result = self.extractor.extract(text)

            all_entities.extend(result.entities)
            all_relations.extend(result.relations)

            movie_title = item.get("title") or item.get("description", "")[:40] or f"Item_{item.get('id', 'unknown')}"
            tag = item.get("tag", "")
            rating = float(item.get("rating", 0))

            self.db.create_relationship(
                source_label="User", source_key="user_id", source_val=user_id,
                rel_type="REVIEWED",
                target_label="Movie", target_key="title", target_val=movie_title,
                rel_props={"tag": tag, "rating": rating}
            )

            for entity in result.entities:
                self.db.create_relationship(
                    source_label="Movie", source_key="title", source_val=movie_title,
                    rel_type="HAS_FEATURE",
                    target_label=entity.type if entity.type else "Entity",
                    target_key="name", target_val=entity.name,
                    rel_props={}
                )

        resolved_entities = self.resolver.resolve_batch(all_entities)

        for entity in resolved_entities:
            self.create_entity_node(entity)

        for relation in all_relations:
            self.create_relation(relation)

        self.build_preference_edges(user_id)

    def build_preference_edges(self, user_id: str):
        query = """
        MATCH (u:User {user_id: $uid})-[r:REVIEWED]->(m:Movie)-[:HAS_GENRE]->(g:Genre)
        WITH u, g, COUNT(m) as strength, AVG(r.rating) as avg_rating
        MERGE (u)-[p:PREFERS_GENRE]->(g)
        SET p.strength = strength, p.avg_rating = avg_rating
        """

        self.db.run_query(query, {"uid": user_id})


    def format_profile_item(self, item: dict) -> str:
        title = item.get("title", "")
        description = item.get("description", item.get("text", ""))
        tag = item.get("tag", "")

        return f"Movie: {title}\nDescription: {description}\nUser applied tag: {tag}"

    def create_entity_node(self, entity: Entity):
        query = f"""
        MERGE (n:{entity.type} {{name: $name}})
        SET n += $props
        """

        self.db.run_query(query, {
            "name": entity.name,
            "props": entity.properties
        })

    def create_relation(self, relation: Relation):
        raw_rel = relation.relation if relation.relation else "RELATED_TO"
        clean_rel_type = raw_rel.replace(".", "_").replace("-", "_").replace(" ", "_").upper()

        source_label = relation.source_type if relation.source_type else "Entity"
        target_label = relation.target_type if relation.target_type else "Entity"

        self.db.create_relationship(
            source_label=source_label,
            source_key="title" if relation.source_type == "Movie" else "name",
            source_val=relation.source,
            rel_type=clean_rel_type,
            target_label=target_label,
            target_key="title" if target_label == "Movie" else "name",
            target_val=relation.target,
            rel_props=relation.properties
        )