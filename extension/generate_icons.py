"""
ShopQ Chrome Extension Icon Generator
Generates valid PNG icons (16, 32, 48, 128px) with ShopQ Dusty Rose (#C96B7A) brand styling.
Zero third-party dependencies (pure Python standard library: struct & zlib).
"""
import zlib
import struct
import math
import os

def create_shopq_icon(size: int) -> bytes:
    """Creates a PNG byte stream for a ShopQ badge at the specified pixel size."""
    width = size
    height = size
    pixels = []

    center_x = (width - 1) / 2.0
    center_y = (height - 1) / 2.0
    corner_radius = size * 0.22

    # Draw rounded square with dusty rose background (#C96B7A) and white 'Q'
    for y in range(height):
        row = []
        for x in range(width):
            # Check rounded rectangle distance
            dx = max(0.0, abs(x - center_x) - (size / 2.0 - corner_radius - 0.5))
            dy = max(0.0, abs(y - center_y) - (size / 2.0 - corner_radius - 0.5))
            dist_sq = dx * dx + dy * dy

            if dist_sq > corner_radius * corner_radius:
                # Outside rounded rectangle
                row.append((0, 0, 0, 0))
                continue

            # Antialiasing at border
            edge_dist = math.sqrt(dist_sq) - corner_radius
            alpha_edge = 1.0
            if edge_dist > -0.75:
                alpha_edge = max(0.0, min(1.0, -edge_dist / 0.75))

            # Base color: Dusty Rose #C96B7A = (201, 107, 122)
            r, g, b = 201, 107, 122
            a = int(255 * alpha_edge)

            # Draw 'Q' inside: circle ring + diagonal tail
            rel_x = (x - center_x) / (size / 2.0)
            rel_y = (y - center_y) / (size / 2.0)
            dist_center = math.sqrt(rel_x ** 2 + rel_y ** 2)

            # Ring between radius 0.28 and 0.58
            in_ring = 0.28 <= dist_center <= 0.58
            
            # Tail for Q: in bottom-right quadrant
            in_tail = (rel_x >= 0.15 and rel_y >= 0.15 and abs(rel_x - rel_y) <= 0.24 and dist_center <= 0.76)

            if (in_ring or in_tail) and a > 0:
                # White color for letter Q
                r, g, b = 255, 255, 255

            row.append((r, g, b, a))
        pixels.append(row)

    # Encode to PNG format
    raw_data = bytearray()
    for row in pixels:
        raw_data.append(0)  # Filter byte 0 (None)
        for r, g, b, a in row:
            raw_data.extend([r, g, b, a])

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack('>I', len(data))
            + tag
            + data
            + struct.pack('>I', zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    magic = b'\x89PNG\r\n\x1a\n'
    ihdr = chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0))
    idat = chunk(b'IDAT', zlib.compress(bytes(raw_data), level=9))
    iend = chunk(b'IEND', b'')
    return magic + ihdr + idat + iend

def main():
    icons_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icons')
    os.makedirs(icons_dir, exist_ok=True)
    sizes = [16, 32, 48, 128]
    for s in sizes:
        png_data = create_shopq_icon(s)
        file_path = os.path.join(icons_dir, f'icon-{s}.png')
        with open(file_path, 'wb') as f:
            f.write(png_data)
        print(f"Generated {file_path} ({len(png_data)} bytes)")

if __name__ == '__main__':
    main()
