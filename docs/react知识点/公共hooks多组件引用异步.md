# 公共hooks 在多个组件引用时，如果需要避免异步接口多次调用的办法

# 完整优化后代码（包含等待请求后同步状态逻辑，解决多组件初次渲染空白闪烁）
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

## 使用示例（任意组件调用）
```jsx
import useIsHisPrePlan from './hooks/useIsHisPrePlan';

const DemoComponent = () => {
  // 传入对应业务参数
  const { currentPlanStatus, isPlanStatusLoading, resetPrePlanCache } = useIsHisPrePlan(
    true,
    false,
    '1001',
    'his_1001'
  );

  if (isPlanStatusLoading) return <div>加载中...</div>;

  return (
    <div>
      <p>预案状态：{currentPlanStatus ?? '暂无数据'}</p>
      <button onClick={resetPrePlanCache}>清空缓存重新请求</button>
    </div>
  );
};
```

## 关键特性说明
1. **并发去重**：多个组件同时挂载只会发起一次接口请求，其余组件等待同一份Promise
2. **无页面闪烁**：等待请求完成后主动同步缓存到当前组件state，不需要等待二次重渲染
3. **全局缓存持久**：一次请求后所有新挂载组件直接读取缓存，不再调接口
4. **支持手动刷新**：导出 `resetPrePlanCache` 可清空缓存强制重新请求接口
5. **状态隔离**：`currentPlanStatus` / `isPlanStatusLoading` 为每个组件独立状态，通过全局缓存统一数据源