# 第一条：在定义 AI 接口返回的嵌套[https://zhida.zhihu.com/search?content_id=275243076&content_type=Article&match_order=1&q=%E6%95%B0%E6%8D%AE%E7%BB%93%E6%9E%84&zhida_source=entity](https://zhida.zhihu.com/search?content_id=275243076&content_type=Article&match_order=1&q=%E6%95%B0%E6%8D%AE%E7%BB%93%E6%9E%84&zhida_source=entity)（如多轮对话、工具调用结果）时，如何用 TypeScript 的泛型与条件类型实现灵活的类型推导？

---

# AI对话消息 type / role 含义

`role` 常见四个枚举值：`user`、`assistant`、`system`、`tool`，是大模型对话接口（OpenAI 格式，国内豆包、通义、文心等基本兼容这套消息结构）里消息角色字段，每条消息对象都有 `role` + `content`，工具调用会额外增加字段。

## 1. role: "system" —— 系统提示

**角色：给模型下达全局人设、规则、背景指令，不是用户对话内容**

- 作用：设定AI身份、约束回答规则、输出格式、安全边界，会话最开始放，优先被模型读取。
- 示例：

```json
{
  "role": "system",
  "content": "你是一名后端工程师，回答简洁，只输出代码和要点，不要多余话术"
}
```

> 注意：不是用户说的话，也不是AI回复，是对模型的顶层指令。

## 2. role: "user" —— 用户

**角色：人类用户输入的提问、指令**

- 作用：代表真实用户说的每一句话。

```json
{ "role": "user", "content": "解释vue3响应式原理" }
```

## 3. role: "assistant" —— 助手

**角色：大模型AI输出的回答**

- 作用：模型返回给用户的文本回答；**如果AI要调用工具时，这里会附带 `tool_calls` 字段，content可以为空**。

```json
{ "role": "assistant", "content": "Vue3使用Proxy实现响应式" }
```

## 4. role: "tool" —— 工具返回结果

**角色：工具函数执行完之后，把工具返回的数据塞回给大模型**

> 只有开启**Function Calling（工具调用）**才会出现这个role。

- 流程：

1. `assistant` 返回消息，携带 `tool_calls`，告诉模型需要调用哪个工具、参数是什么；
2. 业务代码本地执行工具函数（查数据库、调用接口、计算器等）；
3. 将工具执行结果，封装成 `role:tool` 的消息，把 `tool_call_id` 和返回结果带上，塞回消息列表；
4. 大模型拿到tool返回的数据，再生成最终自然语言回答。

示例tool消息：

```json
{
  "role": "tool",
  "tool_call_id": "call_xxxx",
  "content": "上海今天气温28度"
}
```

---

# 完整对话流转示例（带工具调用）

```json
[
  { "role": "system", "content": "你是天气助手，可以调用查询天气工具" },
  { "role": "user", "content": "上海今天多少度" },
  {
    "role": "assistant",
    "content": "",
    "tool_calls": [
      {
        "id": "call_123",
        "function": { "name": "getWeather", "arguments": "{\"city\":\"上海\"}" }
      }
    ]
  },
  {
    "role": "tool",
    "tool_call_id": "call_123",
    "content": "上海今日28℃，多云"
  },
  { "role": "assistant", "content": "上海今天28℃，天气多云。" }
]
```

## 快速记忆总结

| role        | 含义     | 使用场景                        |
| ----------- | -------- | ------------------------------- |
| `system`    | 系统指令 | 设定AI人设、规则，会话配置      |
| `user`      | 用户     | 人的提问输入                    |
| `assistant` | AI助手   | AI输出文本 / AI发起工具调用请求 |
| `tool`      | 工具返回 | 工具函数执行结果回传给模型      |

> 补充：部分老接口还有 `function`，已经废弃，统一改用 `tool`。

如果你需要，我可以顺带讲下 `tool_calls`、`tool_call_id` 之间的对应关系。

---

# TypeScript 泛型+条件类型定义AI接口嵌套返回结构

AI 接口典型场景：多轮对话、工具调用、工具返回结果嵌套，响应体是多层嵌套，结构可变，但部分字段固定。目标：**复用一套类型，自动推导内部 payload 类型，减少重复 interface，区分成功/失败、工具调用、普通消息**。

> 示例业务背景：大模型接口返回，可能：
>
> 1. 普通文本消息
> 2. 携带工具调用请求 `tool_calls`
> 3. 携带工具执行返回结果 `tool_result`
> 4. 嵌套多轮历史对话数组
> 5. 统一外层包装：code、msg、data，`data`内部结构随场景变化

## 一、基础：通用API外层包装（泛型包裹内层data）

绝大多数后端/AI接口外层统一，只有`data`不一样，先用泛型抽离外层。

```
/**
 * 通用接口返回外层壳
 * T：内部data的实际类型
 */
type ApiResponse<T> = {
  code: number
  msg: string
  data: T
}
```

AI多轮对话基础消息单元，消息有不同`role`，内容可能是文本，也可能嵌套工具调用。

```
type Role = "user" | "assistant" | "system" | "tool"

// 工具调用结构体
interface ToolCall {
  id: string
  name: string
  arguments: Record<string, unknown>
}

// 工具执行结果
interface ToolResult {
  tool_call_id: string
  content: string | object
}
```

## 二、条件类型：根据role区分消息载荷

> 条件类型语法：`T extends U ? TrueType : FalseType`
> 利用条件类型，**根据role自动推导消息内部字段**：

- `assistant`：可能携带 `tool_calls`
- `tool`：必须携带 `tool_result`
- `user/system`：只有文本`content`

```
/**
 * 条件类型：根据Role，推导消息附属载荷
 */
type MessagePayloadByRole<R extends Role> =
  R extends "assistant"
    ? { tool_calls?: ToolCall[] }
    : R extends "tool"
      ? { tool_result: ToolResult }
      : {}

/**
 * 消息泛型：R限定role，自动合并对应payload
 */
type ChatMessage<R extends Role = Role> = {
  role: R
  content: string
} & MessagePayloadByRole<R>
```

