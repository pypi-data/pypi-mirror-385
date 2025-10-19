#!/usr/bin/env python3

"""Generate a label from the given text."""
import argparse
import sys
from itertools import count
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

__version__ = "0.1"

I_DONT_KNOW_WHY_MEASURE_TEXT_GIVE_BAD_HEIGHT = 2


def font_exists(font_name: str):
    try:
        ImageFont.truetype(font_name, 10)
    except OSError:
        return False
    else:
        return True


def measure_text(font: ImageFont, text: str) -> tuple[int, int]:
    """Given a text string and a font, measure how much space the text takes."""
    image = Image.new("RGB", (1, 1), "white")
    draw = ImageDraw.Draw(image)
    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    width = right - left
    height = bottom - top
    return width, height


def find_biggest_font_size(font_name: str, text: str, max_width) -> int:
    """Given text string and a font name, find biggest the font size possible."""
    for font_size in count(7):
        font = ImageFont.truetype(font_name, font_size)
        width, _height = measure_text(font, text)
        if width > max_width:
            break
    return font_size - 1


def make_label(text: str, font_name: str, width: int, output_file: Path) -> None:
    font_size = find_biggest_font_size(font_name, text, max_width=width)
    font = ImageFont.truetype(font_name, font_size)
    text_width, text_height = measure_text(font, text)
    height = text_height * I_DONT_KNOW_WHY_MEASURE_TEXT_GIVE_BAD_HEIGHT

    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    draw.text((0, 0), text, font=font, fill="black")
    image.save(output_file)


def parse_arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--width", type=int, default=384)
    parser.add_argument("--font", default="LiberationSans-Regular.ttf")
    parser.add_argument("--output-file", default=Path("label.png"), type=Path)
    parser.add_argument("text")
    return parser.parse_args()


def main():
    args = parse_arguments()
    if not font_exists(args.font):
        print(f"Font {args.font} not found.", file=sys.stderr)
        return 1
    make_label(args.text, args.font, width=args.width, output_file=args.output_file)
    return 0


if __name__ == "__main__":
    sys.exit(main())
