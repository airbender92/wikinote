# JS 前端预览 PDF 的几种方案

主流两大类：

1. **浏览器原生预览**：直接打开PDF，简单但不可定制；
2. **PDF.js（Mozilla开源）**，前端渲染PDF到canvas，高度自定义，项目最常用。

## 方案一：浏览器原生预览（最简单，零依赖）

### 方式1：iframe

```
<!-- pdfUrl 可以是接口返回文件地址、blob地址 -->
<iframe src="/static/demo.pdf" width="100%" height="700px"></iframe>
```

### 方式2：window.open

```
window.open('/static/demo.pdf')
```

### 方式3：blob二进制预览（后端返回文件流场景）

后端返回二进制流，生成blob本地预览，不需要下载：

```
async function previewPdf() {
  const res = await axios.get('/api/getPdf', { responseType: 'blob' })
  const blob = new Blob([res.data], { type: 'application/pdf' })
  const blobUrl = URL.createObjectURL(blob)
  // iframe
  document.querySelector('#pdfIframe').src = blobUrl
  // 用完释放内存
  // URL.revokeObjectURL(blobUrl)
}
```

✅优点：零包，浏览器自带打印、缩放、翻页。
❌缺点：样式完全浏览器控制，不能自定义UI；移动端兼容性参差不齐；部分浏览器会直接下载而不是预览。

> 注意：**跨域PDF，iframe会有限制**。

---

## 方案二：PDF.js（生产最常用，Mozilla官方库）

把PDF解析，渲染成`<canvas>`，完全自己控制UI：翻页、缩放、水印、隐藏打印、自定义工具栏。

> 仓库：mozilla/pdf.js

### 1.安装

```
npm install pdfjs-dist
```

### 基础最小示例（Vue3 / 原生JS通用）

```
<template>
  <div>
    <canvas ref="pdfCanvas"></canvas>
    <button @click="prevPage">上一页</button>
    <button @click="nextPage">下一页</button>
    <div>当前：{{ pageNum }} / {{ totalPage }}</div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as pdfjsLib from 'pdfjs-dist'
// 配置worker，pdf解析需要web worker，必须指定
pdfjsLib.GlobalWorkerOptions.workerSrc = new URL(
  'pdfjs-dist/build/pdf.worker.min.mjs',
  import.meta.url
).toString()

const pdfCanvas = ref(null)
let pdfDoc = ref(null)
const pageNum = ref(1)
const totalPage = ref(0)

// 加载pdf
async function loadPdf(pdfUrl) {
  const loadingTask = pdfjsLib.getDocument(pdfUrl)
  pdfDoc.value = await loadingTask.promise
  totalPage.value = pdfDoc.value.numPages
  await renderPage(pageNum.value)
}

// 渲染指定页码
async function renderPage(num) {
  const page = await pdfDoc.value.getPage(num)
  const canvas = pdfCanvas.value
  const ctx = canvas.getContext('2d')
  const scale = 1.5 // 缩放倍数，清晰度
  const viewport = page.getViewport({ scale })
  canvas.height = viewport.height
  canvas.width = viewport.width
  await page.render({ canvasContext: ctx, viewport }).promise
}

async function prevPage() {
  if(pageNum.value <=1) return
  pageNum.value--
  await renderPage(pageNum.value)
}
async function nextPage() {
  if(pageNum.value >= totalPage.value) return
  pageNum.value++
  await renderPage(pageNum.value)
}

onMounted(()=>{
  loadPdf('/static/demo.pdf')
})
</script>
```

### Blob流加载PDF（后端返回二进制）

```
// res.data是blob
const loadingTask = pdfjsLib.getDocument({ data: res.data })
pdfDoc.value = await loadingTask.promise
```

### 重要坑点

1. **workerSrc 必须配置**，否则主线程解析卡死；vite/webpack配置写法不一样。
2. PDF.js 默认**只渲染canvas，不能选文字**；如果需要文字复制，要开启文本层 `textLayer`。
3. 大PDF文件，内存占用高；
4. 本地file协议打开会报错，必须http服务。
5. 页面销毁：`pdfDoc.value?.destroy()` 释放pdf文档对象，防止内存泄漏。

```
onUnmounted(()=>{
  pdfDoc.value?.destroy()
})
```

## 方案三：成熟封装库（不想自己写翻页逻辑）

- `vue-pdf-embed`：Vue封装好pdf‑js，直接组件，不用自己操作canvas。

```
npm install vue-pdf-embed
```

```
<template>
  <VuePdfEmbed :source="pdfUrl"/>
</template>
<script setup>
import VuePdfEmbed from 'vue-pdf-embed'
</script>
```

## 方案对比

| 方案          | 优点                       | 缺点                         | 适用场景                         |
| ------------- | -------------------------- | ---------------------------- | -------------------------------- |
| iframe原生    | 零依赖，自带打印缩放       | UI不可控，移动端兼容差       | 内部后台快速预览，不要求自定义UI |
| PDF.js 原生   | 高度自定义，可控水印、权限 | 需要自己写翻页缩放逻辑       | 业务系统，需要定制预览           |
| vue‑pdf‑embed | 组件开箱即用               | 封装度高，深度定制需要看源码 | Vue项目快速开发                  |

## 常见业务问题

1. **后端返回文件流**：优先转 blob，传入pdfjs，不要下载到本地。
2. **禁止打印/下载**：只能用PDF.js；iframe原生无法屏蔽打印。
3. **预览支持复制文字**：PDF.js 需要引入 TextLayer 文本DOM层。
4. **预览PDF乱码**：确认后端返回二进制流，axios配置 `responseType:'blob'`。
5. 大PDF卡顿：可以做**虚拟分页，只渲染可视区域页面**。

如果你需要，我可以给一份带文本复制层、缩放、销毁内存处理完整PDF.js代码。
