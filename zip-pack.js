import fs from 'fs';
import path from 'path';
import { ZipArchive } from 'archiver';

const __dirname = path.dirname(decodeURIComponent(new URL(import.meta.url).pathname).replace(/^\/([A-Z]:)/, '$1'));
const zipPath = path.resolve(__dirname, 'dist.zip');

const output = fs.createWriteStream(zipPath);
const archive = new ZipArchive();

output.on('close', () => {
  const sizeMB = (archive.pointer() / 1024 / 1024).toFixed(2);
  console.log(`✅ 打包完成，文件：dist.zip，大小：${sizeMB} MB`);
});

archive.on('error', (err) => {
  throw err;
});

archive.pipe(output);

archive.glob('**', {
  cwd: __dirname,
  ignore: [
    'node_modules/**',
    '.git/**',
    'dist.zip',
    'zip-pack.js'
  ]
});

archive.finalize();