### 使用效果，TS自动校验：

```
// assistant消息，允许tool_calls
const msg1: ChatMessage<"assistant"> = {
  role: "assistant",
  content: "我要调用工具",
  tool_calls: [{ id: "1", name: "search", arguments: { q: "xxx" } }]
}

// tool消息，强制必须有tool_result
const msg2: ChatMessage<"tool"> = {
  role: "tool",
  content: "工具返回内容",
  tool_result: { tool_call_id: "1", content: "搜索结果" }
}

// user消息，不能写tool_calls/tool_result，TS报错
const msg3: ChatMessage<"user"> = {
  role: "user",
  content: "你好"
}
```

## 三、泛型实现：嵌套多轮对话 + 工具调用返回的完整AI响应

AI接口返回`data`一般包含消息数组，同时本次返回可能携带工具调用，也可能不携带。
我们再定义对话接口返回，把消息数组作为泛型参数。

```
/**
 * AI对话data主体
 * M：消息类型，默认 ChatMessage
 */
type AiChatData<M = ChatMessage> = {
  session_id: string
  messages: M[] // 多轮对话，消息数组嵌套
  finish_reason?: "stop" | "tool_calls" | "length"
}

// 完整AI接口响应：套上通用ApiResponse外壳
type AiChatResponse = ApiResponse<AiChatData>
```

### 模拟接口返回数据

```
const resp: AiChatResponse = {
  code: 0,
  msg: "ok",
  data: {
    session_id: "sess_001",
    finish_reason: "tool_calls",
    messages: [
      { role: "user", content: "查天气" },
      {
        role: "assistant",
        content: "",
        tool_calls: [{ id: "t1", name: "get_weather", arguments: { city: "上海" } }]
      }
    ]
  }
}
```

## 四、高级：泛型+条件类型，支持自定义工具入参输出类型

上面`ToolCall["arguments"]`是`Record<string,unknown>`，不够精准。
我们传入工具的**入参、出参泛型参数**，实现工具调用强类型推导。

```
/**
 * 泛型工具调用：TArgs工具入参，TResult工具返回结果
 */
interface IToolCall<TArgs = unknown, TResult = unknown> {
  id: string
  name: string
  arguments: TArgs
}

interface IToolResult<TResult = unknown> {
  tool_call_id: string
  content: TResult
}

/**
 * 条件类型重载，携带工具泛型参数
 */
type MessagePayloadByRoleWithTool<
  R extends Role,
  TArgs = unknown,
  TResult = unknown
> =
  R extends "assistant"
    ? { tool_calls?: IToolCall<TArgs, TResult>[] }
    : R extends "tool"
      ? { tool_result: IToolResult<TResult> }
      : {}

type ChatMessageWithTool<
  R extends Role = Role,
  TArgs = unknown,
  TResult = unknown
> = {
  role: R
  content: string
} & MessagePayloadByRoleWithTool<R, TArgs, TResult>
```

### 示例：强类型「天气查询工具」消息

```
// 定义该工具的入参、返回结构
type WeatherToolArgs = { city: string }
type WeatherToolResult = { temp: number; weather: string }

// 实例化消息类型：绑定天气工具类型
type WeatherAssistantMsg = ChatMessageWithTool<"assistant", WeatherToolArgs, WeatherToolResult>

const weatherMsg: WeatherAssistantMsg = {
  role: "assistant",
  content: "",
  tool_calls: [
    {
      id: "tw1",
      name: "get_weather",
      arguments: { city: "上海" } // TS自动校验必须city字段
    }
  ]
}
```

## 五、条件类型 + 推断infer：提取嵌套响应内部类型

很多场景：拿到`ApiResponse<T>`，想提取内部`data`类型；拿到消息，提取工具调用内部类型。**`infer`条件类型做类型提取**。

```
// 提取ApiResponse中data的类型
type ExtractApiData<T> = T extends ApiResponse<infer D> ? D : never

// 提取AiChatResponse的data类型，等价 AiChatData
type ChatData = ExtractApiData<AiChatResponse>

// 提取消息里的工具调用参数类型
type ExtractToolArgs<T> =
  T extends { tool_calls?: Array<{ arguments: infer A }> } ? A : never
```

使用示例：

```
// 从消息类型中，把工具arguments的类型扒出来
type Args = ExtractToolArgs<WeatherAssistantMsg> // → WeatherToolArgs
```

## 六、区分流式/非流式返回（条件类型开关）

AI接口经常有两种返回：一次性完整返回、SSE流式chunk分片返回。
用**泛型布尔参数+条件类型**切换两种结构。

```
type AiChatDataStream<IsStream extends boolean> = IsStream extends true
  ? {
      session_id: string
      delta: ChatMessage // 流式是增量delta
      is_finish: boolean
    }
  : {
      session_id: string
      messages: ChatMessage[]
      finish_reason?: string
    }

// 流式响应
type AiStreamResponse = ApiResponse<AiChatDataStream<true>>
// 完整一次性响应
type AiFullResponse = ApiResponse<AiChatDataStream<false>>
```

## 七、核心设计思路总结

| 技术点                                  | 解决AI接口什么问题                                           |
| --------------------------------------- | ------------------------------------------------------------ |
| **外层泛型 `ApiResponse<T>`**           | 统一包装code、msg，剥离多变的data                            |
| **条件类型 `Role extends xxx ? A : B`** | 根据消息角色自动附加/剔除工具调用字段，避免大量重复interface |
| **泛型参数传递工具入参/返回值**         | 把业务工具结构注入嵌套消息，实现强类型工具调用               |
| **`infer` 条件推断**                    | 从已定义复杂嵌套响应中提取子类型，不用重复定义               |
| **布尔泛型参数切换结构**                | 一套类型同时支持普通响应、SSE流式分片返回                    |

## 八、常见踩坑点

