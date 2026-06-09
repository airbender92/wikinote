# React Router v5.2 适配修改（v5 没有 useNavigate，用 useHistory）
## 核心差异
- react-router v5：`useHistory()` → `history.push / history.replace`
- react-router v6：`useNavigate()`

## 完整修正后代码
```js
// useIsHisPrePlan.js
import { useState, useEffect } from 'react';
// v5 导入 useHistory、useLocation
import { useHistory, useLocation } from 'react-router-dom';
import documentEditorService from '@/services/xxx';

// 模块级全局缓存（所有组件共享）
let cacheData = null;
let requestPromise = null;
let isFetched = false;

export default function useIsHisPrePlan(isViewPage, isFromHistoryPrePlan, originalPlanId, hisPrePlanId) {
  // v5 获取history实例
  const history = useHistory();
  const location = useLocation();
  const [currentPlanStatus, setCurrentPlanStatus] = useState(null);
  const [isPlanStatusLoading, setIsPlanStatusLoading] = useState(false);

  const handleBaisInfo = async (id) => {
    // 已有缓存直接同步状态
    if (isFetched) {
      setCurrentPlanStatus(cacheData.prePlanStatus);
      setIsPlanStatusLoading(false);
      return;
    }

    // 等待正在进行的请求，同步状态后返回
    if (requestPromise) {
      await requestPromise;
      setCurrentPlanStatus(cacheData.prePlanStatus);
      setIsPlanStatusLoading(false);
      return;
    }

    try {
      setIsPlanStatusLoading(true);
      requestPromise = documentEditorService.findPrePlanBaseInfoByIdApi({ id });
      const response = await requestPromise;

      if (response?.code === "200") {
        cacheData = response.result;
        isFetched = true;
        setCurrentPlanStatus(cacheData.prePlanStatus);

        // ========== v5 更新url query参数逻辑 ==========
        const searchParams = new URLSearchParams(location.search);
        // 替换成你需要的参数名和值
        searchParams.set('planStatus', cacheData.prePlanStatus);
        // 拼接新search
        const newSearch = searchParams.toString();
        // replace 替换当前历史记录，不新增页面栈（推荐）
        history.replace({
          pathname: location.pathname,
          search: newSearch
        });
        // 如果想要新增历史记录就用 history.push(...)
        // history.push({ pathname: location.pathname, search: newSearch });
      } else {
        setCurrentPlanStatus(null);
      }
    } catch (error) {
      console.error('获取预案基础信息失败：', error);
      setCurrentPlanStatus(null);
    } finally {
      setIsPlanStatusLoading(false);
      requestPromise = null;
    }
  };

  useEffect(() => {
    if (isViewPage && !isFromHistoryPrePlan && originalPlanId && hisPrePlanId) {
      handleBaisInfo(originalPlanId);
    } else {
      setCurrentPlanStatus(null);
      setIsPlanStatusLoading(false);
    }
  }, [
    isViewPage,
    originalPlanId,
    hisPrePlanId,
    isFromHistoryPrePlan,
    history,
    location
  ]);

  // 重置缓存方法
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

## 关键修改点说明
1. 导入替换
```js
// v6 废弃
// import { useNavigate } from 'react-router-dom'
// v5 正确
import { useHistory, useLocation } from 'react-router-dom';
```
2. 路由实例获取
```js
const history = useHistory();
```
3. 更新URL逻辑
```js
// v6 navigate 写法废弃
// navigate(xxx, {replace:true})

// v5 替换当前url（无新增历史，返回键不会重复跳转）
history.replace({
  pathname: location.pathname,
  search: newSearch
});

// 如需新增一条历史记录使用 push
// history.push({ pathname: location.pathname, search: newSearch });
```

## 不依赖 react-router 的兜底方案（备用）
如果不想引入路由钩子，直接原生修改浏览器地址：
```js
if (response?.code === "200") {
  cacheData = response.result;
  isFetched = true;
  setCurrentPlanStatus(cacheData.prePlanStatus);

  const searchParams = new URLSearchParams(window.location.search);
  searchParams.set('planStatus', cacheData.prePlanStatus);
  const newUrl = `${window.location.pathname}?${searchParams.toString()}`;
  // 替换当前历史记录
  window.history.replaceState(null, '', newUrl);
}
```