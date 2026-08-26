```js
import { Modal } from "antd";

/**
 * 封装Modal.confirm 为 Promise
 * 如果onOk有异步，可通过throw new Error(''); 抛出错误阻止弹窗关闭
 * 在业务里使用try{}catch(){}，catch里捕获reject (error)
 * @param {*} config
 * @returns
 */
const confirmModal = (config) => {
  return new Promise((resolve, reject) => {
    Modal.confirm({
      ...config,
      // 允许 onOk 传入异步函数，弹窗会等待其执行完成
      onOk: async () => {
        try {
          if (config.onOk) {
            await config.onOk();
          }
          resolve(true);
        } catch (error) {
          // 若中间出错，可阻止弹窗关闭并reject
          reject(error);
        }
      },
      onCancel: () => {
        resolve(false);
      },
    });
  });
};

export { confirmModal };
```

```js
// 使用
const handleDel = async () => {
  const isConfirmed = await confirmModal({
    title: "提示",
    content: "确认删除？",
    okText: "确认",
    cancelText: "取消",
  });
  if (!isConfirmed) {
    return;
  }
};
```
