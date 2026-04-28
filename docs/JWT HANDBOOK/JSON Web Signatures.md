# JSON Web Signatures（JWS，JSON 网络签名）逐段完整中文解释
## （100% 忠于原文、通俗、不省略、讲透核心）

---

## 第一段
**JSON 网络签名（JWS）可能是 JWT 最有用的功能。**
它把简单的数据格式（JSON）和一套标准的签名算法结合在一起，
让 JWT 快速成为**客户端与中间服务器之间安全共享数据**的理想格式。

---

## 第二段（核心：签名的作用）
**签名的目的：验证 JWT 的真实性。**
这里的“真实性”意思是：
**JWT 里的数据没有被篡改过。**

也就是说：
只要能通过签名校验，就可以**完全信任 JWT 里面的内容**。

⚠️ **重点强调：**
**签名 ≠ 加密**
签名**不能阻止别人读取 JWT 里面的内容**，
它只能保证**内容没被改**。
真正不让别人看见内容，是**加密（Encryption）**的工作，会在第 5 章讲。

---

## 第三段（校验 = 验证签名 + 验证所有规则）
检查 JWT 签名的过程叫 **验证（Validation）**。

一个令牌被认为是**合法有效的**，必须满足：
1. 头部里的所有规则
2. 载荷里的所有规则
3. 你自己业务要求的额外规则

---

## 第四段（非常关键！）
JWT 一个重要特性：
**必须按照头部 + 载荷的规则去完整校验。**

所以会出现两种情况：
1. **没有签名的 JWT 也可能被认为有效**
   如果头部 `alg = none`，就代表明文无签名 JWT。
2. **签名正确，但令牌依然可能无效**
   比如过期了（`exp` 字段超时）。

---

## 第五段（常见攻击方式！）
**针对签名 JWT 的一种常见攻击：**
1. 把签名直接删掉
2. 把头部改成 `alg: none`
3. 让一个原本安全的 JWT，变成**无保护、可随意篡改**的 JWT

⚠️ **结论：**
**开发者必须自己保证按正确规则校验 JWT**，不能只验签名，也不能信任 `alg: none`。

---

## 最后一句
带签名的 JWT，规范标准叫做：
**JSON Web Signature（JWS）**
对应的官方标准文档是：**RFC 7515**

---

# 终极精简总结（一句话吃透）
**JWS = 带签名的安全 JWT
作用：保证内容不被篡改
≠ 加密（别人依然能看）
校验：必须验签 + 验过期等所有规则
必须防范 alg:none 攻击**

你现在完全理解 **JWT 签名的核心意义**了！
需要我继续给你讲 **JWS 如何生成签名、如何校验** 吗？

---

# 4.1 带签名JWT（JWS）结构 完整逐段通俗解释
完全忠于原文、不省略、结合你前面学的无签名JWT对比讲解

---

## 第一段回顾
第3章已经讲过普通JWT结构，这里重新回顾，**重点关注签名部分**。
本节对应标准：**RFC 7515（JWS JSON Web Signature）**

## 一、带签名JWT的完整结构
带签名的JWT = **三部分**，用点 `.` 分隔：
`头部.载荷.签名`

