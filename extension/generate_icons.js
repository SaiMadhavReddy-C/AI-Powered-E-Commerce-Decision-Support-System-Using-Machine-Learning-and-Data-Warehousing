/**
 * ShopQ Extension Icon Generator (Node.js)
 * Generates valid PNG icons (16, 32, 48, 128px) with zero external dependencies.
 */
const fs = require('fs');
const path = require('path');
const zlib = require('zlib');

// CRC32 table & function
const crcTable = new Uint32Array(256);
for (let n = 0; n < 256; n++) {
  let c = n;
  for (let k = 0; k < 8; k++) {
    c = (c & 1) ? (0xedb88320 ^ (c >>> 1)) : (c >>> 1);
  }
  crcTable[n] = c;
}

function crc32(buf) {
  let crc = 0xffffffff;
  for (let i = 0; i < buf.length; i++) {
    crc = crcTable[(crc ^ buf[i]) & 0xff] ^ (crc >>> 8);
  }
  return (crc ^ 0xffffffff) >>> 0;
}

function createChunk(type, data) {
  const typeBuf = Buffer.from(type, 'ascii');
  const lenBuf = Buffer.alloc(4);
  lenBuf.writeUInt32BE(data.length, 0);

  const toCrc = Buffer.concat([typeBuf, data]);
  const crcBuf = Buffer.alloc(4);
  crcBuf.writeUInt32BE(crc32(toCrc), 0);

  return Buffer.concat([lenBuf, typeBuf, data, crcBuf]);
}

function generateIcon(size) {
  const width = size;
  const height = size;
  const bytesPerPixel = 4;
  const rowSize = 1 + width * bytesPerPixel;
  const rawData = Buffer.alloc(height * rowSize);

  const centerX = (width - 1) / 2.0;
  const centerY = (height - 1) / 2.0;
  const cornerRadius = size * 0.22;

  for (let y = 0; y < height; y++) {
    const rowOffset = y * rowSize;
    rawData[rowOffset] = 0; // Filter: None

    for (let x = 0; x < width; x++) {
      const pxOffset = rowOffset + 1 + x * bytesPerPixel;

      const dx = Math.max(0, Math.abs(x - centerX) - (size / 2.0 - cornerRadius - 0.5));
      const dy = Math.max(0, Math.abs(y - centerY) - (size / 2.0 - cornerRadius - 0.5));
      const distSq = dx * dx + dy * dy;

      if (distSq > cornerRadius * cornerRadius) {
        // Transparent outside rounded rect
        rawData[pxOffset] = 0;
        rawData[pxOffset + 1] = 0;
        rawData[pxOffset + 2] = 0;
        rawData[pxOffset + 3] = 0;
        continue;
      }

      const edgeDist = Math.sqrt(distSq) - cornerRadius;
      let alphaEdge = 1.0;
      if (edgeDist > -0.75) {
        alphaEdge = Math.max(0, Math.min(1, -edgeDist / 0.75));
      }

      // Base color: Dusty Rose #C96B7A (201, 107, 122)
      let r = 201;
      let g = 107;
      let b = 122;
      let a = Math.round(255 * alphaEdge);

      // Letter 'Q' inside
      const relX = (x - centerX) / (size / 2.0);
      const relY = (y - centerY) / (size / 2.0);
      const distCenter = Math.sqrt(relX * relX + relY * relY);

      const inRing = distCenter >= 0.28 && distCenter <= 0.58;
      const inTail = relX >= 0.15 && relY >= 0.15 && Math.abs(relX - relY) <= 0.24 && distCenter <= 0.76;

      if ((inRing || inTail) && a > 0) {
        // White
        r = 255;
        g = 255;
        b = 255;
      }

      rawData[pxOffset] = r;
      rawData[pxOffset + 1] = g;
      rawData[pxOffset + 2] = b;
      rawData[pxOffset + 3] = a;
    }
  }

  const magic = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);

  const ihdrData = Buffer.alloc(13);
  ihdrData.writeUInt32BE(width, 0);
  ihdrData.writeUInt32BE(height, 4);
  ihdrData[8] = 8; // bit depth
  ihdrData[9] = 6; // color type RGBA
  ihdrData[10] = 0; // compression
  ihdrData[11] = 0; // filter
  ihdrData[12] = 0; // interlace
  const ihdr = createChunk('IHDR', ihdrData);

  const compressed = zlib.deflateSync(rawData, { level: 9 });
  const idat = createChunk('IDAT', compressed);
  const iend = createChunk('IEND', Buffer.alloc(0));

  return Buffer.concat([magic, ihdr, idat, iend]);
}

const iconsDir = path.join(__dirname, 'icons');
if (!fs.existsSync(iconsDir)) {
  fs.mkdirSync(iconsDir, { recursive: true });
}

const sizes = [16, 32, 48, 128];
sizes.forEach(s => {
  const buf = generateIcon(s);
  const outPath = path.join(iconsDir, `icon-${s}.png`);
  fs.writeFileSync(outPath, buf);
  console.log(`Generated icon: ${outPath} (${buf.length} bytes)`);
});
