import datetime
from fastapi import FastAPI

import utilities
from routers import services

async def generate_territory_column(app: FastAPI, table: str, number_of_features_per_territories: int, number_of_territories: int):
    pool = app.state.database

    async with pool.acquire() as con:
        geometry_type = await utilities.get_geometry_type(app, table)

        geometry_column = "geom"

        if 'Point' not in geometry_type:

            await utilities.set_point_geometry(app, table)

            geometry_column = "point_geom"

        for i in range(0,number_of_territories):
            original_id = await utilities.get_starting_id(app, table, geometry_column)

            query = f"""
                UPDATE "{table}"
                SET territory_number = {i}
                WHERE gid in (
                    SELECT b.gid
                    FROM "{table}" a,
                    "{table}" b
                    WHERE a.gid = {original_id}
                    AND a.territory_number IS NULL
                    AND b.territory_number IS NULL
                    ORDER BY a.{geometry_column} <-> b.{geometry_column} ASC
                    LIMIT {number_of_features_per_territories}
                )
            """

            await con.fetchrow(query)
    
    query = f"""
        UPDATE "{table}"
        SET territory_number = {number_of_territories}
        WHERE territory_number IS NULL
    """

    await con.fetchrow(query)
    
    if 'Point' not in geometry_type:
        query = f"""ALTER TABLE "{table}" DROP COLUMN IF EXISTS point_geom;"""

        await con.fetchrow(query)

async def build_territories_by_group_count(app: FastAPI, table: str, number_of_territories: int, process_id: str):
    """
    Method to build territories based off of number of groups.

    """

    start = datetime.datetime.now()

    try:

        pool = app.state.database

        async with pool.acquire() as con:

            query = f"""
                SELECT COUNT(*)
                FROM "{table}" a
            """

            results = await con.fetchrow(query)

            number_of_features = results['count']

            number_of_features_per_territories = int(number_of_features / number_of_territories) + 1

            await generate_territory_column(app, table, number_of_features_per_territories, number_of_territories)

            services.processes[process_id]['status'] = "SUCCESS"
            services.processes[process_id]['completion_time'] = datetime.datetime.now()
            services.processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start

    except Exception as error:
        services.processes[process_id]['status'] = "FAILURE"
        services.processes[process_id]['error'] = str(error)
        services.processes[process_id]['completion_time'] = datetime.datetime.now()
        services.processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start


async def build_territories_by_features_per_group(app: FastAPI, table: str, number_of_features_per_territories: int, process_id: str):
    """
    Method to build territories based off of number of features per group.

    """

    start = datetime.datetime.now()

    try:

        pool = app.state.database

        async with pool.acquire() as con:

            query = f"""
                SELECT COUNT(*)
                FROM "{table}" a
            """

            results = await con.fetchrow(query)

            number_of_features = results['count']

            query = f"""ALTER TABLE "{table}" DROP COLUMN IF EXISTS territory_number;"""

            await con.fetchrow(query)

            query = f"""ALTER TABLE "{table}" ADD COLUMN territory_number integer;"""

            await con.fetchrow(query)

            number_of_territories = int(number_of_features / number_of_features_per_territories)

            await generate_territory_column(app, table, number_of_features_per_territories, number_of_territories)
            
            services.processes[process_id]['status'] = "SUCCESS"
            services.processes[process_id]['completion_time'] = datetime.datetime.now()
            services.processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start
    except Exception as error:
        services.processes[process_id]['status'] = "FAILURE"
        services.processes[process_id]['error'] = str(error)
        services.processes[process_id]['completion_time'] = datetime.datetime.now()
        services.processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start