1. **条件类型分发**：如果传入联合类型`ChatMessage<"assistant"|"tool">`，条件类型会分别对每一个成员计算，符合AI多角色消息场景，但要注意联合类型行为。
2. 不要滥用`unknown`：工具参数尽量用泛型参数传入，少用`any`。
3. 嵌套对象泛型传递：泛型参数需要逐层往下传递，否则内层拿不到自定义工具类型。
4. 接口JSON字段可选：AI接口很多字段是可选（`tool_calls?:`），条件类型返回要加可选符号。

如果你需要，我可以给一份可直接复制的完整 `.d.ts` 类型文件，包含错误样例、类型测试代码。

---

---

# 第二条：当 AI 接口返回的字段可能因模型版本不同而动态变化时，如何设计[https://zhida.zhihu.com/search?content_id=275243076&content_type=Article&match_order=1&q=%E7%B1%BB%E5%9E%8B%E5%AE%88%E5%8D%AB&zhida_source=entity](https://zhida.zhihu.com/search?content_id=275243076&content_type=Article&match_order=1&q=%E7%B1%BB%E5%9E%8B%E5%AE%88%E5%8D%AB&zhida_source=entity)（type guard）与类型收缩策略？

# AI接口多模型版本：TypeScript 类型守卫(type‑guard) + 类型收缩完整方案

> 问题背景：不同大模型版本返回字段不一致。

- 模型A：返回 `tool_calls`，无 `tools`；
- 模型B：废弃`tool_calls`，改用`tools`数组；
- 部分模型返回额外扩展字段 `metadata`，老版本没有；
- 部分字段有时候存在、有时候`null`、有时候直接缺失；
- TS静态类型无法表达“运行时才知道是哪个模型版本”，**静态泛型/条件类型只能做编译期约束，运行时必须靠类型守卫做类型收缩**。

核心思想：

1. 先定义**最大兼容超类型（Supertype）**：把所有版本可能出现的字段全部标记为可选；
2. 编写**类型守卫函数 `isXXX(data: unknown): data is Type`** 在运行时判断模型版本、字段是否存在；
3. 通过守卫完成**类型收缩（narrowing）**，缩小联合类型范围；
4. 搭配`infer`、区分可选/缺失/`null`；
5. 分层策略：外层接口校验 → 判断模型版本 → 收缩消息体 → 收缩工具结构；
6. 兼容：字段缺失、`undefined`、`null`、不同命名别名（`tool_calls` / `tools`）。

---

## 1. 定义兼容全部版本的超类型（父类型）

> 不要写多个互斥interface，维护成本爆炸。
> 所有版本可能出现的字段全部设为**可选**，作为统一超类型。

```
type Role = "user" | "assistant" | "system" | "tool";

/**
 * 兼容多模型版本消息超类型
 * tool_calls：旧版模型
 * tools：新版模型替换字段
 * metadata：部分模型才返回扩展元信息
 */
interface ChatMessageSuper {
  role?: Role;
  content?: string | null;
  // 旧版工具调用
  tool_calls?: Array<{
    id?: string;
    name?: string;
    arguments?: Record<string, unknown>;
  }>;
  // 新版模型替换字段
  tools?: Array<{
    call_id?: string;
    func_name?: string;
    params?: Record<string, unknown>;
  }>;
  metadata?: Record<string, unknown>;
}

/** AI返回外层data超类型，兼容所有模型版本 */
interface AiChatDataSuper {
  session_id?: string;
  messages?: ChatMessageSuper[];
  finish_reason?: string | null;
  model_version?: string; // 模型版本标识，运行时用来判断
}

/** 通用API外层壳 */
interface ApiResponse<T> {
  code: number;
  msg: string;
  data?: T | null;
}

// 接口原始响应，来自fetch解析后 unknown，运行时才知道真实结构
type RawAiResponse = ApiResponse<AiChatDataSuper>;
```

> 注意：这里全部是可选。**编译期无法保证字段一定存在**，必须运行时类型守卫做收缩。

---

## 2. 类型守卫基础语法

```
/**
 * 类型守卫函数签名：返回值写 `val is TargetType`
 * @param val 原始unknown数据
 */
function isChatMessageV1(val: unknown): val is ChatMessageV1 {
  // 内部做运行时判断
}
```

TS在`if(isChatMessageV1(msg)) {}`分支内部自动完成**类型收缩(narrowing)**，if块内变量变成`ChatMessageV1`，访问字段不会报“可能undefined”。

### 区分三种运行时异常情况（AI接口高频坑）

1. 字段**不存在**：`"key" in obj` → false
2. 字段等于 **undefined**：`obj.key === undefined`
3. 字段等于 **null**：`obj.key === null`

> AI接口经常：字段直接不返回，或者返回`null`，这两种不一样，守卫里要区分处理。

---

## 3. 分层类型守卫实战

分层校验：

1. 守卫1：校验整体ApiResponse外层结构
2. 守卫2：根据`model_version`区分模型版本，收缩`AiChatDataSuper`
3. 守卫3：收缩单条Message，区分旧版`tool_calls` /新版`tools`
4. 守卫4：工具调用子项守卫

### 3.1 守卫：校验API外层响应

```
/** 校验接口外层壳是否合法 */
function isApiResponse(val: unknown): val is RawAiResponse {
  if (typeof val !== "object" || val === null) return false;
  const o = val as Record<string, unknown>;
  return typeof o.code === "number" && typeof o.msg === "string";
}
```

### 3.2 根据model_version做版本分支守卫

> 重点：运行时读取`model_version`字符串，收缩为对应版本的数据类型。
> 先定义两个版本的**目标收缩类型**（不是超类型，是确定版本的确定类型）

```
// V1旧模型：使用 tool_calls
interface AiChatDataV1 {
  session_id: string;
  messages: Array<{
    role: Role;
    content: string | null;
    tool_calls: Array<{
      id: string;
      name: string;
      arguments: Record<string, unknown>;
    }>;
  }>;
  finish_reason?: string;
  model_version: "v1";
}

// V2新模型：废弃tool_calls，改用 tools
interface AiChatDataV2 {
  session_id: string;
  messages: Array<{
    role: Role;
    content: string | null;
    tools: Array<{
      call_id: string;
      func_name: string;
      params: Record<string, unknown>;
    }>;
  }>;
  finish_reason?: string;
  model_version: "v2";
}

/**
 * 类型守卫：根据model_version收缩为V1 / V2
 */
function isAiChatDataV1(data: AiChatDataSuper): data is AiChatDataV1 {
  return data.model_version === "v1"
    && Array.isArray(data.messages)
    && typeof data.session_id === "string";
}

function isAiChatDataV2(data: AiChatDataSuper): data is AiChatDataV2 {
  return data.model_version === "v2"
    && Array.isArray(data.messages)
    && typeof data.session_id === "string";
}
```