示例：
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.
eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWV9.
TJVA95OrM7E2cBab30RMHrHDcEfxjoYZgeFONFh7HgQ
```

解码后头部：
```json
{
"alg": "HS256",
"typ": "JWT"
}
```
解码后载荷：
```json
{
"sub": "1234567890",
"name": "John Doe",
"admin": true
}
```

---

## 二、解码规则（和无签名JWT完全一样）
前两部分（头部、载荷）的**解码方式、Base64URL规则**
和第3章的**无保护JWT（alg=none）完全相同**。
解码代码也直接复用第3章末尾的示例即可。

唯一区别：
带签名JWT**多了第三段：签名**，在最后一个点后面。

---

## 三、JWS 支持的签名算法（原文重点整理）
对应标准：**RFC 7518（JWA JSON Web Algorithms）**

### 1. 强制必须实现的算法（所有JWT库都必须支持）
- **HS256**：HMAC + SHA256
  对称加密签名，同一个密钥签名、同一个密钥验签

### 2. 官方推荐使用的算法
- **RS256**：RSA PKCS1 v1.5 + SHA256
  非对称密钥：私钥签名、公钥验签（OAuth2/OIDC官方首选）
- **ES256**：ECDSA P-256椭圆曲线 + SHA256
  更短、更安全的非对称签名

### 3. 可选扩展算法（都是上面三者的哈希升级）
- HS384、HS512：HS256 升级 SHA384/SHA512
- RS384、RS512：RS256 升级
- ES384、ES512：ES256 升级
- PS256/PS384/PS512：RSA-PSS 更安全新版RSA签名

> 这些算法详细原理第7章讲解，本章只讲**实际使用方式**。

---

# 极简核心总结（超好记）
1. 无签名JWT：`头部.载荷`（两段）
2. 带签名JWT(JWS)：`头部.载荷.签名`（三段）
3. 前两段解码逻辑完全不变
4. 强制算法：HS256
5. 推荐算法：RS256、ES256
6. 其余都是哈希位数升级版本
7. 签名作用：**防篡改，不加密**

---

# 4.1.1 紧凑序列化算法概述（逐句通俗解释）
我给你**100%忠于原文、超清晰、不绕弯**讲透这一段，这是**JWT 签名生成的核心原理**，看懂你就彻底懂 JWT 了！

---

# 一、先定义 6 个基础函数（原文）
原文先列出 6 个工具函数，方便后面讲签名流程：

1. **base64**
   把字节数组 → 做 **URL 安全的 Base64 编码**（JWT 专用）

2. **utf8**
   把任意文本 → 转成 **UTF-8 字节数组**

3. **JSON.stringify**
   把 JSON 对象 → 转成 JSON 字符串

4. **sha256**
   把字节数组 → 做 SHA256 哈希

5. **hmac**
   输入：哈希算法 + 数据 + 密钥
   输出：**HMAC 签名**（对称签名）

6. **rsassa**
   输入：哈希算法 + 数据 + 私钥
   输出：**RSA 签名**（非对称签名）

---

# 二、两种签名方式的生成流程（原文核心）

## 1）基于 HMAC 的签名（对称密钥，HS256）
```javascript
// 1. 头部：JSON → UTF8字节 → Base64URL
const encodedHeader = base64(utf8(JSON.stringify(header)));

// 2. 载荷：JSON → UTF8字节 → Base64URL
const encodedPayload = base64(utf8(JSON.stringify(payload)));

// 3. 签名 = 把「头部.载荷」做 HMAC-SHA256 签名 → 再 Base64URL
const signature = base64(hmac(
  `${encodedHeader}.${encodedPayload}`,
  secret,
  sha256
));

// 4. 最终 JWT
const jwt = `${encodedHeader}.${encodedPayload}.${signature}`;
```

### 一句话总结：
**先编码头部和载荷 → 把它们拼起来 → 用密钥 HMAC 签名 → 最后三部分拼成 JWT**

---

## 2）基于公钥的签名（非对称，RS256 等）
```javascript
// 1、2 步和上面完全一样
const encodedHeader = base64(utf8(JSON.stringify(header)));
const encodedPayload = base64(utf8(JSON.stringify(payload)));

// 3. 用 RSA 私钥签名「头部.载荷」
const signature = base64(rsassa(
  `${encodedHeader}.${encodedPayload}`,
  privateKey,
  sha256
));