async def build_territories_by_sum_of_column_per_group(app: FastAPI, table: str, column: str, ideal_sum_of_column_per_territory: int, process_id: str):
    """
    Method to build territories based off of sum of column

    """

    start = datetime.datetime.now()

    try:

        pool = app.state.database

        async with pool.acquire() as con:

            query = f"""
                SELECT COUNT(*)
                FROM "{table}" a
            """

            results = await con.fetchrow(query)

            number_of_features = results['count']

            number_of_features_assigned = 0

            query = f"""ALTER TABLE "{table}" DROP COLUMN IF EXISTS territory_number;"""

            await con.fetchrow(query)

            query = f"""ALTER TABLE "{table}" ADD COLUMN territory_number integer;"""

            await con.fetchrow(query)

            counter = 0

            geometry_type = await utilities.get_geometry_type(app, table)

            geometry_column = "geom"

            if 'Point' not in geometry_type:

                await utilities.set_point_geometry(app, table)

                geometry_column = "point_geom"

            while number_of_features_assigned < number_of_features:
                original_id = await utilities.get_starting_id(app, table, geometry_column)

                query = f"""
                    SELECT b.gid, b."{column}"
                    FROM "{table}" a,
                    "{table}" b
                    WHERE a.gid = {original_id}
                    AND a.territory_number IS NULL
                    AND b.territory_number IS NULL
                    ORDER BY a.{geometry_column} <-> b.{geometry_column} ASC
                """

                features = await con.fetch(query)

                total_territory_sum = 0

                gids = []
                
                for feature in features:
                    if total_territory_sum < ideal_sum_of_column_per_territory:
                        gids.append(str(feature['gid']))
                        total_territory_sum += feature[column]
                        number_of_features_assigned += 1

                gids_list = "','".join(gids)

                query = f"""
                    UPDATE "{table}"
                    SET territory_number = {counter}
                    WHERE gid in ('{gids_list}')
                """

                await con.fetch(query)

                counter += 1
            
            if 'Point' not in geometry_type:
                query = f"""ALTER TABLE "{table}" DROP COLUMN IF EXISTS point_geom;"""

                await con.fetchrow(query)

            services.processes[process_id]['status'] = "SUCCESS"
            services.processes[process_id]['completion_time'] = datetime.datetime.now()
            services.processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start

    except Exception as error:
        services.processes[process_id]['status'] = "FAILURE"
        services.processes[process_id]['error'] = str(error)
        services.processes[process_id]['completion_time'] = datetime.datetime.now()
        services.processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start


async def build_territories_from_point_column(app: FastAPI, table: str, column: int, process_id: str):
    """
    Method to build territories based off of point column.

    """

    start = datetime.datetime.now()

    try:

        pool = app.state.database

        async with pool.acquire() as con:

            query = f"""
                DROP TABLE IF EXISTS {table}_polygons;
            """

            await con.fetchrow(query)

            query = f"""
                CREATE TABLE {table}_polygons
                AS WITH voronoi_polygons (voronoi_geom)
                    AS (
                        SELECT ST_Dump(ST_VoronoiPolygons(ST_Collect(geom)))
                        FROM "{table}"
                    ) 
                SELECT (voronoi_geom).geom 
                FROM voronoi_polygons;
            """

            await con.fetchrow(query)

            query = f"""
                DROP TABLE IF EXISTS {table}_bounds;
            """

            await con.fetchrow(query)

            query = f"""
                CREATE TABLE {table}_bounds as
                SELECT ST_Envelope(ST_Union(geom)) as geom
                FROM "{table}";
            """

            await con.fetchrow(query)

            query = f"""
                DROP TABLE IF EXISTS {table}_polygons_clipped;
            """

            await con.fetchrow(query)

            query = f"""
                CREATE TABLE {table}_polygons_clipped as
                SELECT ST_Intersection(a.geom,b.geom) AS geom
                FROM {table}_polygons as a
                JOIN {table}_bounds as b
                ON ST_INTERSECTS(a.geom, b.geom);
            """

            await con.fetchrow(query)

            query = f"""
                ALTER TABLE {table}_polygons_clipped ADD COLUMN {column} integer;
            """

            await con.fetchrow(query)

            query = f"""
                UPDATE {table}_polygons_clipped as a
                SET {column} = b.{column}
                FROM "{table}" as b
                WHERE ST_INTERSECTS(a.geom, b.geom);
            """

            await con.fetchrow(query)

            new_table_id = utilities.get_new_table_id()

            query = f"""
                DROP TABLE IF EXISTS {new_table_id};	
            """

            await con.fetchrow(query)            

            query = f"""
                CREATE TABLE {new_table_id} AS
                SELECT DISTINCT({column}), ST_Union(geom) as geom
                FROM {table}_polygons_clipped
                GROUP BY {column};
            """

            await con.fetchrow(query)

            query = f"""
                DROP TABLE IF EXISTS {table}_polygons;
            """

            await con.fetchrow(query)

            query = f"""
                DROP TABLE IF EXISTS {table}_polygons_clipped;
            """

            await con.fetchrow(query)

            query = f"""
                DROP TABLE IF EXISTS {table}_bounds;
            """

            await con.fetchrow(query)

        services.processes[process_id]['status'] = "SUCCESS"
        services.processes[process_id]['table_id'] = new_table_id
        services.processes[process_id]['completion_time'] = datetime.datetime.now()
        services.processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start

    except Exception as error:
        services.processes[process_id]['status'] = "FAILURE"
        services.processes[process_id]['error'] = str(error)
        services.processes[process_id]['completion_time'] = datetime.datetime.now()
        services.processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start