可以的，完全没问题。
你可以直接在页面里**用 CDN 引入 less.js**，在 `<style rel="stylesheet/less">` 里写 Less 语法，自动编译。

我直接给你改成**Less + CDN**版本，并且把你那个 `÷2 ÷100` 做成 Less 函数，**设计稿标多少 px 就写多少**，不用自己算。

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Less CDN 750px 设计稿 Demo</title>

  <!-- 引入 Less CDN -->
  <script src="https://cdn.jsdelivr.net/npm/less@4"></script>

  <!-- 这里写 Less 样式 -->
  <style rel="stylesheet/less">
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    // 750px 设计稿专用函数：直接写设计稿上的px
    .px2rem(@px) {
      // 设计稿 ÷2 → 逻辑px ÷100 → rem
      value: @px / 2 / 100rem;
    }

    #box {
      .px2rem(width: 200);   // 设计稿 200px
      .px2rem(height: 200);
      background: #42b983;
      .px2rem(margin: 50);
      margin-left: auto;
      margin-right: auto;
      .px2rem(border-radius: 20);
    }
  </style>
</head>
<body>
  <div id="box"></div>

  <script>
    // 依旧用这套 rem 适配逻辑
    function initRem() {
      const clientWidth = document.documentElement.clientWidth
      // 375 屏幕下 html.font-size = 100px（逻辑像素）
      const fontSize = (clientWidth / 375) * 100
      document.documentElement.style.fontSize = fontSize + 'px'
    }

    initRem()
    window.addEventListener('resize', initRem)
  </script>
</body>
</html>
```

---

## 关键点说明（对应你之前的疑问）

### 1. 为什么是 `@px / 2 / 100rem`
- **÷2**：因为设计稿是 **750px（2倍图）**，要转成 **375 逻辑像素**
- **÷100**：因为我们在 375 屏下设置了
  ```js
  html.style.fontSize = 100px
  ```
  也就是：
  > **1rem = 100px（逻辑像素）**

所以：
> 设计稿 px → ÷2 → 逻辑 px → ÷100 → rem

### 2. 这里的 `100` 对应什么？
**对应：375px 逻辑宽度下的根字体大小 100px，不是设计稿 750px 里的 100px。**

- 设计稿 750px 里的 100px
- = 逻辑像素 50px
- = 0.5rem

---

## 你以后写样式就这么爽
```less
.px2rem(width: 375);  // 半屏宽
.px2rem(height: 100);
.px2rem(font-size: 28); // 设计稿字体28px
```

直接抄设计稿标注，不用心算。