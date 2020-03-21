from pathlib import Path, PurePath
import secrets
from typing import Dict, Literal
from urllib import parse

import requests

from src.core.config import load_app_config

__all__ = [
    "delete",
    "download",
    "move",
    "saved_name"
]


CONFIG = load_app_config()


def delete(prompt_id: str) -> Literal[True]:
    """Delete a media file."""
    f_name = [
        f
        for f in Path(CONFIG["IMAGES_DIR"]).iterdir()
        if f.is_file() and f.name.startswith(prompt_id)
    ]
    if len(f_name) == 1:
        f_name[0].unlink()
    return True


def download(prompt_id: str, url: str) -> Dict[str, str]:
    # Generate a random file name for the download
    original_f_name = original_name(url)
    temp_f_name = "{name}{ext}".format(
        name=secrets.token_hex(12),
        ext=PurePath(original_f_name).suffix
    )

    # Download the media to a temp directory
    r = requests.get(url)
    dl_path = Path(CONFIG["IMAGES_DIR_TEMP"]).resolve() / temp_f_name
    dl_path.write_bytes(r.content)

    # Return the original and temp file name
    return {
        "original": original_f_name,
        "temp": temp_f_name,
        "final": saved_name(prompt_id, url)
    }


def move(details: dict) -> bool:
    """Move a media file from the temporary directory to final location."""
    current_path = Path(CONFIG["IMAGES_DIR_TEMP"]) / details["temp"]
    final_path = Path(CONFIG["IMAGES_DIR"]) / details["final"]
    current_path.replace(final_path)
    return final_path.is_file()


def original_name(url: str) -> str:
    """Extract the media file name from its URL."""
    # Extract the media filename from the URL
    name = parse.urlsplit(url).path.split("/")[2]

    # If there's a colon in the filename,
    # it means there's an image size tag.
    # We want to remove this from the filename
    if ":" in name:
        name = name[:name.find(":")]
    return name


def saved_name(prompt_id: str, url: str) -> str:
    """Generate the media's saved file name."""
    return "{id}-{original}".format(
        id=prompt_id,
        original=original_name(url)
    )