from fastapi import FastAPI
import uuid

def get_new_process_id() -> str:
    """
    Method to return a new process id
    """

    return str(uuid.uuid4())

async def get_starting_id(app: FastAPI, table: str)-> int:
    """
    Method to determine to determine starting gid to generate new territory

    """

    pool = app.state.database

    async with pool.acquire() as con:


        query = f"""
            SELECT a.gid, ST_Distance(ST_Centroid(a.geom), ST_Centroid(b.geom)) as distance
            FROM "{table}" a
            CROSS JOIN "{table}" b
            WHERE a.gid != b.gid
            AND a.group_number IS NULL
            AND b.group_number IS NULL
            ORDER BY distance DESC
            LIMIT 1
        """

        results = await con.fetchrow(query)

        return results['gid']
