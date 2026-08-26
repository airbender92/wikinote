const http = require("http");
const port = 3000;

const server = http.createServer((req, res) => {
  // 设置跨域头 （本地调试需要，使用nginx反向代理后可删除）
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Content-Type", "application/json;charset=utf-8");

  // /api/getData
  if (req.url === "/api/getData" && req.method === "GET") {
    const result = {
      code: 200,
      msg: "来自node后端接口数据",
      data: [11, 22, 33, 44],
    };
    res.writeHead(200);
    res.end(JSON.stringify(result));
    return;
  }

  // 其他路径返回404，因为静态全部由nginx处理
  res.writeHead(404, { "Content-Type": "text/plain;charset=utf-8" });
  res.end("node: 接口不存在");
});

server.listen(port, () => {
  console.log(`node 接口服务启动：http://127.0.0.1:${port}`);
});