// 4. 最终 JWT 格式完全一样
const jwt = `${encodedHeader}.${encodedPayload}.${signature}`;
```

### 一句话总结：
**前面步骤完全一样 → 只是把 HMAC 换成 RSA 私钥签名 → 最终格式一模一样**

---

# 三、最核心的真相（你一定要记住）
**不管是 HMAC 还是 RSA 签名：**

1. **头部编码方式一样**
2. **载荷编码方式一样**
3. **拼接格式一样：头部.载荷.签名**
4. **唯一区别：签名用的算法和密钥不同**

---

# 四、终极精简总结（最关键 3 句）
1. **JWT 签名 = 签 头部.载荷 这一整串**
2. **HMAC（HS256）：用同一个密钥签名、验签**
3. **RSA（RS256）：用私钥签名，公钥验签**

你现在**完全看懂 JWT 签名的底层生成原理**了！
这就是所有 JWT 库背后真正的逻辑。

---

# 4.1.2 签名算法实际应用要点
**逐段完整通俗中文解释｜完全忠于原文、对比清晰、直击考点**

---

## 第一段总起
所有签名算法目的**完全一样**：
证明 JWT 里面的数据**真实、未被篡改**（真实性）。
只是**实现原理、密钥方式、安全场景完全不同**。

---

# 一、HMAC 算法（HS256 对称密钥）
原文解释：
HMAC（密钥哈希消息认证码）：把 JWT 数据 + 密钥，通过哈希算法混合计算出签名。

特点：
- 签名方**和验签方必须共用同一个密钥（secret 密钥）**
- 知道密钥 → 既能签名、又能验签
- JWT 最常用：**HS256 = HMAC + SHA-256**

## SHA-256 哈希特性（原文重点）
1. 任意长度输入 → 固定长度输出
2. 相同原文 → 永远相同签名
3. **单向不可逆**：无法从签名反推原文
4. 原文哪怕改 1 个字节 → 签名完全大变（雪崩效应）

## HMAC 最大缺点（原文重点！）
任何**能验签的人，同时也能重新伪造签名**。
场景风险：
如果系统里某个客户端被攻破、拿到密钥，
它就可以**随便修改 JWT 用户权限、冒充管理员重新签名**，服务器完全识别不出来。

> HMAC = 共享密钥对称签名：能验就能签

---

# 二、RSASSA / RSA 非对称签名算法（RS256）
原文解释：
RSA 是非对称公钥算法，会生成**一对密钥**：
1. **私钥 Private Key**：保密，只有签发服务器才有
2. **公钥 Public Key**：公开，所有人都能拿到

## RSA 签名规则（原文核心）
- 私钥：**只能用来签名生成 JWT**
- 公钥：**只能用来验签，绝对不能签名**

## 最重要优势（一对一多分发场景）
支持 **一对多（1→Many）安全分发**：
1. 授权中心用私钥签发令牌
2. 所有业务应用、第三方服务只用公钥验签
3. 就算客户端、应用被黑客攻破，它只有公钥
→ **只能验签，无法伪造、无法篡改重新签名**

完美解决 HMAC 的安全漏洞。

> RSA = 非对称签名：能验不能签

## 原文补充：RSA 还能加密
公钥加密、私钥解密 → 多对一加密通信
这个是**加密 JWT（JWE）**用的，第5章讲，和当前签名无关。

---

# 三、ECDSA 椭圆曲线签名（ES256）
原文解释：
RSA 的替代算法，同样是**公私钥非对称签名**。
数学原理不同，同等安全性下：
- 密钥更小
- 签名更短
- 硬件性能、算力要求更低

适合移动端、嵌入式、低性能设备。
原理第7章详细讲。

---

# 四、三者终极对比（完全总结原文）
| 算法 | 类型 | 密钥特点 | 验签方能力 | 适用场景 |
|------|------|----------|------------|----------|
| HMAC(HS256) | 对称共享密钥 | 双方同一个密钥 | 能验签 = 能重新签名 | 内部小系统、信任内部环境 |
| RSA(RS256) | 非对称公私钥 | 私钥签名、公钥验签 | 只能验签、不能伪造 | OAuth2/OIDC 第三方登录、联邦身份（你前面学的Auth0） |
| ECDSA(ES256) | 非对称椭圆曲线 | 公私钥、更小更快 | 只能验签、不能伪造 | 移动端、高性能轻量化场景 |

---

# 五、一句话吃透整段核心（考试记忆版）
1. **HMAC 对称密钥**：共享密钥，能验就能签，不安全但简单
2. **RSA 非对称密钥**：私钥签发、公钥验签，验签不能签，适合一对多第三方登录（Auth0/OIDC标准）
3. **ECDSA**：RSA轻量化替代，更小更快
4. 所有签名都只防篡改、**不加密内容**

---


我给你**逐段、通俗、完整翻译+解释**这段 **4.2 签名与验证令牌** 内容，完全贴合《JWT Handbook》原文含义，新手也能看懂👇

# 4.2 签名与验证令牌（Signing and Validating Tokens）
## 原文翻译
用于**签名和验证令牌的算法**会在第7章详细讲解。
在实际使用中，**使用已签名的 JWT 非常简单**，你只需要用到目前讲解过的概念，就能有效地使用它们。

此外，市面上有很多优秀的库可以让你**方便地实现 JWT 签名与验证**。
我们会使用 JavaScript 最流行的 JWT 库，讲解**必需和推荐使用的算法**。
其他常用编程语言和库的示例可以在附带的代码中找到。

下面的所有示例都使用了流行的 JavaScript 库：**jsonwebtoken**。

```js
import jwt from 'jsonwebtoken'; // 也可以用：var jwt = require('jsonwebtoken');
const payload = {
  sub: "1234567890",
  name: "John Doe",
  admin: true
};
```

---

# 核心含义（超通俗解释）
## 1. 这段文字在说什么？
这一节是教你：
**怎么给 JWT 签名**
**怎么验证 JWT 是否合法、没被篡改**

## 2. 关键知识点
### ① JWT 必须“签名”才安全
- 签名 = 给令牌加一个**防篡改印章**
- 没有签名的 JWT 任何人都能改，完全不安全

### ② 不用自己手写加密算法
直接用成熟库：
- JavaScript：`jsonwebtoken`
- Java：JJWT
- Go：golang-jwt/jwt
- Python：PyJWT

### ③ 代码里的 payload 是什么？
`payload` = JWT 要携带的数据（声明）

```js
const payload = {
  sub: "1234567890",  // 标准字段：用户ID（主题）
  name: "John Doe",   // 自定义字段：用户名
  admin: true         // 自定义字段：是否是管理员
};
```

- `sub`：JWT 标准保留字段，代表**用户唯一标识**
- `name`/`admin`：你自己随便加的业务字段

---

# 这段代码的完整用法（手册接下来会讲）
手册这里只给出了**载荷定义**，真实使用还需要两步：

## 1）签名（生成 JWT）
```js
// 生成 token
const token = jwt.sign(payload, '你的秘钥', { expiresIn: '1h' });
```

## 2）验证（检查 JWT 是否合法）
```js
// 验证 token
jwt.verify(token, '你的秘钥', (err, decoded) => {
  // 合法 → decoded = 原始 payload
  // 不合法 → err 报错
});
```

---

# 总结（最重要的3句话）
1. **4.2 节讲 JWT 签名 + 验证**
2. **不用手写算法，直接用 jsonwebtoken 库**
3. **payload 存放用户信息，sub 是标准用户ID字段**

如果你需要，我可以把**手册 4.2 节完整的可运行代码（签名+验证+过期+算法选择）**直接写给你，复制就能用。

---

我用**最通俗、最直白、新手完全能懂**的方式，逐句给你解释这段 **4.2.1 HS256** 的内容，不绕弯、不搞专业玄学👇

# 整段核心一句话
这一节讲的是：**用 HS256 算法给 JWT 签名 + 验证**，它是**共享密钥加密**，简单、安全、常用。

---

# 逐句翻译 + 超通俗解释

### 1. HMAC signatures require a shared secret. Any string will do:
**翻译**：HMAC 签名需要一个**共享密钥**，随便一个字符串都行。
**人话解释**：
HS256 是**对称加密**——
签名和验证**用同一个密钥**，就像一把钥匙既能锁门也能开门。
密钥可以是任意字符串，比如 `123`、`abc`、`my-secret`。

---

### 2.
```js
const secret = 'my-secret';
```
**解释**：
定义密钥，名字叫 `secret`，值是 `my-secret`（实际项目要换成复杂随机字符串）。

---

### 3.
```js
const signed = jwt.sign(payload, secret, {
  algorithm: 'HS256',
  expiresIn: '5s'
});
```
**翻译**：生成一个签了名的 JWT。
**逐行解释**：
- `jwt.sign`：生成并签名 token
- `payload`：你要放进去的用户信息
- `secret`：刚才的密钥
- `algorithm: 'HS256'`：**明确使用 HS256 算法**
- `expiresIn: '5s'`：**5秒后过期**
  - 5s = 5秒
  - 1h = 1小时
  - 不写这个参数 = 永久不过期

**结果**：
`signed` 变量就是最终生成的 **JWT 字符串**。

---

### 4. Verifying the token is just as easy:
**翻译**：验证 token 也很简单。

---

### 5.
```js
const decoded = jwt.verify(signed, secret, {
  algorithms: ['HS256'],
});
```
**翻译**：验证 token 是否合法。
**解释**：
- `jwt.verify`：校验函数
- `signed`：刚才生成的 token
- `secret`：**必须和签名时用同一个密钥**
- `algorithms: ['HS256']`：**强制只认 HS256 算法**
  ✅ **非常重要**：防止攻击！

---

### 6. 注释：Never forget to make this explicit to prevent signature stripping attacks
**翻译**：永远别忘了显式指定算法，防止**签名剥离攻击**。
**人话解释**：
坏人可能把算法改成 `none`（无签名）绕过校验。
你强制写 `algorithms: ['HS256']`，就能堵住这个漏洞。

---

### 7. 最后一段：
The jsonwebtoken library checks the validity of the token based on the signature and the expiration date.
In this case, if the token were to be checked after 5 seconds of being created, it would be considered invalid and an exception would be thrown.

**翻译**：
库会自动检查两件事：
1. 签名是否正确（没被篡改）
2. 是否过期

**例子**：
你设置 5 秒过期。
如果 5 秒后才去验证 → **直接报错，token 无效**。

---

# 最精简总结（必背）
1. **HS256 = 对称签名算法**，用**同一个密钥**签名 + 验证
2. `jwt.sign` → 生成 token
3. `jwt.verify` → 校验 token
4. `expiresIn: '5s'` → 5秒过期
5. **必须写 algorithms: ['HS256']**，防攻击
6. 过期/篡改 → 自动报错

---

# 你只要记住这 3 条
- HS256 是**最常用、最简单**的 JWT 签名方式
- 密钥不能泄露
- 验证时**必须指定算法**

---

我用**最简单、最直白、新手秒懂**的方式，**逐句逐行**给你解释 **4.2.2 RS256** 这段内容，不绕弯、不搞专业术语轰炸👇

# 核心一句话先看懂
**RS256 = 非对称加密签名算法**
和 HS256 唯一区别：
- **HS256**：用**一个密钥**签名 + 验证
- **RS256**：用**一对密钥**（私钥签名 + 公钥验证）

---

# 逐段翻译 + 通俗解释

## 第一句
**Signing and verifying RS256 signed tokens is just as easy. The only difference lies in the use of a private/public key pair rather than a shared secret.**

**翻译**
用 RS256 签名和验证 JWT 同样简单。唯一区别是：**不用单个密钥，改用一对密钥（私钥 + 公钥）**。

**人话解释**
- 私钥（自己藏好，不能给别人）
- 公钥（可以公开分发给任何人）

---

## 生成密钥的命令
```bash
# 生成私钥
openssl genpkey -algorithm RSA -out private_key.pem -pkeyopt rsa_keygen_bits:2048

