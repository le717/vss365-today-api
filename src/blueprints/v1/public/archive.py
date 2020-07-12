from datetime import datetime
from pathlib import Path

from flask import current_app
import xlsxwriter

from src.blueprints import archive
from src.core import database, helpers
from src.core.auth_helpers import authorize_route
from src.core.database import archive as db_archive

from src.core.models.v1.Prompt import Prompt


@authorize_route
@archive.route("/", methods=["POST"])
def post():
    # TODO
    archive_years = database.prompt_get_years()
    archive_range = db_archive.prompt_date_range()
    oldest_date = helpers.format_datetime_pretty(archive_range["oldest"])
    newest_date = helpers.format_datetime_pretty(archive_range["newest"])

    # Put together the save path and file name
    today = datetime.now()
    today_iso = helpers.format_datetime_iso(today)
    today_pretty = helpers.format_datetime_pretty(today)
    file_name = f"vss365today-word-archive-{today_iso}.xlsx"
    save_dir = Path(current_app.config["DOWNLOADS_DIR"]).resolve()
    full_save_path = save_dir / file_name

    # Create a new spreadsheet file
    with xlsxwriter.Workbook(
        full_save_path, {"constant_memory": True, "default_date_format": "yyyy-mm-dd"}
    ) as workbook:
        # Start by creating a page with basic file generation info
        worksheet = workbook.add_worksheet("Info")
        worksheet.write(
            0, 0, f"#vss365 word archive from {oldest_date} to {newest_date}",
        )
        worksheet.write(1, 0, f"Generated by vss365today.com on {today_pretty}")
        worksheet.write(2, 0, "Sorted by date in reverse chronological order")
        worksheet.write_url(3, 0, "https://vss365today.com")

        # Group each year's prompts in their own sheet
        for year in archive_years:
            worksheet = workbook.add_worksheet(str(year))

            # Write the headings
            bolded_text = workbook.add_format()
            bolded_text.set_bold()
            worksheet.write(0, 0, "Date", bolded_text)
            worksheet.write(0, 1, "Word", bolded_text)
            worksheet.write(0, 2, "Host", bolded_text)
            worksheet.write(0, 3, "URL", bolded_text)

            # TODO
            for row, prompt in enumerate(db_archive.get_archive(year)):
                # TODO
                row += 1

                # TODO
                worksheet.write_datetime(row, 0, prompt.date)
                worksheet.write(row, 1, prompt.word)
                worksheet.write(row, 2, prompt.writer_handle)
                worksheet.write_url(
                    row, 3, Prompt.make_url(prompt.writer_handle, prompt.tweet_id)
                )

    # TODO Should there be a no-dup words option?
    # TODO Generate new spreadsheet
    # - https://xlsxwriter.readthedocs.io/getting_started.html
    # TODO Basic archive stats?
    # - Can these just be excel formulas?
    # TODO Delete old spreadsheet or maybe have a 5 day backup?
    # - Doing so would add a GET option to return the latest filename
    # TODO User-configurable "option" for sort order?
    return helpers.make_response(201)
