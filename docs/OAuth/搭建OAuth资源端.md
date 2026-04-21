# 第4章：搭建一个简单的 OAuth 受保护资源 **精准解读**
我**只解读你当前这段内容**，不扩展、不提前，完全贴合书本原文。

---

# 本段核心一句话
**搭建一个「资源服务器」，它只做三件事：接收 token → 验证 token → 决定是否返回受保护数据。**

---

# 1. 本章要做什么？
前面你已经实现了：
- 客户端（获取 token、刷新 token）
- 授权服务器（发 token）

现在要实现第三个组件：
## **受保护资源（Protected Resource）**
也就是**真正存放用户数据的API服务**。

---

# 2. 资源服务器的职责（原文重点）
只做 3 件事：
1. **从 HTTP 请求里取出 token**
   （从 `Authorization: Bearer xxx` 头）
2. **验证这个 token 是否有效**
3. **检查权限，决定是否返回数据**

它**不负责登录**
**不负责发 token**
**不负责授权页面**

---

# 3. 资源服务器如何验证 token？
本章示例中：
- 资源服务器 **和授权服务器共用同一个数据库**
- 这样它可以直接查库，看 token 是否存在、是否有效

真实场景也可以：
- 授权服务器提供检查接口（introspection）
- 或使用 JWT 自包含 token（直接解析）

---

# 4. 架构说明（原文重要）
- 授权服务器（9001）：发 token、管用户授权
- **资源服务器（9002）：管受保护API**
- 客户端（9000）：第三方应用

虽然它们**概念上完全分离**，
但现实中经常**部署在一起、共用数据库**。

本章练习：
- 分开运行（不同端口）
- 但共享数据库，方便验证 token

---

# 5. 本章练习内容
- 给你一个现成的 API
- 你给它加上 OAuth 保护
- 只有带**有效 access_token** 的请求才能访问
- 没有 token / 无效 token → 返回 401 错误

---

# 本段最终极简总结
## 第4章 = 实现 OAuth 架构的第三个角色：
### **受保护资源服务器**
### 功能：验证 token → 保护 API → 返回受保护数据

---
# 4.1 从 HTTP 请求中解析 OAuth token **逐段精准解读**
我**严格只解读你当前这段内容**，完全贴合书本，不扩展、不提前。

---

# 本段核心一句话
**写一个工具函数，从 HTTP 请求的 3 个位置里提取 access_token，优先取请求头。**

---

# 1. 本节要做的事
实现一个 **Express 中间件函数**：
```js
var getAccessToken = function(req, res, next) {

};
```
作用：**从请求里把 token 找出来**。

---

# 2. OAuth 允许的 3 种传 token 方式（RFC 6750）
按优先级排序：

1. **Authorization 请求头（推荐 ✅）**
   ```
   Authorization: Bearer 令牌
   ```
2. **表单 body 参数**
   ```
   access_token=令牌
   ```
3. **URL 查询参数（最后选择 ⚠️）**
   ```
   ?access_token=令牌
   ```

---

# 3. 第一步：从 Authorization 头取 token
```js
var auth = req.headers['authorization'];
if (auth && auth.toLowerCase().indexOf('bearer') == 0) {
  inToken = auth.slice('bearer '.length);
}
```

规则：
- 不区分大小写 `bearer` / `Bearer` / `BEARER`
- 截取掉 `bearer ` 后面的就是 token
- **这是最安全、最推荐的方式**

---

# 4. 第二步：从表单 body 取 token
```js
} else if (req.body && req.body.access_token) {
  inToken = req.body.access_token;
}
```

不推荐原因：
- 限制 API 只能用 form 表单
- JSON 请求无法用

---

# 5. 第三步：从 URL 查询参数取 token
```js
} else if (req.query && req.query.access_token) {
  inToken = req.query.access_token
}
```

**最不推荐 ❌**
原因：
- URL 会被记录在日志
- 容易泄露
- 会被浏览器历史保存
- 只能作为最后选择

---

# 6. 最终这个函数做了什么？
按顺序检查：
1. **请求头 Authorization: Bearer**
2. **body 中的 access_token**
3. **url 中的 ?access_token**

