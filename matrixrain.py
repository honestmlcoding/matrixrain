#!/usr/bin/env python3
import curses
import random
import time
import math
import argparse

# ---------------------------
# Color setup
# ---------------------------

def init_colors():
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN, -1)
    curses.init_pair(2, curses.COLOR_WHITE, -1)

# ---------------------------
# Matrix column model
# ---------------------------

class Column:
    def __init__(self, x, height):
        self.x = x
        self.reset(height)

    def reset(self, height):
        self.y = random.randint(-height, 0)
        self.speed = random.uniform(0.35, 1.15)
        self.length = random.randint(10, max(14, height // 2))

    def step(self, height):
        self.y += self.speed
        if self.y - self.length > height:
            self.reset(height)

# ---------------------------
# Main animation loop
# ---------------------------

def run(stdscr, seconds, fps):
    curses.curs_set(0)
    stdscr.nodelay(True)
    curses.noecho()
    curses.cbreak()

    init_colors()

    start_time = time.time()
    frame_delay = 0.3 / fps
    tick = 0

    rows, cols = stdscr.getmaxyx()

    # Two streams per column for higher density
    columns = []
    for x in range(cols):
        columns.append(Column(x, rows))
        columns.append(Column(x, rows))

    while True:
        now = time.time()
        if seconds > 0 and now - start_time >= seconds:
            break

        # Consume input silently (CTRL-C handled by wrapper)
        try:
            stdscr.getch()
        except Exception:
            pass

        # Handle terminal resize
        new_rows, new_cols = stdscr.getmaxyx()
        if (new_rows, new_cols) != (rows, cols):
            rows, cols = new_rows, new_cols
            columns = []
            for x in range(cols):
                columns.append(Column(x, rows))
                columns.append(Column(x, rows))
            stdscr.erase()

        # Soft clear less often to keep trails dense
        if tick % 12 == 0:
            stdscr.erase()

        cx, cy = cols // 2, rows // 2
        radius = int(min(rows, cols) * 0.35)

        for col in columns:
            col.step(rows)
            for i in range(col.length):
                y = int(col.y - i)
                if 0 <= y < rows:
                    dist = math.hypot(col.x - cx, y - cy)

                    # Emergent ring via brightness/density bias
                    ring_bias = abs(dist - radius)
                    in_ring = ring_bias < radius * 0.08

                    ch = '1' if random.random() > 0.5 else '0'

                    if i == 0:
                        attr = curses.color_pair(2) | curses.A_BOLD
                    elif in_ring and random.random() < 0.6:
                        attr = curses.color_pair(2)
                    else:
                        attr = curses.color_pair(1) | curses.A_DIM

                    try:
                        stdscr.addch(y, col.x, ch, attr)
                    except curses.error:
                        pass

        try:
            stdscr.refresh()
        except curses.error:
            pass

        tick += 1
        time.sleep(frame_delay)

# ---------------------------
# Entrypoint
# ---------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Matrix-style terminal rain with emergent ring pattern."
    )
    parser.add_argument(
        "--seconds", type=int, default=60,
        help="Run duration (0 = infinite). Default: 60"
    )
    parser.add_argument(
        "--fps", type=int, default=30,
        help="Frames per second. Default: 30"
    )
    args = parser.parse_args()

    try:
        curses.wrapper(lambda stdscr: run(stdscr, args.seconds, args.fps))
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
