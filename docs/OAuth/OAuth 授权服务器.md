#  搭建一个简单的 OAuth 授权服务器｜**精准解读**

---

# 本段核心一句话
**授权服务器是 OAuth 最核心、最复杂、最安全的组件，负责：管客户端、认证用户、发令牌、做授权。**

---

# 1. 本章要做什么？
前面你已经学会：
- **客户端**（第3章）
- **资源服务器**（第4章）

现在要实现 **第三个、也是最重要的角色**：
# ✅ **授权服务器（Authorization Server）**

它负责：
1. 管理第三方客户端（client_id / client_secret）
2. 对用户进行认证（登录）
3. 向用户展示授权页面（允许/拒绝）
4. 生成授权码 code
5. 签发 access_token & refresh_token
6. 验证 token、撤销 token

---

# 2. 为什么授权服务器最复杂？（书本重点）
原文明确说：
> **授权服务器是整个 OAuth 生态里最复杂的组件，是整个系统的安全中心。**

原因：
- 只有它能**认证用户**
- 只有它能**注册客户端**
- 只有它能**签发令牌**
- OAuth 标准把**所有复杂性都压在授权服务器上**
- 目的是让**客户端更简单**（因为世界上客户端最多）

---

# 3. 本章要实现的功能
本章只实现 **最核心、最标准** 的流程：
## **授权码模式（authorization code grant）**

包括：
- 注册客户端
- 授权页面（用户允许/拒绝）
- 生成 code
- 兑换 code → access_token
- 刷新 token

---

# 4. 本章使用的技术
- Node.js + Express
- 本地文件数据库（nosql）
- 三个组件分开端口运行

---

# 5.1 Managing OAuth client registrations
## **当前内容精准解读（只讲本段）**

---

# 本段核心一句话
**授权服务器必须“认识”第三方客户端，所以要提前注册：client_id、client_secret、redirect_uris。**

---

# 1. 本节要做什么？
给授权服务器**添加客户端注册信息**，让它知道：
“哪些第三方应用可以来申请令牌”。

这是 OAuth **必须的第一步**。

---

# 2. 注册信息包括 3 项（必须）
```js
{
  "client_id": "oauth-client-1",           // 客户端ID
  "client_secret": "oauth-client-secret-1", // 客户端密钥
  "redirect_uris": ["http://localhost:9000/callback"] // 回调地址
}
```

这三个信息必须**客户端和授权服务器完全一致**。

---

# 3. 为什么要注册？
OAuth 安全原则：
**只有预先注册过的客户端，才能申请令牌。**
防止恶意应用冒充客户端骗取权限。

---

# 4. 授权服务器如何查找客户端？
通过工具函数 `getClient`：
```js
var getClient = function(clientId) {
  return __.find(clients, function(client) {
    return client.client_id == clientId;
  });
};
```

作用：
**根据 client_id 找到注册的客户端信息**

---

# 5. 本节最终结果
授权服务器现在**认识**这个客户端了：
- ID：oauth-client-1
- 密钥：oauth-client-secret-1
- 允许回调：http://localhost:9000/callback

---

# 5.2 Authorizing a client + 5.2.1 The authorization endpoint
## **只解读你当前这段内容 · 100% 精准 · 不扩展**

---

# 本段核心一句话
**实现授权服务器的 /authorize 端点：验证客户端 → 校验 redirect_uri → 展示授权页面给用户。**

---

# 1. 授权服务器必须有 2 个端点（OAuth 强制）
1. **授权端点 /authorize**
   前端信道，用户浏览器访问，用于**用户授权**
2. **令牌端点 /token**
   后端信道，客户端后台访问，用于**发 token**

本章先实现 **第一个：授权端点**。

---

# 2. /authorize 端点做什么？
用户被第三方客户端重定向到这里，
授权服务器要：
1. **识别 client_id 是否合法**
2. **校验 redirect_uri 是否注册过**
3. **展示授权页面（允许/拒绝）**

---

# 3. 代码逻辑逐行解释（书本一模一样）

## ① 根据 client_id 查找客户端
```js
var client = getClient(req.query.client_id);
```

## ② 找不到 → 报错
```js
if (!client) {
  res.render('error', { error: 'Unknown client' });
  return;
}
```

