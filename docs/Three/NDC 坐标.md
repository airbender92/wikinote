# NDC 标准化设备坐标（Three.js）

全称：Normalized Device Coordinates，**标准化设备坐标**

> 
> 范围：`x ∈ [-1, 1]`，`y ∈ [-1, 1]`

- 画布**中心**：`(0, 0)`
- 画布**左侧**：x = -1；画布**右侧**：x = 1
- 画布**顶部**：y = 1；画布**底部**：y = -1> 
> ✅ 重点：网页鼠标Y向下增大，**NDC Y轴方向相反**

## 转换关系：画布像素坐标 → NDC

网页坐标系（canvas容器左上角原点，0,0）

```
xRatio = 相对画布左距离 / 画布宽度      // 0 ~ 1
yRatio = 相对画布上距离 / 画布高度      // 0 ~ 1

ndcX = xRatio * 2 - 1
ndcY = -(yRatio * 2 - 1)
```

### 校验点位

| 点击位置 | xRatio | yRatio | ndcX | ndcY |
| --- | --- | --- | --- | --- |
| 左上角 | 0 | 0 | -1 | 1 |
| 中心点 | 0.5 | 0.5 | 0 | 0 |
| 右下角 | 1 | 1 | 1 | -1 |

## Three.js 标准写法（Raycaster 拾取专用）

```
import * as THREE from 'three'

const mouse = new THREE.Vector2()
const raycaster = new THREE.Raycaster()

// e：React.MouseEvent，绑定在canvas外层容器
function updateNDC(e: React.MouseEvent<HTMLElement>) {
  const rect = e.currentTarget.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top

  mouse.x = (x / rect.width) * 2 - 1
  mouse.y = -( (y / rect.height) * 2 - 1 )

  // 射线
  raycaster.setFromCamera(mouse, camera)
  const hits = raycaster.intersectObjects(scene.children, true)
}
```

## 反向转换：NDC → 画布像素坐标

```
// ndcX, ndcY [-1,1]
const xRatio = (ndcX + 1) / 2
const yRatio = 1 - (ndcY + 1) / 2
const pixelX = xRatio * rect.width
const pixelY = yRatio * rect.height
```

# 关键坑点

1. **CSS尺寸 vs canvas分辨率**
`getBoundingClientRect()` 获取的是CSS渲染大小，**适合Raycaster拾取**。

> 
> 不要用 canvas.offsetWidth！当canvas用css缩放时，offsetWidth和画布像素尺寸不一致会拾取错位。
2. NDC ≠ 世界坐标

- NDC：屏幕投影后的二维坐标，只和相机、画布有关
- 世界坐标：3D场景里物体真实xyz，需要射线计算交点才能拿到

3. 为什么Y要加负号？
浏览器屏幕坐标系：**向下Y变大**
OpenGL/Three NDC：**向上Y变大**，所以必须翻转Y。

## 精简工具函数

```
/**
 * React鼠标事件 直接生成Three NDC Vector2
 */
export function toNDC(e: React.MouseEvent<HTMLElement>, out: THREE.Vector2) {
  const rect = e.currentTarget.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top
  out.x = (x / rect.width) * 2 - 1
  out.y = -( (y / rect.height) * 2 - 1 )
  return out
}
```

需要我顺便把**射线拿到交点的世界坐标**的完整代码一并写出来吗？