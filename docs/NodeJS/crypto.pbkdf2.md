`crypto.pbkdf2` 是 Node.js 内置 **crypto 模块**提供的一个**密码哈希函数**，全称是：
**Password-Based Key Derivation Function 2**
基于密码的密钥派生函数（第2版）

主要用途：**安全存储用户密码**，比单纯 md5/sha1 安全得多。

---

## 一句话作用
- 把用户密码 + 随机盐 + 迭代次数 + 哈希算法
- 经过大量计算，生成一段**慢且难破解**的密钥
- 适合存到数据库做密码验证

---

## 基本语法
```js
crypto.pbkdf2(
  password,    // 原始密码（字符串或Buffer）
  salt,        // 随机盐（建议16字节以上随机数）
  iterations,  // 迭代次数（越大越慢越安全）
  keylen,      // 输出密钥长度
  digest,      // 哈希算法（如 'sha256'）
  callback     // 回调：(err, derivedKey) => {}
)
```

同步版本：
```js
const derivedKey = crypto.pbkdf2Sync(password, salt, iterations, keylen, digest)
```

---

## 完整示例（最常用写法）
```js
const crypto = require('crypto');

// 原始密码
const password = '123456';

// 1. 生成随机盐（推荐 16 字节以上）

```python
import secrets
salt = secrets.token_hex(16)
print(salt)
```
```STDOUT
63315c1b2a542e336e1756181fcb3712

```
```js
const salt = crypto.randomBytes(16).toString('hex');

// 2. 加密密码
crypto.pbkdf2(
  password,
  salt,
  100000,    // 迭代次数
  64,        // 输出 64 字节
  'sha256',
  (err, derivedKey) => {
    if (err) throw err;
    // 最终存储的密码哈希
    const hash = derivedKey.toString('hex');
    console.log('salt:', salt);
    console.log('hash:', hash);
  }
);
```

---

## 关键参数说明
1. **salt（盐）**
   - 必须随机，每个用户不一样
   - 防止彩虹表破解
   - 要和 hash 一起存进数据库

2. **iterations（迭代次数）**
   - 越大计算越慢，暴力破解成本越高
   - 推荐：**100000 次以上**

3. **digest（哈希算法）**
   - 常用：`sha256`、`sha512`
   - 不要用 md5、sha1（已不安全）

4. **keylen**
   - 输出密钥长度，一般 32/64 字节即可

---

## 验证密码逻辑
登录时：
1. 从数据库取出该用户的 `salt` 和 `hash`
2. 用用户输入的密码 + 同样 salt、迭代次数、算法重新计算
3. 对比新生成的 hash 和数据库里的是否一致
4. 一致则密码正确

---

## 为什么用 pbkdf2 而不是 md5/sha？
- md5/sha 太快，黑客可以秒试海量密码
- pbkdf2 **故意做慢**，暴力破解成本极高
- 加盐后，相同密码生成不同结果

---

## 现代更好的选择
如果是新项目，更推荐：
- `crypto.scrypt`（Node.js 推荐）
- `bcrypt`
- `argon2`（目前最安全）

但 `pbkdf2` 兼容性最好、标准通用，依然广泛使用。

如果你需要，我可以给你写一套**完整注册+登录密码验证封装函数**，直接复制就能用。