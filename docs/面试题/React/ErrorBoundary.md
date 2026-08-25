# getDerivedStateFromError

`static getDerivedStateFromError(error)` 是 **React 类组件的静态生命周期**，属于**错误边界(Error Boundary)** API，React 16+ 引入。

> ⚠️ 只捕获**子组件树渲染、生命周期、构造函数**抛出的错误；
> 无法捕获：事件处理器、异步代码、服务端渲染、自身抛出的错误。

## 签名

```
static getDerivedStateFromError(error) {
  // 返回值会更新 state
  return { hasError: true };
}
```

- 静态方法，**不能用 this**
- 参数：捕获到的异常对象 `error`
- 返回：对象用于更新 state；返回 `null` 不更新 state
- 在 **render 阶段执行**，不能做副作用；副作用放 `componentDidCatch`

## 和 componentDidCatch 对比

| API                               | 阶段       | 用途                         |
| --------------------------------- | ---------- | ---------------------------- |
| `static getDerivedStateFromError` | render阶段 | 返回state，渲染降级UI        |
| `componentDidCatch(error, info)`  | commit阶段 | 做副作用：打印日志、上报错误 |

## 完整错误边界示例

```
class ErrorBoundary extends React.Component {
  state = { hasError: false };

  // 发生错误，更新state，渲染错误页面
  static getDerivedStateFromError(error) {
    console.log("捕获错误", error);
    return { hasError: true };
  }

  // 提交阶段，上报日志等副作用
  componentDidCatch(error, errorInfo) {
    // 上报监控系统
  }

  render() {
    if (this.state.hasError) {
      return <div>页面出错，请刷新重试</div>;
    }
    return this.props.children;
  }
}

// 使用
<ErrorBoundary>
  <Child />
</ErrorBoundary>
```

## 关键注意点

1. **必须是类组件**，函数组件本身不能直接做错误边界；React18 后可以用 `react-error-boundary` 库实现函数式错误边界。
2. 错误只会捕获**子组件**，组件自身抛错不会被自己捕获。
3. 发生错误后，默认不会自动恢复；想要恢复，需要提供重置 state 的方法（增加重置按钮）。
4. 不要在里面写接口请求、console上报，上报逻辑放到 `componentDidCatch`。

### 重置错误边界示例

```
static getDerivedStateFromError() {
  return { hasError: true };
}

handleReset = () => {
  this.setState({ hasError: false });
}

render() {
  if(this.state.hasError){
    return <button onClick={this.handleReset}>重试</button>
  }
  return this.props.children
}
```

## React 18 变化

React18 中，`getDerivedStateFromError` 触发时，**会自动卸载出错子树全部内容**；如果想要保留旧UI，需要自己做状态缓存。

## 函数组件替代方案

官方没有原生hooks错误边界，一般用成熟库：`react‑error‑boundary`

```
npm install react-error-boundary
```

```
import { ErrorBoundary } from "react-error-boundary";

function Fallback({ resetErrorBoundary }) {
  return <button onClick={resetErrorBoundary}>重试</button>
}

<ErrorBoundary FallbackComponent={Fallback}>
  <App />
</ErrorBoundary>
```

如果你需要，我可以对比一下 `getDerivedStateFromError` 和 `componentDidCatch` 的执行时序，或者写一个TS版本完整示例。