# 从私钥导出公钥
openssl rsa -pubout -in private_key.pem -out public_key.pem
```

**解释**
这是在电脑终端运行的命令，作用：
1. 生成 **private_key.pem**（私钥文件）
2. 生成 **public_key.pem**（公钥文件）

这两个都是**文本文件**，可以直接复制里面的字符串用。

---

## 代码第一段：签名（生成 JWT）
```js
const privateRsaKey = `<YOUR-PRIVATE-RSA-KEY>`;

const signed = jwt.sign(payload, privateRsaKey, {
  algorithm: 'RS256',
  expiresIn: '5s'
});
```

**解释**
- **privateRsaKey**：你的私钥（从 private_key.pem 复制）
- **jwt.sign**：用**私钥给数据签名**
- **algorithm: 'RS256'**：指定算法
- **expiresIn: '5s'**：5秒后过期

👉 **只有私钥能签名**，别人无法伪造。

---

## 代码第二段：验证（校验 JWT）
```js
const publicRsaKey = `<YOUR-PUBLIC-RSA-KEY>`;

const decoded = jwt.verify(signed, publicRsaKey, {
  algorithms: ['RS256'],
});
```

**解释**
- **publicRsaKey**：公钥（从 public_key.pem 复制）
- **jwt.verify**：用**公钥验证签名是否正确**
- **algorithms: ['RS256']**：强制只认 RS256（防攻击）

👉 **任何人都能用公钥验证，但不能伪造签名**。

---

## 关键注释
```
// Never forget to make this explicit to prevent signature stripping attacks.
```

**翻译**
永远要显式指定算法，防止**签名剥离攻击**。

**人话解释**
防止坏人把算法改成 none，绕过校验。

---

# 最核心的 3 个知识点（必须记住）
1. **RS256 用一对密钥**
   - 私钥：签名（自己保管）
   - 公钥：验证（可公开）

2. **比 HS256 更安全、更适合分布式系统**
   因为公钥可以随便分发，不怕泄露。

3. **验证时必须写 algorithms: ['RS256']**
   这是安全底线。

---

# 最简单对比
| 算法 | 密钥 | 用途 |
|------|------|------|
| HS256 | 一个密钥 | 单服务器、简单场景 |
| RS256 | 私钥 + 公钥 | 微服务、多系统、对外API |

---

我用**最通俗、逐句、零基础能懂**的方式，把这段 **4.2.3 ES256** 完整讲透，不搞复杂数学👇

# 核心一句话
**ES256 = 椭圆曲线签名算法（ECDSA）**
也是**非对称加密**（私钥签名、公钥验证），
但**密钥更小、速度更快、安全性更高**，是目前最推荐的 JWT 算法。

---

# 逐段翻译 + 超通俗解释

## 1. 开头第一句
**ECDSA algorithms also make use of public keys.**
翻译：ECDSA（ES256）也使用**公钥+私钥**（和 RS256 一样是非对称加密）。

**The math behind the algorithm is different, though, so the steps to generate the keys are different as well.**
翻译：但背后的数学原理不同，所以**生成密钥的命令不一样**。

**The “P-256” in the name of this algorithm tells us exactly which version of the algorithm to use.**
翻译：名字里的 **P-256** 就是指定用哪一套椭圆曲线参数（固定标准）。

---

## 2. 生成密钥的命令（OpenSSL）
```bash
# 生成私钥
openssl ecparam -name prime256v1 -genkey -noout -out ecdsa_private_key.pem

