# emit
一句话：
**子组件 → 父组件 发送消息、触发事件**
用来**子改父**、通知父组件做事。

---

# 1. 基本用法（Vue3 + script setup）
## 子组件
```vue
<script setup>
// 定义要触发的事件名
const emit = defineEmits(['sayHi', 'change'])

function send() {
  // 触发事件，传参数
  emit('sayHi', 'Hello 父组件')
}
</script>

<button @click="send">点我通知父组件</button>
```

## 父组件
```vue
<Child @sayHi="handleHi" />

<script setup>
function handleHi(msg) {
  console.log(msg) // Hello 父组件
}
</script>
```

---

# 2. 最经典场景：子组件修改 props
props 是**单向数据流**，子不能直接改，必须 emit 让父改。

子组件：
```js
const props = defineProps(['count'])
const emit = defineEmits(['update:count'])

function add() {
  emit('update:count', props.count + 1)
}
```

父组件：
```vue
<Child :count="count" @update:count="count = $event" />
```

---

# 3. 进阶：封装 v-model（本质就是 emit）
父组件：
```vue
<Child v-model:num="num" />
```

子组件：
```js
const props = defineProps(['num'])
const emit = defineEmits(['update:num'])

// 修改时
emit('update:num', 666)
```

这就是 Vue 双向绑定的**真面目**。

---

# 4. 一次传多个参数
子：
```js
emit('info', '张三', 18, '男')
```

父：
```js
function handleInfo(name, age, gender) { ... }
```

---

# 5. 超级简单总结
- **props：父 → 子 传数据**
- **emit：子 → 父 发事件/传数据**
- 子想改数据 → 不许直接改 → 用 emit 通知父
- v-model 本质就是 `props + emit`

这两个是 Vue 组件通信**最核心、最基础、用得最多**的一对。