### 3.3 在业务代码中完成类型收缩

```
// fetch拿到原始数据，json解析后是 unknown
async function fetchAi(): Promise<void> {
  const res = await fetch("/api/chat");
  const raw: unknown = await res.json();

  // 第一层守卫收缩外层响应
  if (!isApiResponse(raw)) {
    console.error("接口返回格式非法");
    return;
  }
  // raw 此时收缩为 RawAiResponse

  const rawData = raw.data;
  if (!rawData) return;

  // 根据版本收缩
  if (isAiChatDataV1(rawData)) {
    // ✅ 此分支内 rawData 被收缩为 AiChatDataV1
    // TS识别 tool_calls，不会提示可能undefined
    for (const msg of rawData.messages) {
      console.log(msg.tool_calls);
    }
  } else if (isAiChatDataV2(rawData)) {
    // ✅ 此分支收缩为 AiChatDataV2，只能访问 tools
    for (const msg of rawData.messages) {
      console.log(msg.tools);
    }
  } else {
    // 未知模型版本，降级兼容超类型
    console.warn("未知模型版本", rawData.model_version);
  }
}
```

---

## 4. 高阶：泛型类型守卫 + 可复用字段校验工具

AI接口大量可选嵌套，把基础校验抽成小工具函数，避免重复写守卫。

```
/** 判断对象自身是否拥有该key（排除原型链） */
function hasKey<T extends object, K extends string>(obj: T, key: K): obj is T & Record<K, unknown> {
  return Object.prototype.hasOwnProperty.call(obj, key);
}

/** 安全判断数组并且每一项通过子守卫 */
function isArrayOf<T>(val: unknown, guard: (item: unknown) => item is T): val is T[] {
  return Array.isArray(val) && val.every(guard);
}
```

示例使用：

```
const obj = rawData as object;
if(hasKey(obj, "tool_calls")) {
  // obj 被收缩为包含 tool_calls
}
```

---

## 5. 处理「字段别名」：同一个语义不同字段名（tool_calls / tools）

很多模型迭代，只是换字段名，语义一样。

> 不要在类型层面做映射，**运行时守卫后做一层适配层，输出统一内部领域类型**。

设计模式：
`外部超类型（多版本异构） →【类型守卫区分版本】→【适配器adapter】→ 统一内部领域类型`

> 重要原则：**不要让业务逻辑到处写 if(v1) else if(v2)**。适配器把多版本差异屏蔽，业务层只消费一套统一类型。

```
/** 业务内部统一领域模型，业务代码只依赖这个，不感知外部模型版本差异 */
interface DomainMessage {
  role: Role;
  content: string | null;
  toolInvocations: Array<{
    id: string;
    name: string;
    args: Record<string, unknown>;
  }>;
}

/** 适配器：V1外部结构 → 内部领域模型 */
function adaptV1ToDomain(data: AiChatDataV1): DomainMessage[] {
  return data.messages.map(m => ({
    role: m.role,
    content: m.content,
    toolInvocations: m.tool_calls.map(t => ({
      id: t.id,
      name: t.name,
      args: t.arguments
    }))
  }));
}

/** 适配器：V2外部结构 → 内部领域模型 */
function adaptV2ToDomain(data: AiChatDataV2): DomainMessage[] {
  return data.messages.map(m => ({
    role: m.role,
    content: m.content,
    toolInvocations: m.tools.map(t => ({
      id: t.call_id,
      name: t.func_name,
      args: t.params
    }))
  }));
}
```

业务调用：

```
let domainMessages: DomainMessage[];
if(isAiChatDataV1(rawData)) {
  domainMessages = adaptV1ToDomain(rawData);
} else if(isAiChatDataV2(rawData)) {
  domainMessages = adaptV2ToDomain(rawData);
} else {
  domainMessages = [];
}
// 后续业务全部使用 domainMessages，完全屏蔽外部模型字段差异
```

> 架构收益：新增V3模型，只需要新增守卫 + 新增adapter，业务逻辑一行不改。

---

## 6. 类型收缩常见坑与避坑

### 坑1：类型守卫只做`as`强制转换，没有运行时判断

❌错误写法：

```
// 这不是类型守卫！只是类型断言，完全没有运行时校验！
function badGuard(val: unknown): val is AiChatDataV1 {
  return true;
}
```

> `is`标记只是编译期提示；**函数内部必须写真实运行时条件判断**。

### 坑2：`in`操作符不会收缩null/undefined

```
const o: unknown;
if("tool_calls" in o) {} // ❌ o 如果是null/object，会直接抛运行时异常
// 需要先判断 typeof o === 'object' && o !== null
```

### 坑3：超类型过度宽松，全部`any`

不要用`any`，使用`unknown`作为入口；所有外部接口JSON入口一律`unknown`，再走守卫收缩。

### 坑4：守卫只校验顶层对象，不校验嵌套子对象

AI接口是深度嵌套，只校验外层，内部`messages[0].tool_calls`依然不安全。使用上面的`isArrayOf`对子元素逐个守卫。

### 坑5：区分缺失字段 vs null

- `hasKey(obj, 'a') === false`：字段不存在
- `obj.a === null`：字段存在，值为null
  AI接口这两种情况要分开处理。

---

## 7. 整体架构总结（针对模型版本动态变化场景）

