# 组件通信 —— props
一句话：
**父组件 → 子组件 传数据的唯一标准方式。**

---

## 1. 基本使用
父组件：
```vue
<Child :title="title" :list="list" />
```

子组件接收：
```vue
<script setup>
const props = defineProps({
  title: String,
  list: {
    type: Array,
    default: () => []
  }
})
</script>
```

---

## 2. 特点
- **单向数据流**：父 → 子可以，子不能直接改 props
- 子改 props 会报警告（防止数据混乱）
- 父数据更新，子 props 自动更新（响应式）

---

## 3. 子组件想“改”props 怎么办？
### 方法 1：emit 让父自己改（标准）
父：
```vue
<Child :count="count" @update:count="count = $event" />
```

子：
```js
const props = defineProps(['count'])
const emit = defineEmits(['update:count'])

function change() {
  emit('update:count', 100)
}
```

### 方法 2：子复制到本地变量
```js
const props = defineProps(['count'])
const localCount = ref(props.count)
```

### 方法 3：v-model 封装（语法糖）
父：
```vue
<Child v-model:count="count" />
```

子：
```js
const props = defineProps(['count'])
const emit = defineEmits(['update:count'])
```

---

## 4. 常用配置
```js
defineProps({
  // 类型
  title: String,

  // 必传
  list: {
    type: Array,
    required: true
  },

  // 默认值
  visible: {
    type: Boolean,
    default: false
  },

  // 自定义验证
  size: {
    type: String,
    validator: (val) => ['small', 'large'].includes(val)
  }
})
```

---

## 5. 注意点
- **不要直接修改 props**
- 对象/数组是引用类型，子修改会影响父（虽然能改，但不规范）
- props 是**只读**的

---

# 一句话总结
- **props 是父传子**
- 单向数据流
- 子要改 → 用 emit 通知父
- 是 Vue 最基础、最常用、最稳定的通信方式

接下来我可以给你讲：**emit、v-model、ref/$parent、provide/inject、eventBus、pinia** 全套通信方式，按场景帮你分清楚。