找到就存到 `inToken`，没找到就是 `null`。

---

# 本段最终极简总结
## 4.1 只做一件事：
### **写一个中间件，从 3 个位置提取 access_token**
### 优先级：请求头 > 表单 > URL 参数

---
# 4.2 Validating the token against our data store
## **核心一句话总结**
**把从请求里拿到的 token，去数据库里查一下是否存在、有效。有效就允许访问，无效就返回 401。**

---

# 逐段精准解读（只讲当前内容）

## 1. 本节要做什么？
上一节 `getAccessToken` 已经从请求里**取出了 token**
这一节要做的是：
### **去数据库验证这个 token 是不是真的、有效的**

## 2. 环境说明
- 授权服务器和资源服务器**共用同一个数据库**
- 这是小型 OAuth 系统最常见的做法
- 令牌存在 `database.nosql` 文件里

## 3. 数据库查询逻辑
```js
nosql.one(function(token) {
  if (token.access_token == inToken) {
    return token;
  }
}, function(err, token) {
  if (token) {
    console.log("We found a matching token: %s", inToken);
    req.access_token = token;
    next();
    return;
  } else {
    console.log('No matching token was found.');
  }
});
```

### 功能：
- 遍历数据库里的所有 token
- 找到和传进来的 `inToken` 一样的
- 找到 → 把 token 信息绑到 `req.access_token`
- 找不到 → 后面返回 401

## 4. 数据库里的 token 结构
```json
{
  "access_token": "s9nR4qv7qVadTUssVD5DqA7oRLJ2xonn",
  "clientId": "oauth-client-1",
  "scope": ["foo"]
}
```

包含：
- token 值
- 客户端 ID
- 权限范围（scope）

---

# 5. 要不要共享数据库？（书本重要知识点）
原文告诉你 3 种验证 token 的方式：

1. **共享数据库（本章做法）**
   直接查库，简单高效
2. **Token Introspection（第11章讲）**
   资源服务器调用授权服务器的检查接口
   不用共享数据库
3. **JWT（自包含令牌）**
   不用查库，直接解析验证

---

# 6. 把验证函数变成中间件
```js
app.all('*', getAccessToken);
```
让**所有接口**都先检查 token

或者只给特定接口加保护：
```js
app.post("/resource", getAccessToken, function(req, res){
});
```

---

# 7. 最终业务逻辑判断
```js
if (req.access_token) {
  res.json(resource); // 有效 → 返回数据
} else {
  res.status(401).end(); // 无效 → 401 未授权
}
```

---

# 本节最终极简总结
## 4.2 做的只有一件事：
### **取出 token → 查数据库 → 有效就继续，无效就 401**

---

# 你现在学会了资源服务器的全部核心：
✅ 从请求中提取 token
✅ **去数据库验证 token**
✅ 有效返回 200，无效返回 401

**这就是 OAuth 资源服务器的标准工作流程！**

---

# 4.3 Serving content based on the token
## **只解读当前内容 · 精准 · 清晰**

---

# 本段核心一句话
**根据 token 里的信息（scope、用户、客户端）返回不同内容，而不是只做“能/不能访问”。**

---

# 1. 本节要解决什么问题？
之前的资源服务器只做：
- 有 token → 给数据
- 没 token → 401

但真实 API 需要更精细：
- 不同用户 → 不同数据
- 不同权限（scope）→ 不同功能
- 不同客户端 → 不同返回结果

这一节就是**基于 token 内容做动态返回**。

---

# 2. 新增工具函数：requireAccessToken
把“检查有没有 token”抽成公共中间件：

```js
var requireAccessToken = function(req, res, next) {
  if (req.access_token) {
    next(); // 有 token → 继续
  } else {
    res.status(401).end(); // 没 token → 拒绝
  }
});
```

作用：
**所有受保护接口都可以直接复用，不用重复写 401 判断。**

---

# 3. 本节要实现的功能（基于 OAuth 三个维度）
根据 token 里的信息动态返回内容：

1. **scope（权限范围）**
   有 scope A → 返回 A 内容
   有 scope B → 返回 B 内容
2. **resource owner（资源所有者/用户）**
   不同用户 → 看到自己的数据
