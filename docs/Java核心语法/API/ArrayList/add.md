`ArrayList` 的 `add()` 就是**往集合里添加元素**的方法。

---

### 1. 最基本用法
```java
// 创建一个存整数的集合
ArrayList<Integer> list = new ArrayList<>();

// 添加元素
list.add(10);
list.add(20);
list.add(30);
```

现在集合里就是：`[10, 20, 30]`

---

### 2. 你代码里的用法
```java
ArrayList<Integer> locations = new ArrayList<>();
locations.add(randomNum);
locations.add(randomNum + 1);
locations.add(randomNum + 2);
```

就是连续添加 3 个数字，用来表示战舰的 3 个位置。

---

### 3. 两个常用版本
1. **加到末尾**
   ```java
   list.add(元素);
   ```

2. **插到指定位置**（索引从 0 开始）
   ```java
   list.add(1, 15);
   ```
   结果：`[10, 15, 20, 30]`

---

### 4. 关键点
- `add()` 会让集合**自动变长**，不用管长度
- 只能加**对象**，`int` 会自动装箱成 `Integer`
- 每次 `add` 都是加在最后面

---

简单记：
**ArrayList.add(东西) = 把东西放进集合里。**