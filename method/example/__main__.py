"""
Compositioner usage example.

Run as `example` module
"""
import os
import sys

import matplotlib.pyplot as plt
from loguru import logger
from sqlalchemy import create_engine, text

try:
    import compositioner as cm
    from compositioner import get_composition, Territory, Plant
    from compositioner import enumerations as c_enums
except ModuleNotFoundError:
    from pathlib import Path

    print("Compositioner module cannot be imported as usual, trying to use local instance in parent directory")
    sys.path.append(Path(__file__).resolve().parent)
    import compositioner as cm

from .data_collection import (
    collect_cohabitations,
    collect_light_polygons,
    collect_limitation_polygons,
    collect_plants,
    collect_plants_suitable_for_light,
    collect_plants_with_limitation_resistance,
    collect_species_in_parks,
)

if __name__ == "__main__":
    logger.remove()
    logger.add(sys.stderr, level="DEBUG")

    # method usage example

    plants: list[Plant] = [
        Plant(
            name_ru="Название растения",
            name_latin="latin name",
            genus="Род растения",
            life_form="Жизненная форма",
            limitation_factors_resistances={
                c_enums.LimitationFactor.FLOODING: c_enums.ToleranceType.NEGATIVE,
                c_enums.LimitationFactor.GAS_POLLUTION: c_enums.ToleranceType.NEUTRAL,
            },
            humidity_preferences={
                c_enums.HumidityType.HIGH: c_enums.ToleranceType.NEGATIVE,
                c_enums.HumidityType.NORMAL: c_enums.ToleranceType.POSITIVE,
            },
            light_preferences={
                c_enums.LightType.LIGHT: c_enums.ToleranceType.POSITIVE,
            },
            usda_zone_preferences={
                c_enums.UsdaZone.USDA2: c_enums.ToleranceType.NEGATIVE,
                c_enums.UsdaZone.USDA3: c_enums.ToleranceType.NEUTRAL,
                c_enums.UsdaZone.USDA4: c_enums.ToleranceType.POSITIVE,
                c_enums.UsdaZone.USDA5: c_enums.ToleranceType.POSITIVE,
                c_enums.UsdaZone.USDA6: c_enums.ToleranceType.NEUTRAL,
                c_enums.UsdaZone.USDA7: c_enums.ToleranceType.NEGATIVE,
            },
            is_invasive=False,
        ),
    ]
    plants_present: list[Plant] = []
    territory_info = Territory(
        usda_zone=c_enums.UsdaZone.USDA5,
        limitation_factors=[c_enums.LimitationFactor.WINDINESS],
        humidity_types=[c_enums.HumidityType.NORMAL, c_enums.HumidityType.LOW],
        light_types=[c_enums.LightType.LIGHT, c_enums.LightType.DARKENED],
        soil_fertility_types=[c_enums.FertilityType.FERTIL, c_enums.FertilityType.SLIGHTLY_FERTIL],
    )
    composition_plants = get_composition(plants_available=plants, territory=territory_info, plants_present=plants_present)

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

    # getting limitation factors from the database

    try:
        engine = create_engine(
            f"postgresql://{db_user}:{db_pass}@{db_addr}:{db_port}/{db_name}"
        )  # psycopg2 is used here
        with engine.connect() as conn:
            assert conn.execute(text("SELECT 1")).scalar() == 1
    except Exception as exc:
        print(f"Could not establish database connection: {exc!r}")
        raise

    with engine.connect() as conn:
        logger.debug("collecting plants data")
        plants = collect_plants(conn)
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
        best_resolution = cm.get_best_resolution(
            plants, plants_with_limitations_resistance, plants_suitable_for_light, cohabitation_attributes, ax
        )
        IMG_NAME = "resolution_image.png"
        print(f"Saving image to {IMG_NAME}. Best resolution DataFrame:")
        plt.savefig(IMG_NAME)

        print(best_resolution)
    except KeyboardInterrupt:
        print("Skipping get_best_resolution")

    # GRAPH_NAME = "recommended_graph.gexf"
    # print(f"Writing recommended graph for a polygon to {GRAPH_NAME}")
    # cm.write_recommended_composition_gexf(
    #     plants,
    #     plants_with_limitations_resistance,
    #     plants_suitable_for_light,
    #     limitations,
    #     light,
    #     cohabitation_attributes,
    #     polygon, # FIXME: polygon is needed here
    #     GRAPH_NAME
    # )
