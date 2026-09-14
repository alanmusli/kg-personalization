from pydantic import BaseModel, Field

class Entity(BaseModel):
    name: str = Field(description="The canonical name of the entity")
    type: str = Field(description="One of: Movie, Genre, Actor, Director, Tag, Theme")
    properties: dict = Field(default_factory=dict, description="Additional properties")

class Relation(BaseModel):
    source: str = Field(description="Source entity name")
    source_type: str = Field(description="Source entity type, eg Movie, Genre, Actor, Director, Tag or Name")
    relation: str = Field(description="One of the allowed relation types")
    target: str = Field(description="Target entity name")
    target_type: str = Field(description="Target entity type")
    properties: dict = Field(default_factory=dict)

class ExtractionResult(BaseModel):
    entities: list[Entity]
    relations: list[Relation]