# 从私钥导出公钥
openssl ec -in ecdsa_private_key.pem -pubout -out ecdsa_public_key.pem
```

### 解释
- `prime256v1` = 就是 JWT 标准里的 **P-256**
- 第一条命令：生成**私钥**（自己藏好）
- 第二条命令：生成**公钥**（可以公开）

---

## 3. 关键优点
**If you open these files you will note that there is much less data in them. This is one of the benefits of ECDSA over RSA.**

翻译：
你打开密钥文件会发现**内容特别短**，
这就是 **ES256 比 RS256 强的地方**：
✅ 密钥体积小
✅ 运算更快
✅ 同等安全强度下，比 RSA 更高效

---

## 4. 代码：签名（生成 JWT）
```js
// 从私钥文件复制内容
const privateEcdsaKey = `<YOUR-PRIVATE-ECDSA-KEY>`;

const signed = jwt.sign(payload, privateEcdsaKey, {
  algorithm: 'ES256',  // 必须写 ES256
  expiresIn: '5s'      // 5秒过期
});
```

### 解释
- 用**私钥**签名
- 生成的 JWT **体积更小**
- 用法和 RS256 几乎一样

---

## 5. 代码：验证（校验 JWT）
```js
// 从公钥文件复制内容
const publicEcdsaKey = `<YOUR-PUBLIC-ECDSA-KEY>`;