3. **client（客户端）**
   不同第三方应用 → 不同限制或展示

---

# 4. 本章练习的结构
- 资源服务器已经带上 `getAccessToken`
- 已经带上 `requireAccessToken`
- 你要做的：**在接口里根据 token 信息返回不同内容**

---

# 5. 客户端表现
- 客户端有多个按钮，调用不同受保护接口
- 每个接口需要**不同 scope**
- 授权时你可以选择授予哪些 scope
- 接口会根据你授予的 scope 动态返回结果

---

# 本段极简总结
## 4.3 做的事情：
### **不再只是“能/不能访问”
### 而是根据 token 里的 scope、用户、客户端 → 返回不同内容**

---

# 4.3.1 + 4.3.2 完整精准解读（只讲你当前内容）
我**严格只解读你给的这段文字**，不扩展、不提前，100%贴合书本，让你完全看懂。

---

# 先给你 **超级核心总结**
## 4.3 一共讲两件事：
1. **不同接口 → 必须要有不同 scope 才能访问**（4.3.1）
2. **同一个接口 → 根据不同 scope 返回不同数据**（4.3.2）

这就是 OAuth **scope 权限设计**的全部精髓！

---

# 4.3.1 Different scopes for different actions
## 不同动作需要不同权限

### 本段核心一句话
**一个接口 = 一种权限（read / write / delete）**
**有对应 scope 才能调用，没有就返回 403**

---

## 1. 三个接口，三种权限
- `GET /words` → 需要 `read`
- `POST /words` → 需要 `write`
- `DELETE /words` → 需要 `delete`

## 2. 代码逻辑（书本一模一样）
```js
if (__.contains(req.access_token.scope, 'read')) {
  返回数据
} else {
  返回 403 权限不足
}
```

## 3. 权限不足时返回标准格式（OAuth 规范）
```js
res.set('WWW-Authenticate', 'Bearer realm=..., error="insufficient_scope", scope="read"');
res.status(403);
```

## 4. 最终效果
- 给 read → 只能看
- 给 write → 能新增
- 给 delete → 能删除
- 不给 → 调用就报错 403

---

# 4.3.1 极简总结
## **接口级权限控制：一个接口一种 scope**

---

---

# 4.3.2 Different scopes for different data results
## 同一个接口，根据 scope 返回不同数据

### 本段核心一句话
**同一个 API 地址**
**有什么 scope，就返回什么数据**
**没有的权限，对应数据直接隐藏**

---

## 1. 例子：/produce 接口
数据分三类：
- fruit
- veggies
- meats

## 2. 根据 scope 动态返回
```js
var produce = { fruit: [], veggies: [], meats: [] };

if (有 fruit scope) → 填 fruit
if (有 veggies scope) → 填 veggies
if (有 meats scope) → 填 meats
```

## 3. 效果
- 只给 `fruit` → 只返回水果
- 给 `fruit + veggies` → 返回水果+蔬菜
- 都不给 → 返回空对象

## 4. 重点（书本强调）
### **Scope 的含义完全由 API 开发者决定！**
OAuth 只负责**传递权限**，不负责定义权限含义。
你可以定义：
- `fruit`
- `veggies`
- `meats`
- `lowcarb`
- `admin`
- `user.read`
- `order.write`
**随便你定义！**

---

# 4.3.2 极简总结
## **数据级权限控制：同一接口，不同 scope → 不同返回内容**

---

# 整段 4.3 最终终极总结（必背）
## 4.3.1 → 接口级别权限
**不同接口需要不同 scope**

## 4.3.2 → 数据级别权限
**同一个接口，有什么 scope 就返回什么数据**

## 两者合起来 = OAuth 最强大的功能：
# **细粒度权限控制（Scope 权限体系）**

---

# 你现在已经完全学会：
✅ 资源服务器提取 token
✅ 验证 token
✅ **按 scope 控制接口访问**
✅ **按 scope 控制数据返回**

**这就是企业级 OAuth 权限系统的全部核心！**

---

# 4.3.3 Different users for different data results
## **只解读当前内容 · 100% 精准 · 不扩展**

---

