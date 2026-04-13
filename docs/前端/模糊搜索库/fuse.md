# `import Fuse from 'fuse.js'` 到底是什么？
这是引入 **Fuse.js** —— 一个**轻量级、零依赖、前端模糊搜索库**。

不用后端、不用数据库，**纯前端**就能实现：
- 模糊搜索
- 关键词容错搜索
- 列表/表格快速搜索
- 支持拼音、错别字匹配

---

## 1. 核心特点
- **纯前端**，不发请求，本地搜索
- **模糊匹配**：输错字、少打字也能搜到
- **轻量**：极小体积
- **支持配置权重、深度搜索**
- 支持中文、英文、拼音

---

## 2. 安装
```bash
npm install fuse.js
# or
yarn add fuse.js
# or
pnpm add fuse.js
```

---

## 3. 最简单使用示例
```javascript
import Fuse from 'fuse.js'

// 你的数据
const list = [
  { title: '前端开发', author: '张三' },
  { title: '后端开发', author: '李四' },
  { title: 'Webpack 教程', author: '王五' }
]

// 配置
const fuse = new Fuse(list, {
  keys: ['title', 'author'], // 要搜索哪些字段
  threshold: 0.3 // 模糊度：0 精确，1 宽松
})

// 搜索
const result = fuse.search('webpack')
```

**输错字也能搜到：**
```
fuse.search('webpak') → 依然能搜到 Webpack 教程
```

---

## 4. 常用配置（必看）
```js
{
  keys: ['title', 'author'],   // 搜索字段
  threshold: 0.3,              // 容错度（越小越严格）
  ignoreCase: true,            // 忽略大小写
  includeMatches: true,        // 返回匹配详情
  includeScore: true,          // 返回匹配分数
  shouldSort: true             // 按相关性排序
}
```

---

## 5. 适合什么场景？
- 后台管理系统**表格搜索**
- 文档/文章**本地搜索**
- 下拉框**模糊匹配**
- 不想要请求接口的**即时搜索**
- 小数据量（几千条以内体验极好）

---

## 6. 不适合什么场景？
- 大数据量（>1万条）
- 需要高精度、全文检索
- 需要复杂分词、权重检索（用 ElasticSearch）

---

### 超级总结
`import Fuse from 'fuse.js'`
= **前端轻量级模糊搜索神器**

如果你愿意，我可以给你写一个 **React/Vue 中即插即用的模糊搜索组件**！