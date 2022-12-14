from pydantic import BaseModel

class BuildTerritoriesByFeatureCount(BaseModel):
    table: str
    number_of_features_per_territory: int

class BuildTerritoriesByGroupCount(BaseModel):
    table: str
    number_of_territories: int

class BuildTerritoriesByColumnSum(BaseModel):
    table: str
    column: str
    ideal_sum_of_column_per_territory: int

class BuildPolygonTerritoriesFromPointColumn(BaseModel):
    table: str
    column: str
