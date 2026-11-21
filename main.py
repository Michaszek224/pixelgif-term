from PIL import Image
import numpy as np
import os
import argparse
import time


def load_frames(path: str, width: int | None) -> tuple[list[np.ndarray], list[int]]:
    img = Image.open(path)
    frames_count = getattr(img, "n_frames", 1)

    new_size = compute_size(img, width)
    frames = []
    durations = []

    for i in range(frames_count):
        img.seek(i)
        img_changed = img.convert("RGB")  # if case of argb, we dont need alpha channel
        array = np.array(img_changed.resize(new_size))
        frames.append(array)
        duration = img.info.get("duration", 100)
        durations.append(duration)

    return frames, durations


def compute_size(img: Image.Image, width: int | None) -> tuple[int, int]:
    columns, lines = os.get_terminal_size()
    if width is not None:
        columns = width
    max_w = columns
    max_h = (lines - 2) * 2  # again columns are bigger then rows

    # scalling to terminal size
    w, h = img.size

    scale = min(max_w / w, max_h / h, 1)
    new_size = (int(w * scale), int(h * scale))

    return new_size


def play(frames: list[np.ndarray], duration: list[int]) -> None:
    print(len(frames))
    if len(frames) == 1:
        print_frame(frames[0])
        return
    while True:
        zipped = zip(frames, duration)
        for frame, ms in zipped:
            print_frame(frame)
            if ms == 0:
                ms = 100
            time.sleep(ms / 1000)
            n = frame.shape[0] // 2
            print(f"\033[{n}A", end="")


def print_frame(array: np.ndarray) -> None:
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


def main() -> None:
    parser = argparse.ArgumentParser(description="Image for pixel art in terminal")
    parser.add_argument(
        "path",
        help="name of image in images foler. Example: car.jpg for images/car.jpg",
    )
    parser.add_argument("--width", type=int, default=None, help="width of pixel art")
    args = parser.parse_args()

    frames, duration = load_frames(f"images/{args.path}", width=args.width)
    play(frames, duration)


if __name__ == "__main__":
    main()
