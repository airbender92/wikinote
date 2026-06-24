`ArrayList` 的 `indexOf()` 方法，作用是：**返回指定元素第一次出现的索引位置**，如果找不到就返回 `-1`。

---

### 1. 方法签名
```java
public int indexOf(Object o)
```

### 2. 作用
- 遍历列表，**从前往后找**第一个等于 `o` 的元素
- 找到：返回对应的下标（从 0 开始）
- 没找到：返回 `-1`

---

### 3. 简单示例
```java
import java.util.ArrayList;

public class Test {
    public static void main(String[] args) {
        ArrayList<String> list = new ArrayList<>();
        list.add("A");
        list.add("B");
        list.add("C");
        list.add("B");

        System.out.println(list.indexOf("B"));  // 1（第一次出现的位置）
        System.out.println(list.indexOf("X"));  // -1（不存在）
    }
}
```

输出：
```
1
-1
```

---

### 4. 注意点
- **区分大小写、精确匹配**
- 查找 `null` 也可以：`list.indexOf(null)`
- 判断相等用的是 `equals()`，自定义对象要正确重写 `equals()` 和 `hashCode()`
- 时间复杂度：**O(n)**，要从头到尾遍历

---

需要我顺便给你讲 `lastIndexOf()`（从后往前找）或者对比 `contains()` 的区别吗？