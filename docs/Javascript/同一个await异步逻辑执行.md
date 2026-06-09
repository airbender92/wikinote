```js
// useIsHisPrePlan.js
import { useState, useEffect } from 'react';
import documentEditorService from '@/services/xxx'; // 替换为你真实service路径

// 模块级全局缓存（所有调用该hook的组件共享，仅初始化一次）
let cacheData = null;
let requestPromise = null;
let isFetched = false;

/**
 * 历史预案状态hook，多组件共用只请求一次接口
 * @param {boolean} isViewPage 是否预览页面
 * @param {boolean} isFromHistoryPrePlan 是否从历史预案版本进入
 * @param {string|number} originalPlanId 原始预案id
 * @param {string|number} hisPrePlanId 历史预案id
 */
export default function useIsHisPrePlan(isViewPage, isFromHistoryPrePlan, originalPlanId, hisPrePlanId) {
  // 每个组件独立的状态，组件间互不共享
  const [currentPlanStatus, setCurrentPlanStatus] = useState(null);
  const [isPlanStatusLoading, setIsPlanStatusLoading] = useState(false);

  const handleBaisInfo = async (id) => {
    // 1. 已有全局缓存，直接更新当前组件自身状态并退出
    if (isFetched) {
      setCurrentPlanStatus(cacheData.prePlanStatus);
      setIsPlanStatusLoading(false);
      return;
    }

    // 2. 当前已有接口请求在执行，等待请求完成后同步缓存到自身状态再退出
    if (requestPromise) {
      await requestPromise;
      // 关键补充：等待完成后主动更新当前组件state，无需等下一轮重渲染
      setCurrentPlanStatus(cacheData.prePlanStatus);
      setIsPlanStatusLoading(false);
      return;
    }

    // 3. 无缓存、无进行中请求，发起唯一一次接口调用
    try {
      setIsPlanStatusLoading(true);
      // 将请求promise存入全局变量，拦截并发重复调用
      requestPromise = documentEditorService.findPrePlanBaseInfoByIdApi({ id });
      const response = await requestPromise;

      if (response?.code === "200") {
        // 缓存接口返回完整数据，标记已请求完成
        cacheData = response.result;
        isFetched = true;
        setCurrentPlanStatus(cacheData.prePlanStatus);
      } else {
        setCurrentPlanStatus(null);
      }
    } catch (error) {
      console.error('获取预案基础信息失败：', error);
      setCurrentPlanStatus(null);
    } finally {
      setIsPlanStatusLoading(false);
      // 请求结束清空全局请求锁
      requestPromise = null;
    }
  };

  useEffect(() => {
    // 预览模式下 且 非预案版本进入的 且 有历史版本id的，执行接口查询
    if (isViewPage && !isFromHistoryPrePlan && originalPlanId && hisPrePlanId) {
      handleBaisInfo(originalPlanId);
    } else {
      // 不满足查询条件时清空状态
      setCurrentPlanStatus(null);
      setIsPlanStatusLoading(false);
    }
  }, [isViewPage, originalPlanId, hisPrePlanId, isFromHistoryPrePlan]);

  // 提供手动重置缓存方法，用于切换页面/刷新数据场景
  const resetPrePlanCache = () => {
    cacheData = null;
    requestPromise = null;
    isFetched = false;
  };

  return {
    currentPlanStatus,
    isPlanStatusLoading,
    resetPrePlanCache
  };
}
```

# 清晰时序拆解，一句话先给结论
`await requestPromise` 会**阻塞当前代码**，一直等到下面这段完整逻辑全部跑完、Promise 真正 resolve 之后，才会执行 await 后面两行 set 状态代码：
```js
const response = await requestPromise;
if (response?.code === "200") {
  cacheData = response.result;
  isFetched = true;
  setCurrentPlanStatus(cacheData.prePlanStatus);
  // history.replace 更新url
}
```

## 完整时序分步演示（组件A先请求，组件B同时触发handleBaisInfo）
### 步骤1：组件A 执行请求逻辑
1. A 走到 `requestPromise = documentEditorService.findPrePlanBaseInfoByIdApi({ id })`
2. 发起网络请求，把这个Promise存入全局 `requestPromise`
3. A 执行 `const response = await requestPromise;`，A 暂停，等待后端返回

### 步骤2：同一时刻 组件B 进入 if(requestPromise) 分支
```js
if (requestPromise) {
  await requestPromise; // B 在这里卡住，等待A的同一个Promise完成
  setCurrentPlanStatus(cacheData.prePlanStatus);
  setIsPlanStatusLoading(false);
  return;
}
```
此时B停在 `await requestPromise`，**不会往下走set代码**，等网络请求返回。

### 步骤3：后端接口返回，A的Promise resolve，完整走完A的成功逻辑
1. A拿到 `response`
2. 进入 `if (response?.code === "200")`
3. 赋值全局 `cacheData`、`isFetched = true`、执行set、更新url参数
4. A的try代码全部执行完毕，进入finally清空 `requestPromise = null`
5. **此时全局的requestPromise才算真正完成resolve**

### 步骤4：B的await阻塞解除，立刻执行后面两行set
A的整套接口成功、缓存赋值、finally全部走完后，B才会继续执行：
```js
setCurrentPlanStatus(cacheData.prePlanStatus);
setIsPlanStatusLoading(false);
return;
```

## 核心关键点
1. `requestPromise` 是同一个请求对象，**必须等A内部所有接口回调逻辑（包括if成功块、finally）全部执行完毕，await才会放行**；
2. B 的两行 set 一定是在 `if (response?.code === "200") {}` 执行完之后才运行；
3. 不存在“先执行B的set再走A的成功逻辑”的情况，Promise resolve 代表整个请求回调流程全部结束。

## 补充异常场景（接口报错catch）
就算接口进了catch分支：
- 依然会走完 catch、finally，清空 `requestPromise`
- 之后B的await才会放行，此时 `cacheData` 为null，执行setCurrentPlanStatus会赋值null，符合预期。