`Integer.parseInt` 就是：
**把字符串里的数字 → 转成 int 基本类型**

---

## 一句话用法
```java
int 数字 = Integer.parseInt(字符串);
```

比如：
```java
String s = "5";
int num = Integer.parseInt(s); // num 变成 5
```

---

## 为什么你代码里要用它？
你代码里用户输入的是**字符串**：
```java
String stringGuess = "7";
```

但你要拿去**跟数字比较**，所以必须转成 int：
```java
int guess = Integer.parseInt(stringGuess);
```

不然字符串和数字没法直接比大小。

---

## 和 Integer.valueOf 的区别（超级重要）
- `Integer.parseInt("123")` → 返回 **int**
- `Integer.valueOf("123")`  → 返回 **Integer**

在你代码里：
```java
int guess = Integer.parseInt(stringGuess);
```
这里必须用 `parseInt`，因为 guess 是 int 类型。

---

## 总结
- `Integer.parseInt(字符串)` → 转成 **int**
- 专门用来处理用户输入的数字字符串
- 不能转字母，否则会报错