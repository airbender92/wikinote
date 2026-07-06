const fs = require('fs');
const path = require('path');
const archiver = require('archiver');

// 输出压缩包
const output = fs.createWriteStream('dist.zip');
const archive = archiver('zip', { zlib: { level: 9 } });

output.on('close', () => {
  console.log(`打包完成，总大小：${(archive.pointer() / 1024 / 1024).toFixed(2)}MB`);
});

archive.pipe(output);

// 打包当前全部文件，仅排除 node_modules
archive.glob('**', {
  cwd: __dirname,
  ignore: [
    'node_modules/**',
    'dist.zip' // 避免把自己打包进去
  ]
});

archive.finalize();