这段代码就是**用 HashMap 统计每个单词出现次数**的核心逻辑，我一句一句给你讲明白。

# 先看整体
```java
Map<String, Integer> countMap = new HashMap<>();

for(String word : words){
    countMap.put(word, countMap.getOrDefault(word, 0) + 1);
}
```

---

# 1. 第一行
```java
Map<String, Integer> countMap = new HashMap<>();
```
- 创建一个 **HashMap**
- `key` 是单词：`String`
- `value` 是这个单词出现的次数：`Integer`

---

# 2. 循环
```java
for(String word : words) {
```
遍历刚才 `split` 出来的所有单词：
hello、java、hello、world、java、java、spring、springboot

---

# 3. 最关键一行（重点）
```java
countMap.put(word, countMap.getOrDefault(word, 0) + 1);
```

### `getOrDefault(word, 0)` 是什么？
- 去 map 里**查这个单词当前的次数**
- 如果**已经存在**，就返回它的次数
- 如果**不存在**，就返回默认值 **0**

然后 **+1**，再 `put` 回去，就实现了计数。

---

# 举个例子你就秒懂
### 第一次遇到 `hello`
- `getOrDefault("hello", 0)` → 0
- 0 + 1 = 1
- put → `hello=1`

### 第二次遇到 `hello`
- `getOrDefault("hello", 0)` → 1
- 1 + 1 = 2
- put → `hello=2`

### 遇到 `java` 也是一样
第一次：1
第二次：2
第三次：3

---

# 最终统计结果
```
hello=2
java=3
world=1
spring=1
springboot=1
```

---

# 一句话总结
这行代码的作用就是：
**遍历每个单词，有就次数+1，没有就从0开始+1，最后得到每个单词出现多少次。**

如果你需要，我可以把**完整可运行的单词统计程序**直接写给你。