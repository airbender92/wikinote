var http = require('http');
var querystring = require('querystring');
const handler = require('serve-handler');

http.createServer(async function (req, res) {
    // 跨域头
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', "GET,POST,OPTIONS");
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    // 处理预检OPTIONS
    if (req.method === 'OPTIONS') {
        res.writeHead(200);
        res.end();
        return;
    }

    // 👉 自定义接口路由示例：/api
    if (req.url === '/api' && req.method === 'POST') {
        let postData = '';
        req.setEncoding('utf-8');
        req.on('data', function (chunk) {
            postData += chunk;
        });
        req.on('end', function () {
            console.log('收到post数据：', postData);
            // 原样返回
            res.end(postData);
        });
        return; // 必须return，不再往下执行静态服务
    }

    // 不属于接口的请求，交给serve-handler读取www目录静态文件
    await handler(req, res, {
        public: 'www'
    });

}).listen(8080)

console.log('服务启动 http://localhost:8080');