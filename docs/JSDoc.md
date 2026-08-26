```
/**
 * 埋点上报
 * @param {Object} payload - 埋点主体对象
 * @param {string} payload.event - 埋点事件名，必填
 * @param {string} [payload.page] - 页面标识，非必填
 * @param {Record<string, any>} [payload.data] - 业务自定义数据，非必填
 * @param {Object} [extOptions={}] - 扩展配置，非必填，默认{}
 * @param {boolean} [extOptions.force] - 是否跳过限流强制上报，非必填
 * @param {number} [extOptions.limitTime] - 限流时间，毫秒，非必填
 */
const track = (payload, extOptions = {}) => {}
```

### 要点拆解

1. **第二个参数 `extOptions={}`**
   整体是非必填，注释写 `[extOptions={}]`，`[]`标记可选，`={}`标注默认值。
2. **payload 是对象，子属性区分必填/非必填**

- 必填：`payload.xxx - xxx` 不带方括号
- 非必填：`[payload.xxx] - xxx` 方括号包裹

3. TS版本（有类型）

```
interface TrackPayload {
  event: string
  page?: string
  data?: Record<string, any>
}

interface TrackExtOptions {
  force?: boolean
  limitTime?: number
}

/**
 * 埋点上报
 * @param payload 埋点主体对象
 * @param payload.event 埋点事件名，必填
 * @param [payload.page] 页面标识，非必填
 * @param [payload.data] 业务自定义数据，非必填
 * @param [extOptions={}] 扩展配置，非必填，默认{}
 * @param [extOptions.force] 是否跳过限流强制上报，非必填
 * @param [extOptions.limitTime] 限流时间，毫秒，非必填
 */
const track = (payload: TrackPayload, extOptions: TrackExtOptions = {}) => {}
```

### 嵌套记忆口诀

- 参数整体可选：`[参数名=默认值]`
- 对象子属性可选：`[参数.属性]`
- 必填：**不加方括号**

### 示例调用参考

```
track({ event: 'click_add_save', page: '新增弹窗' })
track({ event: 'click_table_search' }, { force: true })
```