## ③ 校验 redirect_uri 是否合法（超级重要）
```js
if (!__.contains(client.redirect_uris, req.query.redirect_uri)) {
  res.render('error', { error: 'Invalid redirect URI' });
  return;
}
```

### 为什么必须校验？
防止攻击者：
- 伪造客户端
- 把用户跳到钓鱼页面
- 劫持授权码

**这是 OAuth 核心安全校验。**

---

# 4. 生成随机 reqid 存储请求（防 CSRF）
```js
var reqid = randomstring.generate(8);
requests[reqid] = req.query;
```

作用：
- 暂时保存这次授权请求
- 等用户点“允许”后，能找回原始请求
- **防 CSRF 攻击**

---

# 5. 渲染授权页面给用户
```js
res.render('approve', {
  client: client,
  reqid: reqid
});
```

页面显示：
- 哪个第三方应用要授权
- 权限范围
- 允许 / 拒绝 按钮

---

# 6. 本段最重要的安全知识点（书本强调）
### **如果 client_id 无效 或 redirect_uri 不匹配 → 直接报错，不跳转！**
因为此时可能是攻击，
**不能把用户重定向到不可信的 URL。**

---

# 本段极简总结（必记）
## /authorize 端点 = 授权服务器的大门
## 工作流程：
1. 检查 client_id 是否存在
2. 检查 redirect_uri 是否合法
3. 生成随机 reqid 保存请求
4. 显示授权页面给用户

---

# 5.2.2 Authorizing the client｜**当前内容逐字精准解读**
我**只讲你现在这段文字**，100% 贴合书本，不扩展、不提前，让你完全跟上。

---

# 本段核心一句话（最重要）
**用户在授权页面点击「允许/拒绝」→ 授权服务器生成授权码 code → 重定向回客户端，并带回 code + state。**

---

# 1. 当前所处阶段
用户已经被带到授权页面，看到：
- 哪个客户端要授权
- **Allow（允许）** / **Deny（拒绝）** 按钮

本节处理：**用户点击按钮后的逻辑**

---

# 2. 授权页面提交到：POST /approve
```js
app.post('/approve', function(req, res) {
});
```

---

# 3. 第一步：通过 reqid 找回原始请求（防 CSRF）
授权页面里有个**隐藏字段**：
```html
<input type="hidden" name="reqid" value="tKVUYQSM">
```

服务端：
```js
var reqid = req.body.reqid;
var query = requests[reqid];  // 找到之前的授权请求
delete requests[reqid];        // 一次性使用，用完删

if (!query) {
  报错：无效请求
}
```

作用：
**防止 CSRF 攻击，确保这次授权是从我们的页面发起的。**

---

# 4. 判断用户点了「允许」还是「拒绝」
```js
if (req.body.approve) {
  // 用户允许
} else {
  // 用户拒绝
}
```

---

# 5. 如果用户拒绝 → 重定向回客户端，带错误
```js
var urlParsed = buildUrl(query.redirect_uri, {
  error: 'access_denied'
});
res.redirect(urlParsed);
```

返回格式：
```
http://localhost:9000/callback?error=access_denied
```

---

# 6. 如果用户允许 → 检查 response_type=code
我们只实现**授权码模式**，所以必须是：
```js
if (query.response_type == 'code') {
  // 正常流程
} else {
  // 不支持的类型 → 报错
}
```

---

# 7. 生成授权码 code（最关键一步）
```js
var code = randomstring.generate(8);  // 生成随机 code
codes[code] = { request: query };      // 存到服务器，等下兑换 token
```

---

# 8. 把 code + state 返回给客户端
```js
var urlParsed = buildUrl(query.redirect_uri, {
  code: code,    // 授权码
  state: query.state  // 原样返回 state
});
res.redirect(urlParsed);
```

最终跳转：
```
http://localhost:9000/callback?code=xxx&state=xxx
```

---

# 9. 书本强调的重要规则
### ✅ state 必须**原样返回**
客户端传什么，授权服务器返回什么。

### ✅ code 是**一次性、短期、临时**的凭证
只能用一次
只能用来换 token
不能直接用来访问资源

---

