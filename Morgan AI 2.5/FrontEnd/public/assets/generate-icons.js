const sharp = require('sharp');
const fs = require('fs');
const path = require('path');

const src = path.join(__dirname, 'morgan-logo', 'morgan-logo.png');
const sizes = [16, 32, 48, 128, 256, 512];
const outDir = path.join(__dirname, 'icons');

if (!fs.existsSync(outDir)) fs.mkdirSync(outDir);

sizes.forEach(size => {
  sharp(src)
    .resize(size, size)
    .toFile(path.join(outDir, `icon-${size}x${size}.png`), (err) => {
      if (err) console.error(`Error creating icon ${size}x${size}:`, err);
      else console.log(`Created icon-${size}x${size}.png`);
    });
});
