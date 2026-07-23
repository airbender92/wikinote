// 1. __dirname 当前文件所在目录
console.log('__dirname：', __dirname);

// 2. __filename 当前文件完整路径
console.log('__filename：', __filename);

// 3. module、exports
console.log('module：', module);
console.log('exports：', exports);

// 4. process
console.log('process.version：', process.version);
console.log('process.platform：', process.platform);

try {
  const fs = require('fs');
  console.log('可以加载 fs 模块 → 是 Node 环境');
} catch (e) {
  console.log('不能加载 fs → 不是 Node');
}

console.log(this);
console.log('module.exports', module.exports);
console.log('isEqual', this === module.exports);