# NPM scripts 钩子命令解析（出自《深入浅出Node.js》2.6.3）

> `scripts` 是 `package.json` 的脚本钩子字段，**NPM 在特定生命周期自动执行对应脚本**，C/C++ 原生扩展模块（`.node`）就高度依赖`install`钩子完成编译。

```json
"scripts": {
  "preinstall": "node preinstall.js",
  "install": "node install.js",
  "uninstall": "node uninstall.js",
  "test": "node test.js"
}
```

## 一、生命周期钩子执行顺序

### 1. `npm install <pkg>` 安装外部包

1. `preinstall` → 执行脚本
2. `install` → 执行脚本

> ✨ **C/C++扩展模块核心场景**：很多原生模块，在`install`脚本调用`node‑gyp rebuild`，自动编译C/C++源码生成`.node`二进制模块。

```json
"scripts": {
  "install": "node‑gyp rebuild"
}
```

> 注意：
>
> - `preinstall` / `install` 是**被安装包自身的钩子**。别人安装你的包，你的包的scripts钩子会运行。
> - ⚠️安全风险：下载第三方包，它的`preinstall/install`会自动执行脚本，可能执行恶意代码。

### 2. `npm uninstall <pkg>` 卸载包

1. `uninstall`：包被卸载前执行，用于清理本地生成文件、缓存。

### 3. `npm test`

直接执行：`npm run test` /简写`npm test`，运行测试套件。
高质量开源包都会配置该脚本，使用者下载后直接执行`npm test`验证包是否正常工作。

## 二、pre / post 通用钩子规则

NPM约定命名规范：**任意脚本，都可以增加`pre‑`、`post‑`前缀，自动成为前置、后置钩子**。

示例：

```json
{
  "scripts": {
    "pretest": "echo 测试开始",
    "test": "mocha",
    "posttest": "echo 测试结束"
  }
}
```

运行`npm test`执行顺序：
`pretest` → `test` → `posttest`

内置支持这套规则：`start / stop / restart / test`都支持`pre/post`钩子。

## 三、常用内置脚本命令（npm简写，不需要写run）

| 命令          | 等价                                                                   | 说明         |
| ------------- | ---------------------------------------------------------------------- | ------------ |
| `npm test`    | `npm run test`                                                         | 执行测试脚本 |
| `npm start`   | `npm run start`                                                        | 启动项目服务 |
| `npm stop`    | `npm run stop`                                                         | 停止服务     |
| `npm restart` | `npm run prestop && npm run stop && npm run prestart && npm run start` | 重启         |

普通自定义脚本**必须使用 `npm run xxx`**，没有简写。

## 四、重要注意点

1. **脚本执行环境**
   脚本运行时，`node_modules/.bin`目录会加入PATH，项目本地安装的依赖命令可以直接写名字，不用写完整路径。
   比如本地装了`mocha`，直接写 `"test":"mocha"`即可。

2. 执行时机区分

- 当你**在自己项目目录执行npm install**：执行你自己项目的`preinstall`，然后安装dependencies；
- 安装第三方依赖包的时候：**执行第三方包自己的scripts钩子，不是你项目的**。

3. C/C++扩展模块工作流程
1. 用户执行`npm install xxx`；
1. 下载包源码；
1. 触发包`install`脚本；
1. 调用`node‑gyp rebuild`，读取`binding.gyp`编译C/C++代码，输出`build/Release/*.node`；
1. JS代码通过`require('./build/Release/xxx.node')`加载编译后的原生模块。

> 这也是部分原生模块安装失败的根源：本机缺少编译工具链（python、VC++、gcc等），`node‑gyp`编译报错。

4. 安全提醒

> 不要随意安装不知名npm包，`preinstall/install`钩子会自动执行shell/node脚本，可以做文件读写、网络请求。

## 五、拓展其他生命周期钩子（书中只提到一部分）

还有这些钩子：

- `prepare`：执行在打包、发布、本地npm install，常用于编译ts源代码
- `prepublishOnly`：发布包之前执行

### 示例完整scripts参考

```json
{
  "scripts": {
    "preinstall": "echo 开始安装包",
    "install": "node‑gyp rebuild",
    "uninstall": "rm‑rf ./build",
    "pretest": "echo 准备执行单元测试",
    "test": "mocha ./test/**/*.test.js",
    "posttest": "echo 单元测试执行完毕"
  }
}
```

## 补充书中原文思考题

> 为什么C/C++扩展模块包需要配置`"install":"node‑gyp rebuild"`钩子？
> 答：
> C/C++源码不能直接被Node加载，必须编译成对应操作系统、CPU架构下的`.node`动态链接库。不同Windows/Linux/macOS二进制不能通用。发布npm包一般不携带编译产物。依靠install钩子，用户本地机器上现场编译源码生成`.node`文件。

如果你需要，我可以给你对比 `preinstall` 和 `prepare` 的区别，或者出几道选择题巩固知识点。
