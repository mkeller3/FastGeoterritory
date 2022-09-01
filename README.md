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
| `POST`  | `/api/v1/services/build_territories_by_feature_count/`                          | [Build Territories By Feature Count](#build-territories-by-feature-count)      |
| `POST`  | `/api/v1/services/build_territories_by_column_sum/`                             | [Build Territories By Column Sum](#build-territories-by-column-sum)  |
| `GET`  | `/api/v1/health_check`                                                           | Server health check: returns `200 OK`    |


