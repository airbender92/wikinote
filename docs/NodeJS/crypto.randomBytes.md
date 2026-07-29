`crypto.randomBytes` 是 Node.js **crypto 模块**里，用来生成**高强度、密码学安全的随机字节**的方法。

简单说：**生成真·安全随机数，专门给加密、盐值、密钥用**。

---

## 基本用法
```js
const crypto = require('crypto');

// 生成 16 字节的安全随机数
const buf = crypto.randomBytes(16);

// 转成十六进制字符串（最常用）
const randomHex = buf.toString('hex');

console.log(randomHex);
```

输出类似：
```
a1b2c3d4e5f678900987654321fedcba
```

---

## 作用
- 生成 **salt（盐值）**
- 生成 token、sessionId、随机密钥
- 用于 `pbkdf2`、`bcrypt`、加密算法等

特点：
- 安全级别高，无法被预测
- 比 `Math.random()` 安全得多（Math.random 不安全，不能用于加密）

---

## 常用场景（配合 pbkdf2）
```js
const salt = crypto.randomBytes(16).toString('hex');

crypto.pbkdf2(password, salt, 100000, 64, 'sha256', (err, key) => {
  // ...
});
```

---

## 同步 / 异步
### 异步（推荐）
```js
crypto.randomBytes(16, (err, buf) => {
  const str = buf.toString('hex');
});
```

### 同步
```js
const buf = crypto.randomBytes(16);
```

---

## 常见长度规范
- 盐值 salt：**16 字节** 起步
- 随机 token：**32 字节**
- 加密密钥：**32 / 64 字节**

---

## 一句话总结
`crypto.randomBytes(size)`
= 生成 `size` 字节的**密码学安全随机 Buffer**，常用于加盐、生成密钥、token。

需要我给你写一个**通用随机字符串工具函数**吗？