# 本段完整流程（极简记忆版）
1. 用户点允许
2. 校验 reqid（防 CSRF）
3. 生成临时授权码 code
4. 把 code + state 带回客户端
5. 授权流程到此结束，等待下一步**兑换 token**

---

# 本段最终极简总结
## 5.2.2 做的只有一件事：
# **处理用户授权 → 生成 code → 重定向回客户端**

---

# 5.3 Issuing a token **完整逐段精准解读**
我**严格只解读你当前这段内容**，100% 贴合书本，不扩展、不提前，让你完全吃透。

---

# 本段核心一句话（最关键）
**客户端用授权码 code →  POST 到 /token 端点 → 授权服务器验证客户端 + 验证 code → 签发 access_token。**

这是**授权码模式最后一步**，也是整个 OAuth 最核心流程。

---

# 本节分为两大部分：
1. **5.3.1 认证客户端（验证 client_id + client_secret）**
2. **5.3.2 处理授权码，签发 access_token**

---

# 5.3.1 Authenticating the client
## 目标：确保来换 token 的是**合法客户端**

### 1. 客户端可以用两种方式传身份（OAuth 规范）
1. **HTTP Basic 请求头（推荐）**
2. **form 表单参数**

授权服务器**两种都支持**。

---

### 2. 先从 Authorization 头取凭证
```js
var auth = req.headers['authorization'];
if (auth) {
  var clientCredentials = decodeClientCredentials(auth);
  var clientId = clientCredentials.id;
  var clientSecret = clientCredentials.secret;
}
```

---

### 3. 再从 form 取（不能两种同时传）
```js
if (req.body.client_id) {
  if (clientId) {
    res.status(401).json({error: 'invalid_client'});
    return;
  }
  clientId = req.body.client_id;
  clientSecret = req.body.client_secret;
}
```

---

### 4. 查找客户端、校验密钥
```js
var client = getClient(clientId);
if (!client) {
  res.status(401).json({error: 'invalid_client'});
  return;
}

if (client.client_secret != clientSecret) {
  res.status(401).json({error: 'invalid_client'});
  return;
}
```

✅ **客户端认证完成**

---

# 5.3.2 Processing the authorization grant request
## 目标：验证 code → 签发 token

### 1. 必须是 grant_type = authorization_code
```js
if (req.body.grant_type == 'authorization_code') {
  // 正常流程
} else {
  res.status(400).json({error: 'unsupported_grant_type'});
  return;
}
```

---

### 2. 取出 code，检查是否存在
```js
var code = codes[req.body.code];

if (!code) {
  res.status(400).json({error: 'invalid_grant'});
  return;
}
```

---

### 3. **用完立即删除 code（超级重要！）**
```js
delete codes[req.body.code];
```

### 为什么？
**code 只能用一次！**
防止重放攻击。

---

### 4. 检查 code 是否属于当前客户端
```js
if (code.request.client_id == clientId) {
  // 合法
} else {
  res.status(400).json({error: 'invalid_grant'});
  return;
}
```

---

### 5. 生成 access_token 并保存
```js
var access_token = randomstring.generate();
nosql.insert({ access_token: access_token, client_id: clientId });
```

---

### 6. 返回 token 给客户端
```js
var token_response = {
  access_token: access_token,
  token_type: 'Bearer'
};

res.status(200).json(token_response);
```

返回格式：
```json
{
  "access_token": "xxx",
  "token_type": "Bearer"
}
```

---

# 书本重要知识点（必须记住）
## 1. OAuth **不规定 token 里面是什么**
可以是：
- 随机字符串（本章做法）
- JWT
- SAML
- 加密串

**客户端不用关心，只要会用就行。**

## 2. token 是给**资源服务器**用的
授权服务器只负责签发，不负责验证。

## 3. code 是一次性的
用一次立即销毁。

---

# 本段最终极简总结
## 5.3 做的只有一件事：
# **验证客户端 → 验证 code → 销毁 code → 签发 access_token**

---

# 🎉 你现在已经完整实现了 OAuth2 授权码模式全流程！
你亲手实现了：

✅ 客户端（第3章）
✅ 资源服务器（第4章）
✅ **授权服务器（第5章）**

✅ 授权码模式完整流程
✅ state 防 CSRF
✅ code 一次性使用
✅ 客户端认证
✅ token 签发与验证

---

