import argparse
import shutil
import time
import sys

from PIL import Image
import numpy as np


def load_frames(path: str) -> tuple[list[np.ndarray], list[int]]:
    img = Image.open(path)
    frames_count = getattr(img, "n_frames", 1)

    new_size = compute_size(img)
    frames = []
    durations = []

    for i in range(frames_count):
        img.seek(i)
        img_changed = img.convert("RGB")  # if case of rgba, we dont need alpha channel
        array = np.array(img_changed.resize(new_size))
        frames.append(array)
        duration = img.info.get("duration", 100)
        durations.append(duration)

    return frames, durations


def cell_ratio(default: float = 2.0) -> float:
    # works only on unix machines, sry windows users :(
    try:
        import fcntl
        import struct
        import termios

        packed = fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, b"\0" * 8)
        rows, cols, xpix, ypix = struct.unpack("HHHH", packed)
    except (ImportError, OSError):
        return default

    if not (rows and cols and xpix and ypix):
        return default

    return (ypix / rows) / (xpix / cols)


def compute_size(img: Image.Image) -> tuple[int, int]:
    columns, lines = shutil.get_terminal_size()

    max_w = max(1, columns)  # width cant be 0
    max_h = max(2, (lines - 2) * 2)  # again columns are bigger then rows

    # scalling to terminal size
    w, h = img.size
    correction = cell_ratio() / 2
    h_corrected = h / correction

    scale = min(max_w / w, max_h / h_corrected, 1)
    new_size = (
        max(1, int(w * scale)),
        max(1, int(h_corrected * scale)),
    )  # handling bad scaling

    return new_size


def play(frames: list[np.ndarray], durations: list[int]) -> None:
    if len(frames) == 1:
        print(render_frame(frames[0]), end="")
        return

    print("\033[?25l", end="")  # hide cursor
    print("\033[?1049h", end="")  # alternative screen

    try:
        rendered = []
        for frame in frames:
            rendered.append(render_frame(frame))

        next_at = time.perf_counter()  # start timer
        while True:
            zipped = zip(rendered, durations)
            for rendered_frame, ms in zipped:
                print("\033[H", end="")  # cursor to top left

                print(rendered_frame, end="", flush=True)  # printing pre-rendered frame
                if ms == 0:
                    ms = 100

                next_at += ms / 1000  # when new frame should be shown

                # time to new frame, including time taken for prining
                delay = next_at - time.perf_counter()
                if delay > 0:
                    time.sleep(delay)
                else:
                    next_at = time.perf_counter()

    except KeyboardInterrupt:
        pass
    finally:
        print("\033[?25h", end="")  # show cursor
        print("\033[?1049l", end="")  # back to terminal before gif


def render_frame(array: np.ndarray) -> str:
    rows, columns, _ = array.shape
    rows = rows - rows % 2  # in case of odd rows

    parts = []
    for row in range(0, rows, 2):  # usuall column * 2 = row
        for column in range(columns):
            r1, g1, b1 = array[row, column]
            r2, g2, b2 = array[row + 1, column]
            parts.append(
                f"\033[38;2;{r1};{g1};{b1}m"  # character colour (foreground) --> upper pixel
                f"\033[48;2;{r2};{g2};{b2}m"  # background colour ---> bottom piksel
                "▀"  # writing block
                "\033[0m"  # reseting to default
            )
        parts.append("\n")
    return "".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser(description="Image for pixel art in terminal")
    parser.add_argument(
        "path",
        help="path to image",
    )
    args = parser.parse_args()

    try:
        frames, durations = load_frames(args.path)
    except FileNotFoundError:
        parser.error(f"File not found: {args.path}")
    except OSError as e:
        parser.error(f"Cannot open image: {e}")

    play(frames, durations)


if __name__ == "__main__":
    main()
