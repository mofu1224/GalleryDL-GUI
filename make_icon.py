"""
make_icon.py — generates assets/icon.ico using only stdlib (no Pillow needed).
Run once before building: python make_icon.py
"""
import os
import struct
import zlib

def _write_png_1x1(color_rgba: tuple) -> bytes:
    """Return a minimal 1x1 RGBA PNG as bytes."""
    r, g, b, a = color_rgba
    raw = b"\x00" + bytes([r, g, b, a])   # filter byte + 1 pixel
    compressed = zlib.compress(raw, 9)

    def chunk(tag: bytes, data: bytes) -> bytes:
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    png = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
                .replace(b"\x00\x00\x00\x08\x02", b"\x08\x02\x00\x00\x00"))
        + chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 6, 0, 0, 0))
    )
    # Build a real minimal PNG properly
    ihdr_data = struct.pack(">IIBBBBB", 1, 1, 8, 6, 0, 0, 0)
    # width=1, height=1, bitdepth=8, colortype=6(RGBA), compress=0, filter=0, interlace=0
    ihdr_data = struct.pack(">II", 1, 1) + bytes([8, 6, 0, 0, 0])
    idat_data = compressed
    iend_data = b""

    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", ihdr_data)
            + chunk(b"IDAT", idat_data)
            + chunk(b"IEND", iend_data))


def make_icon_bmp(size: int, color_rgba: tuple) -> bytes:
    """
    Generate a raw BMP (no file header) suitable for embedding in an ICO.
    Uses a solid filled circle on a transparent background.
    """
    r, g, b, a = color_rgba
    accent   = (0x00, 0x7a, 0xcc, 0xff)   # VS Code Blue
    bg       = (0x1e, 0x1e, 0x1e, 0x00)   # transparent background

    pixels_and = bytearray()  # XOR mask
    pixels_xor = bytearray()  # AND mask (all 0 = opaque)

    cx = cy = size / 2
    radius = size / 2 - 2

    rows = []
    for y in range(size):
        row_xor = bytearray()
        row_and = bytearray()
        for x in range(size):
            dx, dy = x - cx, y - cy
            if dx * dx + dy * dy <= radius * radius:
                ar, ag, ab, aa = accent
                row_xor += bytes([ab, ag, ar, aa])   # BGRA
                row_and += b"\x00"
            else:
                row_xor += bytes([0, 0, 0, 0])
                row_and += b"\x00"
        rows.append((row_xor, row_and))

    # BMP rows are bottom-up
    rows_xor = b"".join(r[0] for r in reversed(rows))
    rows_and = b"".join(r[1] for r in reversed(rows))
    # AND mask padding to DWORD boundary
    and_row_bytes = (size + 31) // 32 * 4
    rows_and_padded = b""
    for y in range(size):
        row = rows[size - 1 - y][1]
        # Pack bits (1 bit per pixel)
        bits = bytearray()
        for i in range(0, size, 8):
            byte = 0
            for bit in range(8):
                if i + bit < size and row[i + bit] == 0:
                    byte |= (0 << (7 - bit))
            bits.append(byte)
        padded = bits + b"\x00" * (and_row_bytes - len(bits))
        rows_and_padded += bytes(padded)

    bmp_header = struct.pack(
        "<IIIHHIIIIII",
        40,             # BITMAPINFOHEADER size
        size,           # width
        size * 2,       # height (doubled for XOR+AND)
        1,              # color planes
        32,             # bits per pixel
        0,              # BI_RGB compression
        len(rows_xor) + len(rows_and_padded),  # image size
        0, 0, 0, 0      # resolution + palette
    )
    return bmp_header + rows_xor + rows_and_padded


def create_ico(path: str):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    sizes = [256, 128, 48, 32, 16]
    accent = (0x00, 0x7a, 0xcc, 0xff)

    images = []
    for sz in sizes:
        data = make_icon_bmp(sz, accent)
        images.append((sz, data))

    # ICO header
    header = struct.pack("<HHH", 0, 1, len(images))

    # Directory entries
    offset = 6 + 16 * len(images)
    directory = b""
    for sz, data in images:
        w = h = 0 if sz == 256 else sz   # 0 means 256 in ICO
        directory += struct.pack(
            "<BBBBHHII",
            w, h,           # width, height
            0,              # color count (0 = >8bpp)
            0,              # reserved
            1,              # color planes
            32,             # bits per pixel
            len(data),
            offset
        )
        offset += len(data)

    with open(path, "wb") as f:
        f.write(header + directory)
        for _, data in images:
            f.write(data)

    print(f"Icon created: {path}")


if __name__ == "__main__":
    create_ico("assets/icon.ico")
