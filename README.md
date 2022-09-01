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
| `GET`  | `/api/v1/health_check`                                                           | Server health check: returns `200 OK`    |

## Endpoint Description's

## Analysis Status
Any time an analysis is submitted it given a process_id to have the analysis run in the background using [FastAPI's Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/). To check the
status of an analysis, you can call this endpoint with the process_id.

## Example Call
```shell
/api/v1/analysis/status/472e29dc-91a8-41d3-b05f-cee34006e3f7
```

## Example Output - Still Running
```json
{
    "status": "PENDING"
}
```

## Example Output - Complete
```json
{
    "status": "SUCCESS",
    "new_table_id": "shnxppipxrppsdkozuroilkubktfodibtqorhucjvxlcdrqyhh",
    "completion_time": "2022-07-06T19:33:17.950059",
    "run_time_in_seconds": 1.78599
}
```

## Example Output - Error
```json
{
    "status": "FAILURE",
    "error": "ERROR HERE",
    "completion_time": "2022-07-08T13:39:47.961389",
    "run_time_in_seconds": 0.040892
}
```