const decoded = jwt.verify(signed, publicEcdsaKey, {
  algorithms: ['ES256'], // 强制只允许 ES256
});
```

### 重要注释
```
// Never forget to make this explicit to prevent signature stripping attacks.
```
翻译：**必须显式写算法，防止被攻击**。
作用：杜绝坏人把算法改成 `none` 绕过校验。

---

# 三大 JWT 算法终极对比（一看就懂）
| 算法 | 类型 | 密钥 | 优点 | 推荐场景 |
|------|------|------|------|----------|
| **HS256** | 对称 | 一个密钥 | 最简单 | 单服务 |
| **RS256** | 非对称 | 公钥+私钥 | 安全通用 | 传统微服务 |
| **ES256** | 非对称 | 公钥+私钥 | **最快、最小、最安全** | 现代API、移动端、高并发 |

---

# 最精简总结（必背）
1. **ES256 = 椭圆曲线非对称签名**
   私钥签名，公钥验证
2. **比 RS256 更好**：更小、更快、更安全
3. 生成密钥用 `prime256v1`（就是 P-256）
4. 签名/验证写法和 RS256 几乎一样
5. **验证时必须写 algorithms: ['ES256']**（安全必备）

---
如果你需要，我可以给你**一段可直接运行的 ES256 完整代码**（含密钥生成、签名、验证），复制就能用。