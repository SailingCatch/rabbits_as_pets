"""
Draw the small icons used in the picture charts (houses, people, pets,
rabbits, a hare) and save them as SVG path strings in one file:

    data/icons.json   [{"name": "house", "path": "M..."}, ...]

Vega-Lite draws a point mark in any shape given as an SVG path that fits
the square from -1 to 1. Each chart looks its icon up by name, so every
chart uses the same drawings.

Each icon is built from simple pieces (ellipses, circles, polygons) and then
scaled to fit the square. All pieces are drawn clockwise so that, where they
overlap, they merge into one silhouette instead of cutting holes.

Usage (from the project folder):
    python3 scripts/make_icons.py
"""

import json
import math
from pathlib import Path

OUTPUT = Path("data/icons.json")


# ---- Pieces -------------------------------------------------------------------
# Each piece returns (path commands, points on its outline). The points are
# only used to find the icon's size so it can be scaled to fit.

def ellipse(cx, cy, rx, ry, angle=0):
    """An ellipse rx wide and ry tall, then turned clockwise by `angle`
    degrees (so a tall ear tilted forward is a small negative angle). Drawn
    as two half-ellipse arcs."""
    a = math.radians(angle)
    ux, uy = math.cos(a) * rx, math.sin(a) * rx     # half the long axis
    start, end = (cx - ux, cy - uy), (cx + ux, cy + uy)
    commands = [("M", start), ("A", (rx, ry, angle, end)), ("A", (rx, ry, angle, start)), ("Z",)]
    outline = [(cx + math.cos(t) * rx * math.cos(a) - math.sin(t) * ry * math.sin(a),
                cy + math.cos(t) * rx * math.sin(a) + math.sin(t) * ry * math.cos(a))
               for t in (i * math.pi / 18 for i in range(36))]
    return commands, outline


def circle(cx, cy, r):
    return ellipse(cx, cy, r, r)


def polygon(points):
    """A closed shape through the points, turned clockwise if it isn't."""
    area = sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(points, points[1:] + points[:1]))
    if area < 0:
        points = points[::-1]
    commands = [("M", points[0])] + [("L", p) for p in points[1:]] + [("Z",)]
    return commands, points


def rect(x0, y0, x1, y1):
    return polygon([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])


# ---- Icons --------------------------------------------------------------------
# Drawn facing left, in a box roughly -1..1 (y grows downwards, as in SVG).

