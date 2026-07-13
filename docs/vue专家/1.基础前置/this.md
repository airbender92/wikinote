# this 一句话核心
**this 不看你写在哪，只看你**怎么调用、谁调用**。**
谁调用它，this 就指向谁。

---

# 1. 最常用的 4 种情况（现实开发 99% 场景）
## ① 普通函数直接调用
```js
function fn() {
  console.log(this)
}

fn()
```
- 非严格模式：`this = window`（浏览器）
- 严格模式：`this = undefined`

**谁都没调用，就是 window / undefined。**

---

## ② 对象方法调用
```js
const obj = {
  name: 'aaa',
  say() {
    console.log(this.name)
  }
}

obj.say()
```
- `obj.xxx()` → **this = obj**
- 谁点的它，this 就是谁

---

## ③ 构造函数 new
```js
function Person(name) {
  this.name = name
}

const p = new Person('tom')
```
- `new` 时：**this = 新创建的对象**

---

## ④ call / apply / bind 手动指定
```js
function fn() {
  console.log(this)
}

fn.call({ a: 1 }) // this = {a:1}
fn.apply({ b: 2 })// this = {b:2}

const bound = fn.bind({ c: 3 })
bound() // this = {c:3}
```
- 手动绑定优先级最高，直接指定 this

---

# 2. 最容易踩坑的 2 个坑
## 坑1：方法被拿出来单独执行
```js
const obj = {
  name: 'aaa',
  say() { console.log(this) }
}

const fn = obj.say
fn() // this 不是 obj，是 window/undefined
```
原因：
**调用方式变了，不再是 obj.say()，而是普通函数调用。**

---

## 坑2：回调函数里的 this
```js
const obj = {
  name: 'aaa',
  fetch() {
    setTimeout(function() {
      console.log(this) // window
    }, 0)
  }
}
```
回调函数是**普通函数调用**，this 丢失。

解决：
1. 箭头函数
2. var _this = this
3. bind

---

# 3. 箭头函数的 this（最重要）
**箭头函数没有自己的 this！**
它的 this 是**继承外层作用域的 this**。

```js
const obj = {
  fn() {
    const f = () => {
      console.log(this)
    }
    f()
  }
}

obj.fn() // this = obj
```

- 箭头函数的 this **在定义时就确定了**
- 无法被 call / apply / bind 改变
- 非常适合回调、定时器

---

# 4. 一句话记忆口诀
- 普通调用 → window / undefined
- 对象点调用 → 对象
- new → 新对象
- call/apply/bind → 你指定的
- 箭头函数 → 看外层 this

---

# 5. 和你前面学的知识串起来
- **作用域**：管变量在哪能访问
- **闭包**：让变量活着
- **this**：管当前函数执行时的“上下文”

这四个东西一打通，JS 核心就彻底通透了。
需要我给你出几道 this 判断题，测一下是否真懂吗？