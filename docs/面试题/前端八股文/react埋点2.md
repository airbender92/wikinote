# async函数中执行 track() 的影响

```js
const handleSubmit = async () => {
  await submitBizApi();
  track({ event: "submit_success" }); // ✅这样写，完全没问题
};
```

✅ **上面这种写法没有任何问题，无负面影响。**

## 关键原理

`track()` 内部**没有返回 Promise**，它只是同步函数：

1. 做节流判断
2. 组装埋点对象
3. 调用 `trackRequest` → 内部执行 `fetch`（fetch本身返回Promise，但是代码**没有return这个Promise，直接丢弃**）
4. 函数执行完毕，立刻返回 `undefined`

### 两种写法对比

```js
// ✅正确：async函数内直接调用，不await
const handleSubmit = async () => {
  await saveApi();
  track({ event: "xxx" });
};
```

```js
// ❌错误：千万不要 await track()
const handleSubmit = async () => {
  await saveApi();
  await track({ event: "xxx" }); // track返回undefined，await undefined 不会报错，但没有意义，误导阅读
};
```

> `await undefined` JS语法不会报错，但是**不会等待埋点网络请求完成**，因为track根本没有把fetch的Promise返回出来。

## 潜在需要注意的2个边界场景

### 场景1：await之后，函数马上结束，紧接着页面跳转/关闭

```js
const handleSubmit = async () => {
  await saveApi();
  track({ event: "submit_success" });
  router.push("/other-page"); // 立刻跳转页面
};
```

- 因为我们开启了 `keepalive:true` ✅，浏览器会尽力把这个fetch请求发送完成；
- keepalive就是专门用来解决这种「页面马上跳转/卸载，希望请求尽量发出去」的场景。

> 没有keepalive的情况下，页面跳转浏览器会直接中断还在进行的fetch。我们代码已经开启，不用担心。

### 场景2：async函数里面，track写在await前面

```js
const handleSubmit = async () => {
  track({ event: "click_submit" }); // 先埋点
  await saveApi(); // 再等待业务接口
};
```

✅ 也完全正常。埋点会立刻发起，和业务接口请求**并行执行，互不阻塞**。

## 和节流一起的行为（当前hook的节流逻辑）

```js
const handleClick = async () => {
  // 用户疯狂点击按钮，反复进入async函数
  track({ event: "click_btn" });
  await someApi();
};
```

即使反复进入async函数，hook内部通过 `lastEventTimeRef.current` 做event节流，500ms内同一个event只会上报一次，不会产生大量埋点请求。

## 总结

1. `track()` 放在 `async` 函数内部**完全可以正常使用，不会阻塞业务**；
2. **绝对不要写 `await track()`**，函数没有返回Promise，await没有实际作用；
3. 如果埋点之后立刻页面跳转，依靠 `keepalive:true` 保障尽可能发出埋点；
4. track是普通同步调用，和前后的`await`互不干扰，可以写在await前面，也可以写在await后面。

> 补充：埋点设计初衷就是**非阻塞弱一致性**，业务逻辑不要依赖埋点请求成功或失败，埋点失败也不影响主业务流程。
