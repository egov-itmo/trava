"""
Derevo library usage example.

Run as `example` module
"""
import os
import sys

import matplotlib.pyplot as plt
from loguru import logger
from sqlalchemy import create_engine, text

from derevo.models.cohabitation import CohabitationType, GeneraCohabitation


try:
    import derevo as cm  # pylint: disable=unused-import
except ModuleNotFoundError:
    from pathlib import Path

    print("Derevo module cannot be imported as usual, trying to use local instance in parent directory")
    sys.path.append(Path(__file__).resolve().parent)
    import derevo as cm

from derevo import Plant, Territory
from derevo import enumerations as d_enum
from derevo import get_compositions
from derevo.optimal_resolution import get_best_resolution

from .data_collection import (
    collect_cohabitations,
    collect_light_polygons,
    collect_limitation_polygons,
    collect_plants,
    collect_plants_dataframe,
    collect_plants_suitable_for_light,
    collect_plants_with_limitation_resistance,
    collect_species_in_parks,
)


if __name__ == "__main__":
    logger.remove()
    logger.add(sys.stderr, level="DEBUG")

    # method usage example

    plants_list: list[Plant] = [
        Plant(
            name_ru="Название растения",
            name_latin="latin name",
            genus="Род растения",
            life_form="Жизненная форма",
            limitation_factors_resistances={
                d_enum.LimitationFactor.FLOODING: d_enum.ToleranceType.NEGATIVE,
                d_enum.LimitationFactor.GAS_POLLUTION: d_enum.ToleranceType.NEUTRAL,
            },
            humidity_preferences={
                d_enum.HumidityType.HIGH: d_enum.ToleranceType.NEGATIVE,
                d_enum.HumidityType.NORMAL: d_enum.ToleranceType.POSITIVE,
            },
            light_preferences={
                d_enum.LightType.LIGHT: d_enum.ToleranceType.POSITIVE,
            },
            usda_zone_preferences={
                d_enum.UsdaZone.USDA2: d_enum.ToleranceType.NEGATIVE,
                d_enum.UsdaZone.USDA3: d_enum.ToleranceType.NEUTRAL,
                d_enum.UsdaZone.USDA4: d_enum.ToleranceType.POSITIVE,
                d_enum.UsdaZone.USDA5: d_enum.ToleranceType.POSITIVE,
                d_enum.UsdaZone.USDA6: d_enum.ToleranceType.NEUTRAL,
                d_enum.UsdaZone.USDA7: d_enum.ToleranceType.NEGATIVE,
            },
            is_invasive=False,
        ),
    ]
    plants_present: list[Plant] = []
    territory_info = Territory(
        usda_zone=d_enum.UsdaZone.USDA5,
        limitation_factors=[d_enum.LimitationFactor.WINDINESS],
        humidity_types=[d_enum.HumidityType.NORMAL, d_enum.HumidityType.LOW],
        light_types=[d_enum.LightType.LIGHT, d_enum.LightType.DARKENED],
        soil_fertility_types=[d_enum.FertilityType.FERTIL, d_enum.FertilityType.SLIGHTLY_FERTIL],
    )

    cohabitation_attributes = [
        GeneraCohabitation("Род растения", "Род растения", CohabitationType.POSITIVE),
        GeneraCohabitation("Род растения", "Другой род растения", CohabitationType.NEGATIVE),
    ]
    composition_plants = get_compositions(
        plants_available=plants_list,
        cohabitation_attributes=cohabitation_attributes,
        territory=territory_info,
        plants_present=plants_present,
    )

    # get plants from database

    try:
        db_addr = os.environ["DB_ADDR"]
        db_port = os.environ.get("DB_PORT", 5432)
        db_name = os.environ["DB_NAME"]
        db_user = os.environ["DB_USER"]
        db_pass = os.environ["DB_PASS"]
    except KeyError as exc:
        print(
            "You must set environment variables DB_ADDR, DB_NAME, DB_USER and DB_PASS to launch this script."
            f" Missing {exc.args[0]}",
        )

    logger.opt(colors=True).info(
        "using <cyan>{}@{}:{}/{}</cyan> database connection", db_user, db_addr, db_port, db_name
    )

    try:
        engine = create_engine(
            f"postgresql://{db_user}:{db_pass}@{db_addr}:{db_port}/{db_name}"
        )  # psycopg2 is used here
        with engine.connect() as conn:
            assert conn.execute(text("SELECT 1")).scalar() == 1
    except Exception as exc:
        print(f"Could not establish database connection: {exc!r}")
        raise

    # new interface

    print("Collecting plants from the database")
    with engine.connect() as conn:
        plants = collect_plants(conn)
    conn.close()
    print(f"{len(plants)} collected")

    # old interface
    # getting limitation and plants factors from the database
    with engine.connect() as conn:
        logger.debug("collecting plants data")
        plants_list = collect_plants_dataframe(conn)
        plants_with_limitations_resistance = collect_plants_with_limitation_resistance(conn)
        plants_suitable_for_light = collect_plants_suitable_for_light(conn)
        cohabitation_attributes = collect_cohabitations(conn)

        logger.debug("collecting species in parks")
        species_in_parks = collect_species_in_parks(conn)

        logger.debug("collecting limitations and lights")
        limitations = collect_limitation_polygons(conn)
        light = collect_light_polygons(conn)
    conn.close()

    print("Launching get_best_resolution method. This may take upto 10-15 minutes, so you may hit Ctrl+C to skip")
    try:
        fig, ax = plt.subplots()
        best_resolution = get_best_resolution(
            plants_list, plants_with_limitations_resistance, plants_suitable_for_light, cohabitation_attributes, ax
        )
        IMG_NAME = "resolution_image.png"
        print(f"Saving image to {IMG_NAME}. Best resolution DataFrame:")
        plt.savefig(IMG_NAME)

        print(best_resolution)
    except KeyboardInterrupt:
        print("Skipping get_best_resolution")
