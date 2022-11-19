# FastGeoterritory

FastGeoterritory is a geospatial api to help build territories for points, lines, and polygons based off of counts of features or a column within your data. FastGeoterritory is written in [Python](https://www.python.org/) using the [FastAPI](https://fastapi.tiangolo.com/) web framework. 

---

**Source Code**: <a href="https://github.com/mkeller3/FastGeoterritory" target="_blank">https://github.com/mkeller3/FastGeoterritory</a>

---

## Requirements

FastGeoterritory requires PostGIS >= 2.4.0.

## Configuration

In order for the api to work you will need to edit the .env with your database connections.

```
DB_HOST=localhost
DB_DATABASE=data
DB_USERNAME=postgres
DB_PASSWORD=postgres
DB_PORT=5432
```

## Usage

### Running Locally

To run the app locally `uvicorn main:app --reload`

### Production
Build Dockerfile into a docker image to deploy to the cloud.

## API

| Method | URL                                                                              | Description                                             |
| ------ | -------------------------------------------------------------------------------- | ------------------------------------------------------- |
| `GET` | `/api/v1/analysis/status/{process_id}`                                            | [Analysis Status](#Analysis-Status)  |
| `POST`  | `/api/v1/services/build_territories_by_feature_count/`                          | [Build Territories By Feature Count](#build-territories-by-feature-count)      |
| `POST`  | `/api/v1/services/build_territories_by_column_sum/`                             | [Build Territories By Column Sum](#build-territories-by-column-sum)  |
| `POST`  | `/api/v1/services/build_territories_from_points_column/`                        | [Build Territories From Points Column](#build-territories-from-points-column)  |
| `GET`  | `/api/v1/health_check`                                                           | Server health check: returns `200 OK`    |

## Endpoint Description's

## Analysis Status
Any time a territory map is being submitted to be built it given a process_id to have the territory be built in the background using [FastAPI's Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/). To check the
status of your territory being built you can call this endpoint with the process_id.

### Analysis Status - Example Call
```shell
/api/v1/services/status/472e29dc-91a8-41d3-b05f-cee34006e3f7
```

### Analysis Status - Example Output - Still Running
```json
{
    "status": "PENDING"
}
```

### Analysis Status - Example Output - Complete
```json
{
    "status": "SUCCESS",
    "new_table_id": "shnxppipxrppsdkozuroilkubktfodibtqorhucjvxlcdrqyhh",
    "completion_time": "2022-07-06T19:33:17.950059",
    "run_time_in_seconds": 1.78599
}
```

### Analysis Status - Example Output - Error
```json
{
    "status": "FAILURE",
    "error": "ERROR HERE",
    "completion_time": "2022-07-08T13:39:47.961389",
    "run_time_in_seconds": 0.040892
}
```

## Build Territories By Feature Count

### Description

Assign each feature into a territory based off of the number of features per territory. A new column will be added to the table called `territory_number`. This will distinguish what territory a feature is part. The api works by starting at one feature, and finding the x closest amount of features to that feature. Once it finds the x closest feature, all those features will be assigned that territory, and the loop will continue until all features are assigned a territory.

### Example

Build new random territories for all Chick Fil A locations with 100 stores in each territory.

### Example Input

```json
{
    "table": "chick_fil_a_locations",
    "number_of_features_per_territory": 100
}
```

### Example Output

```json
{
  "process_id": "c8d7b8d8-3e82-4f93-b441-55a5f51c4171",
  "url": "http://127.0.0.1:8000/api/v1/analysis/status/c8d7b8d8-3e82-4f93-b441-55a5f51c4171"
}
```

### Input Map

![chick fil a input map](/images/default.png)

### Output Map

![chick fil a feature_count map](/images/feature_count.png)

### Example Stats

| Territory Number | Number of Features |
|------------------|--------------------|
| 0                | 100                |
| 1                | 100                |
| 2                | 100                |
| 3                | 100                |
| 4                | 100                |
| 5                | 100                |
| 6                | 100                |
| 7                | 100                |
| 8                | 100                |
| 9                | 100                |
| 10               | 100                |
| 11               | 100                |
| 12               | 100                |
| 13               | 100                |
| 14               | 100                |
| 15               | 100                |
| 16               | 100                |
| 17               | 100                |
| 18               | 100                |
| 19               | 100                |
| 20               | 15                 |

## Build Territories By Column Sum

### Description

Assign each feature into a territory based off of the sum of a column. A new column will be added to the table called `territory_number`. This will distinguish what territory a feature is part. The api works by starting at one feature, and finding the closest features to that feature. Once it finds the closest feature, each feature will be assigned to the group until the `ideal_sum_of_column_per_territory` is met. Once met, it will start building a new group.

### Example

Build new random territories for all Chick Fil A locations with a sales volume of around $400,000.

### Example Input

```json
{
    "table": "chick_fil_a_locations",
    "column": "salesvol",
    "ideal_sum_of_column_per_territory": 400000
}
```

### Example Output

```json
{
  "process_id": "c8d7b8d8-3e82-4f93-b441-55a5f51c4171",
  "url": "http://127.0.0.1:8000/api/v1/analysis/status/c8d7b8d8-3e82-4f93-b441-55a5f51c4171"
}
```

### Input Map

![chick fil a input map](/images/default.png)

### Output Map

![chick fil a column_sum map](/images/column_sum.png)

### Example Stats

| Territory Number | Sum of Sales Volume |
|------------------|---------------------|
| 0                | 400009              |
| 1                | 401329              |
| 2                | 400659              |
| 3                | 402838              |
| 4                | 400434              |
| 5                | 401452              |
| 6                | 400668              |
| 7                | 400695              |
| 8                | 400414              |

## Build Territories From Points Column

### Description

Build polygon territories based off a column in a point table. This endpoint uses [ST_VoronoiPolygons](https://postgis.net/docs/ST_VoronoiPolygons.html) to generate smaller polygons for each feature. After each polygon is assigned, it will combine all polygons with the same column value into larger polygons.

### Example

Build new territories for all Chick Fil A locations based off of the `territory_number` column.

### Example Input

```json
{
    "table": "chick_fil_a_locations",
    "column": "territory_number",
}
```

### Example Output

```json
{
  "process_id": "c8d7b8d8-3e82-4f93-b441-55a5f51c4171",
  "url": "http://127.0.0.1:8000/api/v1/analysis/status/c8d7b8d8-3e82-4f93-b441-55a5f51c4171"
}
```

### Output Map

![chick fil a point_polygons map](/images/point_polygons.png)