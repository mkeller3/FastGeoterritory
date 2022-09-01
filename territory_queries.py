import datetime
from fastapi import FastAPI

import utilities
from routers import services

async def build_territories_by_features_per_group(app: FastAPI, table: str, number_of_features_per_group: int, process_id: str):
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

            query = f"""ALTER TABLE "{table}" DROP COLUMN IF EXISTS group_number;"""

            await con.fetchrow(query)

            query = f"""ALTER TABLE "{table}" ADD COLUMN group_number integer;"""

            await con.fetchrow(query)

            number_of_groups = int(number_of_features / number_of_features_per_group)

            for i in range(0,number_of_groups):
                original_id = await utilities.get_starting_id(app, table)
                query = f"""
                    UPDATE "{table}"
                    SET group_number = {i}
                    WHERE gid in (
                        SELECT b.gid
                        FROM "{table}" a,
                        "{table}" b
                        WHERE a.gid = {original_id}
                        AND a.group_number IS NULL
                        AND b.group_number IS NULL
                        ORDER BY ST_Distance(ST_Centroid(a.geom), ST_Centroid(b.geom)) ASC
                        LIMIT {number_of_features_per_group}
                    )
                """

                await con.fetchrow(query)
            
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

            query = f"""ALTER TABLE "{table}" DROP COLUMN IF EXISTS group_number;"""

            await con.fetchrow(query)

            query = f"""ALTER TABLE "{table}" ADD COLUMN group_number integer;"""

            await con.fetchrow(query)

            counter = 0

            while number_of_features_assigned < number_of_features:
                original_id = await utilities.get_starting_id(app, table)
                query = f"""
                    SELECT b.gid, b."{column}"
                    FROM "{table}" a,
                    "{table}" b
                    WHERE a.gid = {original_id}
                    AND a.group_number IS NULL
                    AND b.group_number IS NULL
                    ORDER BY ST_Distance(ST_Centroid(a.geom), ST_Centroid(b.geom)) ASC
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
                    SET group_number = {counter}
                    WHERE gid in ('{gids_list}')
                """

                await con.fetch(query)

                counter += 1

            services.processes[process_id]['status'] = "SUCCESS"
            services.processes[process_id]['completion_time'] = datetime.datetime.now()
            services.processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start

    except Exception as error:
        services.processes[process_id]['status'] = "FAILURE"
        services.processes[process_id]['error'] = str(error)
        services.processes[process_id]['completion_time'] = datetime.datetime.now()
        services.processes[process_id]['run_time_in_seconds'] = datetime.datetime.now()-start