| 层次                | 技术手段                        | 作用                                                      |
| ------------------- | ------------------------------- | --------------------------------------------------------- |
| 原始输入            | `unknown`                       | 接口JSON解析入口，禁止直接赋值业务类型                    |
| 超类型              | 全部字段可选的Super Interface   | 容纳所有模型版本可能出现的字段                            |
| 类型守卫 type‑guard | `function fn(x:unknown):x is T` | **运行时真实校验**，完成类型收缩(narrowing)，区分模型版本 |
| 版本分支            | if + 守卫判断                   | TS自动收缩为对应版本确定类型                              |
| Adapter适配器       | 转换函数                        | 将多版本异构外部结构，映射为**统一内部领域类型**          |
| 业务层              | 只依赖内部Domain类型            | 业务代码完全感知不到外部模型字段差异                      |

> 补充：泛型+条件类型只能解决**编译期已知变体**；当变体来自运行时（模型版本、服务端返回动态字段），**泛型条件类型无能为力，必须搭配类型守卫做运行时收缩**。

如果你需要，我可以写一份可直接复制完整demo，包含：unknown原始响应、全套守卫、适配器、错误降级、jest简单测试用例。

---

---

# 第三条：请用TypeScript实现一个“类型安全的Prompt模板解析器”，要求支持变量插值、类型校验与默认值

# TS 实现 Prompt 模板解析器

需求要点：

1. 模板字符串变量插值 `${var}`
2. **TypeScript 类型安全校验**（变量类型检查、必填校验）
3. 支持变量默认值 `${var=默认值}`
4. 输出兼容 OpenAI 消息结构 `Message[]`（`system/user/assistant/tool`）
5. 解析模板 + 传入变量上下文，渲染最终 prompt 文本

> 模板语法约定：

- 变量插值：`${变量名}` 必填，不传抛类型错误
- 带默认值：`${变量名=默认文本}`，上下文缺失变量使用默认值
- 不支持嵌套 `${}`

````
/**
 * Prompt模板解析器
 * 语法：${name} 必填 | ${name=defaultVal} 带默认值
 */

// ---------------- 类型定义 ----------------
type PromptRole = "system" | "user" | "assistant" | "tool";

interface Message {
  role: PromptRole;
  content: string;
}

/**
 * 模板配置：支持单条消息 / 消息数组模板
 */
type PromptTemplateDef<TVars extends Record<string, unknown>> =
  | { role: PromptRole; template: string }
  | Array<{ role: PromptRole; template: string }>;

/**
 * 提取模板内变量名与默认值
 */
type TemplateVarMeta = {
  name: string;
  hasDefault: boolean;
  defaultValue?: string;
};

/**
 * 解析结果元信息
 */
interface ParseResult {
  rendered: string;
  vars: TemplateVarMeta[];
}

/**
 * 从模板字符串提取所有变量元信息
 * @param template 原始模板字符串
 */
function extractTemplateVars(template: string): TemplateVarMeta[] {
  const regex = /\$\{([^}]+)\}/g;
  const result: TemplateVarMeta[] = [];
  let match: RegExpExecArray | null;

  while ((match = regex.exec(template)) !== null) {
    const expr = match[1].trim();
    const eqIndex = expr.indexOf("=");
    if (eqIndex > 0) {
      const name = expr.slice(0, eqIndex).trim();
      const defaultValue = expr.slice(eqIndex + 1);
      result.push({ name, hasDefault: true, defaultValue });
    } else {
      result.push({ name: expr, hasDefault: false });
    }
  }
  return result;
}

/**
 * 渲染单个模板字符串，做运行时校验
 * @param template 模板文本
 * @param vars 上下文变量对象
 */
function renderTemplate(template: string, vars: Record<string, unknown>): ParseResult {
  const varMetas = extractTemplateVars(template);

  // 运行时校验：必填变量缺失检查
  for (const meta of varMetas) {
    if (!meta.hasDefault && !(meta.name in vars)) {
      throw new Error(`[PromptTemplate] 缺少必填变量：${meta.name}`);
    }
  }

  let rendered = template.replace(/\$\{([^}]+)\}/g, (_raw, expr: string) => {
    const eqIndex = expr.indexOf("=");
    const varName = eqIndex > 0 ? expr.slice(0, eqIndex).trim() : expr.trim();
    const defaultValue = eqIndex > 0 ? expr.slice(eqIndex + 1) : undefined;

    const val = vars[varName];
    if (val !== undefined && val !== null) {
      return String(val);
    }
    // 使用默认值
    if (defaultValue !== undefined) {
      return defaultValue;
    }
    throw new Error(`变量 ${varName} 无值且无默认值`);
  });

  return { rendered, vars: varMetas };
}

/**
 * Prompt 模板类，提供类型约束，渲染完整 Message[]
 */
export class PromptTemplate<TVars extends Record<string, unknown>> {
  private readonly templateDef: PromptTemplateDef<TVars>;

  constructor(templateDef: PromptTemplateDef<TVars>) {
    this.templateDef = templateDef;
  }

  /**
   * 渲染得到最终消息数组
   * @param ctx 变量上下文，TS强制类型校验
   */
  render(ctx: TVars): Message[] {
    const list = Array.isArray(this.templateDef)
      ? this.templateDef
      : [this.templateDef];

    return list.map((item) => {
      const { rendered } = renderTemplate(item.template, ctx);
      return {
        role: item.role,
        content: rendered,
      };
    });
  }

  /**
   * 获取模板中定义的全部变量元信息
   */
  getVariables(): TemplateVarMeta[] {
    const list = Array.isArray(this.templateDef)
      ? this.templateDef
      : [this.templateDef];
    const allVars: TemplateVarMeta[] = [];
    for (const t of list) {
      allVars.push(...extractTemplateVars(t.template));
    }
    return allVars;
  }
}

// -------------------- 使用示例 --------------------
/*
模板示例：
system：你是{{roleName}}，严格遵守规则：${strictLevel=严格}
user：请分析下面代码：${code}，返回${outputFormat}
*/

// 1. 定义变量类型约束
type MyPromptVars = {
  roleName: string;
  code: string;
  outputFormat: "json" | "markdown";
  // strictLevel 有默认值，可以不传
};

