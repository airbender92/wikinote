/**
 * nodejs 挂载静态资源
 */
const http = require("http");
const fs = require("fs");
const path = require("path");

const port = 3000;

const server = http.createServer((req, res) => {
  const filePath = path.join(__dirname, "www", "index.html");

  fs.readFile(filePath, (err, data) => {
    if (err) {
      res.writeHead(404, { "Content-Type": "text/plain" });
      res.end("404 文件找不到");
      return;
    }
    res.writeHead(200, { "Content-Type": "text/html;charset=utf-8" });
    res.end(data);
  });
});

server.listen(port, () => {
  console.log(`服务启动，访问：http://127.0.0.1:${port}`);
});
