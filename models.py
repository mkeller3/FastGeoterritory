from pydantic import BaseModel

class BuildTerritoriesByFeatureCount(BaseModel):
    table: str
    number_of_features_per_group: int

class BuildTerritoriesByColumnSum(BaseModel):
    table: str
    column: str
    ideal_sum_of_column_per_territory: int