ICONS = {
    "house": [polygon([(0, -1), (1, -0.1), (0.72, -0.1), (0.72, 0.95), (-0.72, 0.95), (-0.72, -0.1), (-1, -0.1)])],

    "person": [
        circle(0, -0.62, 0.3),
        polygon([(-0.62, 1), (-0.62, 0.25), (-0.45, 0.0), (0, -0.1), (0.45, 0.0), (0.62, 0.25), (0.62, 1)]),
    ],

    # Wild rabbit: sitting, ears straight up, lean
    "wild_rabbit": [
        ellipse(0.15, 0.42, 0.6, 0.4, -12),
        circle(-0.42, 0.0, 0.27),
        ellipse(-0.48, -0.55, 0.09, 0.36, -15),
        ellipse(-0.3, -0.53, 0.09, 0.36, 10),
        circle(0.78, 0.28, 0.13),
        ellipse(-0.25, 0.78, 0.18, 0.08),
    ],

    # Pet rabbit: rounder, with floppy "lop" ears hanging beside the head
    "pet_rabbit": [
        ellipse(0.15, 0.4, 0.62, 0.48, -5),
        circle(-0.38, -0.12, 0.32),
        ellipse(-0.66, 0.2, 0.11, 0.34, 18),
        circle(0.8, 0.3, 0.13),
        ellipse(-0.3, 0.82, 0.2, 0.08),
    ],

    # Hare: long legs, long ears, stretched out mid-run
    "hare": [
        ellipse(0.1, 0.15, 0.62, 0.27, -12),
        circle(-0.55, -0.02, 0.2),
        ellipse(-0.44, -0.48, 0.07, 0.42, -30),
        ellipse(-0.32, -0.46, 0.07, 0.4, -15),
        ellipse(0.55, 0.45, 0.11, 0.42, -35),
        ellipse(-0.3, 0.45, 0.06, 0.36, 20),
        circle(0.78, 0.0, 0.1),
    ],

    "dog": [
        ellipse(0.05, 0.05, 0.58, 0.28),
        circle(-0.55, -0.24, 0.25),
        ellipse(-0.82, -0.16, 0.15, 0.1),
        ellipse(-0.45, -0.24, 0.09, 0.2, 20),
        rect(-0.45, 0.1, -0.31, 0.88),
        rect(-0.2, 0.1, -0.06, 0.88),
        rect(0.27, 0.1, 0.41, 0.88),
        rect(0.48, 0.1, 0.62, 0.88),
        ellipse(0.7, -0.2, 0.06, 0.28, 40),
    ],

    "cat": [
        ellipse(0, 0.48, 0.45, 0.48),
        circle(0, -0.35, 0.33),
        polygon([(-0.32, -0.5), (-0.3, -0.98), (-0.05, -0.64)]),
        polygon([(0.32, -0.5), (0.05, -0.64), (0.3, -0.98)]),
        ellipse(0.42, 0.7, 0.07, 0.3, -50),
    ],

    "fish": [
        ellipse(-0.12, 0, 0.66, 0.42),
        polygon([(0.42, 0), (1, -0.48), (1, 0.48)]),
    ],

    "bird": [
        ellipse(0.08, 0.15, 0.55, 0.38, -15),
        circle(-0.45, -0.32, 0.26),
        polygon([(-0.68, -0.38), (-0.98, -0.26), (-0.68, -0.18)]),
        polygon([(0.48, 0.18), (1, 0.0), (0.95, 0.38)]),
        rect(-0.05, 0.48, 0.02, 0.85),
        rect(0.15, 0.48, 0.22, 0.85),
    ],

    # Small mammal: a mouse / guinea-pig shape
    "small_mammal": [
        ellipse(0.1, 0.3, 0.6, 0.42),
        ellipse(-0.55, 0.15, 0.32, 0.26),
        circle(-0.45, -0.15, 0.17),
        ellipse(0.82, 0.5, 0.26, 0.04, 30),
    ],

    # Reptile: a lizard seen from above
    "reptile": [
        ellipse(0, 0.05, 0.2, 0.55),
        ellipse(0, -0.65, 0.15, 0.22),
        ellipse(0.06, 0.78, 0.07, 0.3, 75),
        ellipse(-0.32, -0.28, 0.22, 0.06, -30),
        ellipse(0.32, -0.28, 0.22, 0.06, 30),
        ellipse(-0.32, 0.35, 0.22, 0.06, 30),
        ellipse(0.32, 0.35, 0.22, 0.06, -30),
    ],
}


# ---- Fit and write --------------------------------------------------------------

def to_path(pieces):
    """Scale and centre the pieces to fill -1..1, then write one SVG path."""
    points = [p for _, outline in pieces for p in outline]
    xs, ys = [x for x, _ in points], [y for _, y in points]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    k = 2 / max(max(xs) - min(xs), max(ys) - min(ys))

    def pt(x, y):
        return f"{(x - cx) * k:.3f},{(y - cy) * k:.3f}"

    out = []
    for commands, _ in pieces:
        for command in commands:
            if command[0] in ("M", "L"):
                out.append(command[0] + pt(*command[1]))
            elif command[0] == "A":
                rx, ry, angle, end = command[1]
                out.append(f"A{rx * k:.3f},{ry * k:.3f} {angle} 0,1 {pt(*end)}")
            else:
                out.append("Z")
    return "".join(out)


def main():
    icons = [{"name": name, "path": to_path(pieces)} for name, pieces in ICONS.items()]
    OUTPUT.write_text(json.dumps(icons, indent=1) + "\n")
    print(f"Wrote {OUTPUT}: {len(icons)} icons ({OUTPUT.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
