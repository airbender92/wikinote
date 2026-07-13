# JS Proxy（代理）
一句话：**给对象加一层“拦截外壳”，可以监听读写、修改、删除等所有操作。**

---

# 1. 基础语法
```js
const target = {} // 目标对象

const proxy = new Proxy(target, {
  // 监听读取
  get(target, prop) {
    return target[prop]
  },
  // 监听赋值
  set(target, prop, value) {
    target[prop] = value
    return true
  }
})
```

以后操作 `proxy` 就会走拦截，操作 `target` 不会。

---

# 2. 最常用：get / set
```js
const obj = { name: "张三" }

const proxy = new Proxy(obj, {
  get(target, prop) {
    console.log("读取了：", prop)
    return target[prop]
  },
  set(target, prop, value) {
    console.log("设置了：", prop, "=", value)
    target[prop] = value
    return true
  }
})

proxy.name        // 触发 get
proxy.name = "李四" // 触发 set
```

---

# 3. 还能拦截哪些操作（常用）
- `get` —— 读取属性
- `set` —— 设置属性
- `deleteProperty` —— delete 时触发
- `has` —— in 操作符 `'a' in obj`
- `apply` —— 函数调用时
- `construct` —— new 时

---

# 4. 经典用途：数据响应式（Vue3 原理）
```js
function reactive(target) {
  return new Proxy(target, {
    get(target, prop) {
      // 收集依赖
      return target[prop]
    },
    set(target, prop, value) {
      target[prop] = value
      // 触发更新
      console.log("数据变了，更新视图")
      return true
    }
  })
}

const state = reactive({ name: "小明" })
state.name = "小红" // 数据变了，更新视图
```

---

# 5. 用途：校验、拦截、日志
```js
set(target, prop, value) {
  if (prop === 'age' && typeof value !== 'number') {
    throw new Error('年龄必须是数字')
  }
  target[prop] = value
  return true
}
```

---

# 6. 与 Object.defineProperty 区别
- **Proxy 监听整个对象**，不需要递归遍历
- **支持新增/删除属性**
- **支持数组**（push、pop、length 都能监听）
- 功能更强、性能更好 → Vue3 用它

---

# 一句话总结
**Proxy = 对象的拦截器
能监听读写删，是 Vue3 响应式核心，
功能比 defineProperty 强得多，用法也更简单。**

需要我给你写一个**可直接运行的简易版 Vue3 reactive 响应式完整 demo**吗？