from PIL import Image
import numpy as np
import os
import argparse


def print_in_terminal(array: np.ndarray):
    rows, columns, _ = array.shape
    rows = rows - rows % 2  # in case of odd rows

    for row in range(0, rows, 2):  # usuall column * 2 = row
        for column in range(columns):
            r1, g1, b1 = array[row, column]
            r2, g2, b2 = array[row + 1, column]
            print(
                f"\033[38;2;{r1};{g1};{b1}m"  # character colour (foreground) --> upper pixel
                f"\033[48;2;{r2};{g2};{b2}m"  # background colour ---> bottom piksel
                "▀"  # writing block
                "\033[0m",  # reseting to default
                end="",  # no new line
            )
        print()


def load_and_resize(path: str, width: int) -> np.ndarray:
    img = Image.open(path)
    img = img.convert("RGB")  # if case of argb, we dont need alpha channel

    columns, lines = os.get_terminal_size()
    if width is not None:
        columns = width
    max_w = columns
    max_h = (lines - 2) * 2  # again columns are bigger then rows

    # scalling to terminal size
    w, h = img.size
    scale = min(max_w / w, max_h / h)
    new_size = (int(w * scale), int(h * scale))

    array = np.array(img.resize(new_size))
    return array


def main():
    parser = argparse.ArgumentParser(description="Image for pixel art in terminal")
    parser.add_argument(
        "path",
        help="name of image in images foler. Example: car.jpg for images/car.jpg",
    )
    parser.add_argument("--width", type=int, default=None, help="width of pixel art")
    args = parser.parse_args()

    array = load_and_resize(f"images/{args.path}", width=args.width)
    print_in_terminal(array)


if __name__ == "__main__":
    main()