# 本段核心一句话
**同一个 API 接口 → 根据 token 里的「用户是谁」返回对应用户的私有数据 → 客户端完全不用知道用户ID。**

---

# 1. 本节要实现的功能
- 有两个用户：**Alice** 和 **Bob**
- 各自有自己的收藏数据（电影、食物、音乐）
- **同一个接口 `/favorites`**
- **根据 token 属于谁，返回谁的数据**
- 客户端不需要传用户ID，不需要知道当前是谁

这就是 OAuth **最经典、最核心、最常用**的模式：
## **“以用户名义访问” → 自动返回该用户的数据**

---

# 2. 关键原理（书本重点）
授权服务器在生成 token 时，**把用户信息存在 token 里**：
```json
{
  "access_token": "xxx",
  "user": "alice",       // <-- 关键
  "client_id": "oauth-client-1",
  "scope": ["read"]
}
```

资源服务器拿到 token 就能知道：
**这是哪个用户的令牌。**

---

# 3. 代码实现（书本一模一样）
```js
app.get('/favorites', getAccessToken, requireAccessToken, function(req, res) {
  if (req.access_token.user == 'alice') {
    res.json({user: 'Alice', favorites: aliceFavorites});
  } else if (req.access_token.user == 'bob') {
    res.json({user: 'Bob', favorites: bobFavorites});
  } else {
    res.json({ user: 'Unknown', ... });
  }
});
```

逻辑：
- 看 `req.access_token.user` 是谁
- 返回对应用户的数据

---

# 4. 流程超级清晰
1. 用户（Alice / Bob）去授权服务器登录并授权
2. 授权服务器生成**带有用户ID的 token**
3. 客户端拿着 token 访问 `/favorites`
4. 资源服务器**自动识别用户**
5. 返回**该用户的私有数据**

---

# 4.3.4 Additional access controls
## 精准逐段解读（只讲当前内容，完全贴合书本）

---

## 本段核心一句话（全书最重要结论之一）
**OAuth 本身不做权限决策，OAuth 只负责传输权限信息（token+scope）；
真正决定能不能访问、返回什么数据的，永远是【资源服务器】，资源服务器拥有最终决定权。**

---

# 1. OAuth 的定位（书本重点总结）
OAuth 协议**完全不参与授权判断逻辑**
OAuth 只做一件事：
> 通过令牌，把授权信息（用户、客户端、scope权限）安全传递给资源服务器

至于：
能不能访问？返回什么？限制不限制？
**全部由资源服务器自己决定，OAuth 不管。**

---

# 2. 资源服务器可以额外叠加任意访问控制
书本举例，资源服务器可以在 token 合法的基础上，再增加额外规则：
1. 时间限制：**只能在工作时间访问**，token 有效也不行
2. 客户端黑白名单：禁止某些第三方客户端
3. 用户等级限制：普通用户/管理员权限
4. 调用频率限流：接口防刷
5. 调用外部统一权限策略中心（Policy Engine）
6. 自定义复杂业务权限规则

哪怕 token 完全合法、scope 完全匹配，
资源服务器依然可以**拒绝访问**。

---

# 3. 全书最核心金句（必须背诵）
> **In all cases, resource servers have the final say about what an access token means.**
> **任何情况下，资源服务器对 access_token 的含义、权限、是否放行，拥有最终决定权。**

翻译成人话：
- 授权服务器发了 token ≠ 资源服务器必须认
- 授权服务器定义 scope ≠ 资源服务器必须按这个执行
- 资源服务器可以自己解释 token、自己做二次鉴权、自己拒绝请求

---

# 4. 本章 4.3 全小节终极汇总（你全部学完了）
4.3 一共讲了**4种资源服务器鉴权模式**：
1. **4.3.1 接口级权限**：不同接口需要不同 scope
2. **4.3.2 数据字段级权限**：同一接口，不同 scope 返回不同数据
3. **4.3.3 用户级权限**：同一接口，token 属于哪个用户，返回哪个用户私有数据
4. **4.3.4 扩展自定义权限**：资源服务器可叠加任意业务规则，拥有最终决定权

---

# 极简总结（一句话记住本节）
## OAuth 只传权限，资源服务器**最终决定权限**，可以自定义任意额外访问控制规则。

---





