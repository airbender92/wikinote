`ArrayList` 的 **`isEmpty()`** 方法，作用是：
**判断集合是否为空（里面有没有元素）**

---

## 方法说明
```java
public boolean isEmpty()
```
- 返回 `true`：集合里**一个元素都没有**
- 返回 `false`：集合里**至少有一个元素**

---

## 示例代码
```java
import java.util.ArrayList;

public class Test {
    public static void main(String[] args) {
        ArrayList<String> list = new ArrayList<>();

        System.out.println(list.isEmpty()); // true，刚创建是空的

        list.add("hello");

        System.out.println(list.isEmpty()); // false，有元素了
    }
}
```

---

## 小知识点
- `isEmpty()` 和 `size() == 0` **效果完全一样**
- 但日常写代码更推荐用 `isEmpty()`，更直观、可读性更好

需要我顺便给你对比一下 `clear()`、`remove()` 吗？