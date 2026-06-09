# 完整拆解问题 + 分层解决方案
## 一、先理清现状矛盾点
1. `isOnlyPublished` / `isPlanStatusLoading` **只用在 `else{}` 分支**，和 `if(isIframeEdit || isIframeView)` 的 `handleIframe()` 逻辑完全无关；
2. 但你把这两个状态放进了外层 `useEffect` 的依赖数组，只要它们异步更新，整个 `useEffect` 会**完整重跑一遍**：
   - 重跑时先执行 `dispatch(setTemplate(0))`
   - 再次进入 `if (isIframeEdit || isIframeView)` 分支 → 重复调用 `handleIframe()`
3. 根源：**useEffect 只要依赖数组任意一项变化，整个回调函数全部重新执行，不会只执行 else 部分**。

## 二、分两种落地方案（按需选择）
### 方案1：职责拆分（最优推荐，解耦逻辑）
把两段完全独立的逻辑拆成**两个 useEffect**，各自只监听自己需要的依赖：
#### 1）iframe 专用 useEffect（只跑 handleIframe，不依赖那两个状态）
```tsx
// 只处理iframe初始化逻辑，依赖只保留iframe相关标识
useEffect(() => {
  dispatch(planActions.setTemplate(0));
  if (isIframeEdit || isIframeView) {
    handleIframe();
  }
  return () => {
    dispatch(planActions.reset());
  };
}, [
  isIframeEdit, isIframeView, handleIframe, dispatch,
  hisPrePlanId, originalPlanId, isViewPage, isInitToBeHisPrePlan
]);
```

#### 2）非iframe页面专用 useEffect（只监听那两个异步状态，仅else逻辑）
```tsx
// 仅普通页面逻辑，只监听isOnlyPublished、isPlanStatusLoading
useEffect(() => {
  if (isIframeEdit || isIframeView) return; // iframe模式直接跳过
  try {
    // 你原来else里面用到 isOnlyPublished / isPlanStatusLoading 的业务代码
  } finally {
    setIsStateReady(true);
  }
}, [
  isIframeEdit, isIframeView, setIsStateReady,
  isOnlyPublished, isPlanStatusLoading // 这里只放普通页面需要的状态
]);
```
#### 优势
- iframe 逻辑和普通页面逻辑彻底隔离；
- `isOnlyPublished`、`isPlanStatusLoading` 更新时，只会触发第二个 useEffect，不会重新执行 `handleIframe()`；
- 依赖数组最小化，没有多余重渲染。

---

### 方案2：不拆分Effect，加分支阻断（改造成本低）
如果你暂时不想拆分 useEffect，保留单个 effect，用**ref标记**阻止iframe分支重复执行：
```tsx
// 组件顶层，标记iframe逻辑是否已经执行完成
const iframeExecutedRef = useRef(false);

useEffect(() => {
  dispatch(planActions.setTemplate(0));

  if (isIframeEdit || isIframeView) {
    // 已执行过直接阻断，不再重复调用handleIframe
    if (!iframeExecutedRef.current) {
      iframeExecutedRef.current = true;
      handleIframe();
    }
  } else {
    try {
      // else分支：使用isOnlyPublished、isPlanStatusLoading的逻辑
    } finally {
      setIsStateReady(true);
    }
  }

  return () => {
    dispatch(planActions.reset());
    iframeExecutedRef.current = false; // 组件卸载重置标记
  };
}, [
  isIframeEdit, isIframeView, handleIframe, isInitToBeHisPrePlan, setIsStateReady,
  hisPrePlanId, originalPlanId, isViewPage, dispatch, isOnlyPublished, isPlanStatusLoading
]);
```
#### 原理
哪怕 `isOnlyPublished` / `isPlanStatusLoading` 异步更新触发 effect 重跑，进入iframe分支时 `iframeExecutedRef.current` 已经为 `true`，直接跳过 `handleIframe()`，不会重复发接口。

## 三、额外兜底防护（两种方案都建议加上）
给 `handleIframe` 自身加**执行锁ref**，极端场景下双重防重复：
```tsx
const iframeLoadingRef = useRef(false);
const handleIframe = useCallback(async () => {
  if (iframeLoadingRef.current) return;
  try {
    iframeLoadingRef.current = true;
    // 原有judgeHistoryIframe、dispatch更新store逻辑
  } finally {
    setIsStateReady(true);
    iframeLoadingRef.current = false;
  }
}, [judgeHistoryIframe, isIframeView, isIframeEdit, iframeType, dispatch, setIsStateReady]);
```

## 四、关键总结
1. 不能因为某个状态只在 `else` 分支使用，就放进公共 useEffect 依赖：effect 是整体执行，依赖变化会全量重跑；
2. 最优解是**拆分两个 useEffect**，iframe逻辑、普通页面逻辑各自管理自己的依赖，从根源避免互相干扰；
3. 兜底用ref标记执行状态，防止多次触发接口请求，避免数据重复覆盖、接口冗余调用。