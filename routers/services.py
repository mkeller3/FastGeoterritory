from fastapi import APIRouter, Request, BackgroundTasks

import models
import utilities
import territory_queries

router = APIRouter()

processes = {}

@router.get("/status/{process_id}", tags=["analysis"])
def status(process_id: str):
    if process_id not in processes:
        return {"status": "UNKNOWN", "error": "This process_id does not exist."}
    return processes[process_id]

@router.post("/build_territories_by_feature_count/")
async def map_suitability(info: models.BuildTerritoriesByFeatureCount, request: Request, background_tasks: BackgroundTasks):
    """
    Method to build territories based off of number of features per group.

    """

    process_id = utilities.get_new_process_id()

    process_url = str(request.base_url)

    process_url += f"api/v1/services/status/{process_id}"

    processes[process_id] = {
        "status": "PENDING"
    }

    background_tasks.add_task(
        territory_queries.build_territories_by_features_per_group,
        app=request.app,
        table=info.table,
        number_of_features_per_group=info.number_of_features_per_group,
        process_id=process_id
    )

    return {
        "process_id": process_id,
        "url": process_url
    }

@router.post("/build_territories_by_column_sum/")
async def map_suitability(info: models.BuildTerritoriesByColumnSum, request: Request, background_tasks: BackgroundTasks):
    """
    Method to build territories based off of sum of column

    """

    process_id = utilities.get_new_process_id()

    process_url = str(request.base_url)

    process_url += f"api/v1/services/status/{process_id}"

    processes[process_id] = {
        "status": "PENDING"
    }

    background_tasks.add_task(
        territory_queries.build_territories_by_sum_of_column_per_group,
        app=request.app,
        table=info.table,
        column=info.column,
        ideal_sum_of_column_per_territory=info.ideal_sum_of_column_per_territory,
        process_id=process_id
    )

    return {
        "process_id": process_id,
        "url": process_url
    }

@router.post("/build_territories_from_points_column/", tags=["Services"])
async def build_territories_from_points_column(info: models.BuildPolygonTerritoriesFromPointColumn, request: Request, background_tasks: BackgroundTasks):
    """
    Method to build polygon territories based off of points

    """

    process_id = utilities.get_new_process_id()

    process_url = str(request.base_url)

    process_url += f"api/v1/services/status/{process_id}"

    processes[process_id] = {
        "status": "PENDING"
    }

    background_tasks.add_task(
        territory_queries.build_territories_from_point_column,
        app=request.app,
        table=info.table,
        column=info.column,
        process_id=process_id
    )

    return {
        "process_id": process_id,
        "url": process_url
    }