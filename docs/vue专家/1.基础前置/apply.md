在 JavaScript 里，`apply` 是函数的一个方法，用来**指定函数执行时的 `this`**，并**以数组形式传参**。

---

### 基本语法
```js
函数.apply(this指向, [参数1, 参数2, ...])
```

- 第一个参数：函数内部 `this` 要指向谁
- 第二个参数：**数组 / 类数组**，会被拆成一个个参数传给原函数

---

### 简单示例
```js
function say(a, b) {
  console.log(this.name, a + b);
}

const obj = { name: '张三' };

// this 指向 obj，参数是 [1,2]
say.apply(obj, [1, 2]); 
// 输出：张三 3
```

---

### 常见用途
1. **求数组最大/最小值**
   ```js
   const arr = [3,1,4,2];
   const max = Math.max.apply(Math, arr); // 4
   ```

2. **把类数组转数组 / 借用数组方法**
   ```js
   const likeArr = { 0: 'a', 1: 'b', length: 2 };
   const arr = Array.prototype.slice.apply(likeArr); // ['a','b']
   ```

3. **继承 / 复用方法**
   ```js
   function Person(name) {
     this.name = name;
   }
   function Student(name) {
     Person.apply(this, [name]);
   }
   ```

---

### apply vs call vs bind
- `call`：逐个传参
  ```js
  say.call(obj, 1, 2);
  ```
- `apply`：数组传参
  ```js
  say.apply(obj, [1, 2]);
  ```
- `bind`：返回新函数，不立即执行
  ```js
  const newFn = say.bind(obj, 1, 2);
  newFn();
  ```

需要我给你写几个实际业务场景的例子吗？