# 5.4 Adding refresh token support｜**最终完整版精准解读**
我**只讲你当前这段内容**，100% 贴合书本，不扩展、不提前，让你彻底看懂**刷新令牌机制**。

---

# 本段核心一句话（最重要）
**在签发 access_token 时，同时签发 refresh_token；
当 access_token 过期，客户端用 refresh_token 直接换新的，无需用户参与。**

这是 OAuth **生产级必备功能**。

---

# 本节分为 2 个核心步骤：
1. **签发 refresh_token**（和 access_token 一起发）
2. **处理 refresh_token 请求**（grant_type=refresh_token）

---

# 1. 签发 refresh_token（在 /token 接口里）
当客户端用 code 换 token 时，**同时生成并返回 refresh_token**。

## ① 生成随机 refresh_token
```js
var refresh_token = randomstring.generate();
```

## ② 保存到数据库
```js
nosql.insert({
  refresh_token: refresh_token,
  client_id: clientId
});
```

## ③ 和 access_token 一起返回
```js
var token_response = {
  access_token: access_token,
  token_type: "Bearer",
  refresh_token: refresh_token
};
```

返回结果：
```json
{
  "access_token": "xxx",
  "token_type": "Bearer",
  "refresh_token": "yyy"
}
```

---

# 2. 处理刷新 token 请求（grant_type=refresh_token）
客户端访问：`POST /token`
参数：
```
grant_type=refresh_token
refresh_token=yyy
```

## ① 判断类型
```js
} else if (req.body.grant_type == 'refresh_token') {
```

## ② 查找 refresh_token 是否有效
```js
nosql.one(function(token) {
  return token.refresh_token == req.body.refresh_token;
}, function(err, token) {
  if (!token) {
    res.status(400).json({error: 'invalid_grant'});
    return;
  }
});
```

## ③ 检查是否属于当前客户端（超级重要）
```js
if (token.client_id != clientId) {
  res.status(400).json({error: 'invalid_grant'});
  return;
}
```

防止：
- 偷 refresh_token
- 跨客户端冒用

---

# 3. 生成新 access_token 返回
```js
var access_token = randomstring.generate();

nosql.insert({
  access_token: access_token,
  client_id: clientId
});

var token_response = {
  access_token: access_token,
  token_type: "Bearer",
  refresh_token: token.refresh_token  // 继续使用原 refresh_token
};

res.status(200).json(token_response);
```

---

# 书本强调的 4 个关键知识点（必须记住）
## ① refresh_token **不用于访问资源**
只用于**换新的 access_token**。

## ② refresh_token **长期有效**
access_token 短期；
refresh_token 长期。

## ③ refresh_token 也**可被撤销**
用户可取消授权
服务器可强制作废

## ④ 刷新时 **可以返回新 refresh_token**（可选）
本书例子继续用旧的，真实系统常用**滚动刷新**策略。

---

# 本段极简总结（必背）
## 5.4 做的只有两件事：
1. **签发 refresh_token** 和 access_token 一起返回
2. **处理刷新请求** → 检查 refresh_token → 签发新 access_token

## 最终效果：
# **access_token 过期 → 无感刷新 → 用户完全无感知**

---

# 🎉 你现在已经 **100% 掌握 OAuth2 全套核心功能**
✅ 授权码模式完整流程
✅ state 防 CSRF
✅ 客户端认证
✅ access_token 签发与验证
✅ **refresh_token 签发与刷新**
✅ 资源服务器权限控制（scope + 用户隔离）

**你已经学完本书最核心、最实用、企业级必用的全部 OAuth2 知识！**

---

# 5.5 Adding scope support **超清晰逐段解读**
我用**最直白、最实战、最贴合书本**的方式给你讲，保证你一次性彻底懂👇

---

# 本段核心一句话（最重要）
**给授权服务器加入 scope 权限控制：
客户端申请 → 服务器检查权限范围 → 用户勾选授权 → token 绑定 scope → 资源服务器按 scope 控制权限。**

这就是 OAuth **细粒度权限**的完整实现。

---

# 一、本节要做什么？
给授权服务器增加 5 个功能：
1. **给客户端注册允许的 scope**（如 `foo bar`）
2. **客户端申请 scope**
3. **服务器检查客户端不能超权限申请**
4. **用户在授权页面勾选允许哪些 scope**
5. **把 scope 存进 code → 存进 token → 返回给客户端**

