#!/usr/bin/env python3
"""news-image-20261119 entry: draws a one-page newspaper front page that sums
up the world news of Thursday 19 November 2026 and writes it to
/output/entry.png (1024x1024 PNG, standard library only).

The page is drawn from scratch in pure Python: a tiny PNG encoder (zlib +
struct, both stdlib) and a hand-made 8x8 bitmap font scaled up for the
masthead, headlines and decks. No network, no file reads, no randomness, no
clock: two runs produce byte-identical output.

Run locally with:
    mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import math
import os
import struct
import zlib

W, H = 1024, 1024

PAPER = (247, 243, 234)
INK = (20, 20, 20)
GRAY = (90, 86, 78)
RED = (179, 32, 44)
NAVY = (31, 58, 95)
AMBER = (196, 122, 18)
TEAL = (15, 118, 110)
PURPLE = (109, 40, 217)
WHITE = (255, 255, 255)

# ---------------------------------------------------------------------------
# 8x8 bitmap font, one byte per row, most significant bit on the left.
# Uppercase, digits and the punctuation the page uses. Hand-made here so the
# program needs no font file and no third-party package.
# ---------------------------------------------------------------------------

FONT = {
    "A": (0x18, 0x24, 0x42, 0x42, 0x7E, 0x42, 0x42, 0x42),
    "B": (0x7C, 0x42, 0x42, 0x7C, 0x42, 0x42, 0x42, 0x7C),
    "C": (0x3C, 0x42, 0x40, 0x40, 0x40, 0x40, 0x42, 0x3C),
    "D": (0x78, 0x44, 0x42, 0x42, 0x42, 0x42, 0x44, 0x78),
    "E": (0x7E, 0x40, 0x40, 0x7C, 0x40, 0x40, 0x40, 0x7E),
    "F": (0x7E, 0x40, 0x40, 0x7C, 0x40, 0x40, 0x40, 0x40),
    "G": (0x3C, 0x42, 0x40, 0x40, 0x4E, 0x42, 0x42, 0x3C),
    "H": (0x42, 0x42, 0x42, 0x7E, 0x42, 0x42, 0x42, 0x42),
    "I": (0x3E, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x3E),
    "J": (0x1E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x44, 0x38),
    "K": (0x42, 0x44, 0x48, 0x70, 0x48, 0x44, 0x42, 0x42),
    "L": (0x40, 0x40, 0x40, 0x40, 0x40, 0x40, 0x40, 0x7E),
    "M": (0x42, 0x66, 0x5A, 0x5A, 0x42, 0x42, 0x42, 0x42),
    "N": (0x42, 0x62, 0x52, 0x4A, 0x46, 0x42, 0x42, 0x42),
    "O": (0x3C, 0x42, 0x42, 0x42, 0x42, 0x42, 0x42, 0x3C),
    "P": (0x7C, 0x42, 0x42, 0x7C, 0x40, 0x40, 0x40, 0x40),
    "Q": (0x3C, 0x42, 0x42, 0x42, 0x42, 0x4A, 0x44, 0x3A),
    "R": (0x7C, 0x42, 0x42, 0x7C, 0x48, 0x44, 0x42, 0x42),
    "S": (0x3C, 0x42, 0x40, 0x3C, 0x02, 0x02, 0x42, 0x3C),
    "T": (0x7E, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08),
    "U": (0x42, 0x42, 0x42, 0x42, 0x42, 0x42, 0x42, 0x3C),
    "V": (0x42, 0x42, 0x42, 0x42, 0x42, 0x42, 0x24, 0x18),
    "W": (0x42, 0x42, 0x42, 0x42, 0x5A, 0x5A, 0x66, 0x42),
    "X": (0x42, 0x42, 0x24, 0x18, 0x18, 0x24, 0x42, 0x42),
    "Y": (0x42, 0x42, 0x24, 0x18, 0x08, 0x08, 0x08, 0x08),
    "Z": (0x7E, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x7E),
    "0": (0x3C, 0x42, 0x46, 0x4A, 0x52, 0x62, 0x42, 0x3C),
    "1": (0x08, 0x18, 0x28, 0x08, 0x08, 0x08, 0x08, 0x3E),
    "2": (0x3C, 0x42, 0x02, 0x02, 0x3C, 0x40, 0x40, 0x7E),
    "3": (0x3C, 0x42, 0x02, 0x1C, 0x02, 0x02, 0x42, 0x3C),
    "4": (0x04, 0x0C, 0x14, 0x24, 0x7E, 0x04, 0x04, 0x04),
    "5": (0x7E, 0x40, 0x7C, 0x02, 0x02, 0x02, 0x42, 0x3C),
    "6": (0x1C, 0x20, 0x40, 0x7C, 0x42, 0x42, 0x42, 0x3C),
    "7": (0x7E, 0x02, 0x04, 0x08, 0x10, 0x10, 0x10, 0x10),
    "8": (0x3C, 0x42, 0x42, 0x3C, 0x42, 0x42, 0x42, 0x3C),
    "9": (0x3C, 0x42, 0x42, 0x42, 0x3E, 0x02, 0x04, 0x38),
    " ": (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00),
    ".": (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x18, 0x18),
    ",": (0x00, 0x00, 0x00, 0x00, 0x00, 0x18, 0x08, 0x10),
    ":": (0x00, 0x18, 0x18, 0x00, 0x00, 0x18, 0x18, 0x00),
    ";": (0x00, 0x18, 0x18, 0x00, 0x00, 0x18, 0x08, 0x10),
    "'": (0x08, 0x08, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00),
    "-": (0x00, 0x00, 0x00, 0x00, 0x7E, 0x00, 0x00, 0x00),
    "/": (0x02, 0x04, 0x04, 0x08, 0x08, 0x10, 0x10, 0x20),
    "(": (0x04, 0x08, 0x08, 0x10, 0x10, 0x10, 0x08, 0x04),
    ")": (0x10, 0x08, 0x08, 0x04, 0x04, 0x04, 0x08, 0x10),
    "$": (0x08, 0x3E, 0x28, 0x3E, 0x0A, 0x3E, 0x08, 0x00),
    "%": (0x61, 0x12, 0x08, 0x10, 0x20, 0x48, 0x86, 0x00),
    "&": (0x1C, 0x22, 0x22, 0x14, 0x08, 0x14, 0x22, 0x22),
    "!": (0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x00, 0x08),
    "?": (0x3C, 0x42, 0x02, 0x04, 0x08, 0x08, 0x00, 0x08),
    "+": (0x00, 0x08, 0x08, 0x3E, 0x08, 0x08, 0x00, 0x00),
    "=": (0x00, 0x00, 0x00, 0x7E, 0x00, 0x7E, 0x00, 0x00),
    "\u2022": (0x00, 0x00, 0x18, 0x18, 0x18, 0x00, 0x00, 0x00),
    '"': (0x14, 0x14, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00),
}


# ---------------------------------------------------------------------------
# Pixel canvas: a plain RGB byte buffer with the few primitives the page
# needs. Everything is integer math, so output is fully deterministic.
# ---------------------------------------------------------------------------

class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.buf = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i] = c[0]
            self.buf[i + 1] = c[1]
            self.buf[i + 2] = c[2]

    def fill_rect(self, x, y, w, h, c):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.buf[i] = c[0]
                self.buf[i + 1] = c[1]
                self.buf[i + 2] = c[2]

    def hline(self, x, y, w, c, t=1):
        self.fill_rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.fill_rect(x, y, t, h, c)

    def rect(self, x, y, w, h, c, t=2):
        self.fill_rect(x, y, w, t, c)
        self.fill_rect(x, y + h - t, w, t, c)
        self.fill_rect(x, y, t, h, c)
        self.fill_rect(x + w - t, y, t, h, c)

    def disc(self, cx, cy, r, c):
        # Filled disc, scanline by scanline.
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            self.fill_rect(cx - dx, cy + dy, dx * 2 + 1, 1, c)

    def ring(self, cx, cy, r, c, t=2):
        for dy in range(-r - t, r + t + 1):
            for dx in range(-r - t, r + t + 1):
                d = (dx * dx + dy * dy) ** 0.5
                if r - t <= d <= r + t:
                    self.px(cx + dx, cy + dy, c)

    def chord(self, cx, cy, r, dy, c, t=2):
        # Horizontal chord of a circle at vertical offset dy.
        if abs(dy) >= r:
            return
        dx = int((r * r - dy * dy) ** 0.5)
        self.fill_rect(cx - dx, cy + dy - t // 2, dx * 2 + 1, t, c)

    def ellipse_arc(self, cx, cy, rx, ry, c, t=2):
        # Vertical ellipse outline, sampled point by point.
        for k in range(360):
            a = 2 * math.pi * k / 360
            x = int(cx + rx * math.sin(a))
            y = int(cy + ry * math.cos(a))
            self.fill_rect(x - t // 2, y - t // 2, t, t, c)


def track(scale):
    return max(2, scale)


def text_w(s, scale):
    adv = 8 * scale + track(scale)
    return len(s) * adv - track(scale)


def draw_text(cv, x, y, s, scale, c):
    adv = 8 * scale + track(scale)
    cx = x
    for ch in s:
        glyph = FONT.get(ch)
        if glyph is None:
            cx += adv
            continue
        for row in range(8):
            bits = glyph[row]
            if bits == 0:
                continue
            for col in range(8):
                if bits & (0x80 >> col):
                    cv.fill_rect(cx + col * scale, y + row * scale, scale, scale, c)
        cx += adv


def draw_text_centered(cv, cx, y, s, scale, c):
    draw_text(cv, cx - text_w(s, scale) // 2, y, s, scale, c)


def wrap_lines(text, max_w, scale):
    words = text.split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_w(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_block(cv, x, y, text, max_w, scale, c, leading=None):
    if leading is None:
        leading = 8 * scale + 2 * scale
    lines = wrap_lines(text, max_w, scale)
    for i, line in enumerate(lines):
        draw_text(cv, x, y + i * leading, line, scale, c)
    return y + len(lines) * leading


def kicker(cv, x, y, label, color):
    # Colored tag with white caps text, 26 px tall.
    w = text_w(label, 2) + 20
    cv.fill_rect(x, y, w, 26, color)
    draw_text(cv, x + 10, y + 5, label, 2, WHITE)
    return w


# ---------------------------------------------------------------------------
# Minimal PNG writer: signature, IHDR, one IDAT (zlib level 9, filter 0),
# IEND. Deterministic for identical pixels.
# ---------------------------------------------------------------------------

def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def png_bytes(cv):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.buf[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    data = b"\x89PNG\r\n\x1a\n"
    data += _chunk(b"IHDR", ihdr)
    data += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    data += _chunk(b"IEND", b"")
    return data

# ---------------------------------------------------------------------------
# The news: four stories, all reported on Thursday 19 November 2026.
# Headlines and decks are written from the day's reporting (AP, Reuters,
# The Japan Times, NDTV, The Art Newspaper, Sotheby's). Nothing here is
# invented: every fact below appeared in that day's news.
# ---------------------------------------------------------------------------

LEAD = {
    "kicker": "LEAD • SHENZHEN, CHINA",
    "headline": "TRUMP, XI, PUTIN IN FIRST THREE-WAY SUMMIT",
    "deck": "THE U.S., CHINESE AND RUSSIAN LEADERS MEET IN SHENZHEN AT THE "
            "APEC SUMMIT, WITH NUCLEAR ARMS AND TWO WARS ON THE TABLE.",
}

SECONDARY = [
    {
        "kicker": "GAZA • MIDDLE EAST",
        "headline": "ISRAEL LAUNCHES GROUND OPERATION IN CENTRAL GAZA",
        "deck": "DOZENS FLEE AS TROOPS ADVANCE.",
    },
    {
        "kicker": "ENERGY • STRAIT OF HORMUZ",
        "headline": "OIL TANKERS ABLAZE AFTER HITTING MINES",
        "deck": "THREE TANKERS BURN EAST OF THE STRAIT OF HORMUZ.",
    },
    {
        "kicker": "CULTURE",
        "headline": "VAN GOGH IN $190.4M RECORD SALE",
        "deck": "1890 MASTERPIECE SETS A NEW ARTIST RECORD.",
    },
]


def draw_globe(cv, cx, cy, r):
    # Small bare globe on the paper: white disc, navy meridians, one red
    # marker where the summit is. No panel, no caption.
    cv.disc(cx, cy, r, WHITE)
    cv.ring(cx, cy, r, NAVY, 2)
    for dy in (-37, -18, 0, 18, 37):
        cv.chord(cx, cy, r, dy, NAVY, 2)
    cv.vline(cx - 1, cy - r, 2 * r, NAVY, 2)
    cv.ellipse_arc(cx, cy, 25, r, NAVY, 2)
    cv.ellipse_arc(cx, cy, 46, r, NAVY, 2)
    cv.disc(cx + 30, cy - 24, 4, RED)


def build():
    # Clean layout: wide 64 px margins, one thin rule under the masthead,
    # one under the lead, and nothing else. Three blocks, lots of air.
    cv = Canvas(W, H, PAPER)

    # Masthead: nameplate, then the day.
    draw_text_centered(cv, W // 2, 56, "THE WORLD TODAY", 6, INK)
    draw_text_centered(cv, W // 2, 118, "THURSDAY 19 NOVEMBER 2026", 3, RED)
    cv.hline(64, 168, W - 128, INK, 2)

    # Lead story: plain red kicker, one huge headline, deck on the left
    # with a small globe on the right.
    draw_text(cv, 64, 196, LEAD["kicker"], 2, RED)
    draw_block(cv, 64, 226, LEAD["headline"], W - 128, 6, INK, leading=58)
    draw_block(cv, 64, 428, LEAD["deck"], 700, 2, INK, leading=22)
    draw_globe(cv, 880, 484, 56)
    cv.hline(64, 576, W - 128, INK, 1)

    # Three secondary stories, one row each: gray kicker, headline, deck.
    y = 604
    for story in SECONDARY:
        draw_text(cv, 64, y, story["kicker"], 2, GRAY)
        end = draw_block(cv, 64, y + 26, story["headline"], W - 128, 3, INK,
                         leading=32)
        draw_text(cv, 64, end + 8, story["deck"], 2, INK)
        y += 138
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    data = png_bytes(build())
    with open(os.path.join(out_dir, "entry.png"), "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
