# new Blob 创建JSON二进制对象
```javascript
const blob = new Blob([payload], { type: "application/json" });
```
## 代码解释
1. **`Blob`**：浏览器内置对象，代表二进制大对象，可以存放文本、二进制数据，常用于文件下载、上传、图片处理。
2. **第一个参数 `[payload]`**：**必须是数组**
    - `payload` 一般是 JSON 字符串；如果是 JS 对象，要先 `JSON.stringify(payload)`
    - 数组里可以放多个数据源，会拼接成一个 Blob
3. **第二个参数配置对象**
    - `type: "application/json"`：MIME类型，标记这个二进制内容是JSON格式，下载、传给后端时识别格式。

> ⚠️常见坑：
> ❌错误：直接传对象 `new Blob([{a:1}], {type:'application/json'})`
> 会得到 `[object Object]` 文本，不是合法JSON。
> ✅正确：对象要序列化
```javascript
const payload = { name: "test", id: 1 };
// JS对象转JSON字符串
const jsonStr = JSON.stringify(payload, null, 2);
const blob = new Blob([jsonStr], { type: "application/json" });
```

## 常见配套用法
### 1. Blob 下载成本地 json 文件
```javascript
const blob = new Blob([jsonStr], { type: "application/json" });
const url = URL.createObjectURL(blob);
const a = document.createElement('a');
a.href = url;
a.download = 'data.json'; // 下载文件名
a.click();
URL.revokeObjectURL(url); // 释放内存，一定要调用
```

### 2. FormData上传Blob给后端
```javascript
const formData = new FormData();
// 第二个参数是文件名，后端拿到就是文件
formData.append('file', blob, 'data.json');
fetch('/api/upload', {
  method: 'POST',
  body: formData
})
```

### 3. Blob转回文本
```javascript
const reader = new FileReader();
reader.onload = function(e){
  const text = e.target.result;
  const data = JSON.parse(text);
  console.log(data);
}
reader.readAsText(blob);
```

## 和 File 的区别
- `Blob`：纯二进制数据，没有文件名。
- `File`：继承自Blob，多了文件名、最后修改时间，`new File([jsonStr], "data.json", {type:"application/json"})`

如果你需要，我可以给你封装一个完整可直接复制的下载JSON工具函数。