// 2. 创建模板实例
const myPrompt = new PromptTemplate<MyPromptVars>([
  {
    role: "system",
    template: "你是${roleName}，输出规范等级：${strictLevel=严格}",
  },
  {
    role: "user",
    template: "请分析如下代码片段：\n```ts\n${code}\n```\n输出格式要求：${outputFormat}",
  },
]);

// 3. 渲染，TS自动校验字段与类型
const messages = myPrompt.render({
  roleName: "TypeScript高级工程师",
  code: "const a:number = '123'",
  outputFormat: "json",
  // strictLevel不传，自动使用模板内默认值"严格"
});

console.log(messages);
console.log("模板变量列表：", myPrompt.getVariables());
````

## 输出 messages 样例

````
[
  {
    "role": "system",
    "content": "你是TypeScript高级工程师，输出规范等级：严格"
  },
  {
    "role": "user",
    "content": "请分析如下代码片段：\n```ts\nconst a:number = '123'\n```\n输出格式要求：json"
  }
]
````

## 特性说明

1. **类型安全**：传入 `TVars`，调用 `render(ctx)` TS 静态检查上下文字段、类型；
2. **默认值语法** `${var=xxx}`，上下文没有该变量时启用默认值；
3. **运行时校验**：没有默认值的变量缺失直接抛异常；
4. 支持单条消息 / 多条消息模板（system+user+assistant混合）；
5. `getVariables()` 可以拿到模板解析出的所有变量元信息，用于调试/UI展示；

## 扩展方向（如果你需要）

1. 支持数组变量循环渲染；
2. 支持条件语法 `${if flag}xxx${end}`；
3. 增加 zod 做运行时变量值类型校验（静态TS是编译期，运行时传入任意JS对象，Zod补全运行时类型）；
4. 支持转义 `\${}` 输出字面量 `${`；

如果你需要，我可以把加上 Zod 运行时校验的完整版本给你。

---

---

# 第四条： 如何用TypeScript的模板字面量类型（Template Literal Types）约束AI返回的特定格式字符串（如日期、ID）？

# TypeScript 模板字面量类型约束 AI 返回字符串

> TS **模板字面量类型（Template Literal Types）**：编译期做字符串格式约束，用来限定大模型输出字符串格式：日期、ID、UUID、枚举字符串、自定义编号、JSON前缀等。
> ⚠️ 重要提醒：**TS 只是编译期静态类型，不能校验运行时 AI 返回的真实字符串！**
>
> - 模板字面量类型 = 编译期类型契约，告诉开发者“AI应该返回这个格式”
> - **运行时必须搭配正则 / Zod 做实际校验**，否则模型乱输出字符串类型不会报错。

## 基础语法回顾

```
// 模板字面量类型
type Event = `on${string}`;
type Num = `num-${number}`;
```

---

## 场景1：约束 ISO 日期字符串 `2026-08-24`

期望格式：`YYYY-MM-DD`

> TS不能做完整数字范围校验（不能限制月份只能1‑12），只能约束**字符串结构**；数值合法性交给运行时正则。

```
// 模板字面量：YYYY‑MM‑DD 结构
type Year = `${number}`;
type Month = `0${1|2|3|4|5|6|7|8|9}` | `1${0|1|2}`;
type Day = `0${1|2|3|4|5|6|7|8|9}` | `${1|2}${number}` | `3${0|1}`;

type ISODateYMD = `${Year}-${Month}-${Day}`;

// ✅合法
const d1: ISODateYMD = "2026-08-24";
// ❌TS报错，格式不对
// const d2: ISODateYMD = "2026/08/24";
// const d3: ISODateYMD = "2026‑13‑01"; // 月份13，TS不会拦截！只是结构，不是数值校验
```

> 坑：上面 `Month` 只能约束字符串是`01‑09`、`10‑12`，但`${number}`会允许`19`这种；**模板字面量无法限制数字大小，只能限制字符串文本模式**。

## 场景2：自定义业务ID，例如 `biz‑10086`、`task‑456`

格式：`task‑<数字>`

```
type TaskId = `task‑${number}`;

const idA: TaskId = "task‑1234";
// const idB: TaskId = "task‑abc"; // TS报错
// const idC: TaskId = "tsk‑123"; // TS报错
```

## 场景3：UUID简易格式约束（只约束结构，不校验UUID校验和）

```
type HexChar = "0"|"1"|"2"|"3"|"4"|"5"|"6"|"7"|"8"|"9"
  |"a"|"b"|"c"|"d"|"e"|"f";

type UUIDPart32 = `${HexChar}${HexChar}${HexChar}${HexChar}${HexChar}${HexChar}${HexChar}${HexChar}`;
type UUIDPart16 = `${HexChar}${HexChar}${HexChar}${HexChar}`;

// uuid v4 结构 xxxxxxxx‑xxxx‑4xxx‑xxxx‑xxxxxxxxxxxx
type UUIDLike = `${UUIDPart32}-${UUIDPart16}-4${UUIDPart16}-${UUIDPart16}-${UUIDPart32}`;

const u: UUIDLike = "a1b2c3d4‑1234‑4567‑89ab‑a1b2c3d4e5f6";
```

## 场景4：约束AI返回固定前缀字符串，例如 `RESULT:{"..."}`

大模型要求输出必须以 `RESULT:` 开头，后面接JSON字符串。

```
type AiResultWrapper = `RESULT:${string}`;

// AI返回必须是这个格式
function parseAiOutput(raw: string): AiResultWrapper | null {
  if(raw.startsWith("RESULT:")){
    return raw as AiResultWrapper;
  }
  return null;
}
```

## 场景5：联合+模板字面量，限定一组命令

AI只能返回指定命令：`cmd:create`、`cmd:delete`、`cmd:update`

```
type Command = "create" | "delete" | "update";
type AiCommand = `cmd:${Command}`;

// ✅
const c1: AiCommand = "cmd:create";
// ❌TS报错
// const c2: AiCommand = "cmd:query";
```

---

# 真实AI业务完整模式：模板字面量类型 + Zod运行时校验

