AES加密与解密
CryptoJS.AES.encrypt 是一个用于对数据进行 AES加密 的方法，支持多种模式（如 CBC、ECB）和填充方式（如 PKCS7）。以下是一个简单的加密和解密示例。

```js
// 引入CryptoJS库
const CryptoJS = require("crypto-js");
// 定义明文、密钥和偏移量
const plaintext = "Hello, World!";
const key = CryptoJS.enc.Utf8.parse("1234567890123456"); // 16字节密钥
const iv = CryptoJS.enc.Utf8.parse("6543210987654321"); // 16字节偏移量
// AES加密
const encrypted = CryptoJS.AES.encrypt(plaintext, key, {
   iv: iv,
   mode: CryptoJS.mode.CBC,
   padding: CryptoJS.pad.Pkcs7,
});
console.log("加密后的数据:", encrypted.toString());
// AES解密
const decrypted = CryptoJS.AES.decrypt(encrypted, key, {
   iv: iv,
   mode: CryptoJS.mode.CBC,
   padding: CryptoJS.pad.Pkcs7,
});
console.log("解密后的数据:", decrypted.toString(CryptoJS.enc.Utf8));

```

注意事项

密钥与偏移量：AES加密需要一个固定长度的密钥（128位、192位或256位）和偏移量（IV），通常为16字节。

模式选择：默认模式为 CBC，安全性较高，但需要提供 IV。如果使用 ECB 模式，则无需 IV，但安全性较低。

填充方式：CryptoJS 默认使用 PKCS7 填充，与 PKCS5 等效。

适用场景

数据传输中的加密保护。

前后端一致性加解密（需确保使用相同的模式、填充方式和密钥）。