`toString('hex')` 就是把 **Buffer 二进制数据转成十六进制字符串**，方便存储、打印、传输。

# 一句话解释
- 输入：`Buffer`（二进制字节）
- 输出：**0-9、a-f** 组成的字符串
- 每 **1 个字节 → 2 个十六进制字符**

# 例子
```js
const crypto = require('crypto');

const buf = crypto.randomBytes(16);    // 16 字节 Buffer
const hexStr = buf.toString('hex');    // 转成十六进制字符串
```

- 长度：16 字节 = 128 位
- 转 hex 后：32 个字符（每 4bit 一个 hex 字符）

# 常见搭配
```js
// 生成盐
const salt = crypto.randomBytes(16).toString('hex');

// 生成 token
const token = crypto.randomBytes(32).toString('hex');
```

# 和其他编码对比
- `toString('utf8')`：转普通字符串
- `toString('base64')`：转 Base64，更短
- `toString('hex')`：**标准、无特殊字符、最稳**，数据库存起来最安全

# 记住一个规律
**字节数 × 2 = hex 字符串长度**
- 16 字节 → 32 位 hex
- 32 字节 → 64 位 hex
- 64 字节 → 128 位 hex

需要我给你写一个**hex 转回 Buffer**的反向操作示例吗？