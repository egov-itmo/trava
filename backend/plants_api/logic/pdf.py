"""
Plants compositions PDF generation methods are defined here.
"""
import os
from decimal import Decimal
from math import ceil
from pathlib import Path

from borb.pdf import Document, FixedColumnWidthTable, Image, Page, Paragraph, SingleColumnLayout
from borb.pdf.canvas.font.simple_font.true_type_font import TrueTypeFont
from compositioner import Territory
from loguru import logger
from PIL import Image as PilImage

from plants_api.config.app_settings_global import app_settings
from plants_api.dto import PlantDto

_FONT = "Helvetica"
for possible_font_path in [
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    "C:/Windows/fonts/Arial.ttf",
    os.environ.get("FONT_PATH"),
    "font.ttf",
    "fonts/font.ttf",
]:
    if possible_font_path is None:
        continue
    font_path = Path(possible_font_path)
    if not font_path.exists():
        continue
    try:
        _FONT = TrueTypeFont.true_type_font_from_file(font_path)
    except AssertionError as exc:
        logger.warning("Error on loading font {}: {}", possible_font_path, exc.args)
    except Exception as exc:  # pylint: disable=broad-except
        logger.warning("Error on loading font {}: {!r}", possible_font_path, exc)
    else:
        logger.info("Using {} as pdf generation font", possible_font_path)
        break
if _FONT == "Helvetica":
    logger.opt(colors=True).error(
        "Could not locate font for pdf. Set full ttf font location in environment variable <green>FONT_PATH</green>"
        " or copy its file to the launch directory as <yellow>font.ttf</yellow>"
    )

_PAGE_SIZE = (1600, 1900)
_PLANTS_PER_PAGE = 10


def compositions_to_pdf(  # pylint: disable=too-many-locals,too-many-branches
    compositions: list[list[PlantDto]], territory: Territory
) -> Document:
    """
    Form a PDF file with a given compositions.
    """
    pdf = Document()
    page = Page(*_PAGE_SIZE)
    pdf.add_page(page)
    layout = SingleColumnLayout(page, Decimal(12.0), Decimal(12.0))
    layout.add(Paragraph(f"Next plants composition variants are possible for the given territory ({territory}):"))
    finished_first_composition = False
    for i, composition in enumerate(compositions, 1):
        if finished_first_composition:
            page = Page(*_PAGE_SIZE)
            pdf.add_page(page)
            layout = SingleColumnLayout(page, Decimal(12.0), Decimal(12.0))
        finished_first_composition = True
        layout.add(Paragraph(f"Option #{i} ({len(composition)} plants)"))
        table = FixedColumnWidthTable(
            1 + min(len(composition), _PLANTS_PER_PAGE),
            10,
            list(map(Decimal, [20, 20, 10, 10, 10, 10, 10, 10, 10, 20])),
        )
        finished_first_plants_page = False
        for j, plant in enumerate(composition):
            if j % _PLANTS_PER_PAGE == 0:
                if finished_first_plants_page:
                    try:
                        layout.add(table)
                    except AssertionError as exc:  # pylint: disable=redefined-outer-name
                        logger.warning("Could not insert page: {}", exc.args)
                    else:
                        page = Page(*_PAGE_SIZE)
                        pdf.add_page(page)
                    layout = SingleColumnLayout(page, Decimal(12.0), Decimal(12.0))
                    table = FixedColumnWidthTable(
                        1 + min(len(composition) - j, _PLANTS_PER_PAGE),
                        10,
                        list(map(Decimal, [20, 20, 10, 10, 10, 10, 10, 10, 10, 20])),
                    )
                finished_first_plants_page = True
                layout.add(
                    Paragraph(
                        f"Option #{i} - page {j // _PLANTS_PER_PAGE + 1} of"
                        f" {ceil(len(composition) / _PLANTS_PER_PAGE)}:"
                        f" plants {j + 1}..{min(len(composition), j + _PLANTS_PER_PAGE)}",
                        font=_FONT,
                    )
                )
                for column_name in (
                    "Название",
                    "Латинское название",
                    "Род",
                    "Тип",
                    "Высота",
                    "Размер кроны",
                    "Агрессивность",
                    "Выживаемость",
                    "Инвазивность",
                    "Фото",
                ):
                    table.add(Paragraph(column_name, font=_FONT))
            for cell_data in (
                plant.name_ru,
                plant.name_latin,
                plant.genus,
                plant.type,
                plant.height_avg,
                plant.crown_diameter,
                plant.spread_aggressiveness_level,
                plant.survivability_level,
                plant.is_invasive,
            ):
                table.add(
                    Paragraph(
                        ""
                        if cell_data is None
                        else "+"
                        if isinstance(cell_data, bool) and cell_data
                        else "-"
                        if isinstance(cell_data, bool)
                        else str(cell_data),
                        font=_FONT,
                    )
                )
            img_to_add = Paragraph("")
            if plant.thumbnail_url is not None:
                try:
                    pil_img = PilImage.open(
                        Path(app_settings.photos_dir) / plant.thumbnail_url[len(app_settings.photos_prefix) :]
                    )
                    img_to_add = Image(pil_img)
                except FileNotFoundError:
                    logger.warning(
                        "Thumbnail is not found for plant id={} (thumbnail '{}')", plant.id, plant.thumbnail_url
                    )
                except Exception as exc:  # pylint: disable=broad-except,redefined-outer-name
                    logger.warning("Could not add image {} to PDF: {}", plant.thumbnail_url, exc)
            table.add(img_to_add)
        try:
            layout.add(table)
        except AssertionError as exc:  # pylint: disable=redefined-outer-name
            logger.warning("Could not insert page: {}", exc.args)

    return pdf