> **模板字面量 = 编译期类型契约（给TS看）；Zod正则 = 运行时校验（校验AI真实返回）**
> 只靠模板字面量，AI返回乱字符串，`as`强制转型会绕过TS，类型完全失效。

```
import { z } from "zod";

// 1.TS模板字面量类型（编译期）
type TaskId = `task‑${number}`;

// 2.Zod运行时校验AI输出字符串
const TaskIdSchema = z
  .string()
  .regex(/^task‑\d+$/, "必须为 task‑数字 格式")
  // z.infer 提取出TS类型，和模板字面量对齐
  .brand<TaskId>();

// 从schema提取类型
type TaskIdSafe = z.infer<typeof TaskIdSchema>;

/**
 * 接收AI原始返回字符串，做运行时校验
 */
function safeGetTaskId(aiRawText: string): TaskIdSafe {
  return TaskIdSchema.parse(aiRawText);
}

// 使用
const aiReturn = "task‑996";
const tid = safeGetTaskId(aiReturn);
```

> `.brand<T>()` 是Zod品牌类型，实现**不透明类型**：即使底层都是string，普通string不能直接赋值给`TaskIdSafe`，防止随便传字符串。

## 结合之前PromptTemplate使用示例

```
// AI提示词里告诉模型：输出task‑数字格式
const prompt = new PromptTemplate<{query:string}>({
  role:"user",
  template:"请输出任务ID，格式严格为 task‑数字，不要多余文字，输入：${query}"
});

// 调用大模型拿到rawReply:string
// const rawReply = await llm.chat(messages);
// const taskId = safeGetTaskId(rawReply.trim());
```

---

# 关键限制（非常重要）

1. **模板字面量类型只是编译期静态检查，运行时完全无效**

```
type TaskId = `task‑${number}`;
const fake = "hello" as TaskId; // as强制转型可以绕过TS！AI返回的字符串本质是string
```

2. 无法做**数字范围校验**：例如想限制月份只能1‑12，模板字面量只能做到部分枚举，不能校验数值大小。
3. 复杂正则模式（复杂日期、UUID完整校验）**不要指望TS类型完成，必须运行时正则/Zod**。

## 技巧：提取模板字面量中的参数

TS可以用`infer`提取模板字面量里面的部分：

```
type TaskId = `task‑${number}`;

type ExtractTaskNum<T extends string> =
  T extends `task‑${infer N}` ? N : never;

// 提取出 "1234"
type Num = ExtractTaskNum<"task‑1234">;
```

可以用来：解析AI返回结构化字符串，在类型层面拆分ID里的编号。

---

# 总结最佳实践

1. **模板字面量类型**：用于定义期望输出格式，给IDE提示、约束业务代码，属于「文档化类型契约」。
2. **运行时一定需要 Zod + RegExp**：校验大模型真实返回字符串，AI输出不可信。
3. 使用 Zod Branded Type（品牌类型），防止普通string随意混入格式字符串。
4. Prompt模板中**必须同步告诉AI输出格式**，类型只是代码约束，不能约束模型行为。

如果你想要，我可以写一个完整Demo：把「Prompt模板 + 模板字面量输出类型 + Zod校验 + infer提取字段」串成一套完整AI输出强类型链路。

---

---

# 第五条：设计一个类型系统，用于描述AI Agent执行过程中的状态流转（如思考→执行→观察→完成），并实现类型安全的状态切换

# AI Agent 状态流转类型系统设计

状态流转：**思考(think) → 执行(action) → 观察(observation) → 完成(done)**
流转规则：

1. `think`：Agent内部推理思考，输出下一步要执行什么工具
2. `action`：发起工具调用（tool_call）
3. `observation`：拿到工具返回的观测结果
4. `done`：任务结束，输出最终结果

流转约束：

- think → action 合法
- action → observation 合法
- observation → think / done 合法（拿到观测可以继续思考，也可以直接结束）
- done 为终态，不能再跳转其他状态
- 禁止非法跳转：例如 observation 不能直接跳到 action；done 不允许切换出去

目标：

1. TS 类型层面**禁止非法状态跳转**；
2. 每个状态携带专属数据结构；
3. 状态机实例，提供状态切换方法；
4. 运行时校验，防止运行时非法跳转；
5. 和前面的 PromptTemplate、tool‑call 消息结构打通。

> 核心技术：**可区分联合(Discriminated Union) + 状态转换映射类型**，编译期拦截非法状态迁移。

