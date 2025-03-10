"""
Listing endpoints logic of getting entities from the database is defined here.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncConnection

from plants_api.db.entities import (
    humidity_types,
    light_types,
    limitation_factors,
    soil_acidity_types,
    soil_fertility_types,
    soil_types,
)
from plants_api.dto import ListingDto


async def get_humidity_types_from_db(connection: AsyncConnection) -> list[ListingDto]:
    """
    Get humidity types.
    """
    statement = select(humidity_types.c.id, humidity_types.c.name, humidity_types.c.description).order_by(
        humidity_types.c.id
    )
    return [ListingDto(idx, name, description) for idx, name, description in await connection.execute(statement)]


async def get_light_types_from_db(connection: AsyncConnection) -> list[ListingDto]:
    """
    Get light types.
    """
    statement = select(light_types.c.id, light_types.c.name, light_types.c.description).order_by(light_types.c.id)
    return [ListingDto(idx, name, description) for idx, name, description in await connection.execute(statement)]


async def get_limitation_factors_from_db(connection: AsyncConnection) -> list[ListingDto]:
    """
    Get limitation factors.
    """
    statement = select(limitation_factors.c.id, limitation_factors.c.name, limitation_factors.c.explanation).order_by(
        limitation_factors.c.id
    )
    return [ListingDto(idx, name, description) for idx, name, description in await connection.execute(statement)]


async def get_soil_fertility_types_from_db(connection: AsyncConnection) -> list[ListingDto]:
    """
    Get soil fertility types.
    """
    statement = select(
        soil_fertility_types.c.id, soil_fertility_types.c.name, soil_fertility_types.c.description
    ).order_by(soil_fertility_types.c.id)
    return [ListingDto(idx, name, description) for idx, name, description in await connection.execute(statement)]


async def get_soil_types_from_db(connection: AsyncConnection) -> list[ListingDto]:
    """
    Get soil types.
    """
    statement = select(soil_types.c.id, soil_types.c.name, soil_types.c.description).order_by(soil_types.c.id)
    return [ListingDto(idx, name, description) for idx, name, description in await connection.execute(statement)]


async def get_soil_acidity_types_from_db(connection: AsyncConnection) -> list[ListingDto]:
    """
    Get soil acidity types.
    """
    statement = select(soil_acidity_types.c.id, soil_acidity_types.c.name, soil_acidity_types.c.description).order_by(
        soil_acidity_types.c.id
    )
    return [ListingDto(idx, name, description) for idx, name, description in await connection.execute(statement)]
