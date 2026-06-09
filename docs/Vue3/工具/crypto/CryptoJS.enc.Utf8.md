这句就是：**把解密后的二进制数据，转回正常人能看懂的明文字符串**。

我用最简单、最精准的方式给你讲透：

# 1. 这行是干什么的？
```js
decrypted.toString(CryptoJS.enc.Utf8)
```

意思：
> 解密后得到的是**字节数据（WordArray）**，
> 把它按 **UTF-8 编码** 转换成字符串。

结果就是你原来的明文：
`"123456"`、`"你的密码"` 这种。

---

# 2. 为什么要写 CryptoJS.enc.Utf8？
因为解密出来的不是字符串，是 **字节数组**。

你必须告诉它：
“这些字节是 **UTF-8 编码的文本**，帮我转成字符串。”

如果不写，默认是 Hex 或乱码。

---

# 3. 和加密时的 toString 对比

### 加密时
```js
encrypted.toString()
// 默认 = Base64（用于传输）
```

### 解密时
```js
decrypted.toString(CryptoJS.enc.Utf8)
// 明确转成 UTF-8 明文（用于展示）
```

---

# 4. 完整解密代码（对应你之前的加密）
```js
export function decrypt(cipherText) {
  const keyStr = '1234567890123456'
  const ivStr = 'abcdef1234567890'

  const key = CryptoJS.enc.Utf8.parse(keyStr)
  const iv = CryptoJS.enc.Utf8.parse(ivStr)

  const decrypted = CryptoJS.AES.decrypt(cipherText, key, {
    iv,
    mode: CryptoJS.mode.CBC,
    padding: CryptoJS.pad.Pkcs7,
  })

  // 转成 UTF-8 明文
  return decrypted.toString(CryptoJS.enc.Utf8)
}
```

---

# 5. 超级总结
- `decrypted` 是 **WordArray 字节数据**
- `.toString(CryptoJS.enc.Utf8)`
  → **按 UTF-8 转回明文字符串**
- 这是**解密的标准、正确、唯一写法**
- 不写会得到一串 16 进制乱码，不是原文