```
import { z } from "zod";

// -------------------------- 1. 基础类型定义 --------------------------
export type AgentStateName = "think" | "action" | "observation" | "done";

/**
 * think：Agent思考，产出下一步计划/工具调用意图
 */
interface AgentThinkState {
  state: "think";
  thought: string; // Agent思考文本
  intendedToolCall?: {
    name: string;
    arguments: Record<string, unknown>;
  };
}

/**
 * action：执行工具调用
 */
interface AgentActionState {
  state: "action";
  toolCallId: string;
  toolName: string;
  toolArguments: Record<string, unknown>;
}

/**
 * observation：工具返回观测结果
 */
interface AgentObservationState {
  state: "observation";
  toolCallId: string;
  content: string; // 工具返回原始内容
  error?: string; // 工具调用错误
}

/**
 * done：任务终态，完成
 */
interface AgentDoneState {
  state: "done";
  finalAnswer: string;
  isSuccess: boolean;
}

// Agent全部状态联合类型
export type AgentState = AgentThinkState | AgentActionState | AgentObservationState | AgentDoneState;

/**
 * 🎯 核心：类型层面允许的状态迁移表
 * key = 当前状态；value = 可以跳转到哪些状态
 */
type StateTransitionMap = {
  think: "action";
  action: "observation";
  observation: "think" | "done";
  done: never; // done 终态，不能跳转任何状态
};

/**
 * 根据当前状态，得到允许跳转的目标状态类型
 */
type AllowedNextState<T extends AgentStateName> = StateTransitionMap[T];

// -------------------------- 2. Zod运行时Schema（AI返回/序列化校验） --------------------------
const AgentThinkStateSchema = z.object({
  state: z.literal("think"),
  thought: z.string(),
  intendedToolCall: z
    .object({
      name: z.string(),
      arguments: z.record(z.unknown()),
    })
    .optional(),
});

const AgentActionStateSchema = z.object({
  state: z.literal("action"),
  toolCallId: z.string(),
  toolName: z.string(),
  toolArguments: z.record(z.unknown()),
});

const AgentObservationStateSchema = z.object({
  state: z.literal("observation"),
  toolCallId: z.string(),
  content: z.string(),
  error: z.string().optional(),
});

const AgentDoneStateSchema = z.object({
  state: z.literal("done"),
  finalAnswer: z.string(),
  isSuccess: z.boolean(),
});

export const AgentStateSchema = z.discriminatedUnion("state", [
  AgentThinkStateSchema,
  AgentActionStateSchema,
  AgentObservationStateSchema,
  AgentDoneStateSchema,
]);

// -------------------------- 3. Agent状态机类：类型安全的状态切换 --------------------------
export class AgentStateMachine {
  private _currentState: AgentState;

  /**
   * 初始化，必须从 think 开始
   */
  constructor(initThought: string) {
    this._currentState = {
      state: "think",
      thought: initThought,
    };
  }

  public get current(): AgentState {
    return this._currentState;
  }

  public get stateName(): AgentStateName {
    return this._currentState.state;
  }

  /**
   * 类型安全状态跳转
   * 泛型 TCurrentStateName 锁定当前状态；TNextStateName 只能是允许的下一个状态
   */
  transition<
    TCurrentStateName extends AgentStateName,
    TNextStateName extends AllowedNextState<TCurrentStateName>
  >(nextState: Extract<AgentState, { state: TNextStateName }>): void {
    const curStateName = this._currentState.state as TCurrentStateName;
    const targetStateName = nextState.state as TNextStateName;

    // 运行时校验：防止绕过TS强制as做非法跳转
    const allowed: AgentStateName[] = ((): AgentStateName[] => {
      const map: Record<AgentStateName, AgentStateName[]> = {
        think: ["action"],
        action: ["observation"],
        observation: ["think", "done"],
        done: [],
      };
      return map[curStateName];
    })();

    if (!allowed.includes(targetStateName)) {
      throw new Error(
        `非法状态流转：${curStateName} → ${targetStateName}。允许下一个：${allowed.join(",")}`
      );
    }

    this._currentState = nextState;
  }

  /**
   * 判断是否任务结束
   */
  isFinished(): boolean {
    return this._currentState.state === "done";
  }

  /**
   * 导出可序列化JSON，用于日志、保存Agent快照
   */
  toJSON(): AgentState {
    return AgentStateSchema.parse(this._currentState);
  }
}
```

## 📖 使用示例

```
// 1. 实例化状态机，初始状态 think
const agent = new AgentStateMachine("我需要查询用户信息，调用query_user工具");
console.log(agent.current); // think

// 2. think → action 合法跳转
agent.transition({
  state: "action",
  toolCallId: "call_001",
  toolName: "query_user",
  toolArguments: { userId: 1001 },
});

// 3. action → observation 合法跳转
agent.transition({
  state: "observation",
  toolCallId: "call_001",
  content: "用户姓名：张三，年龄28",
});

// 4. observation → think：继续思考，继续循环Agent
agent.transition({
  state: "think",
  thought: "拿到用户信息，还需要查询订单，继续调用工具",
});

// think → action ... 循环若干轮

// observation → done：结束任务
agent.transition({
  state: "done",
  finalAnswer: "用户张三，28岁，暂无订单",
  isSuccess: true,
});

console.log(agent.isFinished()); // true

// agent.transition({ state:"think", thought:"xxx" })
// ✨编译期直接报错：done状态不允许任何transition；同时运行时也抛异常
```

### 非法跳转演示（TS编译报错）

```
// 当前是 done，尝试跳 think：TS直接红线报错
// agent.transition({ state: "think", thought: "继续干活" });

// 当前 think，尝试直接跳 observation：TS编译报错
// agent.transition({ state:"observation", toolCallId:"xxx", content:"" })
```

## 与 LLM / PromptTemplate 结合

Agent每一轮循环流程：

1. 当前状态 `think`，把历史状态快照塞入PromptTemplate，给到LLM；
2. LLM输出思考+tool_call意图；
3. 状态机 `transition` 到 `action`；
4. 本地执行工具函数；
5. `transition` 到 `observation`；
6. 判断是否可以结束，跳 `done`，否则跳回 `think`，循环。

```
// 伪代码
/*
while (!agent.isFinished()) {
  const messages = promptTemplate.render({
    agentHistory: JSON.stringify(agent.toJSON()),
  });
  const llmResp = await llm.chat(messages);
  // 解析llmResp，生成nextState
  agent.transition(nextState);
}
*/
```

## 关键设计要点解析

1. **可区分联合 `state` 作为判别字段**
   每个状态结构完全不一样，TS可以根据`state`自动收窄类型。
2. `StateTransitionMap` + `AllowedNextState<T>`

> 编译期计算出当前状态允许跳转的目标，**编译器直接拦截非法状态**，IDE有完整提示。

3. **双重防护：编译期类型 + 运行时校验**

- TS防止正常编码写错流转；
- Zod + transition内部运行时校验，防止JSON解析、AI返回、强制类型转换`as`绕过类型系统。

4. `done` 为终态，`StateTransitionMap["done"] = never`，泛型直接禁止传入任何状态。

## 扩展点（可继续迭代）

1. 增加 `error` 异常状态，工具调用失败分支；
2. 增加状态历史栈，保存每一步快照，支持回溯；
3. 把该状态嵌入之前的 `PromptTemplate`，自动序列化agent历史上下文；
4. 增加状态钩子 `onTransition(from,to) => void`，用于日志、埋点；
5. 序列化/反序列化，支持Agent断点续跑，从快照恢复状态机。

如果你需要，我可以扩展一版：**完整Agent循环Run函数，包含消息拼接、工具调用分发、状态自动流转，把前面PromptTemplate、Message类型、本状态机全部整合为一套完整Agent骨架。**

---

---
