# `fs.copyFileSync` 完全讲解
`fs.copyFileSync` 是 **Node.js 内置文件系统模块（fs）** 的方法，作用是：
**同步复制文件** → 把一个文件从源路径复制到目标路径。

简单说：**代码里实现“复制粘贴文件”**。

---

## 1. 基本用法
```javascript
const fs = require('fs');

// 同步复制文件
fs.copyFileSync(源文件, 目标文件);
```

### 示例
```javascript
fs.copyFileSync('./public/index.html', './dist/index.html');
```
效果：把 `public/index.html` 复制到 `dist/index.html`

---

## 2. 完整参数
```javascript
fs.copyFileSync(src, dest[, mode])
```
- `src`：**要复制的源文件路径**
- `dest`：**复制到哪里（目标路径）**
- `mode`：可选，复制模式（一般不用）

---

## 3. 特点（非常重要）
1. **同步执行**
   复制完成前，代码会卡住等待，不会往下执行。
   → 适合构建脚本、初始化操作。

2. **会覆盖目标文件**
   如果目标文件已存在，**直接覆盖**，不会提示。

3. **不能复制文件夹**
   只能复制**文件**，不能复制目录！
   复制目录要用 `fs.cpSync` 或第三方库。

4. **目标目录必须存在**
   如果 `./dist/` 不存在，会报错！
   → 必须先创建目录：
   ```javascript
   fs.mkdirSync('./dist', { recursive: true });
   ```

---

## 4. 最常用实战（Webpack 构建脚本）
复制静态文件到打包目录 `dist`：
```javascript
const fs = require('fs');
const path = require('path');

// 定义路径
const src = path.resolve(__dirname, 'public/index.html');
const dest = path.resolve(__dirname, 'dist/index.html');

// 先创建目标目录（防止不存在报错）
fs.mkdirSync(path.dirname(dest), { recursive: true });

// 复制文件
fs.copyFileSync(src, dest);

console.log('文件复制成功！');
```

---

## 5. 错误处理（推荐写法）
```javascript
try {
  fs.copyFileSync('source.txt', 'target.txt');
  console.log('复制成功');
} catch (err) {
  console.error('复制失败：', err);
}
```

---

## 6. 你会在哪里用到？
- 构建脚本里**复制 HTML / 图片 / 配置文件**到 dist
- 打包前**复制静态资源**
- 自动化脚本里复制模板文件

---

# 超级总结
`fs.copyFileSync` =
**Node.js 同步复制文件**
**只能复制文件，不能复制目录**
**目标目录必须存在**
**常用于构建脚本复制静态资源**

----

我直接给你**两套完整可用的代码**：
1. **异步非阻塞版**（推荐，Node 最佳实践）
2. **集成到 Vite / Webpack 构建流程**（直接放进项目就能用）

你直接复制即可使用。

---

# 1. 异步非阻塞版（推荐）
比同步版性能更好，不会阻塞事件循环，适合大型项目。

```javascript
const fs = require('fs/promises');
const path = require('path');

// 环境配置
const cfgs = {
  isDebug: true, // true=dev, false=prd
};
const buildType = cfgs.isDebug ? 'dev' : 'prd';

/**
 * 异步递归复制文件/文件夹
 * @param {string} from 源路径
 * @param {string} to 目标路径
 */
async function copyFileAsync(from, to) {
  try {
    // 源不存在直接跳过
    if (!(await fs.access(from).catch(() => false))) {
      console.warn(`⚠️ 源不存在：${from}`);
      return;
    }

    const stat = await fs.stat(from);

    // 是文件夹 → 递归复制
    if (stat.isDirectory()) {
      await fs.mkdir(to, { recursive: true });
      const files = await fs.readdir(from);

      for (const file of files) {
        if (!file.startsWith('.')) {
          await copyFileAsync(path.join(from, file), path.join(to, file));
        }
      }
    }
    // 是文件 → 直接复制
    else {
      await fs.copyFile(from, to);
      console.log(`✅ 已复制：${path.relative(__dirname, from)}`);
    }
  } catch (err) {
    console.error(`❌ 复制失败：${from}`, err);
  }
}

// 使用示例
(async () => {
  const source = path.join(__dirname, 'static');
  const target = path.join(__dirname, 'dist', buildType, 'static');

  console.log(`🚀 开始复制文件，当前环境：${buildType}`);
  await copyFileAsync(source, target);
  console.log('\n🎉 所有文件复制完成！');
})();
```

**特点：**
- 不阻塞主线程
- 带错误捕获，不会崩脚本
- 干净日志输出
- 支持多级目录
- 跳过隐藏文件

---

# 2. 集成到 Vite 构建脚本（最常用）
直接放进 `vite.config.js`，**打包时自动复制 static 等资源**。

```javascript
import { defineConfig } from 'vite';
import fs from 'fs/promises';
import path from 'path';

// 环境判断
const isDebug = process.env.NODE_ENV !== 'production';
const buildType = isDebug ? 'dev' : 'prd';

// 复制文件方法
async function copyStatic() {
  const source = path.resolve(__dirname, 'static');
  const target = path.resolve(__dirname, 'dist', buildType, 'static');

  async function copy(from, to) {
    if (!(await fs.access(from).catch(() => false))) return;
    const stat = await fs.stat(from);

    if (stat.isDirectory()) {
      await fs.mkdir(to, { recursive: true });
      const files = await fs.readdir(from);
      for (const f of files) {
        if (!f.startsWith('.')) await copy(path.join(from, f), path.join(to, f));
      }
    } else {
      await fs.copyFile(from, to);
    }
  }

  await copy(source, target);
  console.log(`📦 已复制静态资源到：dist/${buildType}/static`);
}

export default defineConfig({
  build: {
    outDir: `dist/${buildType}`, // 自动输出到对应环境目录
  },
  plugins: [
    {
      name: 'copy-static',
      async closeBundle() {
        await copyStatic();
      },
    },
  ],
});
```

**使用方式：**
- `npm run dev` → 输出到 `dist/dev/`
- `npm run build` → 输出到 `dist/prd/`
- 自动复制 `/static` 文件夹

---

# 3. 集成到 Webpack（vue.config.js / webpack.config.js）
```javascript
const path = require('path');
const fs = require('fs/promises');

module.exports = {
  outputDir: 'dist/' + (process.env.NODE_ENV === 'development' ? 'dev' : 'prd'),

  configureWebpack: {
    plugins: [
      {
        apply: (compiler) => {
          compiler.hooks.done.tapPromise('copy-static', async () => {
            const source = path.resolve(__dirname, 'static');
            const target = path.resolve(
              __dirname,
              'dist',
              process.env.NODE_ENV === 'development' ? 'dev' : 'prd',
              'static'
            );

            async function copy(from, to) {
              if (!(await fs.access(from).catch(() => false))) return;
              const stat = await fs.stat(from);

              if (stat.isDirectory()) {
                await fs.mkdir(to, { recursive: true });
                const files = await fs.readdir(from);
                for (const f of files) {
                  if (!f.startsWith('.')) await copy(path.join(from, f), path.join(to, f));
                }
              } else {
                await fs.copyFile(from, to);
              }
            }

            await copy(source, target);
            console.log('✅ 静态资源复制完成');
          });
        },
      },
    ],
  },
};
```

---

## 你想要哪一种我可以直接帮你适配到你的项目结构
我可以根据你的：
- 项目目录
- 源文件夹
- 目标输出目录
- 构建工具（vite/webpack）

直接给你**最终版可直接运行的代码**。