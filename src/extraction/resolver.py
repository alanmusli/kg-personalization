from src.extraction.models import Entity

class EntityResolver:
    """Normalizacija i pronaogjanje duplikat entiteti vo profil na user."""

    def __init__(self):
        self.entity_map = {}

    def normalize(self, name: str, entity_type: str) -> str:
        normalized = name.strip().lower()

        normalized = normalized.replace("the ", "")

        key = f"{entity_type}:{normalized}"
        if key in self.entity_map:
            return self.entity_map[key]

        self.entity_map[key] = normalized
        return normalized

    #deduplikacija
    def resolve_batch(self, entities: list[Entity]) -> list[Entity]:
        seen = {}
        resolved = []
        for entity in entities:
            canonical = self.normalize(entity.name, entity.type)
            if canonical not in seen:
                entity.name = canonical
                seen[canonical] = entity
                resolved.append(entity)
        return resolved