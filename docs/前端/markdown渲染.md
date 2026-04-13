# `markdown-it` 完全指南
`markdown-it` 是目前**前端最流行、最快、最稳定的 Markdown 解析器**，用来把 **Markdown 语法 → 渲染成 HTML**。

你在很多项目里看到的：
- 文章详情
- 评论区
- 笔记编辑器
- 帮助文档

90% 都是用 `markdown-it` 做的。

---

# 1. 核心作用
一句话：
**把 Markdown 文本 → 安全、快速、可扩展地转换成 HTML**

特点：
- 速度极快
- 支持 GFM（GitHub 风格 Markdown）
- 支持插件扩展（表格、目录、代码高亮、emoji）
- 安全性高（可自动过滤 XSS）

---

# 2. 安装
```bash
npm install markdown-it
# or
yarn add markdown-it
# or
pnpm add markdown-it
```

---

# 3. 最简单使用示例
```javascript
import MarkdownIt from 'markdown-it'

// 初始化
const md = new MarkdownIt({
  html: true,        // 允许解析 HTML
  linkify: true,     // 自动识别链接
  typographer: true  // 优化标点符号
})

// 要渲染的 markdown
const markdownText = `
# 我是标题

这是**加粗**，这是*斜体*

- 列表1
- 列表2
`

// 转换为 HTML
const html = md.render(markdownText)

console.log(html)
```

输出：
```html
<h1>我是标题</h1>
<p>这是<strong>加粗</strong>，这是<em>斜体</em></p>
<ul>
<li>列表1</li>
<li>列表2</li>
</ul>
```

---

# 4. 常用插件（超级实用）
`markdown-it` 生态非常强，你可以直接加插件实现高级功能：

### 1）代码高亮（最常用）
```bash
npm install markdown-it-highlightjs
```
```javascript
import hljs from 'markdown-it-highlightjs'
md.use(hljs)
```

### 2）表格支持
```bash
npm install markdown-it-multimd-table
```

### 3）任务列表（- [x]）
```bash
npm install markdown-it-task-lists
```

### 4）目录（TOC）
```bash
npm install markdown-it-toc-done-right
```

### 5）Emoji
```bash
npm install markdown-it-emoji
```

---

# 5. 常用配置项
```js
{
  html: false,          // 是否允许 HTML 标签
  xhtmlOut: false,      // 是否闭合单标签
  breaks: false,        // 换行自动转 <br>
  linkify: true,        // 自动识别链接
  typographer: false,   // 优化标点
  quotes: '“”‘’',       // 引号替换
  highlight: function (str, lang) { /* 自定义代码高亮 */ }
}
```

---

# 6. 安全提示（防 XSS）
如果你的 Markdown 来自**用户输入**，一定要过滤危险 HTML：

安装：
```bash
npm install xss
```

使用：
```js
import xss from 'xss'
const safeHtml = xss(md.render(markdownText))
```

---

# 7. 适合场景
- 文章展示
- 评论区渲染
- 笔记应用
- 文档站点
- 后台富文本展示（比富文本编辑器轻太多）

---

# 超级总结
`import MarkdownIt from 'markdown-it'`
= **前端最强 Markdown → HTML 解析库**

---

如果你需要，我可以直接给你写一个
**✅ React 中可直接使用的 Markdown 渲染组件（带代码高亮）**
要吗？