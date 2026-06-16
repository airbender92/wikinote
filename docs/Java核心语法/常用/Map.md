这段代码就是**把刚才统计好的单词次数，循环打印出来**，我给你讲得清清楚楚。

# 代码逐行解释
```java
for (Map.Entry<String, Integer> entry : countMap.entrySet()) {
    System.out.println(entry.getKey() + " : " + entry.getValue());
}
```

---

## 1. `countMap.entrySet()`
- `entrySet()` 是 Map 的方法
- 作用：把 Map 里的**所有键值对**打包成一个 **Set 集合**
- 每个元素就是一个 **`Map.Entry`** 对象

---

## 2. `Map.Entry<String, Integer> entry`
- `Entry` 就是一个**键值对**
- 包含两部分：
  - `getKey()`：拿到 key（单词）
  - `getValue()`：拿到 value（出现次数）

---

## 3. 循环内部
```java
entry.getKey()      // 获取单词
entry.getValue()    // 获取次数
```

所以输出类似：
```
hello : 2
java : 3
world : 1
spring : 1
springboot : 1
```

---

# 最简单总结
这就是**遍历 Map 的标准写法**：
拿到每一对 **key-value**，然后打印单词和次数。

---

# 你可能还会见到的两种写法（了解即可）

### 方式2：只遍历 key
```java
for (String key : countMap.keySet()) {
    System.out.println(key + " : " + countMap.get(key));
}
```

### 方式3：Java 8  Lambda
```java
countMap.forEach((k, v) -> System.out.println(k + " : " + v));
```

效果都一样，你用的那种**最经典、最常用**。