---

# 二、逐步骤拆解（书本一模一样）

## 1. 给客户端注册允许的 scope
在授权服务器的客户端配置里加：
```js
var clients = [
{
  "client_id": "oauth-client-1",
  "client_secret": "oauth-client-secret-1",
  "redirect_uris": ["http://localhost:9000/callback"],
  "scope": "foo bar"   <-- 此客户端允许的权限
}
];
```

---

## 2. 客户端申请 scope
客户端跳转到授权时带参数：
```
scope=foo bar
```

授权服务器解析：
```js
var rscope = req.query.scope ? req.query.scope.split(' ') : undefined;
var cscope = client.scope.split(' ');
```

---

## 3. 检查客户端不能申请超出注册范围的 scope
```js
if (__.difference(rscope, cscope).length > 0) {
  // 客户端申请了未允许的 scope
  redirect(error: invalid_scope);
}
```

**安全关键点：**
客户端**不能申请它没资格获得的权限**。

---

## 4. 授权页面显示 scope 勾选框
用户可以**勾选允许哪些权限**：
```html
<% _.each(scope, function(s) { %>
  <li>
    <input type="checkbox" name="scope_<%= s %>" checked>
    <label><%= s %></label>
  </li>
<% }); %>
```

用户可以：
- 全选
- 取消部分
- 一个不给

---

## 5. 服务端解析用户勾选的 scope
```js
var getScopesFromForm = function(body) {
  return _.keys(body)
    .filter(s => s.startsWith("scope_"))
    .map(s => s.slice("scope_".length));
};
```

得到用户真正允许的 scope 列表。

---

## 6. 再次检查：用户勾选的不能超过客户端允许范围
```js
if (__.difference(rscope, cscope).length > 0) {
  redirect(error: invalid_scope);
}
```

**双重验证，保证安全。**

---

## 7. 把 scope 存进授权码 code
```js
codes[code] = {
  request: query,
  scope: rscope   <-- 把用户允许的 scope 存进去
};
```

---

## 8. 兑换 token 时，把 scope 存进 token
```js
nosql.insert({
  access_token: access_token,
  client_id: clientId,
  scope: code.scope   <-- token 绑定 scope
});
```

---

## 9. 把 scope 返回给客户端
```js
var token_response = {
  access_token: access_token,
  token_type: "Bearer",
  refresh_token: refresh_token,
  scope: code.scope.join(' ')  <-- 空格分隔字符串
};
```

返回示例：
```json
{
  "access_token": "xxx",
  "scope": "foo bar"
}
```

---

# 三、scope 完整流转路径（必须记住）
1. 客户端注册时：设定**允许的 scope**
2. 客户端申请：带上想要的 scope
3. 授权服务器：**检查不能超范围**
4. 用户授权：**勾选允许的 scope**
5. 授权码 code：**存储最终 scope**
6. 签发 token：**token 绑定 scope**
7. 资源服务器：**根据 scope 控制权限**（第4章）

---

# 四、书本强调的 3 个重要规则
## 1. scope 是**空格分隔的字符串**
不是数组，因为要在 URL/表单中传递。

## 2. 客户端**只能申请比注册范围更小的 scope**
不能超权限。

## 3. 用户可以**减少 scope**，不能增加
最终 token 的权限 ≤ 客户端注册权限
最终 token 的权限 ≤ 用户勾选权限

---

# 五、极简总结（必背）
## 5.5 做的只有一件事：
# **让授权服务器支持 scope 权限生命周期管理：
申请 → 检查 → 用户授权 → 存入 code → 存入 token → 返回客户端**

---

# 🎉 你现在已经 **100% 掌握 OAuth2 最完整权限体系**
✅ 授权码模式
✅ 客户端认证
✅ token / refresh_token
✅ **scope 细粒度权限（完整流程）**
✅ 资源服务器权限控制
✅ 安全防范（CSRF、code一次性、scope检查）

**你已经学完整本书 OAuth2 核心全部内容！**

---

如果你愿意，我可以把
**第3～5章浓缩成 1 张「OAuth2 终极权限流程图」**
让你永久记住整个体系！
