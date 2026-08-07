import { createServer } from 'http'
import httpProxy from 'http-proxy'

// 路由
const routing = [
  { path: '/api', service: 'api-service', index: 0 },
  { path: '/', service: 'webapp-service', index: 0 }
]

const proxy = httpProxy.createProxyServer({})

// 直接用 HTTP 访问 Consul API，不依赖烂包
async function getServiceInstances(serviceName) {
  const res = await fetch('http://127.0.0.1:8500/v1/agent/services')
  const data = await res.json()

  return Object.values(data).filter(s => s.Service === serviceName)
}

const server = createServer(async (req, res) => {
  console.log('➡️ 请求:', req.url)

  const route = routing.find(r => req.url.startsWith(r.path))
  if (!route) {
    res.writeHead(404).end('Not Found')
    return
  }

  try {
    const instances = await getServiceInstances(route.service)
    console.log('✅ 实例数:', instances.length)

    if (instances.length === 0) {
      res.writeHead(502).end('No instance')
      return
    }

    // 轮询
    route.index = (route.index + 1) % instances.length
    const target = instances[route.index]
    const targetUrl = `http://${target.Address}:${target.Port}`

    console.log('🎯 转发:', targetUrl)

    proxy.web(req, res, { target: targetUrl }, (err) => {
      console.error('代理错误:', err)
      res.writeHead(503).end('Proxy error')
    })

  } catch (err) {
    console.error('❌ 错误:', err.message)
    res.writeHead(500).end('Error')
  }
})

server.listen(8090, () => {
  console.log('✅ 网关已启动 :8090')
})