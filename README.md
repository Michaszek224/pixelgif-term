# pixelgif-term

Printing JPGs, PNGs and GIFs in the terminal.

### Tech Stack

- Python
- Pillow for image handling
- NumPy for data handling

### How to run

```
uv run main.py <path-to-image>
```

For example:

```
uv run main.py cat.jpg
```

GIFs loop until you press `Ctrl+C`.

### How it works

The program parses an image / GIF into numpy arrays, then prints them to the terminal using a trick with the `▀` character: its font colour is the upper pixel and its background colour is the lower pixel. That way one line of the terminal shows 2 rows of pixels.

### Limitations

- Needs a terminal with 24-bit (truecolor) colours, in my case alacritty works
- Images are only scaled down, never up

### Reason to build

- Another project to level up skills
- Animation in background to feed my ADHD
