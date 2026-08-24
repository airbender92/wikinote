# 前端计算文件 MD5

浏览器不能直接原生提供md5 API，主流两种方案：

1. **Spark‑MD5**（最常用，轻量，适合文件、Blob、ArrayBuffer）
2. Web Crypto API（浏览器原生，**不依赖第三方库**，推荐新项目）

> 注意：大文件建议**分片计算**，避免一次性读入内存造成页面卡顿。

---

## 方案一：浏览器原生 Web Crypto API（无第三方依赖 ✅）

只能计算 `ArrayBuffer`，文件需要先读取。

```
/**
 * 计算 ArrayBuffer md5
 * @param {ArrayBuffer} buffer
 * @returns {Promise<string>} 小写md5
 */
async function bufferToMd5(buffer) {
  const hashBuffer = await crypto.subtle.digest('MD5', buffer);
  // 转16进制字符串
  return Array.from(new Uint8Array(hashBuffer))
    .map(b => b.toString(16).padStart(2, '0'))
    .join('');
}

/**
 * File对象计算md5
 * @param {File} file
 * @returns {Promise<string>}
 */
async function getFileMd5(file) {
  const buf = await file.arrayBuffer();
  return bufferToMd5(buf);
}

// 使用示例
// input type="file" onchange
// const md5 = await getFileMd5(file);
```

⚠️ 限制：

- Web Crypto **必须在 HTTPS / localhost** 环境；http 普通域名下 `crypto.subtle` 为 `null`。
- 超大文件一次性读 arrayBuffer 会占内存，大文件不要这么写。

---

## 方案二：spark‑md5 库（兼容性好，支持分片，老http环境可用）

安装

```
npm install spark-md5
```

### 简单用法（小文件）

```
import SparkMD5 from 'spark-md5';

async function getFileMd5(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsArrayBuffer(file);
    reader.onload = e => {
      const md5 = SparkMD5.ArrayBuffer.hash(e.target.result);
      resolve(md5);
    };
    reader.onerror = reject;
  });
}
```

### ✅【重点】大文件分片计算（推荐，防止卡死页面）

> 上传大文件做md5校验，必须分片，不要一次性读取整个文件。

```
import SparkMD5 from 'spark-md5';

/**
 * 分片计算文件md5，避免大文件内存爆炸
 * @param {File} file
 * @param {number} chunkSize 分片大小，默认 2MB
 * @returns {Promise<string>}
 */
function getFileMd5ByChunk(file, chunkSize = 2 * 1024 * 1024) {
  return new Promise((resolve, reject) => {
    const spark = new SparkMD5.ArrayBuffer();
    let current = 0;
    const total = file.size;

    function readNext() {
      const end = Math.min(current + chunkSize, total);
      const blob = file.slice(current, end);
      const reader = new FileReader();
      reader.onload = e => {
        spark.append(e.target.result);
        current = end;
        if (current < total) {
          readNext();
        } else {
          resolve(spark.end());
        }
      };
      reader.onerror = reject;
      reader.readAsArrayBuffer(blob);
    }
    readNext();
  });
}
```

使用：

```
// input file change
const file = e.target.files[0];
const md5 = await getFileMd5ByChunk(file);
console.log('文件md5', md5);
```

---

## React 完整示例（input 文件选择）

```
import { useState } from 'react';
import SparkMD5 from 'spark-md5';

export default function FileMd5Demo() {
  const [md5Str, setMd5Str] = useState('');

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setMd5Str('计算中...');
    const hash = await getFileMd5ByChunk(file);
    setMd5Str(hash);
  };

  function getFileMd5ByChunk(file, chunkSize = 2 * 1024 * 1024) {
    return new Promise((resolve, reject) => {
      const spark = new SparkMD5.ArrayBuffer();
      let current = 0;
      const total = file.size;
      function readNext() {
        const end = Math.min(current + chunkSize, total);
        const blob = file.slice(current, end);
        const reader = new FileReader();
        reader.onload = e => {
          spark.append(e.target.result);
          current = end;
          current < total ? readNext() : resolve(spark.end());
        };
        reader.onerror = reject;
        reader.readAsArrayBuffer(blob);
      }
      readNext();
    });
  }

  return (
    <div>
      <input type="file" onChange={handleFileChange}/>
      <div>MD5：{md5Str}</div>
    </div>
  );
}
```

---

## 常见坑总结

1. `crypto.subtle` http环境不可用，内网http项目优先选 spark‑md5。
2. **大文件千万不要一次性 readAsArrayBuffer**，内存暴涨、页面卡顿，必须分片。
3. FileReader 是异步，不能同步拿md5，全部要 Promise。
4. 前端md5用于**文件秒传、断点续传校验**；md5可以被篡改，**不要做安全加密校验**。

如果你需要，我可以给你一个封装好的 React hook `useFileMd5`。
