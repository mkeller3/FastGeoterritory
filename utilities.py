from fastapi import FastAPI
import uuid

def get_new_process_id() -> str:
    """
    Method to return a new process id
    """

    return str(uuid.uuid4())

async def get_starting_id(app: FastAPI, table: str, geometry_column: str)-> int:
    """
    Method to determine to determine starting gid to generate new territory

    """

    pool = app.state.database

    async with pool.acquire() as con:


        query = f"""
            SELECT a.gid
            FROM "{table}" a
            CROSS JOIN "{table}" b
            WHERE a.gid != b.gid
            AND a.territory_number IS NULL
            AND b.territory_number IS NULL
            ORDER BY a.{geometry_column} <-> b.{geometry_column} DESC
            LIMIT 1
        """

        results = await con.fetchrow(query)

        return results['gid']

async def get_geometry_type(app: FastAPI, table: str)-> int:
    """
    Method to get geometry type of table

    """

    pool = app.state.database

    async with pool.acquire() as con:


        query = f"""
            SELECT ST_GeometryType(geom) as geom_type
            FROM "{table}" a
            LIMIT 1
        """

        results = await con.fetchrow(query)

        return results['geom_type']

async def set_point_geometry(app: FastAPI, table: str)-> int:
    """
    Method to add point geom column to table

    """

    pool = app.state.database

    async with pool.acquire() as con:

        query = f"""ALTER TABLE "{table}" DROP COLUMN IF EXISTS point_geom;"""

        await con.fetchrow(query)

        query = f"""ALTER TABLE "{table}" ADD COLUMN point_geom geometry(Point,4326);"""

        await con.fetchrow(query)

        query = f"""
            UPDATE "{table}" 
            SET point_geom = ST_Centroid(geom);
        """

        await con.fetchrow(query)

        query = f"""DROP INDEX IF EXISTS {table}_point_geom_index;"""

        await con.fetchrow(query)

        query = f"""CREATE INDEX {table}_point_geom_index ON "{table}" USING GIST (point_geom);"""

        await con.fetchrow(query)